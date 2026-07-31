"""
FairExplain AI — SQLAlchemy Declarative Base
=============================================
All ORM models must inherit from `Base`.

A shared `TimestampMixin` provides `created_at` / `updated_at` columns
automatically.  A `UUIDMixin` provides a server-generated UUID primary key.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Project-wide SQLAlchemy declarative base.

    Every model in `app/models/` must inherit from this class so that
    Alembic's autogenerate can discover the full schema automatically.
    """


# ---------------------------------------------------------------------------
# Reusable mixins
# ---------------------------------------------------------------------------


class UUIDPrimaryKeyMixin:
    """Adds a server-generated UUID primary key column named `id`."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )


class TimestampMixin:
    """Adds `created_at` and `updated_at` timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
