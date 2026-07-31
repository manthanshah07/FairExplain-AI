"""
FairExplain AI — Academic Record Model
========================================
Maps to the `academic_records` table per DATA_MODEL.md §3.3.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from app.db.base import Base, UUIDPrimaryKeyMixin


class AcademicRecord(UUIDPrimaryKeyMixin, Base):
    """Academic inputs for one Application (1:1 relationship)."""

    __tablename__ = "academic_records"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Academic scores
    cgpa: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)           # 0.00 – 10.00
    tenth_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 0.00 – 100.00
    twelfth_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    backlogs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)       # active/unresolved

    # Relationship
    application: Mapped["Application"] = relationship(
        "Application", back_populates="academic_record"
    )

    def __repr__(self) -> str:
        return (
            f"<AcademicRecord application_id={self.application_id} "
            f"cgpa={self.cgpa} backlogs={self.backlogs}>"
        )
