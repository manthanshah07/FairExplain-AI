# Product Requirements Document (PRD)

**Product:** FairExplain AI
**Document Status:** Active Engineering Specification
**Current Phase:** Phase 1B Completed & Merged into `main`; Phase 1C Proposed

---

## 1. Vision & Executive Summary

FairExplain AI is an enterprise-grade explainable student financing platform designed to eliminate the "black box" in higher education financial aid. The platform couples a deterministic domain evaluation core with an explainable AI layer, providing students with transparent visibility into:
1. **Scholarship Eligibility**: Which institutional and program scholarships they qualify for based on transparent, auditable rules.
2. **Net Tuition Accounting**: Exactly how confirmed scholarship awards reduce their tuition payable, accounting for institutional and program caps.
3. **Loan-Need Assessment**: The precise education loan amount required after scholarship support has been allocated.
4. **Transparent Explanations**: Plain-English justifications of outcomes with confidence framing and fairness auditing, while keeping human reviewers firmly in control of all final decisions.

> **Core Tenet:** *The deterministic engine calculates. The AI explains. The human decides.*

---

## 2. Target Users & Problem Framing

| Stakeholder Persona | Core Pain Point | Value Delivered by FairExplain AI |
|---|---|---|
| **Students & Families** | Facing opaque loan rejections or scholarship denials without clear explanations; unable to determine true net tuition payable. | Unified view of scholarship eligibility, net tuition payable, and realistic loan requirements with clear, plain-English reasoning. |
| **Universities & Financial Aid** | Managing manual, inconsistent eligibility reviews and fragmented waiver cap enforcement. | Deterministic, auditable eligibility filtering and automated tuition accounting enforcing institutional caps. |
| **Banks & NBFC Underwriters** | Evaluating education loan requests without knowing if the applicant qualifies for scholarships that reduce risk and loan principal. | Pre-screened, scholarship-reduced loan assessments with full decision-support telemetry and audit trails. |
| **Scholarship Providers** | Needing transparent, verifiable candidate screening adhering to specific program charters. | Verifiable eligibility criteria with explicit charter governance for specialized candidate pools. |

---

## 3. Product Feature Scope

| ID | Feature Name | Description | Current State |
|---|---|---|---|
| **F-01** | **Deterministic Eligibility Filter** | Multi-attribute rule evaluation against institution criteria with three-state outcomes (`ELIGIBLE`, `INELIGIBLE`, `PENDING_EVIDENCE`). | **Implemented & Tested (Phase 1B)** |
| **F-02** | **Tuition Accounting Engine** | Allocation of confirmed awards, enforcement of institutional and program caps, independent tracking of payable tuition and waiver allowances, surplus reporting. | **Implemented & Tested (Phase 1B)** |
| **F-03** | **Applicant Profile Management** | Structured intake of academic credentials, financial profile, and enrollment context. | Scaffolded in DB & UI prototype |
| **F-04** | **Document Verification & OCR** | Upload and automated cross-verification of marksheets, income proofs, and IDs against self-reported attributes. | Planned (Phase 3) |
| **F-05** | **Loan Affordability Scoring** | Deterministic affordability assessment on post-scholarship reduced loan principal. | Planned (Phase 2) |
| **F-06** | **Explainable AI Layer** | Plain-English reasoning, confidence framing, and fairness notes generated from deterministic outputs. | Planned (Phase 4) |
| **F-07** | **Fairness Audit & Screening** | Screening for indirect bias and proxy attributes (pincode, surname, etc.) with automatic human review routing. | Planned (Phase 5) |
| **F-08** | **Interactive What-If Simulator** | Client-side exploration allowing students to model hypothetical inputs (e.g., target CGPA) without submitting formal records. | UI Prototype Scaffolded |
| **F-09** | **Audit Trail & PDF Report** | Cryptographically reproducible summary report detailing inputs, policy versions, calculations, and human notices. | Planned (Phase 6) |
| **F-10** | **Admin Review Queue & Analytics**| Institutional dashboard for managing review queues, overrides, and cohort analytics. | UI Prototype Scaffolded |

---

## 4. Operational Boundaries & Non-Goals

The following areas are strictly **out of scope** for the MVP:
- **No Autonomous Lending**: The system never issues legally binding loan approvals, contracts, or disbursements.
- **No Direct Banking Integrations**: No direct integrations with core banking APIs, credit bureaus (CIBIL, Experian), or payment gateways.
- **Single Currency Scope**: Evaluates Indian higher education financing contexts in INR (`₹`). Multi-currency support is deferred.
- **Responsive Web Only**: Mobile-optimized web client; native iOS/Android applications are out of scope.

---

## 5. Success Metrics & Quality Benchmarks

| Metric Category | Target Benchmark | Measurement Method |
|---|---|---|
| **Domain Determinism** | 100% reproducibility | Identical inputs, policy versions, and engine versions produce identical results across all test suites. |
| **Monetary Accuracy** | 100% exact Decimal precision | No floating-point inaccuracies; exact `ROUND_HALF_UP` quantization (`0.01`) enforced in domain core. |
| **Explanation Coverage** | 100% coverage | Every completed assessment produces a structured plain-English explanation. |
| **Fairness Safety** | 0 unflagged proxy leaks | Explanations containing sensitive demographic proxies are 100% routed to human review queues. |
| **API Latency** | $< 3.0$ seconds | End-to-end evaluation and explanation generation time under standard network conditions. |

---

## 6. Risk Analysis & Mitigations

| Identified Risk | Impact | Architectural Mitigation |
|---|---|---|
| **LLM Hallucination or Decision Drift** | High | The LLM Explanation Layer is strictly decoupled from calculations; it only consumes pre-computed domain outputs and is constrained by JSON schemas. |
| **Premature Rejection on Missing Docs** | Medium | The domain core implements the `PENDING_EVIDENCE` state; missing documents never trigger an `INELIGIBLE` status. |
| **Surplus Misinterpretation** | High | Domain accounting explicitly isolates `unapplied_surplus` and documents that surplus is never converted to cash or student refunds. |
| **Sensitive Attribute Leakage** | High | Sensitive attributes fail closed without explicit `charter_authorization` strings, and the Fairness Checker screens outputs for indirect proxies. |
