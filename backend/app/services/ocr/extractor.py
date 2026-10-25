"""
FairExplain AI — OCR Key-Field Extractor
==========================================
Deterministic key-value parser for marksheets, income certificates, and ID proofs.
Extracts numbers and text using regular expressions with confidence scoring.
"""

from __future__ import annotations

import re
from typing import Any

from app.models.uploaded_document import DocumentType


class DocumentKeyExtractor:
    """Parses raw OCR text into structured key-value profiles with confidence metrics."""

    @staticmethod
    def parse_marksheet(text: str) -> dict[str, Any]:
        """Extract CGPA, percentage, and backlogs from marksheet text."""
        fields: dict[str, Any] = {}
        confidence = 0.50

        # CGPA pattern (e.g. "CGPA: 8.85", "Cumulative Grade Point Average (CGPA): 8.92 / 10", "GPA: 7.9")
        cgpa_match = re.search(
            r"(?:cgpa|\bcgpa\b|grade point average|\bgpa\b)[^0-9\n\r]*([0-9]+(?:\.[0-9]+)?)\s*(?:/\s*10)?",
            text,
            re.IGNORECASE,
        )
        if cgpa_match:
            try:
                val = float(cgpa_match.group(1))
                if 0.0 <= val <= 10.0:
                    fields["cgpa"] = val
                    confidence += 0.30
            except ValueError:
                pass

        # Tenth percentage pattern
        tenth_match = re.search(
            r"(?:10th|tenth|ssc|secondary)\s*(?:percentage|marks|aggregate)?\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%",
            text,
            re.IGNORECASE,
        )
        if tenth_match:
            try:
                val = float(tenth_match.group(1))
                if 0.0 <= val <= 100.0:
                    fields["tenth_percent"] = val
                    confidence += 0.10
            except ValueError:
                pass

        # Backlogs pattern (e.g. "Active Backlogs: 0", "Backlogs: NIL")
        backlog_match = re.search(
            r"(?:backlogs?|arrears?)\s*[:=-]?\s*([0-9]+|nil|none|zero)",
            text,
            re.IGNORECASE,
        )
        if backlog_match:
            raw = backlog_match.group(1).lower()
            if raw in ("nil", "none", "zero"):
                fields["backlogs"] = 0
            else:
                try:
                    fields["backlogs"] = int(raw)
                except ValueError:
                    fields["backlogs"] = 0
            confidence += 0.10
        else:
            fields["backlogs"] = 0

        fields["confidence"] = min(1.0, confidence)
        return fields

    @staticmethod
    def parse_income_certificate(text: str) -> dict[str, Any]:
        """Extract annual family income from income certificate text."""
        fields: dict[str, Any] = {}
        confidence = 0.50

        # Match phrases like "Annual Income: Rs. 5,00,000", "Total Family Income: 450000",
        # "Annual Family Income of applicant ... is Rs. 4,80,000"
        income_match = re.search(
            r"(?:annual(?:\s+family)?\s+income|total(?:\s+family)?\s+income|gross\s+income)[\s\S]{0,120}?(?:rs\.?|inr|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)",
            text,
            re.IGNORECASE,
        )
        if income_match:
            raw_str = income_match.group(1).replace(",", "").strip()
            try:
                val = float(raw_str)
                if val >= 0:
                    fields["annual_income"] = val
                    confidence += 0.40
            except ValueError:
                pass

        fields["confidence"] = min(1.0, confidence)
        return fields

    @staticmethod
    def parse_id_proof(text: str) -> dict[str, Any]:
        """Extract identification number and candidate name from ID proof text."""
        fields: dict[str, Any] = {}
        confidence = 0.60

        # Masked ID pattern (e.g. Aadhaar 4 digits or PAN 10 chars)
        pan_match = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b", text)
        aadhaar_match = re.search(r"\b([0-9]{4}\s+[0-9]{4}\s+[0-9]{4})\b", text)

        if pan_match:
            fields["pan_masked"] = f"XXXXXX{pan_match.group(1)[-4:]}"
            confidence += 0.30
        elif aadhaar_match:
            fields["aadhaar_masked"] = f"XXXXXXXX{aadhaar_match.group(1)[-4:]}"
            confidence += 0.30

        fields["confidence"] = min(1.0, confidence)
        return fields

    @classmethod
    def extract_document_fields(
        cls, doc_type: str | DocumentType, text: str
    ) -> dict[str, Any]:
        """Route to appropriate parser by document type."""
        norm_type = doc_type.value if hasattr(doc_type, "value") else str(doc_type).lower()

        if norm_type == "marksheet":
            return cls.parse_marksheet(text)
        elif norm_type == "income_proof":
            return cls.parse_income_certificate(text)
        elif norm_type == "id_proof":
            return cls.parse_id_proof(text)
        return {"confidence": 0.50}
