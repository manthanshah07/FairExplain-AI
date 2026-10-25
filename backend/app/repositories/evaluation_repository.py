"""
FairExplain AI — Evaluation & Accounting Repository
=====================================================
Async repository for persisting and querying evaluation snapshots and tuition balances.
"""

from __future__ import annotations

import uuid
from typing import Any, Mapping

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models import (
    EligibilityEvaluationResult,
    TuitionAccountSummary,
)
from app.models.evaluation import (
    ScholarshipEvaluationModel,
    TuitionAccountSummaryModel,
)
from app.repositories.base import BaseRepository
from app.repositories.mappers import (
    domain_to_orm_accounting,
    domain_to_orm_evaluation,
    orm_to_domain_accounting,
    orm_to_domain_evaluation,
)


class EvaluationRepository(BaseRepository[ScholarshipEvaluationModel]):
    """Repository managing scholarship evaluations, snapshots, and tuition account summaries."""

    model = ScholarshipEvaluationModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def save_evaluation(
        self,
        result: EligibilityEvaluationResult,
        application_id: uuid.UUID,
        applicant_snapshot: Mapping[str, Any] | None = None,
    ) -> ScholarshipEvaluationModel:
        """Persist an evaluation result with criteria evaluation snapshots."""
        model = domain_to_orm_evaluation(result, application_id, applicant_snapshot)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, ["criteria_evaluations"])
        return model

    async def get_latest_evaluation(
        self, application_id: uuid.UUID
    ) -> ScholarshipEvaluationModel | None:
        """Fetch the most recent evaluation for an application."""
        stmt = (
            select(ScholarshipEvaluationModel)
            .options(selectinload(ScholarshipEvaluationModel.criteria_evaluations))
            .where(ScholarshipEvaluationModel.application_id == application_id)
            .order_by(ScholarshipEvaluationModel.created_at.desc())
            .limit(1)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def save_tuition_accounting(
        self,
        summary: TuitionAccountSummary,
        application_id: uuid.UUID,
        calculator_version: str = "1.0.0-phase1b",
    ) -> TuitionAccountSummaryModel:
        """
        Persist tuition account summary and allocations for an application.
        Replaces any existing summary for this application to maintain 1:1 constraint.
        """
        # Delete existing summary if any
        stmt_del = delete(TuitionAccountSummaryModel).where(
            TuitionAccountSummaryModel.application_id == application_id
        )
        await self._session.execute(stmt_del)

        model = domain_to_orm_accounting(summary, application_id, calculator_version)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, ["allocations"])
        return model

    async def get_tuition_summary(
        self, application_id: uuid.UUID
    ) -> TuitionAccountSummaryModel | None:
        """Fetch tuition account summary with allocation details."""
        stmt = (
            select(TuitionAccountSummaryModel)
            .options(selectinload(TuitionAccountSummaryModel.allocations))
            .where(TuitionAccountSummaryModel.application_id == application_id)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()
