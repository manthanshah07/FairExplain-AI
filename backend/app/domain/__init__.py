"""
FairExplain AI — Domain Layer
=============================
Pure Python business logic for deterministic scholarship eligibility evaluation,
tuition accounting, and loan affordability assessment.

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
    LoanOutcome,
)
from app.domain.exceptions import (
    AccountingError,
    AmbiguousAwardPriorityError,
    DisallowedAttributeError,
    DomainError,
    EligibilityError,
    IncompatibleAwardsError,
    InvalidLoanParametersError,
    InvalidMonetaryValueError,
    LoanError,
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
from app.domain.loan import (
    LoanAffordabilityProfile,
    LoanAffordabilityResult,
    assess_loan_affordability,
)
from app.domain.fairness import (
    FLAGGED_POSTAL_PROXIES,
    PROHIBITED_DEMOGRAPHIC_TERMS,
    FairnessAuditReport,
    FairnessViolation,
    compute_disparate_impact_ratio,
    screen_text_for_proxies,
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
    "LoanOutcome",
    # Exceptions
    "AccountingError",
    "AmbiguousAwardPriorityError",
    "DisallowedAttributeError",
    "DomainError",
    "EligibilityError",
    "IncompatibleAwardsError",
    "InvalidLoanParametersError",
    "InvalidMonetaryValueError",
    "LoanError",
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
    "LoanAffordabilityProfile",
    "LoanAffordabilityResult",
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
    "assess_loan_affordability",
    # Fairness Engine
    "FairnessViolation",
    "FairnessAuditReport",
    "screen_text_for_proxies",
    "compute_disparate_impact_ratio",
    "PROHIBITED_DEMOGRAPHIC_TERMS",
    "FLAGGED_POSTAL_PROXIES",
]
