"""
FairExplain AI — CORS Middleware Security Tests
================================================
SEC-02: Verifies that only explicitly allowlisted frontend origins are accepted.
Arbitrary Vercel subdomains (*.vercel.app), attacker domains, and malformed
origins must NEVER receive Access-Control-Allow-Origin or Access-Control-Allow-Credentials headers.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_cors_approved_frontend_origin(client: AsyncClient) -> None:
    """Approved frontend origin receives CORS headers allowing credentialed requests."""
    approved_origin = "http://localhost:5173"

    # Preflight OPTIONS request
    preflight = await client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": approved_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers.get("access-control-allow-origin") == approved_origin
    assert preflight.headers.get("access-control-allow-credentials") == "true"
    assert "POST" in preflight.headers.get("access-control-allow-methods", "")

    # Actual request with Origin header
    resp = await client.get("/health", headers={"Origin": approved_origin})
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == approved_origin


@pytest.mark.anyio
async def test_cors_rejects_unrelated_origin(client: AsyncClient) -> None:
    """Unrelated third-party origin does not receive CORS allow headers."""
    attacker_origin = "https://evil-attacker-site.com"

    # Preflight
    preflight = await client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": attacker_origin,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in preflight.headers

    # Actual request
    resp = await client.get("/health", headers={"Origin": attacker_origin})
    assert "access-control-allow-origin" not in resp.headers


@pytest.mark.anyio
async def test_cors_rejects_arbitrary_vercel_subdomains(client: AsyncClient) -> None:
    """SEC-02: Wildcard *.vercel.app matching is strictly forbidden. Subdomains must be rejected."""
    unauthorized_vercel_origins = [
        "https://malicious-phishing.vercel.app",
        "https://random-student-app.vercel.app",
        "https://fairexplain-fake.vercel.app",
        "https://attacker-corp.vercel.app",
    ]

    for origin in unauthorized_vercel_origins:
        # Preflight check
        preflight = await client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert (
            "access-control-allow-origin" not in preflight.headers
        ), f"Origin {origin} was improperly permitted via CORS preflight!"

        # Actual request check
        resp = await client.get("/health", headers={"Origin": origin})
        assert (
            "access-control-allow-origin" not in resp.headers
        ), f"Origin {origin} was improperly permitted via CORS GET!"


@pytest.mark.anyio
async def test_cors_rejects_malformed_and_prefix_origins(client: AsyncClient) -> None:
    """Prefix matching, substring matching, or malformed origin strings must be rejected."""
    malformed_origins = [
        "http://localhost:5173.attacker.com",
        "https://evil-localhost:5173",
        "http://localhost:5173:8080",
        "null",
        "http://localhost:51730",
    ]

    for origin in malformed_origins:
        preflight = await client.options(
            "/api/v1/auth/login",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert "access-control-allow-origin" not in preflight.headers
