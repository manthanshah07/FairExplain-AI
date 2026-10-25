"""
FairExplain AI — LLM Guardrails & Anti-Hallucination Validator
================================================================
Enforces zero-calculation integrity, demographic proxy shielding,
and structured output compliance per PROMPTS.md and ROADMAP.md §4.
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.services.llm.prompt_templates import MANDATORY_HUMAN_REVIEW_NOTICE

PROHIBITED_TERMS = frozenset({
    "caste",
    "dalit",
    "brahmin",
    "reservation",
    "quota",
    "religion",
    "muslim",
    "hindu",
    "christian",
    "gender",
    "female",
    "male",
    "disabled",
    "handicapped",
})


class GuardrailValidationError(Exception):
    """Raised when an LLM-generated explanation violates architectural invariants."""


def clean_json_markdown(text: str) -> str:
    """Strip markdown code fence blocks if returned by the LLM."""
    clean = text.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\s*```$", "", clean)
    return clean.strip()


def validate_explanation_json(
    raw_response: str, telemetry: dict[str, Any]
) -> dict[str, Any]:
    """
    Validate LLM output against the JSON schema, demographic rules, and authority boundaries.
    Raises GuardrailValidationError on failure.
    """
    cleaned = clean_json_markdown(raw_response)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GuardrailValidationError(f"Response is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise GuardrailValidationError("Top-level JSON payload must be an object.")

    # 1. Required fields
    required_keys = [
        "summary_headline",
        "reasons",
        "accounting_explanation",
        "required_actions",
        "fairness_attestation",
        "human_review_notice",
    ]
    for key in required_keys:
        if key not in data:
            raise GuardrailValidationError(f"Missing required explanation key: '{key}'.")

    # 2. Enforce human governance disclaimer verbatim
    if data["human_review_notice"].strip() != MANDATORY_HUMAN_REVIEW_NOTICE:
        raise GuardrailValidationError(
            f"Invalid human_review_notice. Expected exact text: '{MANDATORY_HUMAN_REVIEW_NOTICE}'."
        )

    # 3. Demographic & Proxy Neutrality Check
    full_text = " ".join([
        str(data.get("summary_headline", "")),
        " ".join(str(r) for r in data.get("reasons", [])),
        str(data.get("accounting_explanation", "")),
        " ".join(str(a) for a in data.get("required_actions", [])),
    ]).lower()

    for term in PROHIBITED_TERMS:
        # Match whole word
        if re.search(rf"\b{re.escape(term)}\b", full_text):
            raise GuardrailValidationError(
                f"Prohibited demographic or proxy attribute detected in explanation text: '{term}'."
            )

    # 4. Status consistency check
    status = telemetry.get("eligibility_status", "").upper()
    headline_lower = data["summary_headline"].lower()
    if status == "INELIGIBLE" and "congratulations" in headline_lower:
        raise GuardrailValidationError("Explanation contradicts INELIGIBLE status.")

    return data
