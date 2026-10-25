"""
FairExplain AI — Integration Tests for Repositories
=====================================================
Validates persistence, foreign key relationships, and query operations
against PostgreSQL using AsyncSessionFactory.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.db.database import AsyncSessionFactory
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
    CriterionEvaluation,
    EligibilityCriterion,
    EligibilityEvaluationResult,
    ScholarshipPolicy,
    TuitionAccountSummary,
)
from app.models.academic_record import AcademicRecord
from app.models.application import Application, ApplicationStatus
from app.models.financial_profile import FinancialProfile
from app.models.user import User, UserRole
from app.repositories.application_repository import ApplicationRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.policy_repository import PolicyRepository


@pytest.mark.anyio
async def test_policy_repository_save_and_retrieve() -> None:
    """Test saving a domain policy and querying it back from PostgreSQL."""
    async with AsyncSessionFactory() as session:
        repo = PolicyRepository(session)
        prog_id = f"TEST_PROG_{uuid.uuid4().hex[:8]}"

        policy = ScholarshipPolicy(
            program_id=prog_id,
            policy_version="1.0.0",
            title="Postgres Policy Test",
            criteria=[
                EligibilityCriterion(
                    criterion_id="CRIT_CGPA",
                    attribute="cgpa",
                    operator=CriterionOperator.GTE,
                    target_value=8.0,
                    is_mandatory=True,
                )
            ],
            incompatible_programs=frozenset(),
            charter_authorizations={},
        )

        saved = await repo.save_domain_policy(policy)
        await session.commit()

        assert saved.id is not None
        assert saved.program_id == prog_id

    # Retrieve in a new session
    async with AsyncSessionFactory() as session:
        repo = PolicyRepository(session)
        loaded = await repo.get_as_domain(prog_id, "1.0.0")
        assert loaded is not None
        assert loaded.program_id == prog_id
        assert len(loaded.criteria) == 1
        assert loaded.criteria[0].criterion_id == "CRIT_CGPA"


@pytest.mark.anyio
async def test_application_repository_aggregate() -> None:
    """Test Application lifecycle, relationships, and queries."""
    async with AsyncSessionFactory() as session:
        # Create user
        user = User(
            name="Test Student",
            email=f"student_{uuid.uuid4().hex[:8]}@example.com",
            hashed_password="hashed_test_password",
            role=UserRole.student,
        )
        session.add(user)
        await session.flush()

        app_repo = ApplicationRepository(session)
        app = await app_repo.create_application(user.id, ApplicationStatus.draft)

        # Add academic record and financial profile
        acad = AcademicRecord(
            application_id=app.id,
            cgpa=Decimal("8.90"),
            tenth_percent=Decimal("92.50"),
            twelfth_percent=Decimal("89.00"),
            backlogs=0,
        )
        fin = FinancialProfile(
            application_id=app.id,
            household_income=Decimal("450000.00"),
            existing_emi=Decimal("5000.00"),
            tuition_fee=Decimal("120000.00"),
            requested_loan=Decimal("80000.00"),
        )
        session.add(acad)
        session.add(fin)
        await session.commit()
        app_id = app.id

    # Query with relations in new session
    async with AsyncSessionFactory() as session:
        app_repo = ApplicationRepository(session)
        full_app = await app_repo.get_with_relations(app_id)
        assert full_app is not None
        assert full_app.academic_record is not None
        assert full_app.academic_record.cgpa == Decimal("8.90")
        assert full_app.financial_profile is not None
        assert full_app.financial_profile.household_income == Decimal("450000.00")

        # Update status
        updated = await app_repo.update_status(app_id, ApplicationStatus.submitted)
        await session.commit()
        assert updated is not None
        assert updated.status == ApplicationStatus.submitted


@pytest.mark.anyio
async def test_evaluation_repository_persistence() -> None:
    """Test persisting evaluation snapshots and tuition account summaries."""
    async with AsyncSessionFactory() as session:
        # Create user & application
        user = User(
            name="Eval Student",
            email=f"eval_{uuid.uuid4().hex[:8]}@example.com",
            hashed_password="pw",
            role=UserRole.student,
        )
        session.add(user)
        await session.flush()

        app = Application(user_id=user.id, status=ApplicationStatus.submitted)
        session.add(app)
        await session.flush()
        app_id = app.id
        await session.commit()

    async with AsyncSessionFactory() as session:
        eval_repo = EvaluationRepository(session)

        # 1. Save evaluation result
        eval_result = EligibilityEvaluationResult(
            program_id="PROG_STEM",
            policy_version="1.0.0",
            status=EligibilityStatus.ELIGIBLE,
            reason="All mandatory criteria passed.",
            criteria_evaluations=[
                CriterionEvaluation(
                    criterion_id="CRIT_1",
                    attribute="cgpa",
                    operator="GTE",
                    target_value=8.0,
                    actual_value=9.0,
                    status=CriterionOutcome.SATISFIED,
                    is_mandatory=True,
                    evidence_required=None,
                    evidence_status=EvidenceStatus.NOT_REQUIRED,
                    reason="Passed",
                )
            ],
            satisfied_count=1,
            failed_count=0,
            pending_count=0,
        )

        saved_eval = await eval_repo.save_evaluation(
            eval_result, app_id, applicant_snapshot={"cgpa": 9.0}
        )
        assert saved_eval.id is not None
        assert saved_eval.status == "eligible"

        # 2. Save tuition accounting summary
        summary = TuitionAccountSummary(
            gross_eligible_tuition=Decimal("100000.00"),
            institutional_cap_applied=Decimal("100000.00"),
            total_effective_reduction=Decimal("60000.00"),
            remaining_payable_tuition=Decimal("40000.00"),
            remaining_waiver_allowance=Decimal("40000.00"),
            total_unapplied_surplus=Decimal("0.00"),
            confirmed_allocations=[
                AwardAllocationResult(
                    award_id="AW_STEM_60K",
                    program_id="PROG_STEM",
                    title="STEM Excellence",
                    priority=1,
                    status=AwardStatus.CONFIRMED,
                    nominal_amount=Decimal("60000.00"),
                    capped_amount=Decimal("60000.00"),
                    effective_reduction=Decimal("60000.00"),
                    unapplied_surplus=Decimal("0.00"),
                )
            ],
            unconfirmed_awards=[],
        )

        saved_summary = await eval_repo.save_tuition_accounting(summary, app_id)
        await session.commit()
        assert saved_summary.id is not None
        assert saved_summary.remaining_payable_tuition == Decimal("40000.00")

    # Read back in fresh session
    async with AsyncSessionFactory() as session:
        eval_repo = EvaluationRepository(session)
        latest_eval = await eval_repo.get_latest_evaluation(app_id)
        assert latest_eval is not None
        assert latest_eval.program_id == "PROG_STEM"
        assert len(latest_eval.criteria_evaluations) == 1

        tuition_summ = await eval_repo.get_tuition_summary(app_id)
        assert tuition_summ is not None
        assert tuition_summ.remaining_payable_tuition == Decimal("40000.00")
        assert len(tuition_summ.allocations) == 1
        assert tuition_summ.allocations[0].award_id == "AW_STEM_60K"
