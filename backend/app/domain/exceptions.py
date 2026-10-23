"""
FairExplain AI — Domain Exceptions
==================================
Hierarchical domain exceptions raised by deterministic business logic.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base exception for all domain logic violations."""


# ---------------------------------------------------------------------------
# Eligibility Exceptions
# ---------------------------------------------------------------------------


class EligibilityError(DomainError):
    """Base exception for scholarship eligibility evaluation errors."""


class MalformedPolicyError(EligibilityError):
    """Raised when a policy or criterion definition is structurally invalid."""


class UnsupportedOperatorError(MalformedPolicyError):
    """Raised when a criterion specifies an unsupported comparison operator."""


class UnsupportedAttributeError(MalformedPolicyError):
    """Raised when a criterion specifies an unrecognized or invalid attribute name."""


class DisallowedAttributeError(MalformedPolicyError):
    """Raised when a criterion attempts to evaluate a prohibited sensitive attribute."""


# ---------------------------------------------------------------------------
# Accounting Exceptions
# ---------------------------------------------------------------------------


class AccountingError(DomainError):
    """Base exception for tuition and award accounting errors."""


class InvalidMonetaryValueError(AccountingError):
    """Raised when an invalid, negative, or unparseable monetary amount is provided."""


class AmbiguousAwardPriorityError(AccountingError):
    """Base exception when award allocation priority is missing or ambiguous."""


class MissingAwardPriorityError(AmbiguousAwardPriorityError):
    """Raised when an applicable confirmed award lacks an explicit priority rank."""


class TiedAwardPriorityError(AmbiguousAwardPriorityError):
    """Raised when multiple applicable confirmed awards share the same priority rank."""


class IncompatibleAwardsError(AccountingError):
    """Raised when mutually exclusive or incompatible confirmed awards are simultaneously applied."""
