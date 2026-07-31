"""
FairExplain AI — Application Model
====================================
Maps to the `applications` table per DATA_MODEL.md §3.2.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ApplicationStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    needs_review = "needs_review"
    ready_for_report = "ready_for_report"
    closed = "closed"


class Application(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A single student's end-to-end scholarship + loan application.
    One user can have multiple applications (e.g., different academic years).
    """

    __tablename__ = "applications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        String(50),
        nullable=False,
        default=ApplicationStatus.draft,
        index=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    user: Mapped["User"] = relationship("User", back_populates="applications")

    academic_record: Mapped["AcademicRecord"] = relationship(
        "AcademicRecord",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan",
    )
    financial_profile: Mapped["FinancialProfile"] = relationship(
        "FinancialProfile",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["UploadedDocument"]] = relationship(
        "UploadedDocument",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    scholarship_assessment: Mapped["ScholarshipAssessment"] = relationship(
        "ScholarshipAssessment",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan",
    )
    loan_assessment: Mapped["LoanAssessment"] = relationship(
        "LoanAssessment",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list["AuditLogEntry"]] = relationship(
        "AuditLogEntry",
        back_populates="application",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Application id={self.id} user_id={self.user_id} status={self.status}>"
