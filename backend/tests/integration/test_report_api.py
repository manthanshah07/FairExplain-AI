"""
FairExplain AI — Integration Tests for Report Download API
============================================================
Tests `GET /api/v1/report/{application_id}/download`.
"""

from __future__ import annotations

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_download_report_pdf(client: AsyncClient) -> None:
    """Test full journey: create application -> evaluate -> download tamper-evident PDF."""
    app_payload = {
        "name": "PDF Report Applicant",
        "email": f"pdf_{uuid.uuid4().hex[:8]}@example.com",
        "academic_record": {
            "cgpa": 8.95,
            "tenth_percent": 93.0,
            "twelfth_percent": 91.0,
            "backlogs": 0,
        },
        "financial_profile": {
            "household_income": 480000.00,
            "existing_emi": 2500.00,
            "tuition_fee": 130000.00,
            "requested_loan": 65000.00,
        },
    }
    create_resp = await client.post("/api/v1/application", json=app_payload)
    app_id = create_resp.json()["data"]["application_id"]

    await client.post(
        "/api/v1/scholarship/evaluate",
        json={"application_id": app_id, "program_id": "MERIT_NEED_2026"},
    )
    await client.post("/api/v1/explanation/generate", json={"application_id": app_id})

    # Download report
    resp = await client.get(f"/api/v1/report/{app_id}/download")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "X-Audit-Digest" in resp.headers
    assert len(resp.headers["X-Audit-Digest"]) == 64
    assert resp.content.startswith(b"%PDF-")


@pytest.mark.anyio
async def test_download_report_404_for_missing(client: AsyncClient) -> None:
    """Download report for non-existent application returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/report/{fake_id}/download")
    assert resp.status_code == 404
