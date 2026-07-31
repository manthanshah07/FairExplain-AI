"""
FairExplain AI — FastAPI Application Entry Point
==================================================
Assembles the full FastAPI application:
  1. Configures structured logging (must be first).
  2. Creates the FastAPI instance with metadata.
  3. Configures CORS.
  4. Registers request-logging middleware.
  5. Registers global exception handlers.
  6. Mounts the health router at root level.
  7. Mounts the versioned API router (/api/v1).
  8. Registers startup / shutdown lifecycle hooks.

Run with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.middleware.logging import RequestLoggingMiddleware
from app.api.router import api_router
from app.routers.health import router as health_router

# ---------------------------------------------------------------------------
# Bootstrap logging before anything else so startup logs are captured.
# ---------------------------------------------------------------------------
configure_logging()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Runs startup logic before `yield` and shutdown logic after.
    The database connection is probed at startup so Railway / Railway
    health checks can surface database issues immediately.
    """
    settings = get_settings()
    logger.info(
        "application_starting",
        name=settings.app_name,
        version=settings.app_version,
        env=settings.app_env,
    )

    # Probe database connectivity at startup
    from app.db.database import check_database_connection

    db_ok = await check_database_connection()
    if db_ok:
        logger.info("database_connected")
    else:
        logger.warning("database_unreachable_at_startup")

    yield  # ← application is running

    logger.info("application_shutting_down")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """
    Factory function that builds and configures the FastAPI application.

    Using a factory makes the app object importable in tests without
    triggering all side effects at module-load time.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "FairExplain AI — Explainable AI platform for scholarship eligibility "
            "and education loan assessment. The Rule Engine is the single source "
            "of truth for all scores. Humans make every final decision."
        ),
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ------------------------------------------------------------------ #
    # CORS                                                                 #
    # ------------------------------------------------------------------ #
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------ #
    # Custom middleware (order matters — added in reverse execution order) #
    # ------------------------------------------------------------------ #
    app.add_middleware(RequestLoggingMiddleware)

    # ------------------------------------------------------------------ #
    # Exception handlers                                                   #
    # ------------------------------------------------------------------ #
    register_exception_handlers(app)

    # ------------------------------------------------------------------ #
    # Routers                                                              #
    # ------------------------------------------------------------------ #
    # Health check — mounted at root so it doesn't require /api/v1 prefix
    app.include_router(health_router)

    # All feature APIs under /api/v1
    app.include_router(api_router)

    logger.info(
        "application_configured",
        cors_origins=settings.allowed_origins,
        docs_enabled=not settings.is_production,
    )

    return app


# ---------------------------------------------------------------------------
# Module-level application instance (used by uvicorn)
# ---------------------------------------------------------------------------
app: FastAPI = create_app()
