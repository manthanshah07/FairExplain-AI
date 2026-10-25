"""
FairExplain AI — Integration Tests for Admin Review Queue & Analytics
=======================================================================
Tests review queue retrieval, review context inspection, determination recording,
rationale enforcement, and institutional cohort analytics.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_admin_review_workflow_and_analytics(
    client: AsyncClient,
    student_auth_headers: dict[str, str],
    reviewer_auth_headers: dict[str, str],
) -> None:
    """Test full administrative cycle: inspect queue, view dossier, approve/override with rationale, check analytics."""
    # 1. Create applicant 1 (Needs Review candidate)
    app1_payload = {
        "name": "Jane Reviewee",
        "email": f"jane_{uuid.uuid4().hex[:8]}@example.com",
        "academic_record": {
            "cgpa": 8.75,
            "tenth_percent": 90.0,
            "twelfth_percent": 88.0,
            "backlogs": 0,
        },
        "financial_profile": {
            "household_income": 350000.00,
            "existing_emi": 0.00,
            "tuition_fee": 120000.00,
            "requested_loan": 60000.00,
        },
    }
    resp1 = await client.post(
        "/api/v1/application",
        json=app1_payload,
        headers=student_auth_headers,
    )
    assert resp1.status_code == 201
    app1_id = resp1.json()["data"]["application_id"]

    # Evaluate scholarship & generate explanation
    await client.post(
        "/api/v1/scholarship/evaluate",
        json={"application_id": app1_id, "program_id": "MERIT_NEED_2026"},
        headers=student_auth_headers,
    )
    await client.post(
        "/api/v1/explanation/generate",
        json={"application_id": app1_id},
        headers=student_auth_headers,
    )

    # Trigger fairness audit which passes cleanly
    await client.post(
        f"/api/v1/admin/fairness/audit/{app1_id}",
        headers=reviewer_auth_headers,
    )

    # 2. Query Review Queue
    queue_resp = await client.get(
        "/api/v1/admin/review-queue?status=all&page_size=100",
        headers=reviewer_auth_headers,
    )
    assert queue_resp.status_code == 200
    queue_data = queue_resp.json()["data"]
    assert queue_data["total"] >= 1
    item_ids = [str(item["application_id"]) for item in queue_data["items"]]
    assert app1_id in item_ids

    # 3. Query Review Context Dossier
    context_resp = await client.get(
        f"/api/v1/admin/application/{app1_id}/review-context",
        headers=reviewer_auth_headers,
    )
    assert context_resp.status_code == 200
    context_data = context_resp.json()["data"]
    assert context_data["application_id"] == app1_id
    assert context_data["applicant"]["name"] is not None
    assert context_data["academic_record"]["cgpa"] == 8.75
    assert context_data["financial_profile"]["tuition_fee"] == 120000.00
    assert "scholarship_evaluation" in context_data
    assert isinstance(context_data["audit_logs"], list)

    # 4. Mandatory Rationale Enforcement: Attempt decision without rationale -> 422
    invalid_decision_resp = await client.post(
        f"/api/v1/admin/application/{app1_id}/decision",
        json={
            "decision": "approve",
            "rationale": "   ",
            "reviewer_id": "officer_alice",
        },
        headers=reviewer_auth_headers,
    )
    assert invalid_decision_resp.status_code == 422

    # 5. Submit valid determination (Approval with rationale)
    decision_resp = await client.post(
        f"/api/v1/admin/application/{app1_id}/decision",
        json={
            "decision": "approve",
            "rationale": "Verified income certificate authenticity directly with registrar.",
            "reviewer_id": "officer_alice",
        },
        headers=reviewer_auth_headers,
    )
    assert decision_resp.status_code == 200
    decision_data = decision_resp.json()["data"]
    assert decision_data["status"] == "ready_for_report"
    assert decision_data["decision"] == "approve"
    assert "audit_log_id" in decision_data

    # Verify application status reflects ready_for_report
    app_check = await client.get(
        f"/api/v1/application/{app1_id}",
        headers=student_auth_headers,
    )
    assert app_check.json()["data"]["status"] == "ready_for_report"

    # Verify audit log is now present in review-context
    context_check = await client.get(
        f"/api/v1/admin/application/{app1_id}/review-context",
        headers=reviewer_auth_headers,
    )
    assert len(context_check.json()["data"]["audit_logs"]) >= 1

    # 6. Test Override determination on a second applicant
    app2_payload = {
        "name": "Bob Overridden",
        "email": f"bob_{uuid.uuid4().hex[:8]}@example.com",
        "academic_record": {
            "cgpa": 6.80,
            "tenth_percent": 75.0,
            "twelfth_percent": 72.0,
            "backlogs": 1,
        },
        "financial_profile": {
            "household_income": 600000.00,
            "existing_emi": 5000.00,
            "tuition_fee": 100000.00,
            "requested_loan": 50000.00,
        },
    }
    resp2 = await client.post(
        "/api/v1/application",
        json=app2_payload,
        headers=student_auth_headers,
    )
    app2_id = resp2.json()["data"]["application_id"]

    override_resp = await client.post(
        f"/api/v1/admin/application/{app2_id}/decision",
        json={
            "decision": "override",
            "rationale": "Dean hardship emergency grant granted on athletic scholarship exception.",
            "reviewer_id": "dean_evans",
            "override_details": {"grant_percentage": 50},
        },
        headers=reviewer_auth_headers,
    )
    assert override_resp.status_code == 200
    assert override_resp.json()["data"]["status"] == "ready_for_report"

    # 7. Check Institutional Analytics endpoint
    analytics_resp = await client.get(
        "/api/v1/admin/analytics",
        headers=reviewer_auth_headers,
    )
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()["data"]
    assert analytics["total_applications"] >= 2
    assert analytics["approved_count"] >= 2
    assert "status_distribution" in analytics
    assert "recent_activity" in analytics
    assert len(analytics["recent_activity"]) >= 2
