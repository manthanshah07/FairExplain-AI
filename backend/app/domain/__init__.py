"""
FairExplain AI — Domain Layer
=============================
Pure Python business logic for deterministic scholarship eligibility evaluation
and tuition accounting.

This package has ZERO external dependencies and is completely isolated from:
- Web frameworks (FastAPI / Starlette)
- Database engines and ORM models (SQLAlchemy)
- External AI SDKs and cloud services
"""

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
    AccountingError,
    AmbiguousAwardPriorityError,
    DisallowedAttributeError,
    DomainError,
    EligibilityError,
    IncompatibleAwardsError,
    InvalidMonetaryValueError,
    MalformedPolicyError,
    MissingAwardPriorityError,
    TiedAwardPriorityError,
    UnsupportedAttributeError,
    UnsupportedOperatorError,
)
from app.domain.models import (
    GENERIC_MERIT_ATTRIBUTES,
    PROGRAM_ELIGIBILITY_ATTRIBUTES,
    SENSITIVE_ATTRIBUTES,
    SUPPORTED_ATTRIBUTES,
    ApplicantProfile,
    AwardAllocationResult,
    AwardSpecification,
    CriterionEvaluation,
    EligibilityCriterion,
    EligibilityEvaluationResult,
    InstitutionalCap,
    ScholarshipPolicy,
    TuitionAccountSummary,
    quantize_currency,
    validate_finite_decimal,
)
from app.domain.eligibility import (
    evaluate_criterion,
    evaluate_scholarship_eligibility,
)
from app.domain.accounting import (
    calculate_tuition_accounting,
)

__all__ = [
    # Enums
    "AttributePurpose",
    "AwardStatus",
    "AwardType",
    "CriterionOperator",
    "CriterionOutcome",
    "EligibilityStatus",
    "EvidenceStatus",
    # Exceptions
    "AccountingError",
    "AmbiguousAwardPriorityError",
    "DisallowedAttributeError",
    "DomainError",
    "EligibilityError",
    "IncompatibleAwardsError",
    "InvalidMonetaryValueError",
    "MalformedPolicyError",
    "MissingAwardPriorityError",
    "TiedAwardPriorityError",
    "UnsupportedAttributeError",
    "UnsupportedOperatorError",
    # Models & Registries
    "ApplicantProfile",
    "AwardAllocationResult",
    "AwardSpecification",
    "CriterionEvaluation",
    "EligibilityCriterion",
    "EligibilityEvaluationResult",
    "GENERIC_MERIT_ATTRIBUTES",
    "InstitutionalCap",
    "PROGRAM_ELIGIBILITY_ATTRIBUTES",
    "SENSITIVE_ATTRIBUTES",
    "SUPPORTED_ATTRIBUTES",
    "ScholarshipPolicy",
    "TuitionAccountSummary",
    "quantize_currency",
    "validate_finite_decimal",
    # Engine Functions
    "evaluate_criterion",
    "evaluate_scholarship_eligibility",
    "calculate_tuition_accounting",
]
