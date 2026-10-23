"""
FairExplain AI — Domain Models
==============================
Immutable, pure-Python domain data structures for eligibility and accounting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Mapping, Sequence

from app.domain.enums import (
    AttributePurpose,
    AwardStatus,
    AwardType,
    CriterionOperator,
    CriterionOutcome,
    EligibilityStatus,
    EvidenceStatus,
)
from app.domain.exceptions import (
    DisallowedAttributeError,
    InvalidMonetaryValueError,
    MalformedPolicyError,
    MissingAwardPriorityError,
    UnsupportedAttributeError,
)

# ---------------------------------------------------------------------------
# Attribute Registry & Purpose Classification
# ---------------------------------------------------------------------------

SUPPORTED_ATTRIBUTES: dict[str, set[AttributePurpose]] = {
    # Academic / Merit attributes
    "cgpa": {AttributePurpose.MERIT_RANKING, AttributePurpose.PROGRAM_ELIGIBILITY},
    "tenth_percent": {AttributePurpose.MERIT_RANKING, AttributePurpose.PROGRAM_ELIGIBILITY},
    "twelfth_percent": {AttributePurpose.MERIT_RANKING, AttributePurpose.PROGRAM_ELIGIBILITY},
    "active_backlogs": {AttributePurpose.MERIT_RANKING, AttributePurpose.PROGRAM_ELIGIBILITY},
    "coursework_score": {AttributePurpose.MERIT_RANKING, AttributePurpose.PROGRAM_ELIGIBILITY},

    # Program-specific context / need / enrollment attributes
    "household_income": {AttributePurpose.PROGRAM_ELIGIBILITY},
    "family_size": {AttributePurpose.PROGRAM_ELIGIBILITY},
    "state_of_domicile": {AttributePurpose.PROGRAM_ELIGIBILITY},
    "state": {AttributePurpose.PROGRAM_ELIGIBILITY},
    "district": {AttributePurpose.PROGRAM_ELIGIBILITY},
    "programme_enrolled": {AttributePurpose.PROGRAM_ELIGIBILITY},
    "programme": {AttributePurpose.PROGRAM_ELIGIBILITY},
    "department": {AttributePurpose.PROGRAM_ELIGIBILITY},
    "institution_id": {AttributePurpose.PROGRAM_ELIGIBILITY},
    "first_generation_college": {AttributePurpose.PROGRAM_ELIGIBILITY},

    # Sensitive attributes (Restricted: requires non-empty policy charter authorization)
    "caste_category": {AttributePurpose.RESTRICTED_SENSITIVE},
    "caste": {AttributePurpose.RESTRICTED_SENSITIVE},
    "gender": {AttributePurpose.RESTRICTED_SENSITIVE},
    "religion": {AttributePurpose.RESTRICTED_SENSITIVE},
    "disability_status": {AttributePurpose.RESTRICTED_SENSITIVE},
}

SENSITIVE_ATTRIBUTES: frozenset[str] = frozenset(
    attr for attr, purposes in SUPPORTED_ATTRIBUTES.items()
    if AttributePurpose.RESTRICTED_SENSITIVE in purposes
)

GENERIC_MERIT_ATTRIBUTES: frozenset[str] = frozenset(
    attr for attr, purposes in SUPPORTED_ATTRIBUTES.items()
    if AttributePurpose.MERIT_RANKING in purposes
)

PROGRAM_ELIGIBILITY_ATTRIBUTES: frozenset[str] = frozenset(
    attr for attr, purposes in SUPPORTED_ATTRIBUTES.items()
    if AttributePurpose.PROGRAM_ELIGIBILITY in purposes
)


def validate_finite_decimal(value: Any, field_name: str = "Monetary value") -> Decimal:
    """Validate that value can be converted to a finite Decimal, rejecting booleans, NaN, and infinities."""
    if isinstance(value, bool):  # In Python, bool is a subclass of int
        raise InvalidMonetaryValueError(f"{field_name} cannot be a boolean value.")
    try:
        if isinstance(value, float):
            d = Decimal(str(value))
        elif isinstance(value, Decimal):
            d = value
        elif isinstance(value, int):
            d = Decimal(value)
        elif isinstance(value, str):
            d = Decimal(value.strip())
        else:
            raise InvalidMonetaryValueError(
                f"{field_name} must be numeric, got {type(value).__name__}."
            )
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise InvalidMonetaryValueError(f"Malformed {field_name}: '{value}'.") from exc

    if not d.is_finite():
        raise InvalidMonetaryValueError(f"{field_name} must be finite (got '{d}').")
    return d


def quantize_currency(value: Any, field_name: str = "Monetary amount") -> Decimal:
    """Round a numeric value to two decimal places using standard ROUND_HALF_UP."""
    d = validate_finite_decimal(value, field_name)
    try:
        return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError) as exc:
        raise InvalidMonetaryValueError(f"Could not quantize {field_name}: '{value}'.") from exc


# ---------------------------------------------------------------------------
# Eligibility Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ApplicantProfile:
    """Applicant's verified data snapshot for eligibility evaluation."""

    applicant_id: str
    attributes: Mapping[str, Any] = field(default_factory=dict)
    verified_evidence: Mapping[str, EvidenceStatus] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Defensive copy to prevent post-construction mutations from external dict references
        object.__setattr__(self, "attributes", dict(self.attributes))
        object.__setattr__(self, "verified_evidence", dict(self.verified_evidence))

    def get_attribute(self, name: str) -> Any:
        """Retrieve attribute value; returns None if missing."""
        return self.attributes.get(name)

    def get_evidence_status(self, evidence_type: str | None) -> EvidenceStatus:
        """Check status of a required evidence type."""
        if not evidence_type:
            return EvidenceStatus.NOT_REQUIRED
        return self.verified_evidence.get(evidence_type, EvidenceStatus.MISSING)


@dataclass(frozen=True)
class EligibilityCriterion:
    """An explicit, institution-configured binary eligibility rule."""

    criterion_id: str
    attribute: str
    operator: CriterionOperator
    target_value: Any
    is_mandatory: bool = True
    required_evidence: str | None = None
    description: str = ""
    charter_authorization: str | None = None

    def __post_init__(self) -> None:
        if not self.criterion_id or not self.criterion_id.strip():
            raise MalformedPolicyError("Criterion criterion_id cannot be empty.")

        if not self.attribute or not self.attribute.strip():
            raise MalformedPolicyError("Criterion attribute name cannot be empty.")

        attr_normalized = self.attribute.strip().lower()

        # Reject unknown or misspelled attributes against the supported registry
        if attr_normalized not in SUPPORTED_ATTRIBUTES:
            raise UnsupportedAttributeError(
                f"Attribute '{self.attribute}' is not recognized in the supported attribute registry. "
                "Unknown or misspelled attributes are rejected."
            )

        # Sensitive attributes require explicit charter authorization
        if attr_normalized in SENSITIVE_ATTRIBUTES:
            if not self.charter_authorization or not self.charter_authorization.strip():
                raise DisallowedAttributeError(
                    f"Attribute '{self.attribute}' is a sensitive attribute and requires an explicit, "
                    "non-empty charter authorization reference (e.g., legislation or institutional charter order)."
                )

        # Validate operator
        if not isinstance(self.operator, CriterionOperator):
            object.__setattr__(
                self, "operator", CriterionOperator.from_string(str(self.operator))
            )


@dataclass(frozen=True)
class ScholarshipPolicy:
    """Institution-published scholarship program policy."""

    program_id: str
    policy_version: str
    title: str
    criteria: Sequence[EligibilityCriterion]
    incompatible_programs: frozenset[str] = field(default_factory=frozenset)
    charter_authorizations: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.program_id or not self.program_id.strip():
            raise MalformedPolicyError("Policy program_id cannot be empty.")
        if not self.policy_version or not self.policy_version.strip():
            raise MalformedPolicyError("Policy policy_version cannot be empty.")
        if not self.criteria:
            raise MalformedPolicyError(
                f"Policy '{self.program_id}' must define at least one eligibility criterion."
            )

        # Enforce true immutability via defensive copy into tuple and frozenset
        object.__setattr__(self, "criteria", tuple(self.criteria))
        object.__setattr__(self, "incompatible_programs", frozenset(self.incompatible_programs))
        object.__setattr__(self, "charter_authorizations", dict(self.charter_authorizations))

        # Validate that sensitive criteria have charter authorization either at criterion or policy level
        for criterion in self.criteria:
            attr_norm = criterion.attribute.strip().lower()
            if attr_norm in SENSITIVE_ATTRIBUTES:
                has_crit_auth = bool(
                    criterion.charter_authorization and criterion.charter_authorization.strip()
                )
                has_pol_auth = bool(
                    self.charter_authorizations.get(attr_norm, "").strip()
                )
                if not (has_crit_auth or has_pol_auth):
                    raise DisallowedAttributeError(
                        f"Policy '{self.program_id}' criterion '{criterion.criterion_id}' uses "
                        f"sensitive attribute '{criterion.attribute}' without a non-empty charter authorization reference."
                    )


@dataclass(frozen=True)
class CriterionEvaluation:
    """Evaluation output for an individual criterion."""

    criterion_id: str
    attribute: str
    operator: str
    target_value: Any
    actual_value: Any
    status: CriterionOutcome
    is_mandatory: bool
    evidence_required: str | None
    evidence_status: EvidenceStatus
    reason: str


@dataclass(frozen=True)
class EligibilityEvaluationResult:
    """Complete evaluation report for a scholarship program."""

    program_id: str
    policy_version: str
    status: EligibilityStatus
    reason: str
    criteria_evaluations: list[CriterionEvaluation]
    satisfied_count: int
    failed_count: int
    pending_count: int


# ---------------------------------------------------------------------------
# Accounting Models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InstitutionalCap:
    """Institutional tuition-waiver policy cap."""

    max_waiver_amount: Decimal | None = None
    max_waiver_percentage: Decimal | None = None

    def __post_init__(self) -> None:
        if self.max_waiver_amount is not None:
            amt = quantize_currency(self.max_waiver_amount, "Institutional max_waiver_amount")
            if amt < Decimal("0.00"):
                raise InvalidMonetaryValueError(
                    "Institutional max_waiver_amount cannot be negative."
                )
            object.__setattr__(self, "max_waiver_amount", amt)

        if self.max_waiver_percentage is not None:
            pct = validate_finite_decimal(
                self.max_waiver_percentage, "Institutional max_waiver_percentage"
            )
            if pct < Decimal("0.00") or pct > Decimal("100.00"):
                raise InvalidMonetaryValueError(
                    "Institutional max_waiver_percentage must be between 0.00 and 100.00."
                )
            object.__setattr__(self, "max_waiver_percentage", pct)

    def calculate_effective_cap(self, gross_tuition: Decimal) -> Decimal:
        """
        Calculate the effective waiver allowance cap.
        If both fixed amount and percentage are configured, the tighter cap applies.
        If neither is configured, the cap is the gross eligible tuition.
        """
        caps: list[Decimal] = []

        if self.max_waiver_amount is not None:
            caps.append(self.max_waiver_amount)

        if self.max_waiver_percentage is not None:
            pct_amount = quantize_currency(
                gross_tuition * (self.max_waiver_percentage / Decimal("100.00")),
                "Percentage cap calculation",
            )
            caps.append(pct_amount)

        if not caps:
            # Unconstrained: allowance equals gross tuition
            return gross_tuition

        return min(caps)


@dataclass(frozen=True)
class AwardSpecification:
    """An award granted or applied to an applicant."""

    award_id: str
    program_id: str
    title: str
    status: AwardStatus
    award_type: AwardType
    priority: int | None = None
    amount: Decimal | None = None
    percentage: Decimal | None = None
    max_award_cap: Decimal | None = None
    incompatible_programs: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.award_id or not self.award_id.strip():
            raise InvalidMonetaryValueError("Award award_id cannot be empty.")

        if self.priority is not None:
            if type(self.priority) is not int or self.priority <= 0:
                raise MissingAwardPriorityError(
                    f"Award '{self.award_id}' priority must be a positive integer (got {self.priority!r})."
                )

        if self.amount is not None:
            amt = quantize_currency(self.amount, "Award amount")
            if amt < Decimal("0.00"):
                raise InvalidMonetaryValueError("Award amount cannot be negative.")
            object.__setattr__(self, "amount", amt)

        if self.percentage is not None:
            pct = validate_finite_decimal(self.percentage, "Award percentage")
            if pct < Decimal("0.00") or pct > Decimal("100.00"):
                raise InvalidMonetaryValueError(
                    "Award percentage must be between 0.00 and 100.00."
                )
            object.__setattr__(self, "percentage", pct)

        if self.max_award_cap is not None:
            cap = quantize_currency(self.max_award_cap, "Award max_award_cap")
            if cap < Decimal("0.00"):
                raise InvalidMonetaryValueError("Award max_award_cap cannot be negative.")
            object.__setattr__(self, "max_award_cap", cap)

        object.__setattr__(
            self, "incompatible_programs", frozenset(self.incompatible_programs)
        )


@dataclass(frozen=True)
class AwardAllocationResult:
    """The allocation and surplus breakdown for a confirmed award."""

    award_id: str
    program_id: str
    title: str
    priority: int
    status: AwardStatus
    nominal_amount: Decimal
    capped_amount: Decimal
    effective_reduction: Decimal
    unapplied_surplus: Decimal
    cap_reason: str | None = None


@dataclass(frozen=True)
class TuitionAccountSummary:
    """Comprehensive, deterministic tuition balance and award accounting report."""

    gross_eligible_tuition: Decimal
    institutional_cap_applied: Decimal
    total_effective_reduction: Decimal
    remaining_payable_tuition: Decimal
    remaining_waiver_allowance: Decimal
    total_unapplied_surplus: Decimal
    confirmed_allocations: list[AwardAllocationResult]
    unconfirmed_awards: list[AwardSpecification]
