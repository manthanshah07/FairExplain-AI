"""
FairExplain AI — Unit Tests for OCR Key-Field Extractor
=========================================================
Tests parsing of marksheets, income certificates, and ID proofs.
"""

import unittest
from app.services.ocr.extractor import DocumentKeyExtractor


class TestDocumentKeyExtractor(unittest.TestCase):
    """Test suite for DocumentKeyExtractor."""

    def test_parse_marksheet_standard(self) -> None:
        """Extract CGPA and backlogs from typical marksheet header."""
        text = """
        UNIVERSITY OF ENGINEERING AND TECHNOLOGY
        Statement of Grades - Fall 2025
        Candidate Name: Ananya Roy
        Cumulative Grade Point Average (CGPA): 8.92 / 10
        Active Backlogs: 0
        Status: Regular PASS
        """
        res = DocumentKeyExtractor.parse_marksheet(text)
        self.assertEqual(res["cgpa"], 8.92)
        self.assertEqual(res["backlogs"], 0)
        self.assertGreaterEqual(res["confidence"], 0.70)

    def test_parse_marksheet_with_nil_backlogs(self) -> None:
        """Handle NIL backlogs correctly."""
        text = "Grade Point Average: 7.50\nBacklogs: NIL"
        res = DocumentKeyExtractor.parse_marksheet(text)
        self.assertEqual(res["cgpa"], 7.50)
        self.assertEqual(res["backlogs"], 0)

    def test_parse_income_certificate(self) -> None:
        """Extract annual income from tehsildar income certificate."""
        text = """
        REVENUE DEPARTMENT - GOVERNMENT OF MAHARASHTRA
        Income Certificate Form No. 12
        This is to certify that the Annual Family Income of applicant Shri Ramesh Patel
        from all sources is Rs. 4,80,000/- (Rupees Four Lakh Eighty Thousand Only).
        Issued Date: 12-01-2026
        """
        res = DocumentKeyExtractor.parse_income_certificate(text)
        self.assertEqual(res["annual_income"], 480000.0)
        self.assertGreaterEqual(res["confidence"], 0.80)

    def test_parse_id_proof_pan(self) -> None:
        """Extract and mask PAN number."""
        text = "INCOME TAX DEPARTMENT - GOVT OF INDIA\nPermanent Account Number: ABCDE1234F"
        res = DocumentKeyExtractor.parse_id_proof(text)
        self.assertEqual(res["pan_masked"], "XXXXXX234F")


if __name__ == "__main__":
    unittest.main()
