"""
FairExplain AI — Audit Log Entry Model
========================================
Maps to the `audit_log_entries` table per DATA_MODEL.md §3.9.

Immutable once written — represents every scoring and explanation event.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AuditEventType(str, enum.Enum):
    score_computed = "score_computed"
    explanation_generated = "explanation_generated"
    fairness_flag = "fairness_flag"
    human_review_action = "human_review_action"
    application_status_changed = "application_status_changed"


class AuditLogEntry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Immutable record of a scoring or explanation event.

    Rules:
    - Never update or delete an audit log entry after creation.
    - `detail` stores event-specific payload as JSON.
    """

    __tablename__ = "audit_log_entries"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[AuditEventType] = mapped_column(
        String(60), nullable=False, index=True
    )
    detail: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict,
        comment="Event-specific payload (e.g., score, version, reviewer_id)"
    )

    # Relationship
    application: Mapped["Application"] = relationship(
        "Application", back_populates="audit_logs"
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLogEntry id={self.id} "
            f"event={self.event_type} app={self.application_id}>"
        )
