"""
FairExplain AI — Integration Tests for Domain-to-ORM Mappers
==============================================================
Validates exact, loss-free round-trip conversions between pure domain dataclasses
and SQLAlchemy ORM models.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

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
)
from app.repositories.mappers import (
    domain_to_orm_accounting,
    domain_to_orm_award,
    domain_to_orm_evaluation,
    domain_to_orm_policy,
    orm_to_domain_accounting,
    orm_to_domain_award,
    orm_to_domain_evaluation,
    orm_to_domain_policy,
)


def test_policy_mapper_roundtrip() -> None:
    """Verify ScholarshipPolicy maps to ORM model and back without data drift."""
    criteria = [
        EligibilityCriterion(
            criterion_id="CRIT_CGPA",
            attribute="cgpa",
            operator=CriterionOperator.GTE,
            target_value=8.5,
            is_mandatory=True,
            required_evidence="marksheet",
            description="Minimum CGPA of 8.5",
        ),
        EligibilityCriterion(
            criterion_id="CRIT_INCOME",
            attribute="household_income",
            operator=CriterionOperator.LTE,
            target_value=500000,
            is_mandatory=True,
            required_evidence="income_certificate",
            description="Income cap 5 LPA",
        ),
    ]

    domain_policy = ScholarshipPolicy(
        program_id="SCHOLAR_MERIT_2026",
        policy_version="1.0.0",
        title="Merit Scholarship 2026",
        criteria=criteria,
        incompatible_programs=frozenset({"SPORTS_2026"}),
        charter_authorizations={"household_income": "CHARTER_ORDER_42"},
    )

    orm_model = domain_to_orm_policy(domain_policy)
    assert orm_model.program_id == "SCHOLAR_MERIT_2026"
    assert orm_model.policy_version == "1.0.0"
    assert len(orm_model.criteria) == 2

    restored = orm_to_domain_policy(orm_model)
    assert restored.program_id == domain_policy.program_id
    assert restored.policy_version == domain_policy.policy_version
    assert restored.title == domain_policy.title
    assert restored.incompatible_programs == domain_policy.incompatible_programs
    assert restored.charter_authorizations == domain_policy.charter_authorizations
    assert len(restored.criteria) == len(domain_policy.criteria)

    c0 = restored.criteria[0]
    assert c0.criterion_id == "CRIT_CGPA"
    assert c0.attribute == "cgpa"
    assert c0.operator == CriterionOperator.GTE
    assert c0.target_value == 8.5
    assert c0.is_mandatory is True
    assert c0.required_evidence == "marksheet"


def test_award_specification_mapper_roundtrip() -> None:
    """Verify AwardSpecification maps to ORM and back with strict Decimal precision."""
    award = AwardSpecification(
        award_id="AWARD_MERIT_101",
        program_id="PROG_MERIT",
        title="Merit Award Tier 1",
        status=AwardStatus.CONFIRMED,
        award_type=AwardType.FIXED_AMOUNT,
        priority=1,
        amount=Decimal("50000.00"),
        percentage=None,
        max_award_cap=Decimal("60000.00"),
        incompatible_programs=frozenset({"NEED_BASED_2026"}),
    )

    app_id = uuid.uuid4()
    orm_model = domain_to_orm_award(award, application_id=app_id)
    assert orm_model.application_id == app_id
    assert orm_model.award_id == "AWARD_MERIT_101"
    assert orm_model.amount == Decimal("50000.00")

    restored = orm_to_domain_award(orm_model)
    assert restored.award_id == award.award_id
    assert restored.program_id == award.program_id
    assert restored.title == award.title
    assert restored.status == AwardStatus.CONFIRMED
    assert restored.award_type == AwardType.FIXED_AMOUNT
    assert restored.priority == 1
    assert restored.amount == Decimal("50000.00")
    assert restored.max_award_cap == Decimal("60000.00")
    assert restored.incompatible_programs == frozenset({"NEED_BASED_2026"})


def test_evaluation_result_mapper_roundtrip() -> None:
    """Verify EligibilityEvaluationResult converts losslessly."""
    crit_evals = [
        CriterionEvaluation(
            criterion_id="CRIT_1",
            attribute="cgpa",
            operator="GTE",
            target_value=8.0,
            actual_value=8.75,
            status=CriterionOutcome.SATISFIED,
            is_mandatory=True,
            evidence_required="marksheet",
            evidence_status=EvidenceStatus.VERIFIED,
            reason="Applicant CGPA 8.75 >= 8.0",
        ),
        CriterionEvaluation(
            criterion_id="CRIT_2",
            attribute="household_income",
            operator="LTE",
            target_value=300000,
            actual_value=450000,
            status=CriterionOutcome.FAILED,
            is_mandatory=True,
            evidence_required="income_cert",
            evidence_status=EvidenceStatus.VERIFIED,
            reason="Applicant income 450000 > 300000",
        ),
    ]

    domain_eval = EligibilityEvaluationResult(
        program_id="PROG_TEST",
        policy_version="2.1.0",
        status=EligibilityStatus.INELIGIBLE,
        reason="1 mandatory criterion failed.",
        criteria_evaluations=crit_evals,
        satisfied_count=1,
        failed_count=1,
        pending_count=0,
    )

    app_id = uuid.uuid4()
    orm_model = domain_to_orm_evaluation(
        domain_eval, app_id, applicant_snapshot={"cgpa": 8.75, "household_income": 450000}
    )

    assert orm_model.application_id == app_id
    assert orm_model.status == "ineligible"
    assert len(orm_model.criteria_evaluations) == 2
    assert orm_model.frozen_applicant_snapshot["cgpa"] == 8.75

    restored = orm_to_domain_evaluation(orm_model)
    assert restored.program_id == domain_eval.program_id
    assert restored.policy_version == domain_eval.policy_version
    assert restored.status == EligibilityStatus.INELIGIBLE
    assert restored.satisfied_count == 1
    assert restored.failed_count == 1
    assert len(restored.criteria_evaluations) == 2
    assert restored.criteria_evaluations[0].status == CriterionOutcome.SATISFIED
    assert restored.criteria_evaluations[1].status == CriterionOutcome.FAILED


def test_tuition_accounting_mapper_roundtrip() -> None:
    """Verify TuitionAccountSummary and allocations convert losslessly with exact Decimals."""
    allocations = [
        AwardAllocationResult(
            award_id="AW_1",
            program_id="PROG_1",
            title="Dean's List Award",
            priority=1,
            status=AwardStatus.CONFIRMED,
            nominal_amount=Decimal("40000.00"),
            capped_amount=Decimal("40000.00"),
            effective_reduction=Decimal("40000.00"),
            unapplied_surplus=Decimal("0.00"),
            cap_reason=None,
        ),
        AwardAllocationResult(
            award_id="AW_2",
            program_id="PROG_2",
            title="Alumni Grant",
            priority=2,
            status=AwardStatus.CONFIRMED,
            nominal_amount=Decimal("30000.00"),
            capped_amount=Decimal("30000.00"),
            effective_reduction=Decimal("10000.00"),
            unapplied_surplus=Decimal("20000.00"),
            cap_reason="Remaining tuition was only 10000.00",
        ),
    ]

    summary = TuitionAccountSummary(
        gross_eligible_tuition=Decimal("50000.00"),
        institutional_cap_applied=Decimal("50000.00"),
        total_effective_reduction=Decimal("50000.00"),
        remaining_payable_tuition=Decimal("0.00"),
        remaining_waiver_allowance=Decimal("0.00"),
        total_unapplied_surplus=Decimal("20000.00"),
        confirmed_allocations=allocations,
        unconfirmed_awards=[],
    )

    app_id = uuid.uuid4()
    orm_model = domain_to_orm_accounting(summary, app_id)

    assert orm_model.gross_eligible_tuition == Decimal("50000.00")
    assert orm_model.remaining_payable_tuition == Decimal("0.00")
    assert orm_model.total_unapplied_surplus == Decimal("20000.00")
    assert len(orm_model.allocations) == 2

    restored = orm_to_domain_accounting(orm_model)
    assert restored.gross_eligible_tuition == Decimal("50000.00")
    assert restored.remaining_payable_tuition == Decimal("0.00")
    assert restored.total_unapplied_surplus == Decimal("20000.00")
    assert len(restored.confirmed_allocations) == 2
    assert restored.confirmed_allocations[0].effective_reduction == Decimal("40000.00")
    assert restored.confirmed_allocations[1].unapplied_surplus == Decimal("20000.00")
