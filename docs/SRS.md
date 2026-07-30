# Software Requirements Specification (SRS)

**Product:** FairExplain AI
**Status:** Draft — v1.0

---

## 1. Introduction

### 1.1 Purpose
Defines the functional and non-functional requirements for FairExplain AI, translating the goals in [PRD.md](./PRD.md) into implementable requirements.

### 1.2 Scope
Covers the web application (frontend + backend), the AI layer (OCR, rule engine, LLM explanation, fairness checker), and reporting/admin features described in the PRD.

### 1.3 Definitions
- **Rule Engine**: deterministic scoring module producing scholarship/loan scores from structured inputs.
- **Explanation Layer**: LLM-based module that converts a computed score into plain-English reasoning.
- **Fairness Checker**: module that audits inputs and LLM outputs for reliance on sensitive/proxy attributes.

## 2. Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | System shall support user registration and login (demo authentication acceptable for MVP; production requires verified identity). |
| FR-2 | System shall collect academic profile data: CGPA, 10th %, 12th %, active backlog count. |
| FR-3 | System shall collect financial profile data: household income, existing EMI obligations, tuition fee, requested loan amount. |
| FR-4 | System shall accept document uploads (marksheets, income proof, ID proof) in PDF/image format. |
| FR-5 | System shall run OCR extraction on uploaded documents and cross-check extracted values against user-entered values, flagging mismatches. |
| FR-6 | System shall compute a Scholarship Score and Scholarship Amount using the deterministic formula in [RULE_ENGINE.md](./RULE_ENGINE.md). |
| FR-7 | System shall compute a Reduced Loan Amount (requested loan − scholarship amount) prior to loan assessment. |
| FR-8 | System shall compute a Loan Assessment outcome (Eligible / Needs Review / Not Recommended) on the reduced loan amount. |
| FR-9 | System shall generate an AI explanation (recommendation, reasons, confidence, fairness note) for every Scholarship and Loan Assessment. |
| FR-10 | System shall run a Fairness Check on every generated explanation before it is shown to the user. |
| FR-11 | System shall allow students to run a What-If Simulation without creating a formal application record. |
| FR-12 | System shall generate a downloadable PDF report summarizing scores, recommendation, and explanation. |
| FR-13 | System shall provide an admin dashboard showing application volume, outcome distribution, and fairness-flag rate. |
| FR-14 | System shall log every scoring event and explanation generation event to an audit trail (see [DATA_MODEL.md](./DATA_MODEL.md)). |
| FR-15 | System shall route any "Needs Review" outcome to a human reviewer queue and shall not present it as a final decision anywhere in the UI. |

## 3. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | UI shall be responsive across desktop, tablet, and mobile viewports. |
| NFR-2 | Average API response time shall be under 3 seconds. |
| NFR-3 | Every AI-generated recommendation shall include a human-readable explanation — no unexplained numeric-only output. |
| NFR-4 | All scoring, document, and explanation events shall be recorded in an audit log with timestamp and rule-engine version. |
| NFR-5 | UI shall meet basic accessibility standards (keyboard navigation, sufficient color contrast, alt text on icons). |
| NFR-6 | Rule engine outputs shall be 100% reproducible: identical inputs and rule-engine version shall always yield identical scores. |
| NFR-7 | Uploaded documents and financial data shall be stored encrypted at rest. |

## 4. Data Dictionary — Inputs

| Field | Type | Notes |
|---|---|---|
| CGPA | Decimal (0–10) | Current cumulative GPA |
| 10th % | Decimal (0–100) | Secondary school percentage |
| 12th % | Decimal (0–100) | Higher secondary percentage |
| Backlogs | Integer | Count of active/unresolved backlogs |
| Household Income | Currency (INR/year) | Self-reported, cross-checked via OCR |
| Existing EMI | Currency (INR/month) | Sum of current loan obligations |
| Tuition Fee | Currency (INR/year) | Annual program fee |
| Requested Loan | Currency (INR) | Amount requested before scholarship reduction |
| Documents | File(s) | Marksheets, income proof, ID proof |

## 5. Data Dictionary — Outputs

| Field | Type | Notes |
|---|---|---|
| Scholarship % | Decimal | Percentage of tuition fee covered |
| Scholarship Amount | Currency (INR) | Scholarship % × tuition fee |
| Remaining Loan | Currency (INR) | Requested loan − scholarship amount |
| Recommendation | Enum | Eligible / Needs Review / Not Recommended |
| Confidence | Decimal (0–100%) | Rule-engine score confidence band |
| Explanation | Text | Plain-English reasoning (LLM-generated) |
| Fairness Note | Text | Result of fairness check on this output |

## 6. External Interface Requirements

- REST API (FastAPI) consumed by the React frontend over HTTPS.
- LLM provider API (Gemini/OpenAI) called server-side only — no client-side API keys.
- OCR service invoked server-side on document upload.

## 7. Traceability

Every functional requirement above maps to a PRD feature (§4 of [PRD.md](./PRD.md)); FR-6–FR-10 map to the Rule Engine and Explanation Layer detailed in [RULE_ENGINE.md](./RULE_ENGINE.md) and [PROMPTS.md](./PROMPTS.md) respectively.
