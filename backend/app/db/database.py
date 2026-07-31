"""
FairExplain AI — Database Engine & Session Factory
====================================================
All database connectivity is centralised here.

The async engine is created once at import time.  A scoped AsyncSession is
yielded by `get_db()` and consumed by FastAPI's dependency injection system
so that every request gets its own isolated session that is automatically
committed (on success) or rolled back (on error) and closed.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config.settings import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_settings = get_settings()

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# NullPool is used so that every connection is closed when the session ends.
# This is the recommended approach for serverless environments (Neon).
engine = create_async_engine(
    _settings.database_url,
    echo=_settings.is_development,   # log SQL only in dev
    pool_pre_ping=True,               # verify connections before use
    poolclass=NullPool,               # required for serverless / Neon
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an `AsyncSession` per request.

    Usage
    -----
        @router.get("/")
        async def handler(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """
    Probe the database to verify connectivity.
    Used by the health endpoint.
    Returns True if the database is reachable, False otherwise.
    """
    try:
        from sqlalchemy import text

        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("database_unreachable", error=str(exc))
        return False
