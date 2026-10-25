"""
FairExplain AI — Unit Tests for Loan Affordability Engine
===========================================================
Pure Python unit tests verifying deterministic loan serviceability calculations.
No external dependencies; runs via standard library unittest.
"""

from decimal import Decimal
import unittest

from app.domain.enums import LoanOutcome
from app.domain.exceptions import (
    InvalidLoanParametersError,
    InvalidMonetaryValueError,
)
from app.domain.loan import (
    LoanAffordabilityProfile,
    LoanAffordabilityResult,
    assess_loan_affordability,
)


class TestLoanAffordability(unittest.TestCase):
    """Test suite for deterministic loan affordability evaluation."""

    def test_eligible_standard(self) -> None:
        """
        Household income: ₹1,200,000 / yr -> Monthly ₹100,000
        40% cap: ₹40,000
        Existing EMI: ₹10,000
        Available capacity: ₹30,000
        Post-scholarship loan: ₹1,200,000 over 60 months -> EMI ₹20,000
        EMI (20k) <= capacity (30k) -> ELIGIBLE
        """
        profile = LoanAffordabilityProfile(
            applicant_id="APP_001",
            household_income=Decimal("1200000.00"),
            existing_emi=Decimal("10000.00"),
            post_scholarship_loan_amount=Decimal("1200000.00"),
            tenure_months=60,
        )
        res = assess_loan_affordability(profile)
        self.assertEqual(res.outcome, LoanOutcome.ELIGIBLE)
        self.assertEqual(res.monthly_income, Decimal("100000.00"))
        self.assertEqual(res.available_monthly_capacity, Decimal("30000.00"))
        self.assertEqual(res.estimated_emi, Decimal("20000.00"))
        self.assertEqual(res.dti_ratio_percent, Decimal("30.00"))

    def test_zero_loan_needed_is_eligible(self) -> None:
        """Post-scholarship tuition balance is zero -> ELIGIBLE with 0 EMI."""
        profile = LoanAffordabilityProfile(
            applicant_id="APP_002",
            household_income=Decimal("600000.00"),
            existing_emi=Decimal("5000.00"),
            post_scholarship_loan_amount=Decimal("0.00"),
            tenure_months=36,
        )
        res = assess_loan_affordability(profile)
        self.assertEqual(res.outcome, LoanOutcome.ELIGIBLE)
        self.assertEqual(res.estimated_emi, Decimal("0.00"))
        self.assertIn("zero", res.reason.lower())

    def test_needs_review_within_20_percent_buffer(self) -> None:
        """
        Monthly income: ₹50,000 (₹600,000 / 12)
        40% budget: ₹20,000
        Existing EMI: ₹5,000
        Available capacity: ₹15,000
        Buffer limit (120%): ₹18,000
        Loan: ₹600,000 / 36 months -> EMI ₹16,666.67
        Capacity (15,000) < EMI (16,666.67) <= Buffer (18,000) -> NEEDS_REVIEW
        """
        profile = LoanAffordabilityProfile(
            applicant_id="APP_003",
            household_income=Decimal("600000.00"),
            existing_emi=Decimal("5000.00"),
            post_scholarship_loan_amount=Decimal("600000.00"),
            tenure_months=36,
        )
        res = assess_loan_affordability(profile)
        self.assertEqual(res.outcome, LoanOutcome.NEEDS_REVIEW)
        self.assertEqual(res.estimated_emi, Decimal("16666.67"))
        self.assertIn("review", res.reason.lower())

    def test_not_recommended_exceeding_buffer(self) -> None:
        """
        Monthly income: ₹50,000
        Available capacity: ₹15,000
        Buffer limit (120%): ₹18,000
        Loan: ₹500,000 / 24 months -> EMI ₹20,833.33
        EMI (20,833.33) > Buffer (18,000) -> NOT_RECOMMENDED
        """
        profile = LoanAffordabilityProfile(
            applicant_id="APP_004",
            household_income=Decimal("600000.00"),
            existing_emi=Decimal("5000.00"),
            post_scholarship_loan_amount=Decimal("500000.00"),
            tenure_months=24,
        )
        res = assess_loan_affordability(profile)
        self.assertEqual(res.outcome, LoanOutcome.NOT_RECOMMENDED)
        self.assertEqual(res.estimated_emi, Decimal("20833.33"))

    def test_existing_emi_exceeds_40_percent_limit(self) -> None:
        """
        Monthly income: ₹100,000
        40% limit: ₹40,000
        Existing EMI: ₹45,000 -> Available capacity: -₹5,000 <= 0 -> NOT_RECOMMENDED
        """
        profile = LoanAffordabilityProfile(
            applicant_id="APP_005",
            household_income=Decimal("1200000.00"),
            existing_emi=Decimal("45000.00"),
            post_scholarship_loan_amount=Decimal("100000.00"),
            tenure_months=60,
        )
        res = assess_loan_affordability(profile)
        self.assertEqual(res.outcome, LoanOutcome.NOT_RECOMMENDED)
        self.assertEqual(res.available_monthly_capacity, Decimal("-5000.00"))

    def test_invalid_parameters_validation(self) -> None:
        """Verify parameter validation raises appropriate exceptions."""
        # Non-positive tenure
        with self.assertRaises(InvalidLoanParametersError):
            LoanAffordabilityProfile(
                applicant_id="APP",
                household_income=Decimal("500000"),
                existing_emi=Decimal("0"),
                post_scholarship_loan_amount=Decimal("100000"),
                tenure_months=0,
            )

        # Negative tenure
        with self.assertRaises(InvalidLoanParametersError):
            LoanAffordabilityProfile(
                applicant_id="APP",
                household_income=Decimal("500000"),
                existing_emi=Decimal("0"),
                post_scholarship_loan_amount=Decimal("100000"),
                tenure_months=-12,
            )

        # Empty applicant id
        with self.assertRaises(InvalidLoanParametersError):
            LoanAffordabilityProfile(
                applicant_id="   ",
                household_income=Decimal("500000"),
                existing_emi=Decimal("0"),
                post_scholarship_loan_amount=Decimal("100000"),
            )

        # Negative income
        with self.assertRaises(InvalidMonetaryValueError):
            LoanAffordabilityProfile(
                applicant_id="APP",
                household_income=Decimal("-100"),
                existing_emi=Decimal("0"),
                post_scholarship_loan_amount=Decimal("100000"),
            )

        # Boolean rejected
        with self.assertRaises(InvalidMonetaryValueError):
            LoanAffordabilityProfile(
                applicant_id="APP",
                household_income=True,  # type: ignore
                existing_emi=Decimal("0"),
                post_scholarship_loan_amount=Decimal("100000"),
            )


if __name__ == "__main__":
    unittest.main()
