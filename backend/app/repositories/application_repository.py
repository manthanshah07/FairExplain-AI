"""
FairExplain AI — Application Repository
=========================================
Async repository for persisting and querying Application aggregates,
academic records, financial profiles, and evaluations.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.academic_record import AcademicRecord
from app.models.application import Application, ApplicationStatus
from app.models.financial_profile import FinancialProfile
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    """Repository managing Application aggregates and relationships."""

    model = Application

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_with_relations(self, application_id: uuid.UUID) -> Application | None:
        """Fetch application aggregate with all core related entities eager loaded."""
        stmt = (
            select(Application)
            .options(
                selectinload(Application.academic_record),
                selectinload(Application.financial_profile),
                selectinload(Application.documents),
                selectinload(Application.evaluations),
                selectinload(Application.tuition_account_summary),
                selectinload(Application.awards),
            )
            .where(Application.id == application_id)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_application(
        self,
        user_id: uuid.UUID,
        status: ApplicationStatus = ApplicationStatus.draft,
    ) -> Application:
        """Create and persist a new application."""
        app = Application(user_id=user_id, status=status)
        self._session.add(app)
        await self._session.flush()
        await self._session.refresh(app)
        return app

    async def update_status(
        self, application_id: uuid.UUID, new_status: ApplicationStatus
    ) -> Application | None:
        """Update the lifecycle status of an application."""
        app = await self.get_by_id(application_id)
        if not app:
            return None
        app.status = new_status
        await self._session.flush()
        await self._session.refresh(app)
        return app

    async def list_by_user(self, user_id: uuid.UUID) -> list[Application]:
        """List all applications belonging to a user."""
        stmt = (
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.created_at.desc())
        )
        res = await self._session.execute(stmt)
        return list(res.scalars().all())
