"""
FairExplain AI — Assessment Report PDF Router
===============================================
REST endpoint for compiling and downloading tamper-evident PDF reports.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.repositories.application_repository import ApplicationRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.services.explanation_service import ExplanationService
from app.services.pdf.report_generator import generate_assessment_pdf

router = APIRouter(tags=["Reporting"])


@router.get(
    "/{application_id}/download",
    summary="Download tamper-evident assessment report as cryptographic PDF",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Downloadable PDF assessment report.",
        }
    },
)
async def download_report(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate, cryptographically sign, and stream official assessment report PDF."""
    app_repo = ApplicationRepository(db)
    eval_repo = EvaluationRepository(db)

    app = await app_repo.get_with_relations(application_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application {application_id} not found.",
        )

    eval_model = await eval_repo.get_latest_evaluation(application_id)
    if not eval_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No evaluation found for application {application_id}.",
        )

    tuition_model = await eval_repo.get_tuition_summary(application_id)
    explanation_res = await ExplanationService.get_explanation(application_id, db)
    explanation_data = explanation_res["explanation"] if explanation_res else {}

    report_payload = {
        "application_id": str(app.id),
        "applicant": {
            "name": getattr(app.user, "name", "Applicant"),
            "email": getattr(app.user, "email", "applicant@example.com"),
        },
        "academic": {
            "cgpa": float(app.academic_record.cgpa) if app.academic_record else 0.0,
            "backlogs": app.academic_record.backlogs if app.academic_record else 0,
        },
        "financial": {
            "household_income": float(app.financial_profile.household_income) if app.financial_profile else 0.0,
            "existing_emi": float(app.financial_profile.existing_emi) if app.financial_profile else 0.0,
            "tuition_fee": float(app.financial_profile.tuition_fee) if app.financial_profile else 0.0,
        },
        "scholarship": {
            "status": eval_model.status,
            "tuition_accounting": {
                "gross_eligible_tuition": float(tuition_model.gross_eligible_tuition) if tuition_model else 0.0,
                "institutional_cap_applied": float(tuition_model.institutional_cap_applied) if tuition_model else 0.0,
                "total_effective_reduction": float(tuition_model.total_effective_reduction) if tuition_model else 0.0,
                "remaining_payable_tuition": float(tuition_model.remaining_payable_tuition) if tuition_model else 0.0,
                "total_unapplied_surplus": float(tuition_model.total_unapplied_surplus) if tuition_model else 0.0,
            },
        },
        "explanation": explanation_data,
    }

    pdf_bytes, audit_hash = generate_assessment_pdf(report_payload)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="assessment_{application_id}.pdf"',
            "X-Audit-Digest": audit_hash,
        },
    )
