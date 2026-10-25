"""
FairExplain AI — Fairness Audit Router
========================================
REST endpoints for administrative fairness metrics and proxy screening audits.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.common import BaseResponse
from app.services.fairness_service import FairnessService

router = APIRouter(tags=["Fairness"])


@router.get(
    "/metrics",
    response_model=BaseResponse[dict[str, Any]],
    summary="Retrieve platform cohort fairness metrics and proxy flag rates",
)
async def get_fairness_metrics(
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Fetch cohort-level fairness analytics, disparate impact ratio, and flag rates."""
    data = await FairnessService.get_fairness_metrics(db)
    return BaseResponse[dict[str, Any]](
        success=True,
        data=data,
        message="Fairness cohort metrics retrieved successfully.",
    )


@router.post(
    "/audit/{application_id}",
    response_model=BaseResponse[dict[str, Any]],
    summary="Screen an application explanation for demographic proxy bias",
)
async def audit_application(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Scan explanation text, redact prohibited terms, and route flagged cases to reviewer queue."""
    data = await FairnessService.audit_explanation(application_id, db)
    return BaseResponse[dict[str, Any]](
        success=True,
        data=data,
        message="Fairness screening audit completed.",
    )
