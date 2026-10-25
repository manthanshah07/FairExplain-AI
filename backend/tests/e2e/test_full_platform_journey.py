"""
FairExplain AI — End-to-End Platform Smoke Test Journey
=========================================================
Tests the complete applicant and administrative institutional journey:
1. Applicant profile submission
2. Supporting document upload (PDF marksheet)
3. OCR cross-verification
4. Deterministic scholarship evaluation
5. Deterministic loan affordability assessment
6. Grounded explainable AI generation with guardrails
7. Fairness screening & proxy leakage audit
8. Admin review context dossier inspection
9. Human reviewer determination with mandatory rationale
10. Download and verification of cryptographic PDF assessment report
11. Cohort analytics aggregation verification
"""

from __future__ import annotations

import io
import uuid
import pytest
from httpx import AsyncClient
from reportlab.pdfgen import canvas


def _create_sample_pdf(content: str = "Test Marksheet CGPA: 9.15") -> bytes:
    """Generate in-memory PDF marksheet bytes for upload."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, "Official Academic Marksheet")
    c.drawString(100, 700, content)
    c.save()
    buf.seek(0)
    return buf.getvalue()


@pytest.mark.anyio
async def test_full_platform_applicant_to_decision_journey(client: AsyncClient) -> None:
    """Execute end-to-end platform smoke test journey."""
    # -------------------------------------------------------------------------
    # Step 1: Submit Application
    # -------------------------------------------------------------------------
    applicant_payload = {
        "name": "Priya Sharma",
        "email": f"priya_{uuid.uuid4().hex[:8]}@university.edu",
        "academic_record": {
            "cgpa": 9.15,
            "tenth_percent": 94.5,
            "twelfth_percent": 92.0,
            "backlogs": 0,
        },
        "financial_profile": {
            "household_income": 300000.00,
            "existing_emi": 0.00,
            "tuition_fee": 150000.00,
            "requested_loan": 75000.00,
        },
    }
    app_resp = await client.post("/api/v1/application", json=applicant_payload)
    assert app_resp.status_code == 201
    app_id = app_resp.json()["data"]["application_id"]
    assert app_id is not None

    # -------------------------------------------------------------------------
    # Step 2: Upload Supporting Academic Marksheet
    # -------------------------------------------------------------------------
    pdf_bytes = _create_sample_pdf("Cumulative Grade Point Average (CGPA): 9.15")
    files = {"file": ("marksheet.pdf", pdf_bytes, "application/pdf")}
    upload_resp = await client.post(
        "/api/v1/documents/upload",
        data={"application_id": app_id, "doc_type": "marksheet"},
        files=files,
    )
    assert upload_resp.status_code == 201
    assert upload_resp.json()["data"]["document_id"] is not None

    # -------------------------------------------------------------------------
    # Step 3: OCR Cross-Verification
    # -------------------------------------------------------------------------
    verify_resp = await client.post(f"/api/v1/documents/verify/{app_id}")
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()["data"]
    assert verify_data["application_id"] == app_id
    assert verify_data["documents_checked"] >= 1

    # -------------------------------------------------------------------------
    # Step 4: Deterministic Scholarship Eligibility Evaluation
    # -------------------------------------------------------------------------
    scholarship_resp = await client.post(
        "/api/v1/scholarship/evaluate",
        json={"application_id": app_id, "program_id": "MERIT_NEED_2026"},
    )
    assert scholarship_resp.status_code == 200
    s_data = scholarship_resp.json()["data"]
    assert s_data["status"] == "eligible"
    assert float(s_data["tuition_accounting"]["remaining_payable_tuition"]) == 75000.00

    # -------------------------------------------------------------------------
    # Step 5: Deterministic Loan Affordability Assessment
    # -------------------------------------------------------------------------
    loan_resp = await client.post(
        "/api/v1/loan/assess",
        json={"application_id": app_id, "tenure_months": 60},
    )
    assert loan_resp.status_code == 200
    l_data = loan_resp.json()["data"]
    assert l_data["outcome"] == "eligible"
    assert float(l_data["post_scholarship_loan_amount"]) == 75000.00
    assert float(l_data["estimated_emi"]) > 0

    # -------------------------------------------------------------------------
    # Step 6: Grounded Explainable AI Generation
    # -------------------------------------------------------------------------
    exp_resp = await client.post(
        "/api/v1/explanation/generate",
        json={"application_id": app_id},
    )
    assert exp_resp.status_code == 200
    exp_data = exp_resp.json()["data"]["explanation"]
    assert exp_data["summary_headline"] != ""
    assert len(exp_data["reasons"]) >= 1
    assert "officer" in exp_data["human_review_notice"].lower() or "review" in exp_data["human_review_notice"].lower()

    # -------------------------------------------------------------------------
    # Step 7: Fairness Screening & Proxy Leakage Audit
    # -------------------------------------------------------------------------
    audit_resp = await client.post(f"/api/v1/admin/fairness/audit/{app_id}")
    assert audit_resp.status_code == 200
    assert audit_resp.json()["data"]["is_clean"] is True

    # -------------------------------------------------------------------------
    # Step 8: Admin Review Dossier Inspection
    # -------------------------------------------------------------------------
    context_resp = await client.get(f"/api/v1/admin/application/{app_id}/review-context")
    assert context_resp.status_code == 200
    ctx = context_resp.json()["data"]
    assert ctx["applicant"]["name"] == "Priya Sharma"
    assert ctx["academic_record"]["cgpa"] == 9.15
    assert ctx["scholarship_evaluation"]["status"] == "eligible"
    assert len(ctx["ocr_diffs"]) >= 1

    # -------------------------------------------------------------------------
    # Step 9: Human Reviewer Approval Determination
    # -------------------------------------------------------------------------
    decision_resp = await client.post(
        f"/api/v1/admin/application/{app_id}/decision",
        json={
            "decision": "approve",
            "rationale": "All verified metrics match official university registry. Approved for full 50% waiver.",
            "reviewer_id": "senior_underwriter_smith",
        },
    )
    assert decision_resp.status_code == 200
    assert decision_resp.json()["data"]["status"] == "ready_for_report"

    # -------------------------------------------------------------------------
    # Step 10: Download Cryptographic Assessment PDF Report
    # -------------------------------------------------------------------------
    pdf_resp = await client.get(f"/api/v1/report/{app_id}/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in pdf_resp.headers["content-disposition"]
    assert len(pdf_resp.content) > 1000
    assert pdf_resp.content.startswith(b"%PDF-")
    assert "x-audit-sha256" in pdf_resp.headers
    sha256_seal = pdf_resp.headers["x-audit-sha256"]
    assert len(sha256_seal) == 64

    # -------------------------------------------------------------------------
    # Step 11: Institutional Analytics Aggregation
    # -------------------------------------------------------------------------
    analytics_resp = await client.get("/api/v1/admin/analytics")
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()["data"]
    assert analytics["total_applications"] >= 1
    assert analytics["approved_count"] >= 1
    assert analytics["eligibility_rate_percent"] > 0
