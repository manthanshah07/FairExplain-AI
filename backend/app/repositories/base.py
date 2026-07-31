"""
FairExplain AI — Base Repository
==================================
A generic, typed base class for all repository implementations.

Repositories are the *only* layer that touches SQLAlchemy directly.
Services depend on repositories, never on the ORM session.

Usage
-----
    class UserRepository(BaseRepository[User]):
        model = User

        async def get_by_email(self, email: str) -> User | None:
            result = await self._session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
"""

from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    CRUD base for all repositories.

    Subclasses must set the `model` class attribute to the SQLAlchemy
    model class they manage.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, record_id: uuid.UUID) -> ModelT | None:
        """Return a single record by primary key, or None if not found."""
        result = await self._session.execute(
            select(self.model).where(self.model.id == record_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_all(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """Return a paginated list of all records."""
        result = await self._session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(self, instance: ModelT) -> ModelT:
        """Persist a new model instance and return it (with generated PK)."""
        self._session.add(instance)
        await self._session.flush()   # assigns PK without committing
        await self._session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        """Remove a record from the database."""
        await self._session.delete(instance)
        await self._session.flush()

    async def count(self) -> int:
        """Return the total number of records in the table."""
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
