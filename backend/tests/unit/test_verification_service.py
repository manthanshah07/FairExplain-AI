"""
FairExplain AI — Unit Tests for Verification Service Rules
============================================================
Tests tolerance thresholds for CGPA and income cross-verification.
"""

from decimal import Decimal
import unittest

from app.services.verification_service import VerificationService


class TestVerificationService(unittest.TestCase):
    """Test suite for cross-verification logic."""

    def test_cgpa_exact_match(self) -> None:
        """Exact CGPA matches."""
        matched, reason = VerificationService.verify_cgpa(8.85, Decimal("8.85"))
        self.assertTrue(matched)
        self.assertIn("matches", reason.lower())

    def test_cgpa_within_tolerance(self) -> None:
        """CGPA within +/- 0.05 tolerance matches."""
        matched, reason = VerificationService.verify_cgpa(8.88, Decimal("8.85"))
        self.assertTrue(matched)

        matched, reason = VerificationService.verify_cgpa(8.81, Decimal("8.85"))
        self.assertTrue(matched)

    def test_cgpa_outside_tolerance(self) -> None:
        """CGPA difference > 0.05 fails verification."""
        matched, reason = VerificationService.verify_cgpa(8.95, Decimal("8.85"))
        self.assertFalse(matched)
        self.assertIn("discrepancy", reason.lower())

    def test_income_within_five_percent(self) -> None:
        """Income within +/- 5% matches."""
        # 500,000 reported vs 520,000 extracted (+4%)
        matched, reason = VerificationService.verify_income(520000.0, Decimal("500000.00"))
        self.assertTrue(matched)

        # 500,000 reported vs 480,000 extracted (-4%)
        matched, reason = VerificationService.verify_income(480000.0, Decimal("500000.00"))
        self.assertTrue(matched)

    def test_income_outside_five_percent(self) -> None:
        """Income difference > 5% fails verification."""
        # 500,000 reported vs 550,000 extracted (+10%)
        matched, reason = VerificationService.verify_income(550000.0, Decimal("500000.00"))
        self.assertFalse(matched)
        self.assertIn("discrepancy", reason.lower())


if __name__ == "__main__":
    unittest.main()
