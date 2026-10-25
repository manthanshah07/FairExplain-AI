"""
FairExplain AI — Authentication Service
=========================================
Business service managing user registration, credential verification,
and Refresh Token Rotation (RTR) lifecycle with replay detection.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.logging import get_logger
from app.core.security import (
    AuthenticationError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_email_domain_allowed,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import AdminCreateUserRequest, RegisterRequest, UserResponse

logger = get_logger(__name__)


class AuthService:
    """Service orchestrating user accounts and session token rotations."""

    @classmethod
    def set_refresh_cookie(cls, response: Response, refresh_token: str) -> None:
        """Set HttpOnly, SameSite cookie with refresh token."""
        settings = get_settings()
        max_age = settings.refresh_token_expire_days * 86400
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=max_age,
            expires=max_age,
            path="/api/v1/auth",
            httponly=True,
            secure=settings.cookie_secure or settings.is_production,
            samesite=settings.cookie_samesite,
        )

    @classmethod
    def clear_refresh_cookie(cls, response: Response) -> None:
        """Clear refresh cookie upon logout."""
        settings = get_settings()
        response.delete_cookie(
            key="refresh_token",
            path="/api/v1/auth",
            httponly=True,
            secure=settings.cookie_secure or settings.is_production,
            samesite=settings.cookie_samesite,
        )

    @classmethod
    async def register(
        cls,
        req: RegisterRequest,
        db: AsyncSession,
    ) -> UserResponse:
        """Register a new user account with domain whitelisting and direct bcrypt hashing."""
        settings = get_settings()
        repo = AuthRepository(db)

        # 1. Enforce domain whitelist if configured
        if not is_email_domain_allowed(req.email, settings.allowed_email_domains):
            logger.warning("registration_rejected_domain_disallowed", email=req.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email domain is not in the approved institutional whitelist: {settings.allowed_email_domains}",
            )

        # 2. Check for duplicate registration
        existing_user = await repo.get_by_email(req.email)
        if existing_user:
            logger.warning("registration_rejected_duplicate_email", email=req.email)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists.",
            )

        # 3. Hash password and persist user strictly as student
        hashed = hash_password(req.password)
        user = await repo.create_user(
            name=req.name,
            email=req.email,
            hashed_password=hashed,
            role=UserRole.student,
        )
        await db.commit()
        await db.refresh(user)

        logger.info("user_registered_successfully", user_id=str(user.id), email=user.email, role=str(user.role))
        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=role_str,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    @classmethod
    async def admin_create_user(
        cls,
        req: AdminCreateUserRequest,
        db: AsyncSession,
        admin: User,
    ) -> UserResponse:
        """Provision a privileged user account (reviewer, admin, etc.) through authorized admin workflow."""
        admin_role_str = admin.role.value if hasattr(admin.role, "value") else str(admin.role)
        if admin_role_str != UserRole.admin.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators may provision privileged user accounts.",
            )

        settings = get_settings()
        repo = AuthRepository(db)

        if not is_email_domain_allowed(req.email, settings.allowed_email_domains):
            logger.warning("admin_provisioning_domain_disallowed", email=req.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email domain is not in the approved institutional whitelist: {settings.allowed_email_domains}",
            )

        existing_user = await repo.get_by_email(req.email)
        if existing_user:
            logger.warning("admin_provisioning_duplicate_email", email=req.email)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists.",
            )

        hashed = hash_password(req.password)
        user = await repo.create_user(
            name=req.name,
            email=req.email,
            hashed_password=hashed,
            role=req.role,
            is_verified=True,  # Privileged staff accounts provisioned by admin are verified
        )
        await db.commit()
        await db.refresh(user)

        logger.info(
            "admin_provisioned_user_success",
            user_id=str(user.id),
            email=user.email,
            assigned_role=str(req.role),
            provisioned_by=str(admin.id),
        )
        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=role_str,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    @classmethod
    async def login(
        cls,
        email: str,
        password: str,
        response: Response,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Authenticate user credentials and issue access token and refresh cookie."""
        settings = get_settings()
        repo = AuthRepository(db)

        user = await repo.get_by_email(email)
        if not user or not user.is_active:
            logger.warning("login_failed_user_not_found_or_inactive", email=email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not verify_password(password, user.hashed_password):
            logger.warning("login_failed_invalid_password", email=email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        # Enforce email verification policy if configured
        if settings.require_email_verification and not user.is_verified:
            logger.warning("login_blocked_unverified_email", email=email)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account email is not verified. Please verify your email before logging in.",
            )

        # Create session tokens with distinct family_id for RTR tracking
        family_id = uuid.uuid4()
        role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
        access_token = create_access_token(
            subject=str(user.id),
            email=user.email,
            role=role_str,
        )
        refresh_token_str, jti, expires_at = create_refresh_token(
            subject=str(user.id),
            family_id=str(family_id),
        )

        # Store refresh token digest in DB
        await repo.store_refresh_token(
            user_id=user.id,
            jti=jti,
            token_str=refresh_token_str,
            expires_at=expires_at,
            family_id=family_id,
        )
        await db.commit()

        # Set secure HttpOnly cookie
        cls.set_refresh_cookie(response, refresh_token_str)

        logger.info("user_login_success", user_id=str(user.id), email=user.email, family_id=str(family_id))
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                role=role_str,
                is_active=user.is_active,
                created_at=user.created_at,
            ),
        }

    @classmethod
    async def refresh_tokens(
        cls,
        raw_refresh_token: str | None,
        response: Response,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """
        Refresh Token Rotation (RTR).
        Validates token, revokes previous token, detects replay theft,
        and atomically issues a new token pair within the same session family.
        """
        settings = get_settings()
        repo = AuthRepository(db)

        if not raw_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing from request cookies.",
            )

        try:
            payload = decode_token(raw_refresh_token, expected_type="refresh")
        except AuthenticationError as e:
            cls.clear_refresh_cookie(response)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            ) from e

        user_id_str = payload["sub"]
        jti = payload["jti"]
        user_uuid = uuid.UUID(user_id_str)

        try:
            # 1. Acquire atomic row-level lock (FOR UPDATE NOWAIT) to prevent concurrency races
            token_record, is_contended = await repo.get_refresh_token_for_update(jti)
            if is_contended:
                # Legitimate concurrent request in flight: Another transaction is actively rotating this token.
                # Do NOT revoke the token family; reject the concurrent duplicate request.
                logger.info(
                    "refresh_token_concurrent_contention_detected",
                    user_id=user_id_str,
                    jti=jti,
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Refresh token is currently being rotated in a concurrent transaction; active session remains valid.",
                )

            if not token_record:
                cls.clear_refresh_cookie(response)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token not recognized.",
                )

            # 2. Cryptographic digest verification
            expected_hash = hashlib.sha256(raw_refresh_token.encode("utf-8")).hexdigest()
            if token_record.token_hash != expected_hash:
                logger.error("refresh_token_hash_mismatch", user_id=user_id_str, jti=jti)
                await repo.revoke_family_tokens(token_record.family_id)
                await db.commit()
                cls.clear_refresh_cookie(response)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token cryptographic digest.",
                )

            now_utc = datetime.now(timezone.utc)

            # 3. Replay Detection (Token Family Compromise)
            if token_record.revoked:
                logger.error(
                    "security_alert_refresh_token_replay_detected",
                    user_id=user_id_str,
                    family_id=str(token_record.family_id),
                    jti=jti,
                )
                await repo.revoke_family_tokens(token_record.family_id)
                await db.commit()
                cls.clear_refresh_cookie(response)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Security alert: Compromised refresh token replayed. Family sessions revoked.",
                )

            # 4. Expiration timestamp verification
            if token_record.expires_at < now_utc:
                cls.clear_refresh_cookie(response)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has expired.",
                )

            # 5. User active verification
            user = await repo.get_by_id(user_uuid)
            if not user or not user.is_active:
                token_record.revoked = True
                await db.commit()
                cls.clear_refresh_cookie(response)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account inactive or not found.",
                )

            # 6. Issue fresh token pair within same session family
            role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
            new_access_token = create_access_token(
                subject=str(user.id),
                email=user.email,
                role=role_str,
            )
            new_refresh_str, new_jti, new_expires_at = create_refresh_token(
                subject=str(user.id),
                family_id=str(token_record.family_id),
            )

            # 7. Update current token and store replacement atomically
            token_record.revoked = True
            token_record.replaced_by = new_jti
            token_record.rotated_at = now_utc

            await repo.store_refresh_token(
                user_id=user.id,
                jti=new_jti,
                token_str=new_refresh_str,
                expires_at=new_expires_at,
                family_id=token_record.family_id,
            )
            await db.commit()

            cls.set_refresh_cookie(response, new_refresh_str)
            logger.info(
                "refresh_token_rotated_successfully",
                user_id=user_id_str,
                old_jti=jti,
                new_jti=new_jti,
                family_id=str(token_record.family_id),
            )

            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": settings.access_token_expire_minutes * 60,
                "user": UserResponse(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    role=role_str,
                    is_active=user.is_active,
                    created_at=user.created_at,
                ),
            }
        except HTTPException:
            raise
        except Exception:
            await db.rollback()
            raise

    @classmethod
    async def logout(
        cls,
        raw_refresh_token: str | None,
        response: Response,
        db: AsyncSession,
    ) -> None:
        """Revoke the active refresh token and clear the session cookie."""
        repo = AuthRepository(db)
        if raw_refresh_token:
            try:
                payload = decode_token(raw_refresh_token, expected_type="refresh")
                jti = payload.get("jti")
                if jti:
                    await repo.revoke_refresh_token(jti)
                    await db.commit()
            except Exception:
                pass  # Ignore decode errors on logout

        cls.clear_refresh_cookie(response)
        logger.info("user_logged_out_successfully")
