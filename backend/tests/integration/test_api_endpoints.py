"""
FairExplain AI — Integration Tests for Business API Endpoints
===============================================================
Tests end-to-end HTTP requests against `/api/v1/application`,
`/api/v1/scholarship/evaluate`, and `/api/v1/loan/assess`.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_full_application_and_evaluation_flow(client: AsyncClient) -> None:
    """Test full journey: create application -> evaluate scholarship -> assess loan."""
    # 1. Create application
    app_payload = {
        "name": "Priya Sharma",
        "email": f"priya_{uuid.uuid4().hex[:8]}@example.com",
        "academic_record": {
            "cgpa": 8.85,
            "tenth_percent": 91.5,
            "twelfth_percent": 88.0,
            "backlogs": 0,
        },
        "financial_profile": {
            "household_income": 600000.00,
            "existing_emi": 5000.00,
            "tuition_fee": 150000.00,
            "requested_loan": 100000.00,
        },
    }

    create_resp = await client.post("/api/v1/application", json=app_payload)
    assert create_resp.status_code == 201
    app_body = create_resp.json()
    assert app_body["success"] is True
    app_id = app_body["data"]["application_id"]
    assert app_id is not None

    # 2. Get application
    get_resp = await client.get(f"/api/v1/application/{app_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["application_id"] == app_id

    # 3. Evaluate scholarship
    scholarship_payload = {
        "application_id": app_id,
        "program_id": "MERIT_NEED_2026",
    }
    scholarship_resp = await client.post(
        "/api/v1/scholarship/evaluate", json=scholarship_payload
    )
    assert scholarship_resp.status_code == 200
    scholarship_body = scholarship_resp.json()
    assert scholarship_body["success"] is True
    eval_data = scholarship_body["data"]
    assert eval_data["application_id"] == app_id
    assert len(eval_data["criteria_evaluations"]) >= 1
    assert eval_data["tuition_accounting"] is not None

    # 4. Assess loan affordability
    loan_payload = {
        "application_id": app_id,
        "tenure_months": 60,
    }
    loan_resp = await client.post("/api/v1/loan/assess", json=loan_payload)
    assert loan_resp.status_code == 200
    loan_body = loan_resp.json()
    assert loan_body["success"] is True
    loan_data = loan_body["data"]
    assert loan_data["application_id"] == app_id
    assert loan_data["outcome"] in ["eligible", "needs_review", "not_recommended"]
    assert float(loan_data["monthly_income"]) == 50000.00
    assert float(loan_data["available_monthly_capacity"]) == 15000.00


@pytest.mark.anyio
async def test_application_validation_error_envelope(client: AsyncClient) -> None:
    """Verify validation errors adhere to standard error response envelope."""
    # Invalid CGPA > 10.0
    bad_payload = {
        "name": "Invalid CGPA Applicant",
        "email": "invalid@example.com",
        "academic_record": {
            "cgpa": 12.5,
            "tenth_percent": 90.0,
            "twelfth_percent": 85.0,
            "backlogs": 0,
        },
        "financial_profile": {
            "household_income": 400000.00,
            "existing_emi": 0.00,
            "tuition_fee": 100000.00,
            "requested_loan": 50000.00,
        },
    }

    resp = await client.post("/api/v1/application", json=bad_payload)
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert "Request validation failed" in body["message"]
    assert len(body["errors"]) >= 1


@pytest.mark.anyio
async def test_non_existent_application_404(client: AsyncClient) -> None:
    """Verify 404 for missing application ID."""
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/application/{fake_id}")
    assert resp.status_code == 404
