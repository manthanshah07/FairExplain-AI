"""
FairExplain AI — Authentication & Token Repository
====================================================
Database persistence for Users and RefreshToken entities.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class AuthRepository(BaseRepository[User]):
    """Repository managing user account authentication and refresh token rotation."""

    model = User

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by case-insensitive unique email."""
        stmt = select(User).where(User.email.ilike(email.strip()))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        name: str,
        email: str,
        hashed_password: str,
        role: UserRole = UserRole.student,
        is_verified: bool = False,
    ) -> User:
        """Create and persist a new user account."""
        user = User(
            name=name.strip(),
            email=email.strip().lower(),
            hashed_password=hashed_password,
            role=role,
            is_active=True,
            is_verified=is_verified,
        )
        self._session.add(user)
        await self._session.flush()
        return user

    async def store_refresh_token(
        self,
        user_id: uuid.UUID,
        jti: str,
        token_str: str,
        expires_at: datetime,
        family_id: uuid.UUID | None = None,
    ) -> RefreshToken:
        """Store SHA-256 hash digest of a newly issued refresh token with family tracking."""
        token_hash = hashlib.sha256(token_str.encode("utf-8")).hexdigest()
        token_record = RefreshToken(
            user_id=user_id,
            jti=jti,
            token_hash=token_hash,
            family_id=family_id or uuid.uuid4(),
            revoked=False,
            expires_at=expires_at,
        )
        self._session.add(token_record)
        await self._session.flush()
        return token_record

    async def get_refresh_token_by_jti(self, jti: str) -> RefreshToken | None:
        """Fetch refresh token record by unique JTI."""
        stmt = select(RefreshToken).where(RefreshToken.jti == jti)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_refresh_token_for_update(self, jti: str) -> tuple[RefreshToken | None, bool]:
        """
        Fetch refresh token record by unique JTI with pessimistic row lock (FOR UPDATE NOWAIT).
        Returns:
            (record, is_concurrent_lock_contended)
            - If row is successfully locked: (record, False)
            - If row is currently locked by a concurrent transaction: (None, True)
            - If row does not exist: (None, False)
        """
        from sqlalchemy.exc import DBAPIError

        stmt = select(RefreshToken).where(RefreshToken.jti == jti).with_for_update(nowait=True)
        try:
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none(), False
        except DBAPIError as e:
            orig = getattr(e, "orig", None)
            pgcode = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
            err_str = str(e).lower()
            if pgcode == "55P03" or "could not obtain lock" in err_str or "locknotavailable" in err_str:
                await self._session.rollback()
                return None, True
            raise

    async def revoke_refresh_token(self, jti: str) -> bool:
        """Mark a single refresh token as revoked."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.jti == jti, RefreshToken.revoked.is_(False))
            .values(revoked=True)
            .execution_options(synchronize_session=False)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0

    async def revoke_family_tokens(self, family_id: uuid.UUID) -> int:
        """
        Revoke all active refresh tokens in a specific token family.
        Invoked when replay or token compromise is detected for a session tree.
        """
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id, RefreshToken.revoked.is_(False))
            .values(revoked=True)
            .execution_options(synchronize_session=False)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> int:
        """
        Revoke all active refresh tokens across all families for a user.
        Invoked during global logout or administrative credential revocation.
        """
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True)
            .execution_options(synchronize_session=False)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount
