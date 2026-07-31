"""
FairExplain AI — Loan Assessment Model
========================================
Maps to the `loan_assessments` table per DATA_MODEL.md §3.7.

Populated by the Rule Engine (Phase 3).
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.scholarship_assessment import AssessmentOutcome


class LoanAssessment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Output of the Loan Rule Engine for an Application."""

    __tablename__ = "loan_assessments"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    reduced_loan_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False,
        comment="requested_loan − scholarship_amount in INR"
    )
    outcome: Mapped[AssessmentOutcome] = mapped_column(
        String(50), nullable=False
    )
    confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, comment="Confidence score 0–100"
    )
    rule_engine_version: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    # Relationship
    application: Mapped["Application"] = relationship(
        "Application", back_populates="loan_assessment"
    )
    explanation_report: Mapped["ExplanationReport | None"] = relationship(
        "ExplanationReport",
        primaryjoin="and_(ExplanationReport.assessment_id == LoanAssessment.id, "
                    "ExplanationReport.assessment_type == 'loan')",
        foreign_keys="ExplanationReport.assessment_id",
        uselist=False,
        viewonly=True,
    )

    def __repr__(self) -> str:
        return (
            f"<LoanAssessment application_id={self.application_id} "
            f"outcome={self.outcome} reduced={self.reduced_loan_amount}>"
        )
