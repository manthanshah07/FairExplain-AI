"""
FairExplain AI — Loan Assessment Pydantic Schemas
==================================================
Validation schemas for deterministic loan affordability evaluation.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class LoanAssessRequest(BaseModel):
    """Payload to evaluate loan affordability for an application."""

    application_id: uuid.UUID
    tenure_months: int = Field(default=60, ge=1, le=360, description="Repayment tenure in months")
    requested_loan_amount: Decimal | None = Field(
        default=None, ge=Decimal("0.00"), description="Optional override of requested loan amount"
    )


class LoanAssessResponseData(BaseModel):
    """Loan serviceability report response payload."""

    application_id: uuid.UUID
    monthly_income: Decimal
    available_monthly_capacity: Decimal
    estimated_emi: Decimal
    post_scholarship_loan_amount: Decimal
    tenure_months: int
    outcome: str
    dti_ratio_percent: Decimal
    capacity_utilization_percent: Decimal
    reason: str

    model_config = {"from_attributes": True}
