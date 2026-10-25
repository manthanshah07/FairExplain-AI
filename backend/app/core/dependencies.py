"""
FairExplain AI — Authentication & Authorization Dependencies
==============================================================
FastAPI dependency injection providers for:
  1. Extracting and validating JWT bearer tokens (`get_current_user`).
  2. Role-based access control (`require_role`).
  3. Ownership / object-level authorization helpers.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Sequence

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import AuthenticationError, decode_token
from app.db.database import get_db
from app.models.user import User, UserRole

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True,
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authenticate request principal from JWT Bearer token.
    Raises HTTP 401 if token is missing, expired, or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token, expected_type="access")
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise credentials_exception
        user_uuid = uuid.UUID(user_id_str)
    except (AuthenticationError, ValueError) as e:
        logger.warning("token_validation_failed", error=str(e))
        raise credentials_exception from e

    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning("authenticated_user_not_found_in_db", user_id=user_id_str)
        raise credentials_exception

    if not user.is_active:
        logger.warning("authenticated_user_inactive", user_id=user_id_str)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated.",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require that the authenticated user is active and email-verified when verification policy is active."""
    from app.config.settings import get_settings
    settings = get_settings()
    if settings.require_email_verification and not current_user.is_verified:
        logger.warning("unverified_user_access_blocked", user_id=str(current_user.id), email=current_user.email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account email is not verified. Please verify your email before accessing this resource.",
        )
    return current_user


def require_role(allowed_roles: Sequence[UserRole | str]) -> Callable[..., User]:
    """
    Dependency factory that enforces Role-Based Access Control (RBAC).
    Raises HTTP 403 Forbidden if current user lacks required role.
    """
    allowed_role_strings = {
        r.value if hasattr(r, "value") else str(r) for r in allowed_roles
    }

    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        user_role_str = (
            current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role)
        )
        if user_role_str not in allowed_role_strings:
            logger.warning(
                "rbac_permission_denied",
                user_id=str(current_user.id),
                user_role=user_role_str,
                allowed_roles=list(allowed_role_strings),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role '{user_role_str}'.",
            )
        return current_user

    return role_checker


async def assert_application_access(
    application_id: uuid.UUID,
    user: User,
    db: AsyncSession,
) -> None:
    """
    Enforce Broken Object-Level Authorization (BOLA) boundary.
    Asserts that the requesting user owns the application or possesses a reviewer/admin role.
    Raises HTTP 404 if application not found, or HTTP 403 if unauthorized.
    """
    user_role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    if user_role_str in [
        UserRole.reviewer.value,
        UserRole.admin.value,
        UserRole.university.value,
    ]:
        return

    from app.models.application import Application

    stmt = select(Application.user_id).where(Application.id == application_id)
    res = await db.execute(stmt)
    owner_id = res.scalar_one_or_none()

    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} not found.",
        )

    if owner_id != user.id:
        logger.warning(
            "bola_access_denied",
            user_id=str(user.id),
            application_id=str(application_id),
            owner_id=str(owner_id),
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to requested application.",
        )
