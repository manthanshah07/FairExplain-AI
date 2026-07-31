"""
FairExplain AI — User Model
============================
Maps to the `users` table per DATA_MODEL.md §3.1.
"""

from __future__ import annotations

import enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, enum.Enum):
    student = "student"
    university = "university"
    bank = "bank"
    scholarship_provider = "scholarship_provider"
    admin = "admin"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An account holder in the FairExplain system."""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        String(50), nullable=False, default=UserRole.student
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"
