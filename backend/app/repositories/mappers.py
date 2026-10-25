"""
FairExplain AI — Bidirectional Domain-to-ORM Mappers
=====================================================
Pure bidirectional translation between immutable domain dataclasses
(`app.domain.models`) and SQLAlchemy declarative ORM models (`app.models`).

Rules:
- Domain layer NEVER imports this file or SQLAlchemy.
- Monetary values are rigorously quantized with Decimal precision.
- Conversions must be completely loss-free in round-trip tests.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Mapping, Sequence

from app.domain.enums import (
    AwardStatus,
    AwardType,
    CriterionOperator,
    CriterionOutcome,
    EligibilityStatus,
    EvidenceStatus,
)
from app.domain.models import (
    AwardAllocationResult,
    AwardSpecification,
    CriterionEvaluation,
    EligibilityCriterion,
    EligibilityEvaluationResult,
    ScholarshipPolicy,
    TuitionAccountSummary,
    quantize_currency,
)
from app.models.award import AwardSpecificationModel
from app.models.evaluation import (
    AwardAllocationModel,
    CriterionEvaluationSnapshotModel,
    ScholarshipEvaluationModel,
    TuitionAccountSummaryModel,
)
from app.models.policy import EligibilityCriterionModel, ScholarshipPolicyModel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _serialize_for_json(val: Any) -> Any:
    """Ensure Decimal and custom objects are JSON-serializable for SQL JSON columns."""
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (list, tuple, set, frozenset)):
        return [_serialize_for_json(x) for x in val]
    if isinstance(val, dict):
        return {k: _serialize_for_json(v) for k, v in val.items()}
    return val


# ---------------------------------------------------------------------------
# Policy & Criteria Mappers
# ---------------------------------------------------------------------------


def domain_to_orm_criterion(criterion: EligibilityCriterion) -> EligibilityCriterionModel:
    """Map pure domain EligibilityCriterion to EligibilityCriterionModel."""
    return EligibilityCriterionModel(
        criterion_id=criterion.criterion_id,
        attribute=criterion.attribute,
        operator=criterion.operator.value,
        target_value=_serialize_for_json(criterion.target_value),
        is_mandatory=criterion.is_mandatory,
        required_evidence=criterion.required_evidence,
        description=criterion.description,
        charter_authorization=criterion.charter_authorization,
    )


def orm_to_domain_criterion(model: EligibilityCriterionModel) -> EligibilityCriterion:
    """Map ORM EligibilityCriterionModel to pure domain EligibilityCriterion."""
    return EligibilityCriterion(
        criterion_id=model.criterion_id,
        attribute=model.attribute,
        operator=CriterionOperator.from_string(model.operator),
        target_value=model.target_value,
        is_mandatory=model.is_mandatory,
        required_evidence=model.required_evidence,
        description=model.description,
        charter_authorization=model.charter_authorization,
    )


def domain_to_orm_policy(policy: ScholarshipPolicy) -> ScholarshipPolicyModel:
    """Map pure domain ScholarshipPolicy to ScholarshipPolicyModel."""
    model = ScholarshipPolicyModel(
        program_id=policy.program_id,
        policy_version=policy.policy_version,
        title=policy.title,
        incompatible_programs=sorted(list(policy.incompatible_programs)),
        charter_authorizations=dict(policy.charter_authorizations),
        is_active=True,
    )
    model.criteria = [domain_to_orm_criterion(c) for c in policy.criteria]
    return model


def orm_to_domain_policy(model: ScholarshipPolicyModel) -> ScholarshipPolicy:
    """Map ORM ScholarshipPolicyModel to pure domain ScholarshipPolicy."""
    return ScholarshipPolicy(
        program_id=model.program_id,
        policy_version=model.policy_version,
        title=model.title,
        criteria=tuple(orm_to_domain_criterion(c) for c in model.criteria),
        incompatible_programs=frozenset(model.incompatible_programs or []),
        charter_authorizations=dict(model.charter_authorizations or {}),
    )


# ---------------------------------------------------------------------------
# Award Specification Mappers
# ---------------------------------------------------------------------------


def domain_to_orm_award(
    award: AwardSpecification, application_id: uuid.UUID | None = None
) -> AwardSpecificationModel:
    """Map pure domain AwardSpecification to AwardSpecificationModel."""
    return AwardSpecificationModel(
        application_id=application_id,
        award_id=award.award_id,
        program_id=award.program_id,
        title=award.title,
        status=award.status.value,
        award_type=award.award_type.value,
        priority=award.priority,
        amount=award.amount,
        percentage=award.percentage,
        max_award_cap=award.max_award_cap,
        incompatible_programs=sorted(list(award.incompatible_programs)),
    )


def orm_to_domain_award(model: AwardSpecificationModel) -> AwardSpecification:
    """Map ORM AwardSpecificationModel to pure domain AwardSpecification."""
    return AwardSpecification(
        award_id=model.award_id,
        program_id=model.program_id,
        title=model.title,
        status=AwardStatus(model.status),
        award_type=AwardType(model.award_type),
        priority=model.priority,
        amount=quantize_currency(model.amount) if model.amount is not None else None,
        percentage=Decimal(str(model.percentage)) if model.percentage is not None else None,
        max_award_cap=quantize_currency(model.max_award_cap) if model.max_award_cap is not None else None,
        incompatible_programs=frozenset(model.incompatible_programs or []),
    )


# ---------------------------------------------------------------------------
# Evaluation Result Mappers
# ---------------------------------------------------------------------------


def domain_to_orm_criterion_eval(
    crit_eval: CriterionEvaluation,
) -> CriterionEvaluationSnapshotModel:
    """Map pure domain CriterionEvaluation to CriterionEvaluationSnapshotModel."""
    return CriterionEvaluationSnapshotModel(
        criterion_id=crit_eval.criterion_id,
        attribute=crit_eval.attribute,
        operator=crit_eval.operator,
        target_value=_serialize_for_json(crit_eval.target_value),
        actual_value=_serialize_for_json(crit_eval.actual_value),
        status=crit_eval.status.value,
        is_mandatory=crit_eval.is_mandatory,
        evidence_required=crit_eval.evidence_required,
        evidence_status=crit_eval.evidence_status.value,
        reason=crit_eval.reason,
    )


def orm_to_domain_criterion_eval(
    model: CriterionEvaluationSnapshotModel,
) -> CriterionEvaluation:
    """Map ORM CriterionEvaluationSnapshotModel to pure domain CriterionEvaluation."""
    return CriterionEvaluation(
        criterion_id=model.criterion_id,
        attribute=model.attribute,
        operator=model.operator,
        target_value=model.target_value,
        actual_value=model.actual_value,
        status=CriterionOutcome(model.status),
        is_mandatory=model.is_mandatory,
        evidence_required=model.evidence_required,
        evidence_status=EvidenceStatus(model.evidence_status),
        reason=model.reason,
    )


def domain_to_orm_evaluation(
    result: EligibilityEvaluationResult,
    application_id: uuid.UUID,
    applicant_snapshot: Mapping[str, Any] | None = None,
) -> ScholarshipEvaluationModel:
    """Map pure domain EligibilityEvaluationResult to ScholarshipEvaluationModel."""
    model = ScholarshipEvaluationModel(
        application_id=application_id,
        program_id=result.program_id,
        policy_version=result.policy_version,
        status=result.status.value,
        reason=result.reason,
        satisfied_count=result.satisfied_count,
        failed_count=result.failed_count,
        pending_count=result.pending_count,
        frozen_applicant_snapshot=_serialize_for_json(dict(applicant_snapshot or {})),
    )
    model.criteria_evaluations = [
        domain_to_orm_criterion_eval(c) for c in result.criteria_evaluations
    ]
    return model


def orm_to_domain_evaluation(
    model: ScholarshipEvaluationModel,
) -> EligibilityEvaluationResult:
    """Map ORM ScholarshipEvaluationModel to pure domain EligibilityEvaluationResult."""
    return EligibilityEvaluationResult(
        program_id=model.program_id,
        policy_version=model.policy_version,
        status=EligibilityStatus(model.status),
        reason=model.reason,
        criteria_evaluations=[
            orm_to_domain_criterion_eval(c) for c in model.criteria_evaluations
        ],
        satisfied_count=model.satisfied_count,
        failed_count=model.failed_count,
        pending_count=model.pending_count,
    )


# ---------------------------------------------------------------------------
# Tuition Accounting Mappers
# ---------------------------------------------------------------------------


def domain_to_orm_allocation(
    allocation: AwardAllocationResult,
) -> AwardAllocationModel:
    """Map pure domain AwardAllocationResult to AwardAllocationModel."""
    return AwardAllocationModel(
        award_id=allocation.award_id,
        program_id=allocation.program_id,
        title=allocation.title,
        priority=allocation.priority,
        status=allocation.status.value,
        nominal_amount=allocation.nominal_amount,
        capped_amount=allocation.capped_amount,
        effective_reduction=allocation.effective_reduction,
        unapplied_surplus=allocation.unapplied_surplus,
        cap_reason=allocation.cap_reason,
    )


def orm_to_domain_allocation(
    model: AwardAllocationModel,
) -> AwardAllocationResult:
    """Map ORM AwardAllocationModel to pure domain AwardAllocationResult."""
    return AwardAllocationResult(
        award_id=model.award_id,
        program_id=model.program_id,
        title=model.title,
        priority=model.priority,
        status=AwardStatus(model.status),
        nominal_amount=quantize_currency(model.nominal_amount),
        capped_amount=quantize_currency(model.capped_amount),
        effective_reduction=quantize_currency(model.effective_reduction),
        unapplied_surplus=quantize_currency(model.unapplied_surplus),
        cap_reason=model.cap_reason,
    )


def domain_to_orm_accounting(
    summary: TuitionAccountSummary,
    application_id: uuid.UUID,
    calculator_version: str = "1.0.0-phase1b",
) -> TuitionAccountSummaryModel:
    """Map pure domain TuitionAccountSummary to TuitionAccountSummaryModel."""
    model = TuitionAccountSummaryModel(
        application_id=application_id,
        gross_eligible_tuition=summary.gross_eligible_tuition,
        institutional_cap_applied=summary.institutional_cap_applied,
        total_effective_reduction=summary.total_effective_reduction,
        remaining_payable_tuition=summary.remaining_payable_tuition,
        remaining_waiver_allowance=summary.remaining_waiver_allowance,
        total_unapplied_surplus=summary.total_unapplied_surplus,
        calculator_version=calculator_version,
    )
    model.allocations = [
        domain_to_orm_allocation(a) for a in summary.confirmed_allocations
    ]
    return model


def orm_to_domain_accounting(
    model: TuitionAccountSummaryModel,
    unconfirmed_awards: Sequence[AwardSpecification] | None = None,
) -> TuitionAccountSummary:
    """Map ORM TuitionAccountSummaryModel to pure domain TuitionAccountSummary."""
    return TuitionAccountSummary(
        gross_eligible_tuition=quantize_currency(model.gross_eligible_tuition),
        institutional_cap_applied=quantize_currency(model.institutional_cap_applied),
        total_effective_reduction=quantize_currency(model.total_effective_reduction),
        remaining_payable_tuition=quantize_currency(model.remaining_payable_tuition),
        remaining_waiver_allowance=quantize_currency(model.remaining_waiver_allowance),
        total_unapplied_surplus=quantize_currency(model.total_unapplied_surplus),
        confirmed_allocations=[
            orm_to_domain_allocation(a) for a in model.allocations
        ],
        unconfirmed_awards=list(unconfirmed_awards or []),
    )
