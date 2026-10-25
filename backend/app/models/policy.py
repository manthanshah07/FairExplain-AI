"""
FairExplain AI — Scholarship Policy ORM Models
================================================
Maps to `scholarship_policies` and `eligibility_criteria` tables
per DATA_MODEL.md §4 and Phase 1B domain contracts.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ScholarshipPolicyModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Institution-configured scholarship program policy.
    Contains versioned eligibility criteria and charter authorizations.
    """

    __tablename__ = "scholarship_policies"

    program_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    policy_version: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    incompatible_programs: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    charter_authorizations: Mapped[dict[str, str]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("program_id", "policy_version", name="uq_policy_program_version"),
    )

    # Relationships
    criteria: Mapped[list["EligibilityCriterionModel"]] = relationship(
        "EligibilityCriterionModel",
        back_populates="policy",
        cascade="all, delete-orphan",
        order_by="EligibilityCriterionModel.criterion_id",
    )

    def __repr__(self) -> str:
        return (
            f"<ScholarshipPolicyModel id={self.id} "
            f"program_id={self.program_id!r} version={self.policy_version!r}>"
        )


class EligibilityCriterionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Explicit, institution-configured binary eligibility rule.
    Child entity of ScholarshipPolicyModel.
    """

    __tablename__ = "eligibility_criteria"

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scholarship_policies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    criterion_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    attribute: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[str] = mapped_column(String(50), nullable=False)
    target_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    required_evidence: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    charter_authorization: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationship
    policy: Mapped["ScholarshipPolicyModel"] = relationship(
        "ScholarshipPolicyModel", back_populates="criteria"
    )

    def __repr__(self) -> str:
        return (
            f"<EligibilityCriterionModel id={self.id} "
            f"criterion_id={self.criterion_id!r} attribute={self.attribute!r} "
            f"operator={self.operator!r}>"
        )
