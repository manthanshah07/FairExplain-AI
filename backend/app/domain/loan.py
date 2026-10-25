"""
FairExplain AI — Deterministic Loan Affordability Engine
==========================================================
Pure Python implementation of loan serviceability assessment per RULE_ENGINE.md §4.2.

Mathematical Model:
- monthly_income = household_income / 12
- available_monthly_capacity = (monthly_income * 0.40) - existing_emi
- estimated_emi = post_scholarship_loan_amount / tenure_months

Decision Rules:
- If estimated_emi <= available_monthly_capacity: ELIGIBLE
- If estimated_emi <= available_monthly_capacity * 1.20: NEEDS_REVIEW
- If estimated_emi > available_monthly_capacity * 1.20: NOT_RECOMMENDED
- If available_monthly_capacity <= 0: NOT_RECOMMENDED
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.domain.enums import LoanOutcome
from app.domain.exceptions import (
    InvalidLoanParametersError,
    InvalidMonetaryValueError,
)
from app.domain.models import quantize_currency, validate_finite_decimal


@dataclass(frozen=True)
class LoanAffordabilityProfile:
    """Inputs required for deterministic loan affordability evaluation."""

    applicant_id: str
    household_income: Decimal
    existing_emi: Decimal
    post_scholarship_loan_amount: Decimal
    tenure_months: int = 60

    def __post_init__(self) -> None:
        if not self.applicant_id or not self.applicant_id.strip():
            raise InvalidLoanParametersError("Applicant ID cannot be empty.")

        if type(self.tenure_months) is not int or self.tenure_months <= 0:
            raise InvalidLoanParametersError(
                f"Tenure months must be a positive integer, got {self.tenure_months!r}."
            )

        inc = quantize_currency(self.household_income, "Household income")
        if inc < Decimal("0.00"):
            raise InvalidMonetaryValueError("Household income cannot be negative.")
        object.__setattr__(self, "household_income", inc)

        emi = quantize_currency(self.existing_emi, "Existing EMI")
        if emi < Decimal("0.00"):
            raise InvalidMonetaryValueError("Existing EMI cannot be negative.")
        object.__setattr__(self, "existing_emi", emi)

        loan = quantize_currency(
            self.post_scholarship_loan_amount, "Post-scholarship loan amount"
        )
        if loan < Decimal("0.00"):
            raise InvalidMonetaryValueError(
                "Post-scholarship loan amount cannot be negative."
            )
        object.__setattr__(self, "post_scholarship_loan_amount", loan)


@dataclass(frozen=True)
class LoanAffordabilityResult:
    """Outcome report of deterministic loan affordability assessment."""

    applicant_id: str
    monthly_income: Decimal
    available_monthly_capacity: Decimal
    estimated_emi: Decimal
    post_scholarship_loan_amount: Decimal
    tenure_months: int
    outcome: LoanOutcome
    dti_ratio_percent: Decimal
    capacity_utilization_percent: Decimal
    reason: str


def assess_loan_affordability(
    profile: LoanAffordabilityProfile,
) -> LoanAffordabilityResult:
    """
    Deterministically assess education loan affordability based on net post-scholarship amount.
    All calculations use Decimal arithmetic quantized to 0.01.
    """
    monthly_income = quantize_currency(
        profile.household_income / Decimal("12.00"), "Monthly income"
    )

    # 40% maximum permissible debt burden
    max_permissible_debt_budget = quantize_currency(
        monthly_income * Decimal("0.40"), "Max permissible debt budget"
    )

    available_monthly_capacity = quantize_currency(
        max_permissible_debt_budget - profile.existing_emi,
        "Available monthly capacity",
    )

    tenure = Decimal(profile.tenure_months)
    estimated_emi = quantize_currency(
        profile.post_scholarship_loan_amount / tenure, "Estimated EMI"
    )

    # If applicant requires zero loan balance
    if profile.post_scholarship_loan_amount == Decimal("0.00"):
        return LoanAffordabilityResult(
            applicant_id=profile.applicant_id,
            monthly_income=monthly_income,
            available_monthly_capacity=available_monthly_capacity,
            estimated_emi=Decimal("0.00"),
            post_scholarship_loan_amount=Decimal("0.00"),
            tenure_months=profile.tenure_months,
            outcome=LoanOutcome.ELIGIBLE,
            dti_ratio_percent=Decimal("0.00"),
            capacity_utilization_percent=Decimal("0.00"),
            reason="Post-scholarship tuition balance is zero; no loan borrowing required.",
        )

    # Calculate metrics
    total_monthly_obligations = profile.existing_emi + estimated_emi
    if monthly_income > Decimal("0.00"):
        dti_ratio = quantize_currency(
            (total_monthly_obligations / monthly_income) * Decimal("100.00"),
            "DTI ratio",
        )
    else:
        dti_ratio = Decimal("100.00")

    if available_monthly_capacity > Decimal("0.00"):
        capacity_utilization = quantize_currency(
            (estimated_emi / available_monthly_capacity) * Decimal("100.00"),
            "Capacity utilization",
        )
    else:
        capacity_utilization = Decimal("999.99")

    # Determine eligibility outcome
    if available_monthly_capacity <= Decimal("0.00"):
        outcome = LoanOutcome.NOT_RECOMMENDED
        reason = (
            f"Existing monthly EMI obligations (₹{profile.existing_emi:,.2f}) exceed or fully "
            f"exhaust the allowable 40% monthly debt limit (₹{max_permissible_debt_budget:,.2f})."
        )
    elif estimated_emi <= available_monthly_capacity:
        outcome = LoanOutcome.ELIGIBLE
        reason = (
            f"Estimated monthly EMI of ₹{estimated_emi:,.2f} is within available monthly capacity "
            f"of ₹{available_monthly_capacity:,.2f}."
        )
    elif estimated_emi <= quantize_currency(available_monthly_capacity * Decimal("1.20")):
        outcome = LoanOutcome.NEEDS_REVIEW
        reason = (
            f"Estimated monthly EMI of ₹{estimated_emi:,.2f} exceeds standard capacity "
            f"(₹{available_monthly_capacity:,.2f}) by less than 20%; eligible for co-borrower review."
        )
    else:
        outcome = LoanOutcome.NOT_RECOMMENDED
        reason = (
            f"Estimated monthly EMI of ₹{estimated_emi:,.2f} significantly exceeds available monthly capacity "
            f"(₹{available_monthly_capacity:,.2f}) by more than 20%."
        )

    return LoanAffordabilityResult(
        applicant_id=profile.applicant_id,
        monthly_income=monthly_income,
        available_monthly_capacity=available_monthly_capacity,
        estimated_emi=estimated_emi,
        post_scholarship_loan_amount=profile.post_scholarship_loan_amount,
        tenure_months=profile.tenure_months,
        outcome=outcome,
        dti_ratio_percent=dti_ratio,
        capacity_utilization_percent=capacity_utilization,
        reason=reason,
    )
