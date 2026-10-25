"""
FairExplain AI — Scholarship Pydantic Schemas
==============================================
Validation schemas for scholarship evaluations and tuition accounting responses.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class AwardInputDTO(BaseModel):
    """Input award to include in tuition accounting calculation."""

    award_id: str
    program_id: str
    title: str
    status: str = "confirmed"
    award_type: str = "fixed_amount"
    priority: int = 1
    amount: Decimal | None = None
    percentage: Decimal | None = None
    max_award_cap: Decimal | None = None
    incompatible_programs: list[str] = Field(default_factory=list)


class ScholarshipEvaluateRequest(BaseModel):
    """Payload to trigger scholarship eligibility evaluation and tuition accounting."""

    application_id: uuid.UUID
    program_id: str = Field(default="MERIT_NEED_2026", description="Scholarship program code")
    policy_version: str | None = Field(default=None, description="Policy version to evaluate against")
    awards: list[AwardInputDTO] = Field(default_factory=list, description="Explicit awards to apply")


class CriterionEvaluationDTO(BaseModel):
    """DTO representing individual criterion evaluation outcome."""

    criterion_id: str
    attribute: str
    operator: str
    target_value: Any
    actual_value: Any
    status: str
    is_mandatory: bool
    evidence_required: str | None = None
    evidence_status: str
    reason: str

    model_config = {"from_attributes": True}


class AwardAllocationDTO(BaseModel):
    """DTO representing an applied award allocation and surplus."""

    award_id: str
    program_id: str
    title: str
    priority: int
    status: str
    nominal_amount: Decimal
    capped_amount: Decimal
    effective_reduction: Decimal
    unapplied_surplus: Decimal
    cap_reason: str | None = None

    model_config = {"from_attributes": True}


class TuitionAccountingDTO(BaseModel):
    """DTO representing post-scholarship tuition balances."""

    gross_eligible_tuition: Decimal
    institutional_cap_applied: Decimal
    total_effective_reduction: Decimal
    remaining_payable_tuition: Decimal
    remaining_waiver_allowance: Decimal
    total_unapplied_surplus: Decimal
    allocations: list[AwardAllocationDTO]

    model_config = {"from_attributes": True}


class ScholarshipEvaluateResponseData(BaseModel):
    """Scholarship evaluation and accounting report response payload."""

    application_id: uuid.UUID
    program_id: str
    policy_version: str
    status: str
    reason: str
    satisfied_count: int
    failed_count: int
    pending_count: int
    criteria_evaluations: list[CriterionEvaluationDTO]
    tuition_accounting: TuitionAccountingDTO | None = None

    model_config = {"from_attributes": True}
