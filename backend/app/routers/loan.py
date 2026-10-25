"""
FairExplain AI — Loan Router
==============================
REST endpoints for deterministic education loan affordability assessment.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
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
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[LoanAssessResponseData]:
    """
    Deterministically calculates monthly capacity, debt-to-income (DTI) ratio,
    and estimated EMI on the post-scholarship net balance.
    """
    data = await LoanService.assess_loan(request, db)
    return BaseResponse[LoanAssessResponseData](
        success=True,
        data=data,
        message="Loan affordability assessed successfully.",
    )
