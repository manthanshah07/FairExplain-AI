"""
FairExplain AI — Rate Limiting Integration Tests
=================================================
Verifies that SlowAPI rate limiting triggers HTTP 429 when limits are reached,
returns the platform-standard error envelope, and that test-only isolation
fixtures do not leak into runtime behavior.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.middleware.rate_limit import limiter


@pytest.mark.anyio
async def test_rate_limiter_triggers_429_on_login() -> None:
    """Verifies that the /api/v1/auth/login endpoint (limited to 5/minute) enforces rate limiting
    and returns an HTTP 429 response matching the platform error envelope format.
    """
    # Explicitly enable limiter for this specific verification test
    limiter.enabled = True
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            status_codes = []
            last_resp = None

            # Execute 7 rapid login attempts (limit is 5/minute)
            for _ in range(7):
                resp = await client.post(
                    "/api/v1/auth/login",
                    json={"email": "ratelimit_test@nitk.edu.in", "password": "WrongPassword123!"},
                )
                status_codes.append(resp.status_code)
                last_resp = resp

            # Verify rate limit triggered
            assert 429 in status_codes, f"Expected 429 in status codes, got: {status_codes}"
            assert last_resp.status_code == 429

            body = last_resp.json()
            assert body["success"] is False
            assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
            assert "Too many requests" in body["error"]["message"]
    finally:
        # Re-disable to maintain isolation for subsequent integration tests
        limiter.enabled = False


def test_rate_limiter_runtime_configuration() -> None:
    """Verify that limiter has headers enabled and default limits configured for runtime."""
    assert limiter._headers_enabled is True
    limits = [str(l.limit) for lg in limiter._default_limits for l in lg]
    assert any("120 per 1 minute" in lim for lim in limits)
