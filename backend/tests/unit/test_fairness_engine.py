"""
FairExplain AI — Unit Tests for Fairness & Proxy Screening Engine
===================================================================
Pure Python tests verifying demographic keyword detection, postal proxy screening,
and disparate impact ratio calculations.
"""

import unittest

from app.domain.fairness import (
    compute_disparate_impact_ratio,
    screen_text_for_proxies,
)


class TestFairnessScreeningEngine(unittest.TestCase):
    """Test suite for domain fairness screening functions."""

    def test_clean_text_passes(self) -> None:
        """Text without demographic keywords or proxies is clean."""
        text = "Applicant has a CGPA of 8.85 and meets the merit criteria without active backlogs."
        report = screen_text_for_proxies(text)
        self.assertTrue(report.is_clean)
        self.assertEqual(report.total_violations_count, 0)
        self.assertEqual(report.sanitized_text, text)

    def test_demographic_keyword_detected_and_redacted(self) -> None:
        """Demographic terms like 'caste' or 'religion' are flagged and redacted."""
        text = "The applicant qualifies under the reserved caste category quota."
        report = screen_text_for_proxies(text)
        self.assertFalse(report.is_clean)
        self.assertGreaterEqual(report.total_violations_count, 2)
        self.assertIn("[REDACTED_DEMOGRAPHIC_PROXY]", report.sanitized_text)
        self.assertNotIn("caste", report.sanitized_text.lower())

    def test_postal_proxy_detected_and_redacted(self) -> None:
        """Flagged socio-economic postal code proxies are flagged and redacted."""
        text = "Applicant resides in municipal district with pincode 400017."
        report = screen_text_for_proxies(text)
        self.assertFalse(report.is_clean)
        self.assertEqual(report.violations[0].violation_type, "geographic_proxy")
        self.assertEqual(report.violations[0].detected_token, "400017")
        self.assertIn("[REDACTED_DEMOGRAPHIC_PROXY]", report.sanitized_text)

    def test_disparate_impact_four_fifths_rule(self) -> None:
        """Verify disparate impact ratio calculation."""
        # 80% / 100% = 0.80 (Compliant benchmark)
        ratio = compute_disparate_impact_ratio(0.80, 1.00)
        self.assertEqual(ratio, 0.80)

        # 60% / 90% = 0.6667 (Below 80% threshold -> Adverse impact)
        ratio_low = compute_disparate_impact_ratio(0.60, 0.90)
        self.assertEqual(ratio_low, 0.6667)

        # Baseline zero edge-case
        self.assertEqual(compute_disparate_impact_ratio(0.50, 0.0), 1.0)


if __name__ == "__main__":
    unittest.main()
