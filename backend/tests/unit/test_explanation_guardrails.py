"""
FairExplain AI — Unit Tests for Explanation Guardrails
========================================================
Tests schema enforcement, demographic attribute rejection, and disclaimer checks.
"""

import json
import unittest

from app.services.llm.guardrails import (
    GuardrailValidationError,
    validate_explanation_json,
)
from app.services.llm.prompt_templates import MANDATORY_HUMAN_REVIEW_NOTICE


class TestExplanationGuardrails(unittest.TestCase):
    """Test suite for LLM guardrails."""

    def setUp(self) -> None:
        self.telemetry = {
            "eligibility_status": "ELIGIBLE",
            "program_id": "TEST_PROG",
        }
        self.valid_payload = {
            "summary_headline": "Eligible for TEST_PROG scholarship.",
            "reasons": ["CGPA of 8.5 meets requirement."],
            "accounting_explanation": "Tuition reduced by 50,000.",
            "required_actions": [],
            "fairness_attestation": "Objective evaluation performed.",
            "human_review_notice": MANDATORY_HUMAN_REVIEW_NOTICE,
        }

    def test_valid_json_passes(self) -> None:
        """Valid JSON meeting all constraints passes validation."""
        raw = json.dumps(self.valid_payload)
        res = validate_explanation_json(raw, self.telemetry)
        self.assertEqual(res["summary_headline"], self.valid_payload["summary_headline"])

    def test_markdown_fences_stripped(self) -> None:
        """Surrounding markdown code block is cleanly stripped."""
        raw = f"```json\n{json.dumps(self.valid_payload)}\n```"
        res = validate_explanation_json(raw, self.telemetry)
        self.assertEqual(res["human_review_notice"], MANDATORY_HUMAN_REVIEW_NOTICE)

    def test_missing_field_fails(self) -> None:
        """Missing required field raises GuardrailValidationError."""
        bad_payload = dict(self.valid_payload)
        del bad_payload["reasons"]
        with self.assertRaises(GuardrailValidationError):
            validate_explanation_json(json.dumps(bad_payload), self.telemetry)

    def test_invalid_disclaimer_fails(self) -> None:
        """Modified human review disclaimer raises GuardrailValidationError."""
        bad_payload = dict(self.valid_payload)
        bad_payload["human_review_notice"] = "This decision is final and binding."
        with self.assertRaises(GuardrailValidationError):
            validate_explanation_json(json.dumps(bad_payload), self.telemetry)

    def test_prohibited_demographic_term_fails(self) -> None:
        """Mentioning sensitive demographic attributes raises GuardrailValidationError."""
        bad_payload = dict(self.valid_payload)
        bad_payload["reasons"] = ["Awarded under female applicant quota."]
        with self.assertRaises(GuardrailValidationError):
            validate_explanation_json(json.dumps(bad_payload), self.telemetry)


if __name__ == "__main__":
    unittest.main()
