"""
FairExplain AI — OCR Services Package
=======================================
"""

from app.services.ocr.base import BaseOCRProvider, OCRExtractionResult
from app.services.ocr.pypdf_provider import PyPDFOCRProvider
from app.services.ocr.extractor import DocumentKeyExtractor

__all__ = [
    "BaseOCRProvider",
    "OCRExtractionResult",
    "PyPDFOCRProvider",
    "DocumentKeyExtractor",
]
