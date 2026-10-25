"""
FairExplain AI — Integration Tests for Fairness Service & Endpoints
=====================================================================
Tests `/api/v1/admin/fairness/metrics` and `/api/v1/admin/fairness/audit/{id}`.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.db.database import AsyncSessionFactory
from app.models.application import Application, ApplicationStatus
from app.models.audit_log import AuditEventType, AuditLogEntry
from app.models.explanation_report import AssessmentType, ExplanationReport


@pytest.mark.anyio
async def test_fairness_audit_and_metrics_flow(client: AsyncClient) -> None:
    """Test fairness audit intercepting prohibited terms and logging telemetry."""
    # 1. Create application and generate explanation
    app_payload = {
        "name": "Audit Test Applicant",
        "email": f"audit_{uuid.uuid4().hex[:8]}@example.com",
        "academic_record": {
            "cgpa": 8.50,
            "tenth_percent": 88.0,
            "twelfth_percent": 86.0,
            "backlogs": 0,
        },
        "financial_profile": {
            "household_income": 400000.00,
            "existing_emi": 0.00,
            "tuition_fee": 100000.00,
            "requested_loan": 50000.00,
        },
    }
    create_resp = await client.post("/api/v1/application", json=app_payload)
    app_id = create_resp.json()["data"]["application_id"]

    await client.post(
        "/api/v1/scholarship/evaluate",
        json={"application_id": app_id, "program_id": "MERIT_NEED_2026"},
    )
    await client.post("/api/v1/explanation/generate", json={"application_id": app_id})

    # 2. Audit clean explanation - should be clean
    audit_resp = await client.post(f"/api/v1/admin/fairness/audit/{app_id}")
    assert audit_resp.status_code == 200
    assert audit_resp.json()["data"]["is_clean"] is True

    # 3. Inject a prohibited term into ExplanationReport directly to test auditor intercept
    async with AsyncSessionFactory() as session:
        stmt = (
            select(ExplanationReport)
            .join(Application, Application.id == uuid.UUID(app_id))
        )
        res = await session.execute(select(ExplanationReport))
        reports = res.scalars().all()
        # Find the one for our app
        rep = reports[-1]
        rep.recommendation_text = "Approved based on regional caste quota and gender."
        await session.commit()

    # 4. Re-run audit - should detect violation, redact, and route to needs_review
    audit_resp2 = await client.post(f"/api/v1/admin/fairness/audit/{app_id}")
    assert audit_resp2.status_code == 200
    audit_body = audit_resp2.json()["data"]
    assert audit_body["is_clean"] is False
    assert audit_body["violations_count"] >= 2
    assert "[REDACTED_DEMOGRAPHIC_PROXY]" in audit_body["sanitized_text"]

    # 5. Check application status transitioned to needs_review
    get_app = await client.get(f"/api/v1/application/{app_id}")
    assert get_app.json()["data"]["status"] == "needs_review"

    # 6. Verify fairness metrics endpoint
    metrics_resp = await client.get("/api/v1/admin/fairness/metrics")
    assert metrics_resp.status_code == 200
    metrics_body = metrics_resp.json()["data"]
    assert metrics_body["total_applications"] >= 1
    assert metrics_body["fairness_flagged_applications"] >= 1
