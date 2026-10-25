"""
FairExplain AI — Application Pydantic Schemas
==============================================
Validation schemas for application creation, academic records, and financial profiles.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AcademicRecordInput(BaseModel):
    """Academic input validation schema."""

    cgpa: Decimal = Field(..., ge=Decimal("0.0"), le=Decimal("10.0"), description="CGPA on 10.0 scale")
    tenth_percent: Decimal = Field(..., ge=Decimal("0.0"), le=Decimal("100.0"), description="10th grade percentage")
    twelfth_percent: Decimal = Field(..., ge=Decimal("0.0"), le=Decimal("100.0"), description="12th grade percentage")
    backlogs: int = Field(default=0, ge=0, description="Active backlog count")

    model_config = {"from_attributes": True}


class FinancialProfileInput(BaseModel):
    """Financial input validation schema (all amounts in INR)."""

    household_income: Decimal = Field(..., ge=Decimal("0.00"), description="Annual household income in INR")
    existing_emi: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"), description="Monthly existing EMI commitments")
    tuition_fee: Decimal = Field(..., ge=Decimal("0.00"), description="Annual tuition fee in INR")
    requested_loan: Decimal = Field(..., ge=Decimal("0.00"), description="Requested education loan amount in INR")

    model_config = {"from_attributes": True}


class ApplicationCreateRequest(BaseModel):
    """Payload to submit or draft a new application."""

    user_id: uuid.UUID | None = Field(default=None, description="Existing user UUID or created automatically")
    name: str = Field(default="Applicant", min_length=1, max_length=255)
    email: str = Field(default="applicant@example.com", min_length=3, max_length=255)
    academic_record: AcademicRecordInput
    financial_profile: FinancialProfileInput


class ApplicationResponseData(BaseModel):
    """Application detail response payload."""

    application_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    academic_record: AcademicRecordInput | None = None
    financial_profile: FinancialProfileInput | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
