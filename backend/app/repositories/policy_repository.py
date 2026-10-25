"""
FairExplain AI — Policy Repository
====================================
Async repository for persisting and querying ScholarshipPolicy models and criteria.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models import ScholarshipPolicy
from app.models.policy import EligibilityCriterionModel, ScholarshipPolicyModel
from app.repositories.base import BaseRepository
from app.repositories.mappers import domain_to_orm_policy, orm_to_domain_policy


class PolicyRepository(BaseRepository[ScholarshipPolicyModel]):
    """Repository managing scholarship policies and eligibility criteria."""

    model = ScholarshipPolicyModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_program_and_version(
        self, program_id: str, version: str
    ) -> ScholarshipPolicyModel | None:
        """Fetch policy with eager loaded criteria matching program_id and version."""
        stmt = (
            select(ScholarshipPolicyModel)
            .options(selectinload(ScholarshipPolicyModel.criteria))
            .where(
                ScholarshipPolicyModel.program_id == program_id,
                ScholarshipPolicyModel.policy_version == version,
                ScholarshipPolicyModel.is_active.is_(True),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_latest_by_program(
        self, program_id: str
    ) -> ScholarshipPolicyModel | None:
        """Fetch the most recently created active policy for a program."""
        stmt = (
            select(ScholarshipPolicyModel)
            .options(selectinload(ScholarshipPolicyModel.criteria))
            .where(
                ScholarshipPolicyModel.program_id == program_id,
                ScholarshipPolicyModel.is_active.is_(True),
            )
            .order_by(ScholarshipPolicyModel.created_at.desc())
            .limit(1)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_active_policies(self) -> list[ScholarshipPolicyModel]:
        """List all currently active scholarship policies with criteria."""
        stmt = (
            select(ScholarshipPolicyModel)
            .options(selectinload(ScholarshipPolicyModel.criteria))
            .where(ScholarshipPolicyModel.is_active.is_(True))
            .order_by(ScholarshipPolicyModel.program_id)
        )
        res = await self._session.execute(stmt)
        return list(res.scalars().all())

    async def save_domain_policy(
        self, domain_policy: ScholarshipPolicy
    ) -> ScholarshipPolicyModel:
        """Translate a domain policy and persist it with criteria."""
        orm_model = domain_to_orm_policy(domain_policy)
        self._session.add(orm_model)
        await self._session.flush()
        await self._session.refresh(orm_model, ["criteria"])
        return orm_model

    async def get_as_domain(
        self, program_id: str, version: str | None = None
    ) -> ScholarshipPolicy | None:
        """Fetch policy and return it as a pure domain ScholarshipPolicy dataclass."""
        if version:
            model = await self.get_by_program_and_version(program_id, version)
        else:
            model = await self.get_latest_by_program(program_id)

        if not model:
            return None
        return orm_to_domain_policy(model)
