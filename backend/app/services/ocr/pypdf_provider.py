"""
FairExplain AI — PyPDF OCR & Document Extraction Provider
===========================================================
Extracts textual content from PDF files and images using pypdf.
"""

from __future__ import annotations

import io
from pypdf import PdfReader

from app.services.ocr.base import BaseOCRProvider, OCRExtractionResult


class PyPDFOCRProvider(BaseOCRProvider):
    """Text extraction adapter utilizing pypdf."""

    name: str = "pypdf"

    async def extract_text(
        self, file_bytes: bytes, mime_type: str
    ) -> OCRExtractionResult:
        """Extract text from PDF stream or plain text fallback."""
        if not file_bytes:
            return OCRExtractionResult(
                raw_text="",
                confidence=0.0,
                extracted_fields={},
                provider_name=self.name,
            )

        extracted_text_chunks: list[str] = []
        confidence = 0.95

        try:
            if "pdf" in mime_type.lower():
                reader = PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text_chunks.append(text)
            else:
                # Text or decode fallback
                text = file_bytes.decode("utf-8", errors="ignore")
                extracted_text_chunks.append(text)
                confidence = 0.85

            raw_text = "\n".join(extracted_text_chunks).strip()
            if not raw_text:
                confidence = 0.50

            return OCRExtractionResult(
                raw_text=raw_text,
                confidence=confidence,
                extracted_fields={},
                provider_name=self.name,
            )
        except Exception:
            return OCRExtractionResult(
                raw_text="",
                confidence=0.0,
                extracted_fields={},
                provider_name=self.name,
            )
