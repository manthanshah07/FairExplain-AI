"""
FairExplain AI — Admin Service
================================
Service logic for the Human-in-the-Loop review queue, reviewer determinations,
and institutional cohort analytics aggregations.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.academic_record import AcademicRecord
from app.models.application import Application, ApplicationStatus
from app.models.audit_log import AuditEventType, AuditLogEntry
from app.models.evaluation import (
    CriterionEvaluationSnapshotModel,
    ScholarshipEvaluationModel,
    TuitionAccountSummaryModel,
)
from app.models.explanation_report import AssessmentType, ExplanationReport
from app.models.financial_profile import FinancialProfile
from app.models.loan_assessment import LoanAssessment
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.schemas.admin import (
    AdminAnalyticsResponse,
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    ReviewQueueItem,
    ReviewQueueResponse,
)


class AdminService:
    """Service handling human reviewer queues, override determinations, and institutional metrics."""

    @classmethod
    async def get_review_queue(
        cls,
        db: AsyncSession,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> ReviewQueueResponse:
        """Fetch applications awaiting review or filtered by status, with computed priority and flags."""
        stmt = (
            select(Application)
            .options(
                selectinload(Application.user),
                selectinload(Application.documents),
                selectinload(Application.evaluations),
                selectinload(Application.audit_logs),
            )
            .order_by(desc(Application.created_at))
        )

        if status_filter and status_filter.lower() != "all":
            try:
                app_status = ApplicationStatus(status_filter.lower())
                stmt = stmt.where(Application.status == app_status)
            except ValueError:
                pass
        else:
            # Default to applications in needs_review or submitted
            stmt = stmt.where(
                Application.status.in_([
                    ApplicationStatus.needs_review,
                    ApplicationStatus.submitted,
                    ApplicationStatus.ready_for_report,
                ])
            )

        res = await db.execute(stmt)
        applications = res.scalars().all()

        queue_items: list[ReviewQueueItem] = []
        for app in applications:
            flags: list[str] = []
            has_doc_mismatch = any(doc.mismatch_flag for doc in (app.documents or []))
            if has_doc_mismatch:
                flags.append("Document discrepancy detected")

            has_fairness_flag = any(
                log.event_type == AuditEventType.fairness_flag for log in (app.audit_logs or [])
            )
            if has_fairness_flag:
                flags.append("Fairness / Demographic proxy detected")

            latest_eval = app.evaluations[0] if app.evaluations else None
            program_id = latest_eval.program_id if latest_eval else None
            if latest_eval and latest_eval.status.lower() == "pending_evidence":
                flags.append("Pending evidence required")

            # Determine priority
            app_status_val = app.status.value if hasattr(app.status, "value") else str(app.status)
            if has_fairness_flag or has_doc_mismatch:
                priority = "high"
            elif app_status_val == ApplicationStatus.needs_review.value:
                priority = "medium"
            else:
                priority = "low"

            applicant_name = app.user.name if app.user else "Applicant"
            applicant_email = app.user.email if app.user else "applicant@example.com"
            submission_date = app.created_at.strftime("%Y-%m-%d %H:%M") if app.created_at else "N/A"

            queue_items.append(
                ReviewQueueItem(
                    application_id=app.id,
                    applicant_name=applicant_name,
                    applicant_email=applicant_email,
                    submission_date=submission_date,
                    status=app_status_val,
                    program_id=program_id,
                    flags=flags,
                    priority=priority,
                )
            )

        # Sort: high > medium > low, then by created_at desc (reverse of queue order)
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        queue_items.sort(key=lambda item: priority_rank.get(item.priority, 3))

        total = len(queue_items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = queue_items[start_idx:end_idx]

        return ReviewQueueResponse(
            items=paginated_items,
            total=total,
            page=page,
            page_size=page_size,
        )

    @classmethod
    async def get_review_context(
        cls,
        application_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Fetch the complete dossier for an application for human reviewer inspection."""
        stmt = (
            select(Application)
            .options(
                selectinload(Application.user),
                selectinload(Application.academic_record),
                selectinload(Application.financial_profile),
                selectinload(Application.documents),
                selectinload(Application.evaluations).selectinload(
                    ScholarshipEvaluationModel.criteria_evaluations
                ),
                selectinload(Application.tuition_account_summary),
                selectinload(Application.awards),
                selectinload(Application.audit_logs),
            )
            .where(Application.id == application_id)
        )
        res = await db.execute(stmt)
        app = res.scalar_one_or_none()

        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found.",
            )

        # Retrieve loan assessment if any
        loan_stmt = (
            select(LoanAssessment)
            .where(LoanAssessment.application_id == application_id)
            .order_by(LoanAssessment.created_at.desc())
        )
        loan_res = await db.execute(loan_stmt)
        loan_assessment = loan_res.scalars().first()

        # Retrieve latest evaluation and explanation
        latest_eval = app.evaluations[0] if app.evaluations else None
        explanation_data: dict[str, Any] | None = None
        if latest_eval:
            exp_stmt = (
                select(ExplanationReport)
                .where(
                    ExplanationReport.assessment_id == latest_eval.id,
                    ExplanationReport.assessment_type == AssessmentType.scholarship,
                )
                .order_by(ExplanationReport.created_at.desc())
            )
            exp_res = await db.execute(exp_stmt)
            exp_report = exp_res.scalars().first()
            if exp_report:
                explanation_data = {
                    "recommendation_text": exp_report.recommendation_text,
                    "reasons": exp_report.reasons,
                    "confidence_note": exp_report.confidence_note,
                    "fairness_note": exp_report.fairness_note,
                    "llm_prompt_version": exp_report.llm_prompt_version,
                }

        # OCR Diffs / Document verifications
        ocr_diffs = []
        for doc in (app.documents or []):
            ocr_diffs.append({
                "document_id": str(doc.id),
                "doc_type": doc.doc_type.value if hasattr(doc.doc_type, "value") else str(doc.doc_type),
                "file_url": doc.file_url,
                "mismatch_flag": doc.mismatch_flag,
                "extracted_data": doc.ocr_extracted_data or {},
            })

        # Academic record
        academic_data = {}
        if app.academic_record:
            academic_data = {
                "cgpa": float(app.academic_record.cgpa),
                "tenth_percent": float(app.academic_record.tenth_percent),
                "twelfth_percent": float(app.academic_record.twelfth_percent),
                "backlogs": app.academic_record.backlogs,
            }

        # Financial profile
        financial_data = {}
        if app.financial_profile:
            financial_data = {
                "household_income": float(app.financial_profile.household_income),
                "existing_emi": float(app.financial_profile.existing_emi),
                "tuition_fee": float(app.financial_profile.tuition_fee),
                "requested_loan": float(app.financial_profile.requested_loan),
            }

        # Scholarship evaluation data
        eval_data = None
        if latest_eval:
            eval_data = {
                "id": str(latest_eval.id),
                "program_id": latest_eval.program_id,
                "policy_version": latest_eval.policy_version,
                "status": latest_eval.status,
                "reason": latest_eval.reason,
                "satisfied_count": latest_eval.satisfied_count,
                "failed_count": latest_eval.failed_count,
                "pending_count": latest_eval.pending_count,
                "criteria_breakdown": [
                    {
                        "criterion_id": c.criterion_id,
                        "attribute": c.attribute,
                        "operator": c.operator,
                        "target_value": c.target_value,
                        "actual_value": c.actual_value,
                        "status": c.status,
                        "reason": c.reason,
                    }
                    for c in (latest_eval.criteria_evaluations or [])
                ],
            }

        # Loan assessment data
        loan_data = None
        if loan_assessment:
            loan_data = {
                "reduced_loan_amount": float(loan_assessment.reduced_loan_amount),
                "outcome": loan_assessment.outcome.value if hasattr(loan_assessment.outcome, "value") else str(loan_assessment.outcome),
                "confidence": float(loan_assessment.confidence),
                "rule_engine_version": loan_assessment.rule_engine_version,
            }

        # Audit logs
        logs = [
            {
                "id": str(log.id),
                "event_type": log.event_type.value if hasattr(log.event_type, "value") else str(log.event_type),
                "detail": log.detail,
                "created_at": log.created_at.isoformat() if log.created_at else "",
            }
            for log in (app.audit_logs or [])
        ]

        return {
            "application_id": str(app.id),
            "status": app.status.value if hasattr(app.status, "value") else str(app.status),
            "created_at": app.created_at.isoformat() if app.created_at else "",
            "updated_at": app.updated_at.isoformat() if app.updated_at else "",
            "applicant": {
                "id": str(app.user.id) if app.user else "",
                "name": app.user.name if app.user else "Applicant",
                "email": app.user.email if app.user else "",
            },
            "academic_record": academic_data,
            "financial_profile": financial_data,
            "ocr_diffs": ocr_diffs,
            "scholarship_evaluation": eval_data,
            "loan_assessment": loan_data,
            "explanation": explanation_data,
            "audit_logs": logs,
        }

    @classmethod
    async def record_decision(
        cls,
        application_id: uuid.UUID,
        request: ReviewDecisionRequest,
        db: AsyncSession,
        reviewer: User | None = None,
    ) -> ReviewDecisionResponse:
        """Submit a mandatory-justification reviewer decision (approve, override, reject, request_evidence)."""
        rationale_clean = request.rationale.strip()
        if not rationale_clean or len(rationale_clean) < 3:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Mandatory justification is required for human reviewer determinations.",
            )

        stmt = select(Application).where(Application.id == application_id)
        res = await db.execute(stmt)
        app = res.scalar_one_or_none()

        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found.",
            )

        # Transition application status
        if request.decision in ("approve", "override"):
            app.status = ApplicationStatus.ready_for_report
        elif request.decision == "reject":
            app.status = ApplicationStatus.closed
        elif request.decision == "request_evidence":
            app.status = ApplicationStatus.needs_review

        # Bind reviewer_id strictly to authenticated principal if present
        actual_reviewer_id = str(reviewer.id) if reviewer else (request.reviewer_id or "reviewer")

        # Create immutable AuditLogEntry
        audit_entry = AuditLogEntry(
            application_id=app.id,
            event_type=AuditEventType.human_review_action,
            detail={
                "decision": request.decision,
                "rationale": rationale_clean,
                "reviewer_id": actual_reviewer_id,
                "override_details": request.override_details or {},
                "determined_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(app)
        await db.refresh(audit_entry)

        return ReviewDecisionResponse(
            application_id=app.id,
            status=app.status.value if hasattr(app.status, "value") else str(app.status),
            decision=request.decision,
            rationale=rationale_clean,
            audit_log_id=audit_entry.id,
        )

    @classmethod
    async def get_analytics(cls, db: AsyncSession) -> AdminAnalyticsResponse:
        """Compute institutional analytics across all cohorts."""
        # 1. Total applications and status counts
        total_res = await db.execute(select(func.count(Application.id)))
        total_applications = total_res.scalar() or 0

        status_counts_res = await db.execute(
            select(Application.status, func.count(Application.id)).group_by(Application.status)
        )
        status_distribution: dict[str, int] = {
            "draft": 0,
            "submitted": 0,
            "needs_review": 0,
            "ready_for_report": 0,
            "closed": 0,
        }
        for st, count in status_counts_res.all():
            key = st.value if hasattr(st, "value") else str(st)
            status_distribution[key] = count

        pending_review_count = status_distribution.get("needs_review", 0)
        approved_count = status_distribution.get("ready_for_report", 0)
        rejected_count = status_distribution.get("closed", 0)

        # 2. Eligibility rate percent
        eval_total_res = await db.execute(select(func.count(ScholarshipEvaluationModel.id)))
        eval_total = eval_total_res.scalar() or 0

        eval_eligible_res = await db.execute(
            select(func.count(ScholarshipEvaluationModel.id)).where(
                func.lower(ScholarshipEvaluationModel.status) == "eligible"
            )
        )
        eval_eligible = eval_eligible_res.scalar() or 0
        eligibility_rate_percent = (
            round((eval_eligible / eval_total) * 100, 2) if eval_total > 0 else 0.0
        )

        # 3. Average tuition reduction
        avg_tuition_res = await db.execute(
            select(func.avg(TuitionAccountSummaryModel.total_effective_reduction))
        )
        avg_reduction_dec = avg_tuition_res.scalar()
        average_tuition_reduction = float(avg_reduction_dec) if avg_reduction_dec else 0.0

        # 4. Fairness flag incidence rate
        fairness_flags_res = await db.execute(
            select(func.count(func.distinct(AuditLogEntry.application_id))).where(
                AuditLogEntry.event_type == AuditEventType.fairness_flag
            )
        )
        fairness_flag_apps = fairness_flags_res.scalar() or 0
        fairness_flag_incidence_rate = (
            round((fairness_flag_apps / total_applications) * 100, 2)
            if total_applications > 0
            else 0.0
        )

        # 5. Average turnaround time (default 3.5 hours benchmark)
        average_turnaround_hours = 3.5

        # 6. Recent activity from audit logs
        recent_logs_stmt = (
            select(AuditLogEntry)
            .order_by(desc(AuditLogEntry.created_at))
            .limit(10)
        )
        recent_res = await db.execute(recent_logs_stmt)
        recent_activity = [
            {
                "id": str(log.id),
                "application_id": str(log.application_id),
                "event_type": log.event_type.value if hasattr(log.event_type, "value") else str(log.event_type),
                "detail": log.detail,
                "timestamp": log.created_at.isoformat() if log.created_at else "",
            }
            for log in recent_res.scalars().all()
        ]

        return AdminAnalyticsResponse(
            total_applications=total_applications,
            pending_review_count=pending_review_count,
            approved_count=approved_count,
            rejected_count=rejected_count,
            eligibility_rate_percent=eligibility_rate_percent,
            average_tuition_reduction=average_tuition_reduction,
            fairness_flag_incidence_rate=fairness_flag_incidence_rate,
            average_turnaround_hours=average_turnaround_hours,
            status_distribution=status_distribution,
            recent_activity=recent_activity,
        )
