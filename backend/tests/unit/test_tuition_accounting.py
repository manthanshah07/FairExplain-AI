"""
Unit tests for deterministic tuition and confirmed-award accounting.
"""

from __future__ import annotations

from decimal import Decimal
import unittest

from app.domain.enums import AwardStatus, AwardType
from app.domain.exceptions import (
    IncompatibleAwardsError,
    InvalidMonetaryValueError,
    MissingAwardPriorityError,
    TiedAwardPriorityError,
)
from app.domain.models import (
    AwardSpecification,
    InstitutionalCap,
)
from app.domain.accounting import (
    calculate_tuition_accounting,
)


class TestTuitionAccounting(unittest.TestCase):
    """Test suite for deterministic tuition accounting and award capping."""

    def test_acceptance_case_exact_values(self) -> None:
        """
        Approved Acceptance Case:
        - Gross eligible tuition: ₹100,000
        - Institutional waiver cap: ₹80,000
        - Confirmed award A: ₹50,000, priority 1
        - Confirmed award B: ₹40,000, priority 2

        Expected results:
        - Total effective tuition reduction: ₹80,000
        - Remaining payable tuition: ₹20,000
        - Unapplied surplus for award B: ₹10,000
        - Remaining waiver allowance: ₹0
        """
        gross = Decimal("100000.00")
        cap = InstitutionalCap(max_waiver_amount=Decimal("80000.00"))

        award_a = AwardSpecification(
            award_id="award_a",
            program_id="prog_merit",
            title="Merit Award A",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("50000.00"),
            priority=1,
        )
        award_b = AwardSpecification(
            award_id="award_b",
            program_id="prog_need",
            title="Need Award B",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("40000.00"),
            priority=2,
        )

        summary = calculate_tuition_accounting(
            gross_eligible_tuition=gross,
            awards=[award_a, award_b],
            institutional_cap=cap,
        )

        # Invariant checks
        self.assertEqual(summary.gross_eligible_tuition, Decimal("100000.00"))
        self.assertEqual(summary.institutional_cap_applied, Decimal("80000.00"))
        self.assertEqual(summary.total_effective_reduction, Decimal("80000.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("20000.00"))
        self.assertEqual(summary.remaining_waiver_allowance, Decimal("0.00"))
        self.assertEqual(summary.total_unapplied_surplus, Decimal("10000.00"))

        # Breakdown checks
        self.assertEqual(len(summary.confirmed_allocations), 2)

        alloc_a = summary.confirmed_allocations[0]
        self.assertEqual(alloc_a.award_id, "award_a")
        self.assertEqual(alloc_a.nominal_amount, Decimal("50000.00"))
        self.assertEqual(alloc_a.effective_reduction, Decimal("50000.00"))
        self.assertEqual(alloc_a.unapplied_surplus, Decimal("0.00"))
        self.assertIsNone(alloc_a.cap_reason)

        alloc_b = summary.confirmed_allocations[1]
        self.assertEqual(alloc_b.award_id, "award_b")
        self.assertEqual(alloc_b.nominal_amount, Decimal("40000.00"))
        self.assertEqual(alloc_b.effective_reduction, Decimal("30000.00"))
        self.assertEqual(alloc_b.unapplied_surplus, Decimal("10000.00"))
        self.assertIn("Institutional waiver cap", alloc_b.cap_reason)

    def test_fixed_and_percentage_awards(self) -> None:
        """Percentage awards are computed as percentage of gross tuition."""
        gross = Decimal("200000.00")
        # Award A: 25% of 200,000 = 50,000
        award_pct = AwardSpecification(
            award_id="award_pct",
            program_id="prog_pct",
            title="25% Tuition Waiver",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.PERCENTAGE_OF_TUITION,
            percentage=Decimal("25.00"),
            priority=1,
        )
        # Award B: Fixed ₹30,000
        award_fix = AwardSpecification(
            award_id="award_fix",
            program_id="prog_fix",
            title="Fixed Grant",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("30000.00"),
            priority=2,
        )

        summary = calculate_tuition_accounting(
            gross_eligible_tuition=gross,
            awards=[award_pct, award_fix],
        )

        self.assertEqual(summary.total_effective_reduction, Decimal("80000.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("120000.00"))
        self.assertEqual(summary.total_unapplied_surplus, Decimal("0.00"))

    def test_program_level_cap_applied(self) -> None:
        """An award amount cannot exceed its max_award_cap."""
        gross = Decimal("200000.00")
        # 50% of 200,000 is 100,000, but program caps award at 60,000
        award = AwardSpecification(
            award_id="award_capped",
            program_id="prog_capped",
            title="50% Capped Waiver",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.PERCENTAGE_OF_TUITION,
            percentage=Decimal("50.00"),
            max_award_cap=Decimal("60000.00"),
            priority=1,
        )

        summary = calculate_tuition_accounting(gross_eligible_tuition=gross, awards=[award])
        alloc = summary.confirmed_allocations[0]

        self.assertEqual(alloc.nominal_amount, Decimal("100000.00"))
        self.assertEqual(alloc.capped_amount, Decimal("60000.00"))
        self.assertEqual(alloc.effective_reduction, Decimal("60000.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("140000.00"))

    def test_percentage_institutional_cap_and_tighter_cap_resolution(self) -> None:
        """If both fixed amount and percentage caps are configured, the tighter cap applies."""
        gross = Decimal("100000.00")
        # 75% of 100,000 = 75,000. Fixed amount cap = 60,000. Tighter cap is 60,000.
        dual_cap = InstitutionalCap(
            max_waiver_amount=Decimal("60000.00"),
            max_waiver_percentage=Decimal("75.00"),
        )
        award = AwardSpecification(
            award_id="award_1",
            program_id="prog_1",
            title="Full Waiver",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("100000.00"),
            priority=1,
        )

        summary = calculate_tuition_accounting(
            gross_eligible_tuition=gross,
            awards=[award],
            institutional_cap=dual_cap,
        )

        self.assertEqual(summary.institutional_cap_applied, Decimal("60000.00"))
        self.assertEqual(summary.total_effective_reduction, Decimal("60000.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("40000.00"))
        self.assertEqual(summary.total_unapplied_surplus, Decimal("40000.00"))

    def test_no_configured_institutional_cap(self) -> None:
        """When no institutional cap is specified, waiver allowance equals gross tuition."""
        gross = Decimal("150000.00")
        award = AwardSpecification(
            award_id="award_full",
            program_id="prog_full",
            title="Full Award",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("150000.00"),
            priority=1,
        )

        summary = calculate_tuition_accounting(
            gross_eligible_tuition=gross,
            awards=[award],
            institutional_cap=None,  # No cap configured
        )

        self.assertEqual(summary.institutional_cap_applied, Decimal("150000.00"))
        self.assertEqual(summary.total_effective_reduction, Decimal("150000.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("0.00"))
        self.assertEqual(summary.remaining_waiver_allowance, Decimal("0.00"))

    def test_unconfirmed_awards_do_not_reduce_payable_tuition(self) -> None:
        """Awards in ELIGIBLE, APPLIED, PENDING, or PROVISIONALLY_AWARDED do not reduce payable tuition."""
        gross = Decimal("100000.00")
        confirmed_award = AwardSpecification(
            award_id="conf_1",
            program_id="prog_conf",
            title="Confirmed 20k",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("20000.00"),
            priority=1,
        )
        applied_award = AwardSpecification(
            award_id="appl_1",
            program_id="prog_appl",
            title="Applied 50k",
            status=AwardStatus.APPLIED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("50000.00"),
            priority=2,
        )
        provisional_award = AwardSpecification(
            award_id="prov_1",
            program_id="prog_prov",
            title="Provisional 30k",
            status=AwardStatus.PROVISIONALLY_AWARDED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("30000.00"),
            priority=3,
        )

        summary = calculate_tuition_accounting(
            gross_eligible_tuition=gross,
            awards=[confirmed_award, applied_award, provisional_award],
        )

        # Only the confirmed 20,000 reduces payable tuition
        self.assertEqual(summary.total_effective_reduction, Decimal("20000.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("80000.00"))
        self.assertEqual(len(summary.confirmed_allocations), 1)
        self.assertEqual(len(summary.unconfirmed_awards), 2)

    def test_missing_priority_raises_error(self) -> None:
        """Confirmed award with priority=None must raise MissingAwardPriorityError."""
        gross = Decimal("100000.00")
        award = AwardSpecification(
            award_id="award_no_prio",
            program_id="prog_1",
            title="No Priority Award",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("10000.00"),
            priority=None,  # Missing
        )

        with self.assertRaises(MissingAwardPriorityError):
            calculate_tuition_accounting(gross_eligible_tuition=gross, awards=[award])

    def test_tied_priority_raises_error(self) -> None:
        """Confirmed awards sharing the same priority rank must raise TiedAwardPriorityError."""
        gross = Decimal("100000.00")
        award1 = AwardSpecification(
            award_id="award_1",
            program_id="prog_1",
            title="Award 1",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("20000.00"),
            priority=1,
        )
        award2 = AwardSpecification(
            award_id="award_2",
            program_id="prog_2",
            title="Award 2",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("30000.00"),
            priority=1,  # Tied!
        )

        with self.assertRaises(TiedAwardPriorityError):
            calculate_tuition_accounting(gross_eligible_tuition=gross, awards=[award1, award2])

    def test_incompatible_awards_raise_error(self) -> None:
        """Simultaneous confirmed awards that declare incompatibility must raise IncompatibleAwardsError."""
        gross = Decimal("100000.00")
        award_merit = AwardSpecification(
            award_id="merit_full",
            program_id="merit_scheme",
            title="Merit Full Scheme",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("50000.00"),
            priority=1,
            incompatible_programs=frozenset({"need_scheme"}),
        )
        award_need = AwardSpecification(
            award_id="need_full",
            program_id="need_scheme",
            title="Need Full Scheme",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("40000.00"),
            priority=2,
            incompatible_programs=frozenset({"merit_scheme"}),
        )

        with self.assertRaises(IncompatibleAwardsError):
            calculate_tuition_accounting(
                gross_eligible_tuition=gross,
                awards=[award_merit, award_need],
            )

    def test_zero_tuition_and_awards_exceeding_tuition(self) -> None:
        """When gross tuition is zero, effective reduction is zero and award becomes unapplied surplus."""
        gross = Decimal("0.00")
        award = AwardSpecification(
            award_id="award_surplus",
            program_id="prog_1",
            title="Award for zero tuition",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("25000.00"),
            priority=1,
        )

        summary = calculate_tuition_accounting(gross_eligible_tuition=gross, awards=[award])

        self.assertEqual(summary.remaining_payable_tuition, Decimal("0.00"))
        self.assertEqual(summary.total_effective_reduction, Decimal("0.00"))
        self.assertEqual(summary.total_unapplied_surplus, Decimal("25000.00"))

    def test_negative_gross_tuition_raises_error(self) -> None:
        """Negative gross tuition must raise InvalidMonetaryValueError."""
        with self.assertRaises(InvalidMonetaryValueError):
            calculate_tuition_accounting(gross_eligible_tuition=Decimal("-100.00"), awards=[])

    def test_decimal_rounding_round_half_up(self) -> None:
        """Tuition calculations round half-up at two decimal places."""
        gross = Decimal("100000.00")
        # 33.335% of 100,000 = 33,335.00
        # 33.333% of 100,000 = 33,333.00
        award = AwardSpecification(
            award_id="award_round",
            program_id="prog_round",
            title="Odd percentage award",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.PERCENTAGE_OF_TUITION,
            percentage=Decimal("33.335"),
            priority=1,
        )

        summary = calculate_tuition_accounting(gross_eligible_tuition=gross, awards=[award])
        alloc = summary.confirmed_allocations[0]

        self.assertEqual(alloc.nominal_amount, Decimal("33335.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("66665.00"))

    def test_unconstrained_tuition_exhaustion_reports_payable_zero_not_cap(self) -> None:
        """
        Phase 1B.1 Audit Counterexample:
        Gross = ₹50,000. Cap = None (unconstrained policy).
        Award 1: Fixed ₹50,000, Priority 1.
        Award 2: Fixed ₹10,000, Priority 2.

        Expected:
        - Award 1: effective = 50,000, surplus = 0
        - Award 2: effective = 0, full surplus = 10,000
        - Award 2 cap_reason must report 'Remaining payable tuition reached zero',
          NEVER 'Institutional waiver cap reached'.
        """
        gross = Decimal("50000.00")
        award1 = AwardSpecification(
            award_id="a1_50k",
            program_id="prog_1",
            title="Full Tuition Award",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("50000.00"),
            priority=1,
        )
        award2 = AwardSpecification(
            award_id="a2_10k",
            program_id="prog_2",
            title="Secondary Award",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("10000.00"),
            priority=2,
        )

        summary = calculate_tuition_accounting(
            gross_eligible_tuition=gross,
            awards=[award1, award2],
            institutional_cap=None,  # Unconstrained
        )

        self.assertEqual(summary.total_effective_reduction, Decimal("50000.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("0.00"))
        self.assertEqual(summary.total_unapplied_surplus, Decimal("10000.00"))

        alloc2 = summary.confirmed_allocations[1]
        self.assertEqual(alloc2.nominal_amount, Decimal("10000.00"))
        self.assertEqual(alloc2.effective_reduction, Decimal("0.00"))
        self.assertEqual(alloc2.unapplied_surplus, Decimal("10000.00"))
        self.assertEqual(alloc2.cap_reason, "Remaining payable tuition reached zero")

    def test_boolean_priority_raises_error(self) -> None:
        """Boolean values (True/False) must not be accepted as integer priorities."""
        gross = Decimal("50000.00")
        with self.assertRaises(MissingAwardPriorityError):
            AwardSpecification(
                award_id="award_bool_prio",
                program_id="p1",
                title="Bool Priority Award",
                status=AwardStatus.CONFIRMED,
                award_type=AwardType.FIXED_AMOUNT,
                amount=Decimal("10000.00"),
                priority=True,  # type: ignore[arg-type]
            )

    def test_non_finite_monetary_values_raise_error(self) -> None:
        """Non-finite inputs (NaN, Infinity) must raise InvalidMonetaryValueError."""
        non_finite_values = [
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
            float("nan"),
            float("inf"),
            float("-inf"),
        ]
        for val in non_finite_values:
            with self.assertRaises(InvalidMonetaryValueError):
                calculate_tuition_accounting(gross_eligible_tuition=val, awards=[])

            with self.assertRaises(InvalidMonetaryValueError):
                InstitutionalCap(max_waiver_percentage=val)

    def test_zero_percent_institutional_cap(self) -> None:
        """An institutional cap configured as 0.00% must yield 0 effective reduction and 100% surplus."""
        gross = Decimal("100000.00")
        cap_zero = InstitutionalCap(max_waiver_percentage=Decimal("0.00"))
        award = AwardSpecification(
            award_id="award_z",
            program_id="prog_z",
            title="Award under 0% cap",
            status=AwardStatus.CONFIRMED,
            award_type=AwardType.FIXED_AMOUNT,
            amount=Decimal("50000.00"),
            priority=1,
        )

        summary = calculate_tuition_accounting(
            gross_eligible_tuition=gross,
            awards=[award],
            institutional_cap=cap_zero,
        )

        self.assertEqual(summary.institutional_cap_applied, Decimal("0.00"))
        self.assertEqual(summary.total_effective_reduction, Decimal("0.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("100000.00"))
        self.assertEqual(summary.total_unapplied_surplus, Decimal("50000.00"))
        self.assertEqual(
            summary.confirmed_allocations[0].cap_reason,
            "Institutional waiver cap reached",
        )

    def test_all_awards_unconfirmed_leaves_tuition_untouched(self) -> None:
        """When all awards are in non-confirmed statuses, payable tuition is unchanged and reduction is zero."""
        gross = Decimal("75000.00")
        awards = [
            AwardSpecification(
                award_id="a_app",
                program_id="p1",
                title="Applied",
                status=AwardStatus.APPLIED,
                award_type=AwardType.FIXED_AMOUNT,
                amount=Decimal("25000.00"),
                priority=1,
            ),
            AwardSpecification(
                award_id="a_elig",
                program_id="p2",
                title="Eligible",
                status=AwardStatus.ELIGIBLE,
                award_type=AwardType.FIXED_AMOUNT,
                amount=Decimal("30000.00"),
                priority=2,
            ),
            AwardSpecification(
                award_id="a_prov",
                program_id="p3",
                title="Provisional",
                status=AwardStatus.PROVISIONALLY_AWARDED,
                award_type=AwardType.FIXED_AMOUNT,
                amount=Decimal("20000.00"),
                priority=3,
            ),
        ]

        summary = calculate_tuition_accounting(gross_eligible_tuition=gross, awards=awards)

        self.assertEqual(summary.total_effective_reduction, Decimal("0.00"))
        self.assertEqual(summary.remaining_payable_tuition, Decimal("75000.00"))
        self.assertEqual(summary.total_unapplied_surplus, Decimal("0.00"))
        self.assertEqual(len(summary.confirmed_allocations), 0)
        self.assertEqual(len(summary.unconfirmed_awards), 3)

    def test_repeatability_and_determinism(self) -> None:
        """Running the calculation multiple times with identical inputs yields bit-for-bit identical results."""
        gross = Decimal("85000.00")
        cap = InstitutionalCap(max_waiver_amount=Decimal("50000.00"))
        awards = [
            AwardSpecification(
                award_id="a1",
                program_id="p1",
                title="A1",
                status=AwardStatus.CONFIRMED,
                award_type=AwardType.FIXED_AMOUNT,
                amount=Decimal("30000.00"),
                priority=1,
            ),
            AwardSpecification(
                award_id="a2",
                program_id="p2",
                title="A2",
                status=AwardStatus.CONFIRMED,
                award_type=AwardType.FIXED_AMOUNT,
                amount=Decimal("35000.00"),
                priority=2,
            ),
        ]

        run1 = calculate_tuition_accounting(gross, awards, cap)
        run2 = calculate_tuition_accounting(gross, awards, cap)

        self.assertEqual(run1.remaining_payable_tuition, run2.remaining_payable_tuition)
        self.assertEqual(run1.total_effective_reduction, run2.total_effective_reduction)
        self.assertEqual(run1.total_unapplied_surplus, run2.total_unapplied_surplus)
        self.assertEqual(run1.remaining_waiver_allowance, run2.remaining_waiver_allowance)


if __name__ == "__main__":
    unittest.main()
