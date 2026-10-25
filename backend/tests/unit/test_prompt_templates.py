"""
FairExplain AI — Unit Tests for Telemetry Serializer
======================================================
Tests serialization of domain evaluations into standard PROMPTS.md telemetry JSON.
"""

from decimal import Decimal
import unittest

from app.domain.enums import CriterionOutcome, EligibilityStatus
from app.domain.models import (
    CriterionEvaluation,
    EligibilityEvaluationResult,
    TuitionAccountSummary,
)
from app.services.llm.prompt_templates import build_input_telemetry


class TestPromptTelemetrySerializer(unittest.TestCase):
    """Test suite for LLM input telemetry serialization."""

    def test_telemetry_serialization(self) -> None:
        """Verify telemetry serialization contains all required fields and string numbers."""
        eval_result = EligibilityEvaluationResult(
            program_id="PROG_ENG_2026",
            policy_version="1.2.0",
            status=EligibilityStatus.ELIGIBLE,
            reason="All mandatory criteria passed.",
            criteria_evaluations=[
                CriterionEvaluation(
                    criterion_id="CRIT_CGPA",
                    attribute="cgpa",
                    operator="gte",
                    target_value=Decimal("8.00"),
                    actual_value=Decimal("8.50"),
                    status=CriterionOutcome.SATISFIED,
                    is_mandatory=True,
                    evidence_required="marksheet",
                    evidence_status=None,  # type: ignore
                    reason="Passed",
                )
            ],
            satisfied_count=1,
            failed_count=0,
            pending_count=0,
        )

        acct = TuitionAccountSummary(
            gross_eligible_tuition=Decimal("120000.00"),
            institutional_cap_applied=Decimal("100000.00"),
            total_effective_reduction=Decimal("60000.00"),
            remaining_payable_tuition=Decimal("60000.00"),
            remaining_waiver_allowance=Decimal("40000.00"),
            total_unapplied_surplus=Decimal("0.00"),
            confirmed_allocations=[],
            unconfirmed_awards=[],
        )

        telemetry = build_input_telemetry(eval_result, acct)
        self.assertEqual(telemetry["program_id"], "PROG_ENG_2026")
        self.assertEqual(telemetry["eligibility_status"], "ELIGIBLE")
        self.assertEqual(telemetry["criteria_summary"]["satisfied_count"], 1)
        self.assertEqual(
            telemetry["tuition_accounting"]["gross_eligible_tuition"], "120000.00"
        )
        self.assertEqual(
            telemetry["tuition_accounting"]["remaining_payable_tuition"], "60000.00"
        )


if __name__ == "__main__":
    unittest.main()
