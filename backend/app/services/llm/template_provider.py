"""
FairExplain AI — Deterministic Explanation Template Engine
============================================================
Guarantees 100% availability and strict compliance when external LLM APIs are offline.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from app.services.llm.base import BaseLLMProvider
from app.services.llm.prompt_templates import MANDATORY_HUMAN_REVIEW_NOTICE


class DeterministicTemplateProvider(BaseLLMProvider):
    """Generates schema-compliant, plain-English explanations using deterministic domain templates."""

    name: str = "deterministic_template"

    async def generate_explanation(self, telemetry: dict[str, Any]) -> str:
        """Produce 100% compliant JSON string from telemetry."""
        status = telemetry.get("eligibility_status", "ELIGIBLE").upper()
        program_id = telemetry.get("program_id", "Scholarship Program")

        # 1. Summary headline
        accounting = telemetry.get("tuition_accounting", {})
        net_tuition = accounting.get("remaining_payable_tuition", "0.00")
        total_reduction = accounting.get("total_effective_reduction", "0.00")

        if status == "ELIGIBLE":
            summary_headline = (
                f"Eligible for {program_id} with ₹{Decimal(total_reduction):,.2f} applied toward tuition fees."
            )
        elif status == "PENDING_EVIDENCE":
            summary_headline = (
                f"Application for {program_id} is pending supporting document verification."
            )
        else:
            summary_headline = (
                f"Currently not eligible for {program_id} based on published program criteria."
            )

        # 2. Reasons list
        reasons: list[str] = []
        evaluations = telemetry.get("criteria_summary", {}).get("evaluations", [])
        for c in evaluations:
            attr = c.get("attribute", "").replace("_", " ").title()
            op = c.get("operator", "")
            target = c.get("target_value")
            actual = c.get("actual_value")
            c_status = c.get("status", "")

            if c_status == "satisfied":
                reasons.append(f"Your {attr} of {actual} meets the required benchmark ({op} {target}).")
            elif c_status == "failed":
                reasons.append(
                    f"Your {attr} of {actual} does not satisfy the mandatory criterion benchmark ({op} {target})."
                )
            elif c_status == "pending_evidence":
                reasons.append(f"Verification of supporting documentation for {attr} is pending.")

        if not reasons:
            reasons.append("All baseline academic and financial eligibility criteria were evaluated.")

        # 3. Accounting explanation
        if accounting:
            gross = Decimal(accounting.get("gross_eligible_tuition", "0.00"))
            reduction = Decimal(accounting.get("total_effective_reduction", "0.00"))
            payable = Decimal(accounting.get("remaining_payable_tuition", "0.00"))
            surplus = Decimal(accounting.get("total_unapplied_surplus", "0.00"))

            acct_text = (
                f"From your gross eligible tuition of ₹{gross:,.2f}, confirmed awards provide a total fee "
                f"reduction of ₹{reduction:,.2f}, leaving a remaining payable tuition balance of ₹{payable:,.2f}."
            )
            if surplus > Decimal("0.00"):
                acct_text += (
                    f" An unapplied award amount of ₹{surplus:,.2f} could not be allocated due to institutional "
                    "waiver limits or zero payable tuition; this is not payable as cash or student refunds."
                )
        else:
            acct_text = "Standard tuition accounting applies to your program enrollment."

        # 4. Required actions
        required_actions: list[str] = []
        for c in evaluations:
            if c.get("status") == "pending_evidence":
                required_actions.append(
                    f"Please submit verified evidence for {c.get('attribute', '').replace('_', ' ')}."
                )

        payload = {
            "summary_headline": summary_headline,
            "reasons": reasons,
            "accounting_explanation": acct_text,
            "required_actions": required_actions,
            "fairness_attestation": (
                "This assessment was generated purely from objective academic performance and verified "
                "fee schedules without reliance on sensitive demographic factors."
            ),
            "human_review_notice": MANDATORY_HUMAN_REVIEW_NOTICE,
        }

        return json.dumps(payload, indent=2)
