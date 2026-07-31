"""
FairExplain AI — Health Check Router
======================================
Provides a `/health` endpoint for:
- Load balancer / Railway health checks
- Monitoring / uptime services
- Integration test pre-flight validation

Response follows the standard envelope from `app/schemas/common.py`.
"""

from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.db.database import check_database_connection
from app.schemas.common import BaseResponse

router = APIRouter(tags=["Health"])


class HealthData(BaseResponse[dict]):
    """Typed health payload for documentation generation."""


@router.get(
    "/health",
    summary="Health check",
    description=(
        "Returns the application status, version, and database connectivity. "
        "Used by Railway and monitoring services."
    ),
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def health_check() -> JSONResponse:
    """
    Full health check: verifies the application is running and the database
    is reachable.  Returns HTTP 200 if healthy, HTTP 503 if degraded.
    """
    settings = get_settings()
    db_ok = await check_database_connection()

    health_payload: dict = {
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
    }

    if db_ok:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=BaseResponse[dict](
                success=True,
                data=health_payload,
                message="Service is healthy.",
            ).model_dump(),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=BaseResponse[dict](
                success=False,
                data=health_payload,
                message="Service is degraded — database unreachable.",
            ).model_dump(),
        )


@router.get(
    "/ping",
    summary="Liveness probe",
    description="Minimal liveness check — does not probe the database.",
    status_code=status.HTTP_200_OK,
)
async def ping() -> dict[str, str]:
    """Fast liveness probe — no database call."""
    return {"status": "ok"}
