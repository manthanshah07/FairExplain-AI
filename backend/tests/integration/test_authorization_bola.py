"""
FairExplain AI — Authorization & BOLA Security Regression Tests
===============================================================
Verifies:
1. Unauthenticated requests are rejected with 401 across protected routes.
2. Cross-tenant / cross-user application access is rejected with 403 (BOLA prevention).
3. Cross-tenant document access is rejected with 403.
4. Role-Based Access Control (RBAC) blocks non-reviewers/students from reviewer actions.
5. Authorized reviewers can inspect student applications and record decisions.
6. Reviewer identity in audit logs is strictly bound to the authenticated JWT principal.
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.db.database import AsyncSessionFactory
from app.models.audit_log import AuditLogEntry
from app.models.user import User


@pytest.mark.anyio
async def test_unauthenticated_requests_return_401(client: AsyncClient) -> None:
    """Unauthenticated requests must be rejected with 401 Unauthorized across all protected surfaces."""
    dummy_id = uuid.uuid4()

    # Application endpoint
    resp = await client.get(f"/api/v1/application/{dummy_id}")
    assert resp.status_code == 401

    # Admin endpoints
    resp = await client.get("/api/v1/admin/review-queue")
    assert resp.status_code == 401

    resp = await client.post(
        f"/api/v1/admin/application/{dummy_id}/decision",
        json={"decision": "approve", "rationale": "Test justification"},
    )
    assert resp.status_code == 401

    # Document endpoints
    resp = await client.get(f"/api/v1/documents/application/{dummy_id}")
    assert resp.status_code == 401

    resp = await client.get(f"/api/v1/documents/{dummy_id}/download-url")
    assert resp.status_code == 401

    # Report & domain endpoints
    resp = await client.get(f"/api/v1/report/{dummy_id}/pdf")
    assert resp.status_code == 401

    resp = await client.post(
        "/api/v1/scholarship/evaluate",
        json={"application_id": str(dummy_id), "program_id": "MERIT_NEED_2026"},
    )
    assert resp.status_code == 401

    resp = await client.post(
        "/api/v1/loan/assess",
        json={"application_id": str(dummy_id)},
    )
    assert resp.status_code == 401

    resp = await client.get(f"/api/v1/explanation/{dummy_id}")
    assert resp.status_code == 401

    resp = await client.get("/api/v1/admin/fairness/metrics")
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_bola_student_cannot_access_other_student_application(
    client: AsyncClient,
    student_user: User,
    student_auth_headers: dict[str, str],
    other_student_user: User,
    other_student_auth_headers: dict[str, str],
) -> None:
    """BOLA check: Student B must NOT be able to access Student A's application."""
    # Student A creates an application
    create_resp = await client.post(
        "/api/v1/application",
        json={
            "name": student_user.name,
            "email": student_user.email,
            "academic_record": {
                "cgpa": 9.2,
                "tenth_percent": 95.0,
                "twelfth_percent": 93.0,
                "backlogs": 0,
            },
            "financial_profile": {
                "household_income": 450000.0,
                "existing_emi": 0.0,
                "tuition_fee": 120000.0,
                "requested_loan": 80000.0,
            },
        },
        headers=student_auth_headers,
    )
    assert create_resp.status_code == 201
    app_id = create_resp.json()["data"]["application_id"]

    # Student A can access own application
    get_a_resp = await client.get(f"/api/v1/application/{app_id}", headers=student_auth_headers)
    assert get_a_resp.status_code == 200
    assert get_a_resp.json()["data"]["application_id"] == app_id

    # Student B attempts to access Student A's application -> 403 Forbidden
    get_b_resp = await client.get(f"/api/v1/application/{app_id}", headers=other_student_auth_headers)
    assert get_b_resp.status_code == 403
    assert "Forbidden" in get_b_resp.json().get("detail", "") or "Access denied" in get_b_resp.json().get("detail", "")


@pytest.mark.anyio
async def test_bola_student_cannot_access_other_student_documents(
    client: AsyncClient,
    student_user: User,
    student_auth_headers: dict[str, str],
    other_student_auth_headers: dict[str, str],
) -> None:
    """BOLA check: Student B must NOT be able to list Student A's documents."""
    # Create application for Student A
    create_resp = await client.post(
        "/api/v1/application",
        json={
            "name": student_user.name,
            "email": student_user.email,
            "academic_record": {
                "cgpa": 8.5,
                "tenth_percent": 90.0,
                "twelfth_percent": 88.0,
                "backlogs": 0,
            },
            "financial_profile": {
                "household_income": 500000.0,
                "existing_emi": 2000.0,
                "tuition_fee": 100000.0,
                "requested_loan": 50000.0,
            },
        },
        headers=student_auth_headers,
    )
    app_id = create_resp.json()["data"]["application_id"]

    # Student A can view documents list
    doc_a_resp = await client.get(
        f"/api/v1/documents/application/{app_id}",
        headers=student_auth_headers,
    )
    assert doc_a_resp.status_code == 200

    # Student B is rejected with 403 Forbidden
    doc_b_resp = await client.get(
        f"/api/v1/documents/application/{app_id}",
        headers=other_student_auth_headers,
    )
    assert doc_b_resp.status_code == 403


@pytest.mark.anyio
async def test_rbac_student_blocked_from_reviewer_actions(
    client: AsyncClient,
    student_user: User,
    student_auth_headers: dict[str, str],
) -> None:
    """RBAC check: Students are forbidden from admin/reviewer endpoints."""
    # Review queue
    resp = await client.get("/api/v1/admin/review-queue", headers=student_auth_headers)
    assert resp.status_code == 403

    # Analytics
    resp = await client.get("/api/v1/admin/analytics", headers=student_auth_headers)
    assert resp.status_code == 403

    # Decision recording
    resp = await client.post(
        f"/api/v1/admin/application/{uuid.uuid4()}/decision",
        json={"decision": "approve", "rationale": "Unauthorized attempt"},
        headers=student_auth_headers,
    )
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_reviewer_can_inspect_application_and_post_decision(
    client: AsyncClient,
    student_user: User,
    student_auth_headers: dict[str, str],
    reviewer_user: User,
    reviewer_auth_headers: dict[str, str],
) -> None:
    """Authorized reviewer can access student dossier and record determination."""
    # Create application for student
    create_resp = await client.post(
        "/api/v1/application",
        json={
            "name": student_user.name,
            "email": student_user.email,
            "academic_record": {
                "cgpa": 8.0,
                "tenth_percent": 85.0,
                "twelfth_percent": 82.0,
                "backlogs": 0,
            },
            "financial_profile": {
                "household_income": 300000.0,
                "existing_emi": 0.0,
                "tuition_fee": 150000.0,
                "requested_loan": 100000.0,
            },
        },
        headers=student_auth_headers,
    )
    app_id = create_resp.json()["data"]["application_id"]

    # Reviewer inspects application dossier
    review_resp = await client.get(
        f"/api/v1/admin/application/{app_id}/review-context",
        headers=reviewer_auth_headers,
    )
    assert review_resp.status_code == 200
    assert review_resp.json()["data"]["application_id"] == app_id

    # Reviewer records determination
    decision_resp = await client.post(
        f"/api/v1/admin/application/{app_id}/decision",
        json={
            "decision": "approve",
            "rationale": "Applicant fulfills low-income criteria with high academic standing.",
            "reviewer_id": "forged_malicious_id",  # Attempt to forge identity
        },
        headers=reviewer_auth_headers,
    )
    assert decision_resp.status_code == 200
    decision_body = decision_resp.json()["data"]
    assert decision_body["decision"] == "approve"
    assert decision_body["status"] == "ready_for_report"

    # Verify audit log recorded the actual authenticated principal (ignoring forged ID)
    async with AsyncSessionFactory() as session:
        stmt = (
            select(AuditLogEntry)
            .where(AuditLogEntry.id == uuid.UUID(decision_body["audit_log_id"]))
        )
        res = await session.execute(stmt)
        audit_entry = res.scalar_one_or_none()
        assert audit_entry is not None
        assert audit_entry.detail["reviewer_id"] == str(reviewer_user.id)
        assert audit_entry.detail["reviewer_id"] != "forged_malicious_id"
