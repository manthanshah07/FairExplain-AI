"""
FairExplain AI — Eligibility Filter Engine
==========================================
Pure Python deterministic evaluation of institution-configured scholarship criteria.
Distinguishes SATISFIED, FAILED, and PENDING_EVIDENCE states.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from app.domain.enums import (
    CriterionOperator,
    CriterionOutcome,
    EligibilityStatus,
    EvidenceStatus,
)
from app.domain.exceptions import MalformedPolicyError
from app.domain.models import (
    ApplicantProfile,
    CriterionEvaluation,
    EligibilityCriterion,
    EligibilityEvaluationResult,
    ScholarshipPolicy,
)


def _to_decimal_if_numeric(val: Any) -> Decimal | None:
    """Attempt conversion to Decimal if the value is an int, float, Decimal or numeric string."""
    if isinstance(val, (int, float, Decimal)):
        try:
            return Decimal(str(val))
        except (InvalidOperation, TypeError):
            return None
    if isinstance(val, str):
        try:
            return Decimal(val.strip())
        except (InvalidOperation, TypeError):
            return None
    return None


def _compare_values(actual: Any, operator: CriterionOperator, target: Any) -> bool:
    """
    Compare actual against target according to the operator.
    Raises MalformedPolicyError on type incompatibility.
    """
    actual_num = _to_decimal_if_numeric(actual)
    target_num = _to_decimal_if_numeric(target)

    # If both are numeric, perform exact Decimal comparison
    both_numeric = (actual_num is not None) and (target_num is not None)

    if operator in (CriterionOperator.IN, CriterionOperator.NOT_IN):
        if not isinstance(target, (list, tuple, set, frozenset)):
            raise MalformedPolicyError(
                f"Operator '{operator.value}' requires target_value to be a list, tuple, or set. "
                f"Got: {type(target).__name__}"
            )
        if actual_num is not None:
            # Check numerically against collection elements
            target_nums = [_to_decimal_if_numeric(item) for item in target]
            in_set = any(t is not None and actual_num == t for t in target_nums)
        else:
            in_set = actual in target

        return in_set if operator == CriterionOperator.IN else not in_set

    if both_numeric:
        a = actual_num
        t = target_num
        if operator == CriterionOperator.EQ:
            return a == t
        if operator == CriterionOperator.NEQ:
            return a != t
        if operator == CriterionOperator.GT:
            return a > t
        if operator == CriterionOperator.GTE:
            return a >= t
        if operator == CriterionOperator.LT:
            return a < t
        if operator == CriterionOperator.LTE:
            return a <= t

    # Non-numeric or mixed comparisons
    if operator == CriterionOperator.EQ:
        return actual == target
    if operator == CriterionOperator.NEQ:
        return actual != target

    # Order comparisons (<, <=, >, >=) require compatible types
    try:
        if operator == CriterionOperator.GT:
            return actual > target
        if operator == CriterionOperator.GTE:
            return actual >= target
        if operator == CriterionOperator.LT:
            return actual < target
        if operator == CriterionOperator.LTE:
            return actual <= target
    except TypeError as exc:
        raise MalformedPolicyError(
            f"Cannot compare '{type(actual).__name__}' with '{type(target).__name__}' "
            f"using operator '{operator.value}': {exc}"
        ) from exc

    raise MalformedPolicyError(f"Unhandled operator: {operator}")


def evaluate_criterion(
    criterion: EligibilityCriterion, applicant: ApplicantProfile
) -> CriterionEvaluation:
    """
    Evaluate a single criterion against an applicant's verified profile.
    Returns CriterionEvaluation with SATISFIED, FAILED, or PENDING_EVIDENCE.
    """
    actual_val = applicant.get_attribute(criterion.attribute)
    evidence_status = applicant.get_evidence_status(criterion.required_evidence)

    # 1. If evidence is required and not verified, outcome is PENDING_EVIDENCE
    if (
        criterion.required_evidence is not None
        and evidence_status != EvidenceStatus.VERIFIED
    ):
        return CriterionEvaluation(
            criterion_id=criterion.criterion_id,
            attribute=criterion.attribute,
            operator=criterion.operator.value,
            target_value=criterion.target_value,
            actual_value=actual_val,
            status=CriterionOutcome.PENDING_EVIDENCE,
            is_mandatory=criterion.is_mandatory,
            evidence_required=criterion.required_evidence,
            evidence_status=evidence_status,
            reason=(
                f"Required evidence '{criterion.required_evidence}' is {evidence_status.value}; "
                "evaluation is pending verified evidence."
            ),
        )

    # 2. If attribute value is missing from the applicant profile
    if actual_val is None:
        return CriterionEvaluation(
            criterion_id=criterion.criterion_id,
            attribute=criterion.attribute,
            operator=criterion.operator.value,
            target_value=criterion.target_value,
            actual_value=None,
            status=CriterionOutcome.PENDING_EVIDENCE,
            is_mandatory=criterion.is_mandatory,
            evidence_required=criterion.required_evidence,
            evidence_status=evidence_status,
            reason=(
                f"Attribute '{criterion.attribute}' value is not provided in applicant profile; "
                "evaluation is pending data submission."
            ),
        )

    # 3. Compare actual against target
    is_satisfied = _compare_values(actual_val, criterion.operator, criterion.target_value)

    if is_satisfied:
        return CriterionEvaluation(
            criterion_id=criterion.criterion_id,
            attribute=criterion.attribute,
            operator=criterion.operator.value,
            target_value=criterion.target_value,
            actual_value=actual_val,
            status=CriterionOutcome.SATISFIED,
            is_mandatory=criterion.is_mandatory,
            evidence_required=criterion.required_evidence,
            evidence_status=evidence_status,
            reason=(
                f"Criterion satisfied: {criterion.attribute} ({actual_val}) "
                f"{criterion.operator.value} {criterion.target_value}."
            ),
        )

    return CriterionEvaluation(
        criterion_id=criterion.criterion_id,
        attribute=criterion.attribute,
        operator=criterion.operator.value,
        target_value=criterion.target_value,
        actual_value=actual_val,
        status=CriterionOutcome.FAILED,
        is_mandatory=criterion.is_mandatory,
        evidence_required=criterion.required_evidence,
        evidence_status=evidence_status,
        reason=(
            f"Criterion failed: {criterion.attribute} ({actual_val}) does not satisfy "
            f"{criterion.operator.value} {criterion.target_value}."
        ),
    )


def evaluate_scholarship_eligibility(
    policy: ScholarshipPolicy, applicant: ApplicantProfile
) -> EligibilityEvaluationResult:
    """
    Evaluate all criteria defined in a scholarship policy against an applicant.

    Rules:
    - ELIGIBLE: Every mandatory criterion is SATISFIED.
    - INELIGIBLE: At least one mandatory criterion is FAILED.
    - PENDING_EVIDENCE: None FAILED, and at least one is PENDING_EVIDENCE.
    """
    evaluations: list[CriterionEvaluation] = []
    satisfied_count = 0
    failed_count = 0
    pending_count = 0

    for criterion in policy.criteria:
        eval_result = evaluate_criterion(criterion, applicant)
        evaluations.append(eval_result)

        if eval_result.status == CriterionOutcome.SATISFIED:
            satisfied_count += 1
        elif eval_result.status == CriterionOutcome.FAILED:
            failed_count += 1
        elif eval_result.status == CriterionOutcome.PENDING_EVIDENCE:
            pending_count += 1

    # Evaluate overall status considering mandatory criteria
    failed_mandatory = [e for e in evaluations if e.is_mandatory and e.status == CriterionOutcome.FAILED]
    pending_mandatory = [e for e in evaluations if e.is_mandatory and e.status == CriterionOutcome.PENDING_EVIDENCE]
    satisfied_mandatory = [e for e in evaluations if e.is_mandatory and e.status == CriterionOutcome.SATISFIED]

    if failed_mandatory:
        status = EligibilityStatus.INELIGIBLE
        failed_attrs = ", ".join(e.attribute for e in failed_mandatory)
        reason = f"Ineligible: {len(failed_mandatory)} mandatory criterion/criteria failed ({failed_attrs})."
    elif pending_mandatory:
        status = EligibilityStatus.PENDING_EVIDENCE
        pending_attrs = ", ".join(e.attribute for e in pending_mandatory)
        reason = f"Pending: {len(pending_mandatory)} mandatory criterion/criteria pending evidence ({pending_attrs})."
    else:
        status = EligibilityStatus.ELIGIBLE
        reason = f"Eligible: All {len(satisfied_mandatory)} mandatory criteria satisfied."

    return EligibilityEvaluationResult(
        program_id=policy.program_id,
        policy_version=policy.policy_version,
        status=status,
        reason=reason,
        criteria_evaluations=evaluations,
        satisfied_count=satisfied_count,
        failed_count=failed_count,
        pending_count=pending_count,
    )
