"""
FairExplain AI — Evaluation & Accounting Snapshot ORM Models
==============================================================
Maps to:
- `scholarship_evaluations`
- `criterion_evaluation_snapshots`
- `tuition_account_summaries`
- `award_allocations`
per DATA_MODEL.md §4 and Phase 1B domain contracts.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ScholarshipEvaluationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Frozen snapshot of a scholarship program eligibility evaluation result.
    Links directly to an application and records the criteria evaluation breakdown.
    """

    __tablename__ = "scholarship_evaluations"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    program_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    policy_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
        comment="ELIGIBLE | INELIGIBLE | PENDING_EVIDENCE"
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    satisfied_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pending_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    frozen_applicant_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )

    # Relationships
    application: Mapped["Application"] = relationship(
        "Application", back_populates="evaluations"
    )
    criteria_evaluations: Mapped[list["CriterionEvaluationSnapshotModel"]] = relationship(
        "CriterionEvaluationSnapshotModel",
        back_populates="evaluation",
        cascade="all, delete-orphan",
        order_by="CriterionEvaluationSnapshotModel.criterion_id",
    )

    def __repr__(self) -> str:
        return (
            f"<ScholarshipEvaluationModel id={self.id} "
            f"program_id={self.program_id!r} status={self.status!r}>"
        )


class CriterionEvaluationSnapshotModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Evaluation output for an individual criterion snapshot.
    Child entity of ScholarshipEvaluationModel.
    """

    __tablename__ = "criterion_evaluation_snapshots"

    evaluation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scholarship_evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criterion_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    attribute: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[str] = mapped_column(String(50), nullable=False)
    target_value: Mapped[Any] = mapped_column(JSON, nullable=True)
    actual_value: Mapped[Any] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="SATISFIED | FAILED | PENDING_EVIDENCE"
    )
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    evidence_required: Mapped[str | None] = mapped_column(String(100), nullable=True)
    evidence_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="NOT_REQUIRED"
    )
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Relationship
    evaluation: Mapped["ScholarshipEvaluationModel"] = relationship(
        "ScholarshipEvaluationModel", back_populates="criteria_evaluations"
    )

    def __repr__(self) -> str:
        return (
            f"<CriterionEvaluationSnapshotModel id={self.id} "
            f"criterion_id={self.criterion_id!r} status={self.status!r}>"
        )


class TuitionAccountSummaryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Comprehensive, deterministic tuition balance and award accounting report.
    One-to-one per application.
    """

    __tablename__ = "tuition_account_summaries"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    gross_eligible_tuition: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    institutional_cap_applied: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    total_effective_reduction: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    remaining_payable_tuition: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    remaining_waiver_allowance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    total_unapplied_surplus: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    calculator_version: Mapped[str] = mapped_column(
        String(50), nullable=False, default="1.0.0-phase1b"
    )

    # Relationships
    application: Mapped["Application"] = relationship(
        "Application", back_populates="tuition_account_summary"
    )
    allocations: Mapped[list["AwardAllocationModel"]] = relationship(
        "AwardAllocationModel",
        back_populates="account_summary",
        cascade="all, delete-orphan",
        order_by="AwardAllocationModel.priority",
    )

    def __repr__(self) -> str:
        return (
            f"<TuitionAccountSummaryModel id={self.id} "
            f"gross={self.gross_eligible_tuition} net={self.remaining_payable_tuition} "
            f"surplus={self.total_unapplied_surplus}>"
        )


class AwardAllocationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Allocation and surplus breakdown for a confirmed award.
    Child entity of TuitionAccountSummaryModel.
    """

    __tablename__ = "award_allocations"

    account_summary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tuition_account_summaries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    award_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    program_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    nominal_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    capped_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    effective_reduction: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    unapplied_surplus: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    cap_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationship
    account_summary: Mapped["TuitionAccountSummaryModel"] = relationship(
        "TuitionAccountSummaryModel", back_populates="allocations"
    )

    def __repr__(self) -> str:
        return (
            f"<AwardAllocationModel id={self.id} "
            f"award_id={self.award_id!r} priority={self.priority} "
            f"reduction={self.effective_reduction} surplus={self.unapplied_surplus}>"
        )
