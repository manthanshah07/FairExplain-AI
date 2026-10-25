"""
FairExplain AI — Award & Institutional Cap ORM Models
======================================================
Maps to `award_specifications` and `institutional_caps` tables
per DATA_MODEL.md §4 and Phase 1B domain contracts.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AwardSpecificationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    An award granted or available to an application.
    Enforces priority, caps, and incompatible programs per Phase 1B contracts.
    """

    __tablename__ = "award_specifications"

    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    award_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    program_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    award_type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    max_award_cap: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    incompatible_programs: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # Relationship
    application: Mapped["Application | None"] = relationship(
        "Application", back_populates="awards"
    )

    def __repr__(self) -> str:
        return (
            f"<AwardSpecificationModel id={self.id} "
            f"award_id={self.award_id!r} status={self.status!r} priority={self.priority}>"
        )


class InstitutionalCapModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    Institutional tuition-waiver policy cap configuration.
    """

    __tablename__ = "institutional_caps"

    institution_code: Mapped[str] = mapped_column(
        String(100), nullable=False, default="DEFAULT", index=True
    )
    max_waiver_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    max_waiver_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<InstitutionalCapModel id={self.id} "
            f"institution={self.institution_code!r} "
            f"max_amount={self.max_waiver_amount} max_pct={self.max_waiver_percentage}>"
        )
