"""
FairExplain AI — Dependency Injection Providers
=================================================
Centralises all FastAPI `Depends()` providers.

Routers should import only from this module — never from `app.db.database`
or `app.config.settings` directly — so that swapping implementations
(e.g., in tests) requires changing only this file.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.db.database import get_db


# ---------------------------------------------------------------------------
# Database session
# ---------------------------------------------------------------------------


async def get_database(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AsyncSession, None]:
    """
    Thin alias for `get_db` that routes through this module.

    Usage
    -----
        @router.get("/")
        async def handler(db: AsyncSession = Depends(get_database)):
            ...
    """
    yield db


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


def get_app_settings() -> Settings:
    """
    Provide the application settings singleton.

    Usage
    -----
        @router.get("/")
        async def handler(settings: Settings = Depends(get_app_settings)):
            ...
    """
    return get_settings()
