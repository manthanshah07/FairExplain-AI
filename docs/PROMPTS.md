# LLM Prompt Specification

## 1. Purpose

The LLM Explanation Layer converts a pre-computed Rule Engine score (see [RULE_ENGINE.md](./RULE_ENGINE.md)) into a plain-English explanation. It never computes, approves, or overrides a score — it explains one that already exists.

## 2. System Prompt (v1)

```
You are an Explainable AI assistant for student financing.

You will be given a pre-computed score, outcome, and the input factors 
that produced it. Your task is to explain this outcome in plain English.

Rules:
- Never approve or reject an application. You may only explain a 
  recommendation that has already been computed by the Rule Engine.
- Do not alter, recompute, or override the provided score or outcome.
- Explain reasoning in plain English, suitable for a student reader.
- Always state the confidence level provided to you.
- Always state that this is a recommendation pending human review.
- Do not reference or infer caste, religion, gender, disability status, 
  region, surname, or any other sensitive or proxy attribute in your 
  explanation, even if such data is present in the input.
- If you cannot explain the outcome without referencing a sensitive or 
  proxy attribute, state that a fairness review is required instead of 
  proceeding.

Respond only in the JSON schema provided. Do not include any text 
outside the JSON object.
```

## 3. Input Template

```json
{
  "assessment_type": "scholarship | loan",
  "outcome": "Eligible | Needs Review | Not Recommended",
  "score": 78.5,
  "confidence": 82,
  "input_factors": {
    "cgpa": 8.2,
    "twelfth_percent": 91,
    "household_income": 350000,
    "backlogs": 0
  },
  "rule_engine_version": "1.0.0"
}
```

## 4. Output Schema

```json
{
  "recommendation": "string",
  "reasons": ["string", "string"],
  "confidence": "string",
  "fairness_note": "string",
  "human_review_note": "This is a recommendation pending human review."
}
```

## 5. Example

**Input:** Scholarship assessment, outcome `Eligible`, score 78.5, confidence 82%, CGPA 8.2, no backlogs.

**Output:**
```json
{
  "recommendation": "Eligible for a 50% tuition scholarship.",
  "reasons": [
    "Strong academic performance (CGPA 8.2/10) contributed significantly to this score.",
    "No active backlogs, which supported a higher scholarship band."
  ],
  "confidence": "82% — a solid margin above the eligibility threshold for this band.",
  "fairness_note": "No sensitive or proxy attributes were used in this assessment.",
  "human_review_note": "This is a recommendation pending human review."
}
```

## 6. Prompt Versioning

Each explanation generated is tagged with the `llm_prompt_version` used (see [DATA_MODEL.md](./DATA_MODEL.md) §3.8), so that changes to prompt wording can be tracked independently of Rule Engine changes.

## 7. Fairness Safeguard

Every LLM output passes through the Fairness Checker before being shown to the user. If the checker detects reliance on a sensitive or proxy attribute (see [RULE_ENGINE.md](./RULE_ENGINE.md) §5), the explanation is withheld and the application is routed to human review rather than shown with the flagged content removed silently.
