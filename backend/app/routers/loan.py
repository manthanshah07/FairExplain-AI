"""
FairExplain AI — Loan Router
==============================
REST endpoints for deterministic education loan affordability assessment.
Protected by BOLA ownership checks.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import assert_application_access, get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.common import BaseResponse
from app.schemas.loan import LoanAssessRequest, LoanAssessResponseData
from app.services.loan_service import LoanService

router = APIRouter(tags=["Loan"])


@router.post(
    "/assess",
    response_model=BaseResponse[LoanAssessResponseData],
    status_code=status.HTTP_200_OK,
    summary="Assess education loan serviceability and EMI affordability",
)
async def assess_loan(
    request: LoanAssessRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[LoanAssessResponseData]:
    """
    Deterministically calculates monthly capacity, debt-to-income (DTI) ratio,
    and estimated EMI on the post-scholarship net balance.
    Enforces object-level ownership authorization.
    """
    await assert_application_access(request.application_id, current_user, db)

    data = await LoanService.assess_loan(request, db)
    return BaseResponse[LoanAssessResponseData](
        success=True,
        data=data,
        message="Loan affordability assessed successfully.",
    )
