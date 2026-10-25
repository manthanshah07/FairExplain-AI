"""
FairExplain AI — Document Cross-Verification Service
======================================================
Cross-checks OCR extracted document fields against applicant self-reported data.
Detects discrepancies, flags mismatches, creates audit logs, and routes to human review.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationStatus
from app.models.audit_log import AuditEventType, AuditLogEntry
from app.models.uploaded_document import DocumentType, UploadedDocument
from app.repositories.application_repository import ApplicationRepository


class VerificationService:
    """Service performing automated document verification and discrepancy screening."""

    @staticmethod
    def verify_cgpa(extracted_cgpa: float, self_reported_cgpa: Decimal) -> tuple[bool, str]:
        """
        Compare CGPA within +/- 0.05 tolerance.
        Returns (is_match, reason).
        """
        diff = abs(Decimal(str(extracted_cgpa)) - self_reported_cgpa)
        if diff <= Decimal("0.05"):
            return True, f"Extracted CGPA ({extracted_cgpa:.2f}) matches self-reported ({self_reported_cgpa:.2f})."
        return False, (
            f"CGPA discrepancy: Extracted {extracted_cgpa:.2f} differs from self-reported "
            f"{self_reported_cgpa:.2f} by {diff:.2f} (exceeds ±0.05 tolerance)."
        )

    @staticmethod
    def verify_income(extracted_income: float, self_reported_income: Decimal) -> tuple[bool, str]:
        """
        Compare household income within +/- 5% tolerance.
        Returns (is_match, reason).
        """
        rep = float(self_reported_income)
        if rep == 0:
            match = extracted_income == 0
            return match, "Zero income verified." if match else "Non-zero income extracted for zero reported."

        pct_diff = abs(extracted_income - rep) / rep
        if pct_diff <= 0.05:
            return True, (
                f"Extracted income (₹{extracted_income:,.2f}) matches self-reported "
                f"(₹{rep:,.2f}) within 5% tolerance."
            )
        return False, (
            f"Income discrepancy: Extracted ₹{extracted_income:,.2f} differs from self-reported "
            f"₹{rep:,.2f} by {pct_diff * 100:.1f}% (exceeds 5% tolerance)."
        )

    @classmethod
    async def verify_application_documents(
        cls, application_id: uuid.UUID, db: AsyncSession
    ) -> dict[str, Any]:
        """
        Cross-check all uploaded documents for an application against self-reported attributes.
        Flags mismatches and logs audit entries.
        """
        app_repo = ApplicationRepository(db)
        app = await app_repo.get_with_relations(application_id)
        if not app:
            raise ValueError(f"Application {application_id} not found.")

        results: dict[str, Any] = {
            "application_id": str(application_id),
            "verified": True,
            "discrepancies": [],
            "documents_checked": len(app.documents),
        }

        has_mismatch = False

        for doc in app.documents:
            extracted = doc.ocr_extracted_data or {}
            doc_type_str = (
                doc.doc_type.value if hasattr(doc.doc_type, "value") else str(doc.doc_type)
            )

            if doc_type_str == "marksheet" and "cgpa" in extracted:
                if app.academic_record:
                    matched, reason = cls.verify_cgpa(
                        extracted["cgpa"], app.academic_record.cgpa
                    )
                    if not matched:
                        has_mismatch = True
                        doc.mismatch_flag = True
                        results["discrepancies"].append({
                            "doc_type": "marksheet",
                            "field": "cgpa",
                            "extracted": extracted["cgpa"],
                            "reported": float(app.academic_record.cgpa),
                            "reason": reason,
                        })
                    else:
                        doc.mismatch_flag = False

            elif doc_type_str == "income_proof" and "annual_income" in extracted:
                if app.financial_profile:
                    matched, reason = cls.verify_income(
                        extracted["annual_income"],
                        app.financial_profile.household_income,
                    )
                    if not matched:
                        has_mismatch = True
                        doc.mismatch_flag = True
                        results["discrepancies"].append({
                            "doc_type": "income_proof",
                            "field": "household_income",
                            "extracted": extracted["annual_income"],
                            "reported": float(app.financial_profile.household_income),
                            "reason": reason,
                        })
                    else:
                        doc.mismatch_flag = False

        if has_mismatch:
            results["verified"] = False
            # Update application status to needs_review
            app.status = ApplicationStatus.needs_review

            # Record audit entry
            audit_entry = AuditLogEntry(
                application_id=app.id,
                event_type=AuditEventType.human_review_action,
                detail={
                    "action": "document_verification_mismatch_flagged",
                    "discrepancies": results["discrepancies"],
                },
            )
            db.add(audit_entry)

        await db.commit()
        return results
