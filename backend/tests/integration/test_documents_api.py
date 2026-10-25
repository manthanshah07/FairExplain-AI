"""
FairExplain AI — Integration Tests for Document Upload and Verification API
=============================================================================
Tests `/api/v1/documents/upload`, `list`, and `verify`.
"""

from __future__ import annotations

import io
import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_document_upload_and_verification_pipeline(
    client: AsyncClient,
    student_auth_headers: dict[str, str],
) -> None:
    """Test full document upload, extraction, and automated cross-verification."""
    # 1. Create an application first
    app_payload = {
        "name": "Kavita Nair",
        "email": f"kavita_{uuid.uuid4().hex[:8]}@example.com",
        "academic_record": {
            "cgpa": 8.75,
            "tenth_percent": 90.0,
            "twelfth_percent": 88.0,
            "backlogs": 0,
        },
        "financial_profile": {
            "household_income": 450000.00,
            "existing_emi": 2000.00,
            "tuition_fee": 120000.00,
            "requested_loan": 80000.00,
        },
    }
    create_resp = await client.post(
        "/api/v1/application",
        json=app_payload,
        headers=student_auth_headers,
    )
    assert create_resp.status_code == 201
    app_id = create_resp.json()["data"]["application_id"]

    # 2. Upload marksheet matching reported CGPA (8.75)
    marksheet_content = b"GRADE REPORT\nCandidate: Kavita Nair\nCGPA: 8.75\nBacklogs: 0\n"
    files = {
        "file": ("marksheet.txt", marksheet_content, "text/plain"),
    }
    data = {
        "application_id": app_id,
        "doc_type": "marksheet",
    }
    upload_resp = await client.post(
        "/api/v1/documents/upload",
        data=data,
        files=files,
        headers=student_auth_headers,
    )
    assert upload_resp.status_code == 201
    upload_body = upload_resp.json()
    assert upload_body["success"] is True
    assert upload_body["data"]["extracted_fields"]["cgpa"] == 8.75

    # 3. List documents for application
    list_resp = await client.get(
        f"/api/v1/documents/application/{app_id}",
        headers=student_auth_headers,
    )
    assert list_resp.status_code == 200
    docs = list_resp.json()["data"]
    assert len(docs) == 1
    assert docs[0]["doc_type"] == "marksheet"

    # 4. Trigger verification - should succeed with no discrepancies
    verify_resp = await client.post(
        f"/api/v1/documents/verify/{app_id}",
        headers=student_auth_headers,
    )
    assert verify_resp.status_code == 200
    verify_body = verify_resp.json()["data"]
    assert verify_body["verified"] is True
    assert len(verify_body["discrepancies"]) == 0


@pytest.mark.anyio
async def test_document_verification_mismatch_triggers_review(
    client: AsyncClient,
    student_auth_headers: dict[str, str],
) -> None:
    """Discrepant document upload triggers mismatch flag and needs_review status."""
    # 1. Create application with reported income 500,000
    app_payload = {
        "name": "Mismatch Applicant",
        "email": f"mismatch_{uuid.uuid4().hex[:8]}@example.com",
        "academic_record": {
            "cgpa": 8.0,
            "tenth_percent": 85.0,
            "twelfth_percent": 85.0,
            "backlogs": 0,
        },
        "financial_profile": {
            "household_income": 500000.00,
            "existing_emi": 0.00,
            "tuition_fee": 100000.00,
            "requested_loan": 50000.00,
        },
    }
    create_resp = await client.post(
        "/api/v1/application",
        json=app_payload,
        headers=student_auth_headers,
    )
    app_id = create_resp.json()["data"]["application_id"]

    # 2. Upload income proof showing 900,000 (>5% diff)
    income_content = b"INCOME CERTIFICATE\nTotal Family Income: Rs. 9,00,000\n"
    files = {
        "file": ("income.txt", income_content, "text/plain"),
    }
    data = {
        "application_id": app_id,
        "doc_type": "income_proof",
    }
    await client.post(
        "/api/v1/documents/upload",
        data=data,
        files=files,
        headers=student_auth_headers,
    )

    # 3. Trigger verification - should flag discrepancy
    verify_resp = await client.post(
        f"/api/v1/documents/verify/{app_id}",
        headers=student_auth_headers,
    )
    assert verify_resp.status_code == 200
    verify_body = verify_resp.json()["data"]
    assert verify_body["verified"] is False
    assert len(verify_body["discrepancies"]) == 1
    assert verify_body["discrepancies"][0]["field"] == "household_income"

    # 4. Verify application status transitioned to needs_review
    get_resp = await client.get(
        f"/api/v1/application/{app_id}",
        headers=student_auth_headers,
    )
    assert get_resp.json()["data"]["status"] == "needs_review"


@pytest.mark.anyio
async def test_document_upload_size_limit(
    client: AsyncClient,
    student_auth_headers: dict[str, str],
) -> None:
    """Files exceeding 10MB are rejected with 413."""
    # Create application first so student is authorized
    create_resp = await client.post(
        "/api/v1/application",
        json={
            "name": "Size Limit Applicant",
            "email": f"sizelimit_{uuid.uuid4().hex[:8]}@example.com",
            "academic_record": {
                "cgpa": 8.0,
                "tenth_percent": 85.0,
                "twelfth_percent": 85.0,
                "backlogs": 0,
            },
            "financial_profile": {
                "household_income": 500000.00,
                "existing_emi": 0.00,
                "tuition_fee": 100000.00,
                "requested_loan": 50000.00,
            },
        },
        headers=student_auth_headers,
    )
    app_id = create_resp.json()["data"]["application_id"]

    oversized_content = b"0" * (11 * 1024 * 1024)  # 11 MB
    files = {
        "file": ("oversized.pdf", oversized_content, "application/pdf"),
    }
    data = {
        "application_id": app_id,
        "doc_type": "marksheet",
    }
    resp = await client.post(
        "/api/v1/documents/upload",
        data=data,
        files=files,
        headers=student_auth_headers,
    )
    assert resp.status_code == 413
