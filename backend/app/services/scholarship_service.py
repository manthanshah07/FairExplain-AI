"""
FairExplain AI — Scholarship Business Service
===============================================
Orchestrates deterministic eligibility evaluation, multi-award tuition accounting,
and snapshot persistence.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.accounting import calculate_tuition_accounting
from app.domain.eligibility import evaluate_scholarship_eligibility
from app.domain.enums import (
    AwardStatus,
    AwardType,
    CriterionOperator,
    EligibilityStatus,
    EvidenceStatus,
)
from app.domain.models import (
    ApplicantProfile,
    AwardSpecification,
    EligibilityCriterion,
    InstitutionalCap,
    ScholarshipPolicy,
    quantize_currency,
)
from app.repositories.application_repository import ApplicationRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.policy_repository import PolicyRepository
from app.schemas.scholarship import (
    AwardAllocationDTO,
    CriterionEvaluationDTO,
    ScholarshipEvaluateRequest,
    ScholarshipEvaluateResponseData,
    TuitionAccountingDTO,
)


class ScholarshipService:
    """Service executing scholarship evaluations and tuition accounting."""

    @staticmethod
    async def get_or_seed_policy(
        program_id: str, version: str | None, policy_repo: PolicyRepository
    ) -> ScholarshipPolicy:
        """Fetch policy from DB or seed standard default program policy."""
        domain_pol = await policy_repo.get_as_domain(program_id, version)
        if domain_pol:
            return domain_pol

        # Default policy configuration
        default_policy = ScholarshipPolicy(
            program_id=program_id,
            policy_version=version or "1.0.0",
            title="Institutional Merit & Need Scholarship Program",
            criteria=[
                EligibilityCriterion(
                    criterion_id="CRIT_CGPA",
                    attribute="cgpa",
                    operator=CriterionOperator.GTE,
                    target_value=Decimal("8.00"),
                    is_mandatory=True,
                    required_evidence="marksheet",
                    description="Minimum CGPA of 8.00 required.",
                ),
                EligibilityCriterion(
                    criterion_id="CRIT_BACKLOGS",
                    attribute="active_backlogs",
                    operator=CriterionOperator.LTE,
                    target_value=0,
                    is_mandatory=True,
                    description="Zero active backlogs required.",
                ),
                EligibilityCriterion(
                    criterion_id="CRIT_INCOME",
                    attribute="household_income",
                    operator=CriterionOperator.LTE,
                    target_value=Decimal("800000.00"),
                    is_mandatory=False,
                    required_evidence="income_proof",
                    description="Preferred household income below 8 LPA for need-based bonus.",
                ),
            ],
            incompatible_programs=frozenset(),
            charter_authorizations={},
        )
        await policy_repo.save_domain_policy(default_policy)
        return default_policy

    @staticmethod
    async def evaluate_application(
        req: ScholarshipEvaluateRequest, db: AsyncSession
    ) -> ScholarshipEvaluateResponseData:
        """Evaluate application eligibility, compute accounting, and persist audit snapshots."""
        app_repo = ApplicationRepository(db)
        policy_repo = PolicyRepository(db)
        eval_repo = EvaluationRepository(db)

        # 1. Fetch application aggregate
        app = await app_repo.get_with_relations(req.application_id)
        if not app:
            raise ValueError(f"Application {req.application_id} not found.")

        # 2. Assemble applicant attributes
        attributes: dict[str, Any] = {}
        if app.academic_record:
            attributes["cgpa"] = app.academic_record.cgpa
            attributes["tenth_percent"] = app.academic_record.tenth_percent
            attributes["twelfth_percent"] = app.academic_record.twelfth_percent
            attributes["active_backlogs"] = app.academic_record.backlogs
        if app.financial_profile:
            attributes["household_income"] = app.financial_profile.household_income
            attributes["existing_emi"] = app.financial_profile.existing_emi
            attributes["tuition_fee"] = app.financial_profile.tuition_fee

        # 3. Assemble verified evidence from documents
        evidence_map: dict[str, EvidenceStatus] = {}
        for doc in app.documents:
            doc_type_str = doc.doc_type.value if hasattr(doc.doc_type, "value") else str(doc.doc_type)
            if not doc.mismatch_flag:
                evidence_map[doc_type_str] = EvidenceStatus.VERIFIED
            else:
                evidence_map[doc_type_str] = EvidenceStatus.UNVERIFIED

        # If no documents are uploaded yet, mark required evidence types as MISSING
        if not evidence_map:
            evidence_map["marksheet"] = EvidenceStatus.MISSING
            evidence_map["income_proof"] = EvidenceStatus.MISSING

        profile = ApplicantProfile(
            applicant_id=str(app.id),
            attributes=attributes,
            verified_evidence=evidence_map,
        )

        # 4. Load policy & evaluate eligibility
        policy = await ScholarshipService.get_or_seed_policy(
            req.program_id, req.policy_version, policy_repo
        )
        eval_result = evaluate_scholarship_eligibility(policy, profile)

        # 5. Persist evaluation snapshot
        await eval_repo.save_evaluation(eval_result, app.id, applicant_snapshot=attributes)

        # 6. Prepare awards & compute tuition accounting
        gross_tuition = (
            app.financial_profile.tuition_fee
            if app.financial_profile
            else Decimal("100000.00")
        )

        awards_to_apply: list[AwardSpecification] = []
        if req.awards:
            for dto in req.awards:
                awards_to_apply.append(
                    AwardSpecification(
                        award_id=dto.award_id,
                        program_id=dto.program_id,
                        title=dto.title,
                        status=AwardStatus(dto.status),
                        award_type=AwardType(dto.award_type),
                        priority=dto.priority,
                        amount=dto.amount,
                        percentage=dto.percentage,
                        max_award_cap=dto.max_award_cap,
                        incompatible_programs=frozenset(dto.incompatible_programs),
                    )
                )
        elif eval_result.status == EligibilityStatus.ELIGIBLE:
            # Automatic institutional merit award grant
            awards_to_apply.append(
                AwardSpecification(
                    award_id=f"MERIT_AUTO_{uuid.uuid4().hex[:6]}",
                    program_id=policy.program_id,
                    title="Institutional Merit Grant",
                    status=AwardStatus.CONFIRMED,
                    award_type=AwardType.PERCENTAGE_OF_TUITION,
                    priority=1,
                    percentage=Decimal("50.00"),
                )
            )

        accounting_summary = calculate_tuition_accounting(
            gross_eligible_tuition=gross_tuition,
            awards=awards_to_apply,
            institutional_cap=InstitutionalCap(),
        )

        # 7. Persist tuition account summary
        await eval_repo.save_tuition_accounting(accounting_summary, app.id)
        await db.commit()

        # 8. Build response DTO
        crit_dtos = [
            CriterionEvaluationDTO(
                criterion_id=c.criterion_id,
                attribute=c.attribute,
                operator=c.operator,
                target_value=c.target_value,
                actual_value=c.actual_value,
                status=c.status.value,
                is_mandatory=c.is_mandatory,
                evidence_required=c.evidence_required,
                evidence_status=c.evidence_status.value,
                reason=c.reason,
            )
            for c in eval_result.criteria_evaluations
        ]

        alloc_dtos = [
            AwardAllocationDTO(
                award_id=a.award_id,
                program_id=a.program_id,
                title=a.title,
                priority=a.priority,
                status=a.status.value,
                nominal_amount=a.nominal_amount,
                capped_amount=a.capped_amount,
                effective_reduction=a.effective_reduction,
                unapplied_surplus=a.unapplied_surplus,
                cap_reason=a.cap_reason,
            )
            for a in accounting_summary.confirmed_allocations
        ]

        tuition_dto = TuitionAccountingDTO(
            gross_eligible_tuition=accounting_summary.gross_eligible_tuition,
            institutional_cap_applied=accounting_summary.institutional_cap_applied,
            total_effective_reduction=accounting_summary.total_effective_reduction,
            remaining_payable_tuition=accounting_summary.remaining_payable_tuition,
            remaining_waiver_allowance=accounting_summary.remaining_waiver_allowance,
            total_unapplied_surplus=accounting_summary.total_unapplied_surplus,
            allocations=alloc_dtos,
        )

        return ScholarshipEvaluateResponseData(
            application_id=app.id,
            program_id=policy.program_id,
            policy_version=policy.policy_version,
            status=eval_result.status.value,
            reason=eval_result.reason,
            satisfied_count=eval_result.satisfied_count,
            failed_count=eval_result.failed_count,
            pending_count=eval_result.pending_count,
            criteria_evaluations=crit_dtos,
            tuition_accounting=tuition_dto,
        )
