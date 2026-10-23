# Software Requirements Specification (SRS)

**Product:** FairExplain AI
**Document Status:** Active Engineering Specification
**Current Phase:** Phase 1B Completed & Merged into `main`; Phase 1C Proposed

---

## 1. Introduction

### 1.1 Purpose
This document translates the product goals defined in [PRD.md](./PRD.md) into concrete, testable functional and non-functional engineering requirements for FairExplain AI.

### 1.2 System Scope
The system comprises:
1. **Deterministic Domain Core** (`backend/app/domain/`): Implemented in pure Python 3.10+; owns eligibility evaluation and tuition accounting calculations.
2. **Backend API & Persistence Layer** (`backend/app/`): FastAPI application framework and SQLAlchemy 2 persistence services.
3. **Frontend Client Application** (`frontend/src/`): React + Vite + TypeScript user interface.
4. **Explainable AI & Fairness Layer**: LLM explanation generation and proxy-attribute screening guardrails.

---

## 2. Functional Requirements

| Requirement ID | Specification | Status & Traceability |
|---|---|---|
| **FR-01** | System shall maintain user profiles categorized by role (`student`, `university`, `bank`, `scholarship_provider`, `admin`). | Scaffolded in `models/user.py` |
| **FR-02** | System shall collect academic profile attributes: `cgpa`, `tenth_percent`, `twelfth_percent`, `active_backlogs`, and `coursework_score`. | Scaffolded in `models/academic_record.py` |
| **FR-03** | System shall collect financial profile attributes: `household_income`, `existing_emi`, `tuition_fee`, and `requested_loan`. | Scaffolded in `models/financial_profile.py` |
| **FR-04** | System shall support document uploads (`marksheet`, `income_proof`, `id_proof`) in PDF and image formats. | Scaffolded in `models/uploaded_document.py` |
| **FR-05** | System shall execute OCR extraction on uploaded documents and cross-check extracted data against self-reported attributes. | Planned (Phase 3) |
| **FR-06** | System shall deterministically evaluate scholarship eligibility using institution criteria, supporting `EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`, `IN`, `NOT_IN` operators and returning `ELIGIBLE`, `INELIGIBLE`, or `PENDING_EVIDENCE`. | **Implemented & Tested (Phase 1B)** (`backend/app/domain/eligibility.py`) |
| **FR-07** | System shall strictly validate criteria attributes against `SUPPORTED_ATTRIBUTES`, rejecting unknown attributes and requiring explicit `charter_authorization` for sensitive attributes. | **Implemented & Tested (Phase 1B)** (`backend/app/domain/models.py`) |
| **FR-08** | System shall allocate confirmed scholarship awards against gross eligible tuition in strict ascending priority order, applying institutional and program caps and tracking surplus. | **Implemented & Tested (Phase 1B)** (`backend/app/domain/accounting.py`) |
| **FR-09** | System shall enforce that only awards with lifecycle status `CONFIRMED` reduce tuition payable; provisional, pending, or unconfirmed awards shall not reduce payable tuition. | **Implemented & Tested (Phase 1B)** (`backend/app/domain/accounting.py`) |
| **FR-10** | System shall reject confirmed awards with missing or tied priority ranks and reject mutually exclusive incompatible awards with explicit domain exceptions. | **Implemented & Tested (Phase 1B)** (`backend/app/domain/accounting.py`) |
| **FR-11** | System shall perform loan affordability assessment on the post-scholarship reduced loan principal. | Planned (Phase 2) |
| **FR-12** | System shall generate a structured plain-English explanation for every completed assessment using a constrained LLM prompt contract. | Planned (Phase 4) (Contract in `PROMPTS.md`) |
| **FR-13** | System shall screen all generated explanations for sensitive demographic proxies and route flagged cases to human review. | Planned (Phase 5) |
| **FR-14** | System shall provide a client-side What-If Simulator allowing prospective applicants to model scenarios without persisting formal applications. | Prototype Scaffolded in UI |
| **FR-15** | System shall compile a downloadable PDF summary report embedding calculations, explanation text, policy versions, and human-review disclaimers. | Planned (Phase 6) |
| **FR-16** | System shall record every domain evaluation, explanation generation pass, fairness flag, and human review action in an immutable audit log. | Scaffolded in `models/audit_log.py` |

---

## 3. Non-Functional Requirements

| ID | Requirement | Metric / Verification Method |
|---|---|---|
| **NFR-01** | **Deterministic Reproducibility** | Identical inputs, policy versions, and engine versions must yield identical outputs with 100% mathematical consistency across runs. |
| **NFR-02** | **Zero External Dependencies in Domain Core** | `backend/app/domain/` must have zero third-party dependencies, running purely on Python 3.10+ standard library. |
| **NFR-03** | **Finite Monetary Arithmetic** | Monetary calculations must use `Decimal` with finite-value validation and `ROUND_HALF_UP` quantization to two decimal places (`0.01`). Floats and booleans are prohibited. |
| **NFR-04** | **Human Authority Governance** | System outputs are strictly labeled as decision-support recommendations. Human reviewers retain sole legal and operational decision authority. |
| **NFR-05** | **Response Time Latency** | Domain calculations must execute in $< 50\text{ ms}$; end-to-end API response time (including AI explanation) must be $< 3.0\text{ seconds}$. |
| **NFR-06** | **Responsive & Accessible UI** | Frontend must be fully responsive across mobile (390px), tablet, and desktop (1280px+), adhering to WCAG 2.1 AA contrast standards. |
| **NFR-07** | **Data Protection at Rest** | Financial profile data and uploaded identity documents must be encrypted at rest in the database and cloud storage. |

---

## 4. Input & Output Data Dictionaries

### 4.1 Domain Inputs (`backend/app/domain/models.py`)
| Field Name | Type | Constraints / Registry |
|---|---|---|
| `cgpa` | Decimal | 0.00 – 10.00 (`MERIT_RANKING`, `PROGRAM_ELIGIBILITY`) |
| `tenth_percent` | Decimal | 0.00 – 100.00 (`MERIT_RANKING`, `PROGRAM_ELIGIBILITY`) |
| `twelfth_percent` | Decimal | 0.00 – 100.00 (`MERIT_RANKING`, `PROGRAM_ELIGIBILITY`) |
| `active_backlogs` | Integer | $\ge 0$ count (`MERIT_RANKING`, `PROGRAM_ELIGIBILITY`) |
| `household_income` | Decimal | $\ge 0.00$ INR/year (`PROGRAM_ELIGIBILITY`) |
| `tuition_fee` | Decimal | $> 0.00$ INR/year (`PROGRAM_ELIGIBILITY`) |
| `caste_category` | String | Sensitive attribute; requires non-empty `charter_authorization` |
| `gender` | String | Sensitive attribute; requires non-empty `charter_authorization` |
| `disability_status`| String / Bool | Sensitive attribute; requires non-empty `charter_authorization` |

### 4.2 Accounting Outputs (`backend/app/domain/models.py`)
| Field Name | Type | Description |
|---|---|---|
| `gross_eligible_tuition` | Decimal | Base tuition fee subject to scholarship allocation (`0.01` precision). |
| `institutional_cap_applied` | Decimal | Effective waiver limit under institutional policies. |
| `total_effective_reduction` | Decimal | Sum of actual fee reductions achieved by confirmed awards. |
| `remaining_payable_tuition` | Decimal | Net tuition balance payable by the student. |
| `remaining_waiver_allowance` | Decimal | Unused waiver allowance remaining under institutional caps. |
| `total_unapplied_surplus` | Decimal | Award value that exceeded tuition or caps (not cash or refund). |
| `confirmed_allocations` | List | Detailed per-award breakdown (nominal, capped, reduction, surplus, cap reason). |
| `unconfirmed_awards` | List | Non-confirmed awards that did not reduce payable tuition. |
