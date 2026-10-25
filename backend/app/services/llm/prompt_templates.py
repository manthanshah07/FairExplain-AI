"""
FairExplain AI — Prompt Templates & Telemetry Serializer
==========================================================
System prompts, input telemetry contract, and serialization per PROMPTS.md.
"""

from __future__ import annotations

from typing import Any

from app.domain.models import (
    EligibilityEvaluationResult,
    TuitionAccountSummary,
)

SYSTEM_PROMPT = """You are an Explainable AI assistant for FairExplain AI, an educational financing platform.

You will receive a structured JSON object containing deterministic domain outputs:
- Scholarship eligibility status (ELIGIBLE, INELIGIBLE, or PENDING_EVIDENCE)
- Detailed criterion-level evaluations
- Tuition accounting breakdown (gross tuition, applied reductions, remaining payable tuition, surplus)
- Engine version and policy version

Your sole responsibility is to translate these deterministic findings into clear, empathetic, and objective plain-English explanations for the applicant and financial aid officer.

Mandatory Constraints:
1. Never approve, reject, or award funding. Frame all determinations as recommendations pending authorized human review.
2. Do not recompute, alter, or contradict the provided numerical amounts, balances, or eligibility statuses.
3. If criteria failed, explain the exact criteria shortfall objectively without clinical jargon.
4. If evidence is pending, clearly specify which supporting documents are required to complete verification.
5. If unapplied surplus exists, explain that surplus represents award room constrained by institutional policy or zero balance, and is not cash or a student refund.
6. Strictly avoid referencing sensitive demographic attributes (caste, religion, gender, disability) or geographical proxies (pincode, locality) in your explanation reasoning.
7. If you cannot explain an outcome without referencing a prohibited attribute, output a statement that a human fairness review is required.

You MUST respond strictly with a valid JSON object matching the requested schema. Do not output markdown fences or explanatory text outside the JSON object.
"""

MANDATORY_HUMAN_REVIEW_NOTICE = (
    "This is a decision-support recommendation pending review and approval by an authorized institutional officer."
)


def build_input_telemetry(
    eval_result: EligibilityEvaluationResult,
    accounting_summary: TuitionAccountSummary | None = None,
    engine_version: str = "1.0.0-phase1b",
) -> dict[str, Any]:
    """Serialize pure domain evaluation and tuition accounting into standard PROMPTS.md telemetry JSON."""
    criteria_list = [
        {
            "criterion_id": c.criterion_id,
            "attribute": c.attribute,
            "operator": c.operator,
            "target_value": float(c.target_value) if hasattr(c.target_value, "__float__") else c.target_value,
            "actual_value": float(c.actual_value) if hasattr(c.actual_value, "__float__") else c.actual_value,
            "status": c.status.value,
            "is_mandatory": c.is_mandatory,
            "reason": c.reason,
        }
        for c in eval_result.criteria_evaluations
    ]

    telemetry: dict[str, Any] = {
        "program_id": eval_result.program_id,
        "policy_version": eval_result.policy_version,
        "engine_version": engine_version,
        "eligibility_status": eval_result.status.value.upper(),
        "criteria_summary": {
            "satisfied_count": eval_result.satisfied_count,
            "failed_count": eval_result.failed_count,
            "pending_count": eval_result.pending_count,
            "evaluations": criteria_list,
        },
    }

    if accounting_summary:
        telemetry["tuition_accounting"] = {
            "gross_eligible_tuition": str(accounting_summary.gross_eligible_tuition),
            "institutional_cap_applied": str(accounting_summary.institutional_cap_applied),
            "total_effective_reduction": str(accounting_summary.total_effective_reduction),
            "remaining_payable_tuition": str(accounting_summary.remaining_payable_tuition),
            "total_unapplied_surplus": str(accounting_summary.total_unapplied_surplus),
            "confirmed_awards": [
                {
                    "award_id": a.award_id,
                    "priority": a.priority,
                    "nominal_amount": str(a.nominal_amount),
                    "effective_reduction": str(a.effective_reduction),
                }
                for a in accounting_summary.confirmed_allocations
            ],
        }

    return telemetry
