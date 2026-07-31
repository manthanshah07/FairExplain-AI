"""
FairExplain AI — Health Endpoint Tests
========================================
Tests for /health and /ping without requiring a real database.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.anyio
async def test_ping_returns_ok(client: AsyncClient) -> None:
    """The /ping liveness probe should always return 200 with status ok."""
    response = await client.get("/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_health_healthy(client: AsyncClient) -> None:
    """/health should return 200 when the database is reachable."""
    with patch(
        "app.routers.health.check_database_connection",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    assert body["data"]["database"] == "connected"


@pytest.mark.anyio
async def test_health_degraded(client: AsyncClient) -> None:
    """/health should return 503 when the database is unreachable."""
    with patch(
        "app.routers.health.check_database_connection",
        new_callable=AsyncMock,
        return_value=False,
    ):
        response = await client.get("/health")
    assert response.status_code == 503
    body = response.json()
    assert body["success"] is False
    assert body["data"]["status"] == "degraded"
