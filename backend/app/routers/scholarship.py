"""
FairExplain AI — Scholarship Router
====================================
REST endpoints for deterministic scholarship eligibility evaluation and tuition accounting.
Protected by BOLA ownership checks.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import assert_application_access, get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.common import BaseResponse
from app.schemas.scholarship import (
    ScholarshipEvaluateRequest,
    ScholarshipEvaluateResponseData,
)
from app.services.scholarship_service import ScholarshipService

router = APIRouter(tags=["Scholarship"])


@router.post(
    "/evaluate",
    response_model=BaseResponse[ScholarshipEvaluateResponseData],
    status_code=status.HTTP_200_OK,
    summary="Evaluate scholarship eligibility and compute tuition accounting",
)
async def evaluate_scholarship(
    request: ScholarshipEvaluateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ScholarshipEvaluateResponseData]:
    """
    Deterministically evaluates applicant criteria against the specified scholarship policy,
    applies institutional caps, and records the frozen evaluation snapshots.
    Enforces object-level ownership authorization.
    """
    await assert_application_access(request.application_id, current_user, db)

    data = await ScholarshipService.evaluate_application(request, db)
    return BaseResponse[ScholarshipEvaluateResponseData](
        success=True,
        data=data,
        message="Scholarship eligibility and tuition accounting evaluated successfully.",
    )
