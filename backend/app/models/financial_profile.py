"""
FairExplain AI — Financial Profile Model
==========================================
Maps to the `financial_profiles` table per DATA_MODEL.md §3.4.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin


class FinancialProfile(UUIDPrimaryKeyMixin, Base):
    """Financial inputs for one Application (1:1 relationship)."""

    __tablename__ = "financial_profiles"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # All monetary fields in INR
    household_income: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, comment="Annual household income in INR"
    )
    existing_emi: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"),
        comment="Monthly EMI obligations in INR"
    )
    tuition_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="Annual tuition fee in INR"
    )
    requested_loan: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, comment="Total loan amount requested in INR"
    )

    # Relationship
    application: Mapped["Application"] = relationship(
        "Application", back_populates="financial_profile"
    )

    def __repr__(self) -> str:
        return (
            f"<FinancialProfile application_id={self.application_id} "
            f"household_income={self.household_income}>"
        )
