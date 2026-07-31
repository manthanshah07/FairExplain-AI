"""
FairExplain AI — Uploaded Document Model
==========================================
Maps to the `uploaded_documents` table per DATA_MODEL.md §3.5.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DocumentType(str, enum.Enum):
    marksheet = "marksheet"
    income_proof = "income_proof"
    id_proof = "id_proof"


class UploadedDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    A document uploaded in support of an Application.

    Stores a reference to the file in external storage plus the OCR
    extraction result (populated in Phase 4).  The `mismatch_flag` is
    set when the OCR value conflicts with the self-reported form value.
    """

    __tablename__ = "uploaded_documents"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    doc_type: Mapped[DocumentType] = mapped_column(
        String(50), nullable=False
    )
    file_url: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Storage reference (e.g., S3 / Supabase URL)"
    )
    # Populated by OCR pipeline (Phase 4) — null until processed
    ocr_extracted_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=None
    )
    mismatch_flag: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="True if OCR value conflicts with self-reported value"
    )

    # Relationship
    application: Mapped["Application"] = relationship(
        "Application", back_populates="documents"
    )

    def __repr__(self) -> str:
        return (
            f"<UploadedDocument id={self.id} "
            f"doc_type={self.doc_type} mismatch={self.mismatch_flag}>"
        )
