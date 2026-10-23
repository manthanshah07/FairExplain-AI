# LLM Prompt Specification & Explanation Contract

**Specification of system prompts, input templates, JSON output schemas, and fairness guardrails for the FairExplain AI Explainability Layer.**

---

## 1. Architectural Role & Invariants

The LLM Explanation Layer converts pre-computed deterministic results from the domain layer (`backend/app/domain/`) into accessible, plain-English explanations.

### Non-Negotiable Invariants
1. **No Calculation Authority**: The LLM model **never** computes eligibility, determines award amounts, calculates tuition balances, or assigns numerical scores.
2. **No Decision Modification**: The LLM model cannot alter an `ELIGIBLE`, `INELIGIBLE`, or `PENDING_EVIDENCE` outcome.
3. **Strict Human Governance**: Every explanation generated must explicitly state that the outcome is a recommendation pending human review.
4. **Demographic & Proxy Neutrality**: The explanation must not reference, infer, or justify decisions based on protected demographic attributes (caste, religion, gender, disability) or known proxies (surnames, residential pincodes), even if present in the evaluation context.

---

## 2. System Prompt (v1.0)

```
You are an Explainable AI assistant for FairExplain AI, an educational financing platform.

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
```

---

## 3. Input Telemetry Contract

The backend `/explanation` service supplies the LLM with structured telemetry derived from `EligibilityEvaluationResult` and `TuitionAccountSummary`:

```json
{
  "program_id": "MERIT-ENG-2026",
  "policy_version": "2026.1",
  "engine_version": "1.0.0-phase1b",
  "eligibility_status": "ELIGIBLE",
  "criteria_summary": {
    "satisfied_count": 3,
    "failed_count": 0,
    "pending_count": 0,
    "evaluations": [
      {
        "criterion_id": "CRIT-CGPA",
        "attribute": "cgpa",
        "operator": "gte",
        "target_value": 8.0,
        "actual_value": 8.45,
        "status": "satisfied",
        "is_mandatory": true,
        "reason": "Actual value 8.45 satisfies gte 8.0"
      },
      {
        "criterion_id": "CRIT-BACKLOGS",
        "attribute": "active_backlogs",
        "operator": "eq",
        "target_value": 0,
        "actual_value": 0,
        "status": "satisfied",
        "is_mandatory": true,
        "reason": "Actual value 0 satisfies eq 0"
      }
    ]
  },
  "tuition_accounting": {
    "gross_eligible_tuition": "120000.00",
    "institutional_cap_applied": "100000.00",
    "total_effective_reduction": "75000.00",
    "remaining_payable_tuition": "45000.00",
    "total_unapplied_surplus": "0.00",
    "confirmed_awards": [
      {
        "award_id": "AWD-INST-50",
        "priority": 1,
        "nominal_amount": "60000.00",
        "effective_reduction": "60000.00"
      },
      {
        "award_id": "AWD-DEPT-FIXED",
        "priority": 2,
        "nominal_amount": "15000.00",
        "effective_reduction": "15000.00"
      }
    ]
  }
}
```

---

## 4. Structured Output JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ExplanationResponse",
  "type": "object",
  "required": [
    "summary_headline",
    "reasons",
    "accounting_explanation",
    "required_actions",
    "fairness_attestation",
    "human_review_notice"
  ],
  "properties": {
    "summary_headline": {
      "type": "string",
      "description": "Clear one-sentence summary of the recommendation and net balance."
    },
    "reasons": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Bulleted plain-English explanations referencing satisfied or failed criteria."
    },
    "accounting_explanation": {
      "type": "string",
      "description": "Explanation of how confirmed awards reduced tuition and the remaining payable balance."
    },
    "required_actions": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Action items for the student (e.g., pending documents needed), or empty if none."
    },
    "fairness_attestation": {
      "type": "string",
      "description": "Statement confirming evaluation was based on objective academic and financial factors."
    },
    "human_review_notice": {
      "type": "string",
      "enum": ["This is a decision-support recommendation pending review and approval by an authorized institutional officer."]
    }
  }
}
```

---

## 5. Explanation Example

```json
{
  "summary_headline": "Eligible for Merit Engineering Scholarship with ₹75,000.00 applied toward tuition fees.",
  "reasons": [
    "Your cumulative GPA of 8.45 meets the program requirement of 8.00 or higher.",
    "Zero active backlogs satisfies the academic standing requirement."
  ],
  "accounting_explanation": "From your gross tuition of ₹1,20,000.00, your confirmed institutional award (₹60,000.00) and departmental award (₹15,000.00) provide a total fee reduction of ₹75,000.00, leaving a remaining payable tuition balance of ₹45,000.00.",
  "required_actions": [],
  "fairness_attestation": "This assessment was generated purely from objective academic performance and verified fee schedules without reliance on sensitive demographic factors.",
  "human_review_notice": "This is a decision-support recommendation pending review and approval by an authorized institutional officer."
}
```

---

## 6. Prompt Versioning & Auditability

All explanations are stored in `ExplanationReport` (`backend/app/models/explanation_report.py`) alongside the `llm_prompt_version` string (e.g., `v1.0-phase4`). This guarantees that prompt wording and system behavior can be audited and versioned independently of domain logic versions.
