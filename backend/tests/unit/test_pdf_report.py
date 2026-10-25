"""
FairExplain AI — Unit Tests for PDF Report Compiler and Hasher
================================================================
Tests PDF generation and cryptographic SHA-256 digest computation.
"""

import unittest

from app.services.pdf.hasher import compute_audit_hash
from app.services.pdf.report_generator import generate_assessment_pdf


class TestPDFReportGenerator(unittest.TestCase):
    """Test suite for PDF report generation."""

    def test_compute_audit_hash_deterministic(self) -> None:
        """Audit hash is deterministic regardless of key insertion order."""
        payload1 = {"app_id": "123", "status": "ELIGIBLE", "score": 90}
        payload2 = {"status": "ELIGIBLE", "score": 90, "app_id": "123"}
        h1 = compute_audit_hash(payload1)
        h2 = compute_audit_hash(payload2)
        self.assertEqual(len(h1), 64)
        self.assertEqual(h1, h2)

    def test_generate_assessment_pdf(self) -> None:
        """Verify report generation produces valid PDF bytes with embedded hash."""
        data = {
            "application_id": "APP_PDF_TEST_001",
            "applicant": {"name": "Test Student", "email": "student@test.edu"},
            "academic": {"cgpa": 8.75, "backlogs": 0},
            "financial": {
                "household_income": 500000.0,
                "existing_emi": 5000.0,
                "tuition_fee": 150000.0,
            },
            "scholarship": {
                "status": "eligible",
                "tuition_accounting": {
                    "gross_eligible_tuition": 150000.0,
                    "institutional_cap_applied": 100000.0,
                    "total_effective_reduction": 75000.0,
                    "remaining_payable_tuition": 75000.0,
                    "total_unapplied_surplus": 0.0,
                },
            },
            "explanation": {
                "summary_headline": "Eligible for scholarship with 75k reduction.",
                "reasons": ["CGPA meets merit bar."],
                "accounting_explanation": "Tuition reduced by half.",
            },
        }

        pdf_bytes, audit_hash = generate_assessment_pdf(data)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertEqual(len(audit_hash), 64)


if __name__ == "__main__":
    unittest.main()
