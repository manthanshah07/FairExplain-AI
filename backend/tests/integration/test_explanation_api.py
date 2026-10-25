"""
FairExplain AI — Integration Tests for Explanation API
========================================================
Tests `/api/v1/explanation/generate` and `GET /api/v1/explanation/{application_id}`.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient

from app.services.llm.prompt_templates import MANDATORY_HUMAN_REVIEW_NOTICE


@pytest.mark.anyio
async def test_explanation_generation_flow(
    client: AsyncClient,
    student_auth_headers: dict[str, str],
) -> None:
    """Test full journey: create application -> evaluate scholarship -> generate grounded explanation."""
    # 1. Create application
    app_payload = {
        "name": "Devika Sen",
        "email": f"devika_{uuid.uuid4().hex[:8]}@example.com",
        "academic_record": {
            "cgpa": 8.90,
            "tenth_percent": 92.0,
            "twelfth_percent": 90.0,
            "backlogs": 0,
        },
        "financial_profile": {
            "household_income": 550000.00,
            "existing_emi": 3000.00,
            "tuition_fee": 140000.00,
            "requested_loan": 70000.00,
        },
    }
    create_resp = await client.post(
        "/api/v1/application",
        json=app_payload,
        headers=student_auth_headers,
    )
    assert create_resp.status_code == 201
    app_id = create_resp.json()["data"]["application_id"]

    # 2. Evaluate scholarship
    eval_resp = await client.post(
        "/api/v1/scholarship/evaluate",
        json={"application_id": app_id, "program_id": "MERIT_NEED_2026"},
        headers=student_auth_headers,
    )
    assert eval_resp.status_code == 200

    # 3. Generate explanation
    exp_resp = await client.post(
        "/api/v1/explanation/generate",
        json={"application_id": app_id},
        headers=student_auth_headers,
    )
    assert exp_resp.status_code == 200
    exp_body = exp_resp.json()
    assert exp_body["success"] is True
    exp_data = exp_body["data"]["explanation"]
    assert exp_data["human_review_notice"] == MANDATORY_HUMAN_REVIEW_NOTICE
    assert "headline" in exp_data["summary_headline"].lower() or len(exp_data["summary_headline"]) > 5
    assert len(exp_data["reasons"]) >= 1

    # 4. Retrieve saved explanation
    get_exp_resp = await client.get(
        f"/api/v1/explanation/{app_id}",
        headers=student_auth_headers,
    )
    assert get_exp_resp.status_code == 200
    get_exp_body = get_exp_resp.json()
    assert get_exp_body["data"]["explanation"]["human_review_notice"] == MANDATORY_HUMAN_REVIEW_NOTICE
