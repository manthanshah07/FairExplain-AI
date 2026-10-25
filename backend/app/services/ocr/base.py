"""
FairExplain AI — OCR Provider Interfaces
==========================================
Protocol and DTO definitions for pluggable document text extraction engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class OCRExtractionResult:
    """Standardized output from OCR extraction engine."""

    raw_text: str
    confidence: float
    extracted_fields: dict[str, Any] = field(default_factory=dict)
    provider_name: str = "default"


class BaseOCRProvider(Protocol):
    """Protocol implemented by all OCR extraction adapters."""

    async def extract_text(
        self, file_bytes: bytes, mime_type: str
    ) -> OCRExtractionResult:
        """Extract raw text and key fields from binary file payload."""
        ...
