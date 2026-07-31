"""
FairExplain AI — Scholarship Assessment Model
===============================================
Maps to the `scholarship_assessments` table per DATA_MODEL.md §3.6.

Populated by the Rule Engine (Phase 3).  This model is created in Phase 2
so the database schema is ready when the Rule Engine is integrated.
"""

from __future__ import annotations

import enum
import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AssessmentOutcome(str, enum.Enum):
    eligible = "Eligible"
    needs_review = "Needs Review"
    not_recommended = "Not Recommended"


class ScholarshipAssessment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Output of the Scholarship Rule Engine for an Application."""

    __tablename__ = "scholarship_assessments"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    scholarship_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, comment="Scholarship percentage (0–100)"
    )
    scholarship_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, comment="scholarship_percent × tuition_fee in INR"
    )
    outcome: Mapped[AssessmentOutcome] = mapped_column(
        String(50), nullable=False
    )
    rule_engine_version: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Semver string for reproducibility"
    )

    # Relationship
    application: Mapped["Application"] = relationship(
        "Application", back_populates="scholarship_assessment"
    )
    explanation_report: Mapped["ExplanationReport | None"] = relationship(
        "ExplanationReport",
        primaryjoin="and_(ExplanationReport.assessment_id == ScholarshipAssessment.id, "
                    "ExplanationReport.assessment_type == 'scholarship')",
        foreign_keys="ExplanationReport.assessment_id",
        uselist=False,
        viewonly=True,
    )

    def __repr__(self) -> str:
        return (
            f"<ScholarshipAssessment application_id={self.application_id} "
            f"outcome={self.outcome} pct={self.scholarship_percent}>"
        )
