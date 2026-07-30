# Rule Engine Specification

## 1. Purpose

The Rule Engine is the sole source of truth for scholarship and loan scores. It is deterministic, versioned, and documented here so that identical inputs always produce identical outputs (SRS NFR-6). The LLM Explanation Layer never computes scores — it only explains scores the Rule Engine has already produced.

## 2. Design Principles

- **Deterministic** — no randomness, no model inference in the scoring path itself.
- **Versioned** — every score is tagged with a `rule_engine_version` so historical results remain reproducible even after the formula is tuned.
- **Transparent** — every weight and threshold below is documented and adjustable, not hardcoded silently.

## 3. Scholarship Scoring Model *(proposed default — tunable)*

### 3.1 Inputs
CGPA, 12th %, Household Income, Active Backlogs.

### 3.2 Weighted Score

| Factor | Weight | Normalization |
|---|---|---|
| CGPA | 40% | `(CGPA / 10) × 100` |
| 12th % | 20% | Used as-is (0–100 scale) |
| Household Income (need) | 30% | Inverse-scaled: lower income → higher score, capped at a configurable income ceiling |
| Backlogs | 10% (penalty) | `max(0, 100 − backlogs × 20)` |

```
Scholarship Score = (0.40 × CGPA_norm) + (0.20 × Twelfth_%) 
                   + (0.30 × Income_need_score) + (0.10 × Backlog_score)
```

### 3.3 Scholarship % Bands

| Scholarship Score | Scholarship % of Tuition |
|---|---|
| ≥ 85 | 75% |
| 70–84 | 50% |
| 50–69 | 25% |
| < 50 | 0% |

`Scholarship Amount = Scholarship % × Tuition Fee`

## 4. Loan Assessment Model *(proposed default — tunable)*

### 4.1 Inputs
Reduced Loan Amount (post-scholarship), Household Income, Existing EMI, Documents verification status, Scholarship outcome.

### 4.2 Affordability Check

```
Available Monthly Capacity = (Household Income / 12) × 0.40 − Existing EMI
Estimated New EMI = Reduced Loan Amount / (loan tenure in months)
```

### 4.3 Outcome Logic

| Condition | Outcome |
|---|---|
| Estimated New EMI ≤ Available Monthly Capacity **and** no document mismatch flags | **Eligible** |
| Estimated New EMI ≤ Available Monthly Capacity **but** unresolved document mismatch | **Needs Review** |
| Estimated New EMI > Available Monthly Capacity by ≤ 20% | **Needs Review** |
| Estimated New EMI > Available Monthly Capacity by > 20% | **Not Recommended** |

### 4.4 Confidence Score
Confidence is derived from how far the estimated EMI sits from the capacity threshold — closer to the boundary yields lower confidence, communicated to the student rather than hidden:

```
Confidence = 100 − min(100, |Estimated EMI − Available Capacity| / Available Capacity × 100)
```

## 5. Fairness Safeguards

The Rule Engine never takes caste, religion, gender, disability status, or region as direct inputs. The Fairness Checker additionally screens for **proxy attributes** that could reintroduce bias indirectly, including but not limited to:

- Pincode/geography used as a stand-in for caste or religious demographics.
- Surname-based inference.
- School/institution name used as a socioeconomic proxy beyond its legitimate academic signal.

Any explanation referencing these proxies is flagged for human review rather than auto-published.

## 6. Output States

| Outcome | Meaning |
|---|---|
| **Eligible** | Recommended for approval, pending human sign-off. |
| **Needs Review** | Borderline or flagged case; routed to a human reviewer queue. |
| **Not Recommended** | Does not meet criteria under current inputs; explanation includes the specific shortfall. |

## 7. Reproducibility & Versioning

Every scoring run is tagged with the active `rule_engine_version`. Changing any weight, band, or threshold above requires incrementing this version — past assessments retain the version they were computed under so results remain auditable even as the formula evolves.

## 8. Edge Cases

| Case | Handling |
|---|---|
| OCR fails to extract a required field | Application flagged `needs_review`; scoring proceeds on self-reported value with a mismatch flag noted. |
| Requested loan ≤ Scholarship amount | Reduced Loan Amount floored at 0; Loan Assessment outcome is **Eligible** with a note that no loan is required. |
| Missing financial data | Application blocked from scoring until FinancialProfile is complete. |
