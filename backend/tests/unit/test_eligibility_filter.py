"""
Unit tests for deterministic scholarship eligibility evaluation.
"""

from __future__ import annotations

from decimal import Decimal
import unittest

from app.domain.enums import (
    CriterionOperator,
    CriterionOutcome,
    EligibilityStatus,
    EvidenceStatus,
)
from app.domain.exceptions import (
    DisallowedAttributeError,
    MalformedPolicyError,
    UnsupportedAttributeError,
    UnsupportedOperatorError,
)
from app.domain.models import (
    ApplicantProfile,
    EligibilityCriterion,
    ScholarshipPolicy,
)
from app.domain.eligibility import (
    evaluate_criterion,
    evaluate_scholarship_eligibility,
)


class TestEligibilityFilter(unittest.TestCase):
    """Test suite for deterministic scholarship eligibility filtering."""

    def setUp(self) -> None:
        self.criterion_cgpa = EligibilityCriterion(
            criterion_id="crit_cgpa",
            attribute="cgpa",
            operator=CriterionOperator.GTE,
            target_value=Decimal("8.0"),
            is_mandatory=True,
            required_evidence="marksheet",
            description="Minimum CGPA of 8.0",
        )
        self.criterion_income = EligibilityCriterion(
            criterion_id="crit_income",
            attribute="household_income",
            operator=CriterionOperator.LTE,
            target_value=Decimal("600000.00"),
            is_mandatory=True,
            required_evidence="income_proof",
            description="Household income under 6 Lakhs",
        )
        self.policy = ScholarshipPolicy(
            program_id="merit_need_scholarship_2026",
            policy_version="1.0.0",
            title="Merit and Need Scholarship",
            criteria=[self.criterion_cgpa, self.criterion_income],
        )

    def test_all_mandatory_criteria_satisfied(self) -> None:
        """When every mandatory criterion is satisfied and evidence verified -> ELIGIBLE."""
        applicant = ApplicantProfile(
            applicant_id="app_001",
            attributes={
                "cgpa": Decimal("8.5"),
                "household_income": Decimal("450000.00"),
            },
            verified_evidence={
                "marksheet": EvidenceStatus.VERIFIED,
                "income_proof": EvidenceStatus.VERIFIED,
            },
        )
        result = evaluate_scholarship_eligibility(self.policy, applicant)

        self.assertEqual(result.status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(result.satisfied_count, 2)
        self.assertEqual(result.failed_count, 0)
        self.assertEqual(result.pending_count, 0)
        self.assertIn("All 2 mandatory criteria satisfied", result.reason)
        self.assertTrue(all(c.status == CriterionOutcome.SATISFIED for c in result.criteria_evaluations))

    def test_one_mandatory_criterion_failed(self) -> None:
        """When at least one mandatory criterion fails -> INELIGIBLE."""
        applicant = ApplicantProfile(
            applicant_id="app_002",
            attributes={
                "cgpa": Decimal("7.8"),  # Below 8.0
                "household_income": Decimal("400000.00"),
            },
            verified_evidence={
                "marksheet": EvidenceStatus.VERIFIED,
                "income_proof": EvidenceStatus.VERIFIED,
            },
        )
        result = evaluate_scholarship_eligibility(self.policy, applicant)

        self.assertEqual(result.status, EligibilityStatus.INELIGIBLE)
        self.assertEqual(result.satisfied_count, 1)
        self.assertEqual(result.failed_count, 1)
        self.assertEqual(result.pending_count, 0)
        self.assertIn("1 mandatory criterion/criteria failed", result.reason)

    def test_missing_evidence_is_pending_not_failed(self) -> None:
        """Missing evidence document must produce PENDING_EVIDENCE, not FAILED."""
        applicant = ApplicantProfile(
            applicant_id="app_003",
            attributes={
                "cgpa": Decimal("8.5"),
                "household_income": Decimal("400000.00"),
            },
            verified_evidence={
                "marksheet": EvidenceStatus.VERIFIED,
                # income_proof is completely missing from verified_evidence
            },
        )
        result = evaluate_scholarship_eligibility(self.policy, applicant)

        self.assertEqual(result.status, EligibilityStatus.PENDING_EVIDENCE)
        self.assertEqual(result.satisfied_count, 1)
        self.assertEqual(result.failed_count, 0)
        self.assertEqual(result.pending_count, 1)

        income_eval = next(c for c in result.criteria_evaluations if c.criterion_id == "crit_income")
        self.assertEqual(income_eval.status, CriterionOutcome.PENDING_EVIDENCE)
        self.assertEqual(income_eval.evidence_status, EvidenceStatus.MISSING)
        self.assertIn("missing", income_eval.reason.lower())

    def test_unverified_evidence_is_pending(self) -> None:
        """Uploaded but unverified evidence must produce PENDING_EVIDENCE."""
        applicant = ApplicantProfile(
            applicant_id="app_004",
            attributes={
                "cgpa": Decimal("9.0"),
                "household_income": Decimal("350000.00"),
            },
            verified_evidence={
                "marksheet": EvidenceStatus.UNVERIFIED,  # Document uploaded but not yet verified
                "income_proof": EvidenceStatus.VERIFIED,
            },
        )
        result = evaluate_scholarship_eligibility(self.policy, applicant)

        self.assertEqual(result.status, EligibilityStatus.PENDING_EVIDENCE)
        cgpa_eval = next(c for c in result.criteria_evaluations if c.criterion_id == "crit_cgpa")
        self.assertEqual(cgpa_eval.status, CriterionOutcome.PENDING_EVIDENCE)
        self.assertEqual(cgpa_eval.evidence_status, EvidenceStatus.UNVERIFIED)

    def test_mixed_failed_and_pending_criteria(self) -> None:
        """When at least one criterion fails and another is pending, overall status must be INELIGIBLE."""
        applicant = ApplicantProfile(
            applicant_id="app_005",
            attributes={
                "cgpa": Decimal("7.2"),  # FAILED (< 8.0)
                "household_income": Decimal("350000.00"),
            },
            verified_evidence={
                "marksheet": EvidenceStatus.VERIFIED,
                # income_proof is missing -> PENDING_EVIDENCE
            },
        )
        result = evaluate_scholarship_eligibility(self.policy, applicant)

        self.assertEqual(result.status, EligibilityStatus.INELIGIBLE)
        self.assertEqual(result.failed_count, 1)
        self.assertEqual(result.pending_count, 1)
        self.assertIn("Ineligible: 1 mandatory criterion/criteria failed", result.reason)

    def test_missing_attribute_value_is_pending_evidence(self) -> None:
        """When an attribute value is not provided in profile, status must be PENDING_EVIDENCE."""
        applicant = ApplicantProfile(
            applicant_id="app_006",
            attributes={
                "cgpa": Decimal("8.5"),
                # household_income attribute missing entirely
            },
            verified_evidence={
                "marksheet": EvidenceStatus.VERIFIED,
                "income_proof": EvidenceStatus.VERIFIED,
            },
        )
        result = evaluate_scholarship_eligibility(self.policy, applicant)

        self.assertEqual(result.status, EligibilityStatus.PENDING_EVIDENCE)
        income_eval = next(c for c in result.criteria_evaluations if c.criterion_id == "crit_income")
        self.assertEqual(income_eval.status, CriterionOutcome.PENDING_EVIDENCE)
        self.assertIn("not provided", income_eval.reason.lower())

    def test_unsupported_operator_raises_error(self) -> None:
        """Specifying an unsupported operator string must raise UnsupportedOperatorError."""
        with self.assertRaises(UnsupportedOperatorError):
            EligibilityCriterion(
                criterion_id="crit_invalid_op",
                attribute="cgpa",
                operator="regex_match",  # Unsupported
                target_value=".*",
            )

    def test_unknown_or_misspelled_attribute_raises_error(self) -> None:
        """Unknown or misspelled attributes like cgpaa must fail closed at definition time."""
        with self.assertRaises(UnsupportedAttributeError):
            EligibilityCriterion(
                criterion_id="crit_typo",
                attribute="cgpaa",  # Typo
                operator=CriterionOperator.GTE,
                target_value=Decimal("8.0"),
            )

    def test_disallowed_sensitive_attribute_without_charter_raises_error(self) -> None:
        """Sensitive attributes without non-empty charter authorization must raise DisallowedAttributeError."""
        sensitive_attrs = ["caste", "religion", "gender", "disability_status", "caste_category"]
        for attr in sensitive_attrs:
            with self.assertRaises(DisallowedAttributeError):
                EligibilityCriterion(
                    criterion_id=f"crit_{attr}",
                    attribute=attr,
                    operator=CriterionOperator.EQ,
                    target_value="any",
                    charter_authorization="",  # Empty / missing
                )

    def test_sensitive_attribute_with_criterion_charter_authorization_allowed(self) -> None:
        """Sensitive attribute with valid non-empty charter authorization is permitted and evaluated."""
        criterion = EligibilityCriterion(
            criterion_id="crit_women_stem",
            attribute="gender",
            operator=CriterionOperator.EQ,
            target_value="Female",
            charter_authorization="STATE-ACT-2024-WOMEN-IN-STEM",
            is_mandatory=True,
            required_evidence="id_proof",
        )
        policy = ScholarshipPolicy(
            program_id="women_stem_scholarship",
            policy_version="1.0.0",
            title="Women in STEM Scholarship",
            criteria=[criterion],
        )
        app_female = ApplicantProfile(
            applicant_id="app_f",
            attributes={"gender": "Female"},
            verified_evidence={"id_proof": EvidenceStatus.VERIFIED},
        )
        result = evaluate_scholarship_eligibility(policy, app_female)
        self.assertEqual(result.status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(result.satisfied_count, 1)

    def test_sensitive_attribute_with_policy_charter_authorization_allowed(self) -> None:
        """Policy-level charter authorization covers criteria without individual references."""
        criterion = EligibilityCriterion(
            criterion_id="crit_caste",
            attribute="caste_category",
            operator=CriterionOperator.IN,
            target_value=["SC", "ST"],
            charter_authorization="GOV-ORDER-SCST-QUOTA-42",
        )
        policy = ScholarshipPolicy(
            program_id="affirmative_action_scholarship",
            policy_version="1.0.0",
            title="Affirmative Action Grant",
            criteria=[criterion],
            charter_authorizations={"caste_category": "GOV-ORDER-SCST-QUOTA-42"},
        )
        applicant = ApplicantProfile(
            applicant_id="app_sc",
            attributes={"caste_category": "SC"},
        )
        result = evaluate_scholarship_eligibility(policy, applicant)
        self.assertEqual(result.status, EligibilityStatus.ELIGIBLE)

    def test_optional_criterion_failed_does_not_affect_overall_eligibility(self) -> None:
        """When mandatory criteria pass, a failed optional criterion does not make overall result INELIGIBLE."""
        optional_criterion = EligibilityCriterion(
            criterion_id="crit_optional_coursework",
            attribute="coursework_score",
            operator=CriterionOperator.GTE,
            target_value=Decimal("90.0"),
            is_mandatory=False,  # Optional bonus criterion
        )
        policy_with_opt = ScholarshipPolicy(
            program_id="policy_with_opt",
            policy_version="1.0.0",
            title="Policy With Optional Rule",
            criteria=[self.criterion_cgpa, optional_criterion],
        )
        applicant = ApplicantProfile(
            applicant_id="app_opt_fail",
            attributes={
                "cgpa": Decimal("8.5"),  # Satisfies mandatory cgpa >= 8.0
                "coursework_score": Decimal("75.0"),  # Fails optional >= 90.0
            },
            verified_evidence={"marksheet": EvidenceStatus.VERIFIED},
        )
        result = evaluate_scholarship_eligibility(policy_with_opt, applicant)

        self.assertEqual(result.status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(result.satisfied_count, 1)
        self.assertEqual(result.failed_count, 1)
        # Reason string must accurately count only mandatory satisfied criteria
        self.assertIn("All 1 mandatory criteria satisfied", result.reason)

    def test_optional_criterion_pending_does_not_affect_overall_eligibility(self) -> None:
        """When mandatory criteria pass, a pending optional criterion does not hold up overall ELIGIBLE status."""
        optional_criterion = EligibilityCriterion(
            criterion_id="crit_optional_cert",
            attribute="first_generation_college",
            operator=CriterionOperator.EQ,
            target_value=True,
            is_mandatory=False,
            required_evidence="first_gen_cert",
        )
        policy_with_opt = ScholarshipPolicy(
            program_id="policy_with_opt_pend",
            policy_version="1.0.0",
            title="Policy With Optional Rule Pending",
            criteria=[self.criterion_cgpa, optional_criterion],
        )
        applicant = ApplicantProfile(
            applicant_id="app_opt_pend",
            attributes={
                "cgpa": Decimal("8.5"),
                "first_generation_college": True,
            },
            verified_evidence={
                "marksheet": EvidenceStatus.VERIFIED,
                # first_gen_cert missing
            },
        )
        result = evaluate_scholarship_eligibility(policy_with_opt, applicant)

        self.assertEqual(result.status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(result.satisfied_count, 1)
        self.assertEqual(result.pending_count, 1)
        self.assertIn("All 1 mandatory criteria satisfied", result.reason)

    def test_scholarship_policy_immutability(self) -> None:
        """ScholarshipPolicy criteria collection cannot be modified post-construction."""
        criteria_list = [self.criterion_cgpa]
        policy = ScholarshipPolicy(
            program_id="immutable_policy",
            policy_version="1.0.0",
            title="Immutable Policy",
            criteria=criteria_list,
        )
        # Criteria is stored as tuple
        self.assertIsInstance(policy.criteria, tuple)
        with self.assertRaises(AttributeError):
            policy.criteria.append(self.criterion_income)  # type: ignore[attr-defined]

        # Mutating external list has no effect
        criteria_list.append(self.criterion_income)
        self.assertEqual(len(policy.criteria), 1)

    def test_applicant_profile_defensive_copy(self) -> None:
        """Mutating external dictionary passed to ApplicantProfile does not change profile attributes."""
        external_attrs = {"cgpa": Decimal("8.5")}
        external_evidence = {"marksheet": EvidenceStatus.VERIFIED}
        applicant = ApplicantProfile(
            applicant_id="app_defensive",
            attributes=external_attrs,
            verified_evidence=external_evidence,
        )
        external_attrs["cgpa"] = Decimal("5.0")
        external_evidence["marksheet"] = EvidenceStatus.UNVERIFIED

        self.assertEqual(applicant.get_attribute("cgpa"), Decimal("8.5"))
        self.assertEqual(applicant.get_evidence_status("marksheet"), EvidenceStatus.VERIFIED)

    def test_required_evidence_type_mismatch(self) -> None:
        """When required evidence type is income_proof, marksheet verification does not satisfy it."""
        applicant = ApplicantProfile(
            applicant_id="app_mismatch",
            attributes={
                "household_income": Decimal("400000.00"),
            },
            verified_evidence={
                "marksheet": EvidenceStatus.VERIFIED,  # Wrong document type provided
            },
        )
        eval_result = evaluate_criterion(self.criterion_income, applicant)
        self.assertEqual(eval_result.status, CriterionOutcome.PENDING_EVIDENCE)
        self.assertEqual(eval_result.evidence_status, EvidenceStatus.MISSING)

    def test_unsupported_attribute_name_syntax_raises_error(self) -> None:
        """Attribute names with special characters or invalid syntax must raise UnsupportedAttributeError."""
        with self.assertRaises(UnsupportedAttributeError):
            EligibilityCriterion(
                criterion_id="crit_bad_attr",
                attribute="cgpa; DROP TABLE users;--",
                operator=CriterionOperator.GT,
                target_value=8.0,
            )

    def test_malformed_policy_empty_criteria_raises_error(self) -> None:
        """A policy with zero criteria must raise MalformedPolicyError."""
        with self.assertRaises(MalformedPolicyError):
            ScholarshipPolicy(
                program_id="empty_policy",
                policy_version="1.0.0",
                title="Empty Policy",
                criteria=[],
            )

    def test_in_operator_with_non_collection_raises_error(self) -> None:
        """Using 'in' operator with a non-collection target must raise MalformedPolicyError."""
        criterion = EligibilityCriterion(
            criterion_id="crit_in",
            attribute="programme",
            operator=CriterionOperator.IN,
            target_value="not_a_list",  # String instead of list/set
        )
        applicant = ApplicantProfile(
            applicant_id="app_test",
            attributes={"programme": "B.Tech"},
        )
        with self.assertRaises(MalformedPolicyError):
            evaluate_criterion(criterion, applicant)

    def test_in_and_not_in_operators(self) -> None:
        """Test valid collection membership operators."""
        crit_in = EligibilityCriterion(
            criterion_id="crit_dept",
            attribute="department",
            operator=CriterionOperator.IN,
            target_value=["CSE", "ECE", "MECH"],
        )
        crit_not_in = EligibilityCriterion(
            criterion_id="crit_blocked_state",
            attribute="state",
            operator=CriterionOperator.NOT_IN,
            target_value=["XX", "YY"],
        )
        policy = ScholarshipPolicy(
            program_id="dept_policy",
            policy_version="1.0.0",
            title="Dept Policy",
            criteria=[crit_in, crit_not_in],
        )

        app_pass = ApplicantProfile(
            applicant_id="app_dept_1",
            attributes={"department": "CSE", "state": "MH"},
        )
        res_pass = evaluate_scholarship_eligibility(policy, app_pass)
        self.assertEqual(res_pass.status, EligibilityStatus.ELIGIBLE)

        app_fail = ApplicantProfile(
            applicant_id="app_dept_2",
            attributes={"department": "CIVIL", "state": "MH"},
        )
        res_fail = evaluate_scholarship_eligibility(policy, app_fail)
        self.assertEqual(res_fail.status, EligibilityStatus.INELIGIBLE)

    def test_deterministic_structured_explanations(self) -> None:
        """Evaluation results must provide structured, reproducible explanation strings."""
        applicant = ApplicantProfile(
            applicant_id="app_explain",
            attributes={
                "cgpa": Decimal("9.2"),
                "household_income": Decimal("750000.00"),
            },
            verified_evidence={
                "marksheet": EvidenceStatus.VERIFIED,
                "income_proof": EvidenceStatus.VERIFIED,
            },
        )
        result1 = evaluate_scholarship_eligibility(self.policy, applicant)
        result2 = evaluate_scholarship_eligibility(self.policy, applicant)

        self.assertEqual(result1.status, result2.status)
        self.assertEqual(result1.reason, result2.reason)
        self.assertEqual(len(result1.criteria_evaluations), len(result2.criteria_evaluations))

        for c1, c2 in zip(result1.criteria_evaluations, result2.criteria_evaluations):
            self.assertEqual(c1.criterion_id, c2.criterion_id)
            self.assertEqual(c1.status, c2.status)
            self.assertEqual(c1.reason, c2.reason)

    def test_no_implicit_ranking_or_fabricated_criteria(self) -> None:
        """The eligibility filter evaluates ONLY the declared criteria; no unstated merit scores exist."""
        single_crit_policy = ScholarshipPolicy(
            program_id="single_rule_policy",
            policy_version="1.0.0",
            title="Single Rule Policy",
            criteria=[self.criterion_cgpa],
        )
        applicant = ApplicantProfile(
            applicant_id="app_only_cgpa",
            attributes={
                "cgpa": Decimal("8.5"),
                # Zero other attributes provided
            },
            verified_evidence={"marksheet": EvidenceStatus.VERIFIED},
        )
        result = evaluate_scholarship_eligibility(single_crit_policy, applicant)

        self.assertEqual(result.status, EligibilityStatus.ELIGIBLE)
        self.assertEqual(len(result.criteria_evaluations), 1)
        self.assertEqual(result.criteria_evaluations[0].criterion_id, "crit_cgpa")


if __name__ == "__main__":
    unittest.main()
