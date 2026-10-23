"""
FairExplain AI — Domain Enums
=============================
Canonical enumerations for eligibility outcomes, operators, and award lifecycles.
"""

from __future__ import annotations

from enum import Enum


class CriterionOperator(str, Enum):
    """Comparison operators supported in eligibility criteria."""

    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"

    @classmethod
    def from_string(cls, val: str) -> CriterionOperator:
        """Parse operator from string with synonym mapping."""
        mapping = {
            "eq": cls.EQ,
            "==": cls.EQ,
            "=": cls.EQ,
            "equals": cls.EQ,
            "neq": cls.NEQ,
            "!=": cls.NEQ,
            "not_equals": cls.NEQ,
            "gt": cls.GT,
            ">": cls.GT,
            "gte": cls.GTE,
            ">=": cls.GTE,
            "lt": cls.LT,
            "<": cls.LT,
            "lte": cls.LTE,
            "<=": cls.LTE,
            "in": cls.IN,
            "not_in": cls.NOT_IN,
        }
        normalized = val.strip().lower()
        if normalized not in mapping:
            from app.domain.exceptions import UnsupportedOperatorError

            raise UnsupportedOperatorError(
                f"Unsupported criterion operator: '{val}'. "
                f"Supported operators are: {list(mapping.keys())}"
            )
        return mapping[normalized]


class CriterionOutcome(str, Enum):
    """Evaluation outcome for an individual criterion."""

    SATISFIED = "satisfied"
    FAILED = "failed"
    PENDING_EVIDENCE = "pending_evidence"


class EligibilityStatus(str, Enum):
    """Overall eligibility status of an applicant for a scholarship program."""

    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    PENDING_EVIDENCE = "pending_evidence"


class EvidenceStatus(str, Enum):
    """Verification state of a required supporting evidence document."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    MISSING = "missing"
    NOT_REQUIRED = "not_required"


class AwardStatus(str, Enum):
    """Lifecycle status of a scholarship award for an applicant."""

    CONFIRMED = "confirmed"
    ELIGIBLE = "eligible"
    APPLIED = "applied"
    PENDING = "pending"
    PROVISIONALLY_AWARDED = "provisionally_awarded"
    REJECTED = "rejected"


class AwardType(str, Enum):
    """Method by which the scholarship award amount is computed."""

    FIXED_AMOUNT = "fixed_amount"
    PERCENTAGE_OF_TUITION = "percentage_of_tuition"


class AttributePurpose(str, Enum):
    """Permitted purpose classifications for domain attributes."""

    MERIT_RANKING = "merit_ranking"
    PROGRAM_ELIGIBILITY = "program_eligibility"
    RESTRICTED_SENSITIVE = "restricted_sensitive"
