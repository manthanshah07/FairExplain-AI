"""
FairExplain AI — Loan Service
==============================
Orchestrates deterministic loan affordability assessment on post-scholarship balances.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.loan import (
    LoanAffordabilityProfile,
    assess_loan_affordability,
)
from app.models.loan_assessment import LoanAssessment
from app.repositories.application_repository import ApplicationRepository
from app.schemas.loan import LoanAssessRequest, LoanAssessResponseData


class LoanService:
    """Service evaluating education loan affordability and debt burdens."""

    @staticmethod
    async def assess_loan(
        req: LoanAssessRequest, db: AsyncSession
    ) -> LoanAssessResponseData:
        """Assess loan affordability on net tuition balance."""
        app_repo = ApplicationRepository(db)
        app = await app_repo.get_with_relations(req.application_id)
        if not app:
            raise ValueError(f"Application {req.application_id} not found.")

        if not app.financial_profile:
            raise ValueError(f"Application {req.application_id} has no financial profile.")

        # Determine net post-scholarship loan requirement
        if req.requested_loan_amount is not None:
            post_scholarship_loan = req.requested_loan_amount
        elif app.tuition_account_summary:
            post_scholarship_loan = app.tuition_account_summary.remaining_payable_tuition
        else:
            post_scholarship_loan = app.financial_profile.requested_loan

        profile = LoanAffordabilityProfile(
            applicant_id=str(app.id),
            household_income=app.financial_profile.household_income,
            existing_emi=app.financial_profile.existing_emi,
            post_scholarship_loan_amount=post_scholarship_loan,
            tenure_months=req.tenure_months,
        )

        domain_result = assess_loan_affordability(profile)

        # Update or create LoanAssessment entity
        res = await db.execute(
            select(LoanAssessment).where(LoanAssessment.application_id == app.id)
        )
        existing_assessment = res.scalar_one_or_none()

        if existing_assessment:
            existing_assessment.reduced_loan_amount = domain_result.post_scholarship_loan_amount
            existing_assessment.outcome = domain_result.outcome.value
            existing_assessment.confidence = min(
                Decimal("100.00"), domain_result.capacity_utilization_percent
            )
            existing_assessment.rule_engine_version = "1.0.0-phase2"
        else:
            new_assessment = LoanAssessment(
                application_id=app.id,
                reduced_loan_amount=domain_result.post_scholarship_loan_amount,
                outcome=domain_result.outcome.value,
                confidence=min(
                    Decimal("100.00"), domain_result.capacity_utilization_percent
                ),
                rule_engine_version="1.0.0-phase2",
            )
            db.add(new_assessment)

        await db.commit()

        return LoanAssessResponseData(
            application_id=app.id,
            monthly_income=domain_result.monthly_income,
            available_monthly_capacity=domain_result.available_monthly_capacity,
            estimated_emi=domain_result.estimated_emi,
            post_scholarship_loan_amount=domain_result.post_scholarship_loan_amount,
            tenure_months=domain_result.tenure_months,
            outcome=domain_result.outcome.value,
            dti_ratio_percent=domain_result.dti_ratio_percent,
            capacity_utilization_percent=domain_result.capacity_utilization_percent,
            reason=domain_result.reason,
        )
