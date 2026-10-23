# PROJECTCONTEXT.md

> **Purpose:** This document provides AI coding agents (Claude Code, Cursor, Codex, Gemini CLI, etc.) and software engineers with the authoritative architectural context, non-negotiable constraints, verified current status, and development conventions required to contribute consistently to FairExplain AI.

---

## 1. Project Identity & Status

- **Project Name:** FairExplain AI
- **Repository Path:** `/Users/manthanshah/Documents/FairExplainAI/FairExplain-AI`
- **Current Verified Status:**
  - **Phase 1B (Deterministic Domain Core): COMPLETED and MERGED into `main`** (Commit `72d0a03`, PR #5).
  - **Phase 1C (Persistence Layer): PROPOSED and AWAITING EXPLICIT IMPLEMENTATION APPROVAL** (Audited as `READY WITH BLOCKERS`).
  - **Backend Scaffold & Frontend Prototype:** Present, partially scaffolded; business endpoints and live database persistence are not yet active.
- **Mission:** Build an explainable, deterministic education financing platform that evaluates scholarship eligibility, calculates post-scholarship tuition balances, and prepares structured explanations while maintaining strict human-in-the-loop decision governance.

---

## 2. Verified Implementation Status

Do not guess whether a component or route exists. The repository state has been audited as follows:

| Layer / Component | Verified Implementation State | Notes |
|---|---|---|
| **Deterministic Domain Core** | **Implemented & Tested** (`backend/app/domain/`) | Pure Python 3.10+, zero external dependencies. **40/40 unit tests pass** (`tests/unit/`). |
| **Domain Tests** | **Executable & Passing** | Runs via `PYTHONPATH=. python3 -m unittest discover -s tests/unit`. No third-party packages required. |
| **Backend Scaffold** | **Scaffolded** (`backend/app/main.py`) | FastAPI app with logging, middleware, CORS, lifespan, and `/health`. |
| **API Routers** | **Scaffolded / Inactive** (`backend/app/api/router.py`) | Feature routers (`/auth`, `/application`, `/scholarship`, `/loan`) are commented out pending integration. |
| **Database Models** | **Scaffolded** (`backend/app/models/`) | Initial SQLAlchemy 2 ORM models exist (User, Application, AcademicRecord, FinancialProfile, UploadedDocument, ScholarshipAssessment, LoanAssessment, ExplanationReport, AuditLogEntry). |
| **Database Migrations** | **Not Initialized** (`backend/alembic/versions/`) | Alembic configuration exists, but `versions/` contains only `.gitkeep`. No migration revisions have been generated or applied. |
| **Persistence Repositories** | **Scaffolded / Inactive** (`backend/app/repositories/`) | Generic base repository scaffold exists; domain-specific repositories are not yet implemented. |
| **Frontend Client** | **Prototype / Mock-backed** (`frontend/src/`) | React + Vite client with full UI flows running against mock data (`mock-data.ts`). |
| **OCR Service** | **Not Implemented** | Document processing pipeline is planned for future phases. |
| **LLM Explanation Service** | **Prompt Contract Specified** | Specifications exist in `docs/PROMPTS.md`; backend service integration is planned for future phases. |
| **Fairness Checker** | **Designed** | Proxy screening rules defined; runtime checker is planned for future phases. |

---

## 3. Approved Domain Contracts (Phase 1B Invariants)

The Phase 1B domain core implements strict contracts in `backend/app/domain/`. Any future changes or persistence layers must conform to these invariants:

### 3.1 Eligibility Filtering vs. Ranking
- **Filtering is Not Ranking**: Phase 1B implements deterministic eligibility filtering against explicit program criteria. Merit ranking, percentile scoring, and competitive cohort comparisons are distinct downstream processes and are **not** part of Phase 1B.
- **Three-State Outcomes**:
  - `ELIGIBLE`: All mandatory criteria satisfied; all required evidence verified.
  - `INELIGIBLE`: One or more mandatory criteria failed.
  - `PENDING_EVIDENCE`: No mandatory criteria failed, but one or more criteria require evidence that is missing or unverified.
- **Evidence Integrity**: Missing or unverified evidence must **never** be silently treated as a failed criterion.
- **Attribute Registry & Safety**:
  - Supported attributes are strictly registered in `SUPPORTED_ATTRIBUTES` and categorized as `MERIT_RANKING`, `PROGRAM_ELIGIBILITY`, or `RESTRICTED_SENSITIVE`.
  - Unknown or misspelled attributes fail closed (`UnsupportedAttributeError`).
  - Sensitive attributes (`caste_category`, `caste`, `gender`, `religion`, `disability_status`) require an explicit, non-empty `charter_authorization` string at the criterion or policy level (`DisallowedAttributeError`).
  - *Charter authorization is a technical prerequisite enforcing institutional governance, not a legal clearance declaration.*

### 3.2 Tuition Accounting & Award Allocation
- **Eligibility is Not an Award**: Eligibility does not guarantee funding.
- **Confirmed Awards Only**: Only awards with lifecycle status `CONFIRMED` reduce actual tuition payable. Provisional, pending, eligible, applied, or rejected awards must **never** reduce payable tuition.
- **Strict Priority Enforcement**: Confirmed awards must specify a unique, positive integer priority rank (`priority >= 1`). Missing or tied priorities raise `MissingAwardPriorityError` or `TiedAwardPriorityError`. Arbitrary fallback ordering is prohibited.
- **Incompatible Awards**: Mutually exclusive confirmed awards raise `IncompatibleAwardsError`.
- **Independent Balance Tracking**:
  - `gross_eligible_tuition`: Starting tuition amount.
  - `institutional_cap_applied`: Effective waiver limit under institutional policies.
  - `total_effective_reduction`: Sum of actual reductions applied by confirmed awards.
  - `remaining_payable_tuition`: Net amount payable by the student.
  - `remaining_waiver_allowance`: Remaining room under the institutional waiver cap.
  - `total_unapplied_surplus`: Amount by which awards exceed tuition or caps.
- **Surplus Semantics**: Unapplied surplus is **not** cash, not a living-expense stipend, and not a refund to the student.
- **Monetary Precision**: All currency math uses `Decimal`, explicit finite-value validation (`validate_finite_decimal`), and `ROUND_HALF_UP` quantization to two decimal places (`0.01`).

---

## 4. Phase 1C Persistence Audit & Proposed Scope

Phase 1C was audited and assessed as **`READY WITH BLOCKERS`**. It is currently **proposed and awaiting explicit implementation approval**.

### 4.1 Identified Blockers
1. **Dependency & Environment Setup**: The local development environment requires a dedicated Python virtual environment to run database tests and migrations cleanly.
2. **Empty Migration History**: Alembic has no initial baseline revision. A safe initial migration must be established against a disposable PostgreSQL instance.
3. **Model & Domain Contract Gaps**: The existing scaffold models (`backend/app/models/`) do not yet represent:
   - Versioned scholarship policy catalogs and individual criteria definitions.
   - Award lifecycle specifications and multi-award priority allocations.
   - Criterion-level evaluation breakdown snapshots (`CriterionEvaluation`).
   - Detailed tuition accounting balance records (`TuitionAccountSummary`).
   - Frozen input snapshots required for historical reproducibility.

### 4.2 Proposed Phase 1C Sub-Milestones
- **Phase 1C.1 — Persistence Foundation**:
  - Establish isolated Python environment and migration tooling.
  - Align SQLAlchemy models with approved domain contracts.
  - Generate and verify the initial Alembic migration against a disposable test database.
  - Preserve all 40 Phase 1B domain unit tests.
- **Phase 1C.2 — Domain Persistence & Repositories**:
  - Implement bidirectional adapters between domain dataclasses and ORM models.
  - Implement repository boundaries for policy retrieval and assessment persistence.
  - Persist frozen evaluation snapshots and detailed tuition account balances.
  - Verify PostgreSQL persistence round-trips.

*API exposure, JWT authentication, RBAC, frontend integration, and OCR pipelines remain strictly outside Phase 1C.*

---

## 5. Non-Negotiable Core Principles

1. **Deterministic Logic Owns Calculations**: Python domain logic owns all eligibility rules and tuition accounting. The AI model **never** calculates scores, changes decisions, or overrides calculations.
2. **The AI Recommends; Humans Decide**: All system determinations are non-binding recommendations. Authorized human reviewers (university/bank officers) retain final decision authority.
3. **Evidence Distinction**: OCR extraction is not verification. Unverified evidence is pending, not failed.
4. **Reproducibility**: Historical assessments must eventually be reproducible from frozen input snapshots, policy versions/checksums, and engine versions.
5. **Zero External Dependencies in Domain Core**: `backend/app/domain/` must remain pure Python. Never import FastAPI, SQLAlchemy, Pydantic, or external libraries into the domain package.

---

## 6. Codebase Conventions & Guidelines

### Backend Conventions
- **Domain Layer (`backend/app/domain/`)**: Pure Python 3.10+, dataclasses, enums, Decimal arithmetic, custom domain exceptions.
- **Persistence Layer (`backend/app/models/`)**: SQLAlchemy 2 declarative models using `Mapped[...]` and `mapped_column(...)`.
- **API Layer (`backend/app/routers/`)**: Thin routers validating requests with Pydantic schemas, delegating to business services, and returning structured envelopes.
- **Testing**:
  - Domain tests must remain executable via standard library `unittest` (`PYTHONPATH=. python3 -m unittest discover -s tests/unit`).
  - Integration tests use `pytest` and test databases. Never run tests against production databases.

### Frontend Conventions
- **Component Architecture**: Reusable UI components in `src/components/`, pages in `src/pages/`, client API hooks in `src/hooks/`.
- **Styling**: Tailwind CSS + shadcn/ui. Accessible, high-contrast, modern interface.
- **API Layer**: Centralized API client modules in `src/services/` with strict TypeScript types (`src/types/`).

---

## 7. Change Boundary Rules

When working on documentation:
- **Allowed**: Editing Markdown files in `docs/` and root `README.md`, updating diagrams, fixing broken documentation links, correcting commands.
- **Forbidden**: Modifying application source code (`.py`, `.ts`, `.tsx`), SQL migrations, lockfiles, `.env` files, or dependency manifests without explicit task authorization.
