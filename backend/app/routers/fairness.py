"""
FairExplain AI — Fairness Audit Router
========================================
REST endpoints for administrative fairness metrics and proxy screening audits.
Protected by reviewer and admin role checks.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import BaseResponse
from app.services.fairness_service import FairnessService

router = APIRouter(tags=["Fairness"])

_reviewer_guard = require_role([
    UserRole.reviewer,
    UserRole.admin,
    UserRole.university,
])


@router.get(
    "/metrics",
    response_model=BaseResponse[dict[str, Any]],
    summary="Retrieve platform cohort fairness metrics and proxy flag rates",
)
async def get_fairness_metrics(
    current_user: User = Depends(_reviewer_guard),
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
    current_user: User = Depends(_reviewer_guard),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict[str, Any]]:
    """Scan explanation text, redact prohibited terms, and route flagged cases to reviewer queue."""
    data = await FairnessService.audit_explanation(application_id, db)
    return BaseResponse[dict[str, Any]](
        success=True,
        data=data,
        message="Fairness screening audit completed.",
    )
