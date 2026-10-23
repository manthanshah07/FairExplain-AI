# Development Roadmap & Implementation Status

This document defines the phased engineering roadmap for FairExplain AI. It tracks verified deliverables, exit criteria, and implementation status across all development milestones.

---

## 1. Roadmap Overview & Status Matrix

| Phase | Milestone | Status | Key Deliverable | Verified Exit Criteria |
|---|---|---|---|---|
| **Phase 1A** | **Scaffolding & Prototype** | **Scaffolded** | FastAPI async app structure, SQLAlchemy 2 ORM models, React + Vite UI prototype. | Prototype navigable with mock data; `/health` endpoint responding. |
| **Phase 1B** | **Deterministic Domain Core** | **Completed & Merged** | Pure Python eligibility filter and tuition accounting engine (`backend/app/domain/`). | **40/40 unit tests passing** via standard library `unittest` (PR #5, commit `72d0a03`). |
| **Phase 1C** | **Persistence & Data Layer** | **Proposed (Ready with Blockers)** | Align persistence models with Phase 1B domain contracts; Alembic baseline migration; repository adapters. | Schema created via Alembic; persistence round-trip tests passing against PostgreSQL; Phase 1B tests preserved. |
| **Phase 2** | **Business API Services** | **Planned** | FastAPI endpoints for `/api/v1/application`, `/scholarship`, and `/loan` connected to domain services. | End-to-end HTTP request/response validation with Pydantic schemas; full error handling. |
| **Phase 3** | **OCR & Document Verification** | **Planned** | Server-side document processing, text extraction, and cross-verification against self-reported data. | Automated mismatch flagging; missing evidence mapped to `PENDING_EVIDENCE`. |
| **Phase 4** | **LLM Explanation Layer** | **Planned** | Grounded explanation generation via Gemini/OpenAI implementing structured prompt contract. | 100% of assessments generate valid JSON explanations; LLM never computes or overrides scores. |
| **Phase 5** | **Fairness Audit & Screening** | **Planned** | Automated proxy-attribute screening auditing explanation outputs for indirect bias. | Sensitive attributes and proxies flagged for human review; audit logged. |
| **Phase 6** | **Reporting & PDF Generation** | **Planned** | Downloadable PDF reports combining domain accounting, explanation, and human-review notice. | PDF generation service operational; complete audit trail embedded. |
| **Phase 7** | **Admin Review & Analytics** | **Planned** | Institutional reviewer queues and administrative analytics dashboard. | Review queue operational with decision recording; dashboard displaying cohort metrics. |
| **Phase 8** | **Release & Production** | **Planned** | Production deployment on Vercel, Railway, and managed PostgreSQL with full end-to-end verification. | Production environment operational; security, privacy, and compliance checks passed. |

---

## 2. Milestone Details & Verification

### Phase 1A — Project Scaffolding & Initial Prototype
- **Status:** Scaffolded & Merged
- **Scope:**
  - Setup FastAPI backend with structured logging, CORS, error handling, and `/health` router.
  - Setup SQLAlchemy 2 async database connection configuration and base declarative models.
  - Setup React + Vite + TypeScript frontend with Tailwind CSS and shadcn/ui component library.
  - Create interactive mock application flow and results presentation using synthetic data (`mock-data.ts`).
- **Exit Criteria:** Backend boots and passes health checks; frontend renders core application views.

### Phase 1B — Deterministic Domain Core
- **Status:** **Completed & Merged into `main`** (Commit `72d0a03`, PR #5)
- **Scope:**
  - Implement pure Python scholarship eligibility filtering engine (`backend/app/domain/eligibility.py`):
    - Binary and multi-attribute evaluation against institution-configured criteria.
    - Three-state outcomes: `ELIGIBLE`, `INELIGIBLE`, and `PENDING_EVIDENCE`.
    - Mandatory vs. optional criteria semantics.
    - Supported attribute registry (`SUPPORTED_ATTRIBUTES`) and purpose classification.
    - Sensitive attribute governance requiring explicit `charter_authorization`.
  - Implement deterministic tuition accounting engine (`backend/app/domain/accounting.py`):
    - Confirmed award allocation against gross tuition in strictly ascending priority order.
    - Explicit priority enforcement; missing or tied priorities raise explicit exceptions.
    - Detection and rejection of incompatible confirmed awards.
    - Institutional waiver caps and program-level caps.
    - Independent tracking of `remaining_payable_tuition` and `remaining_waiver_allowance`.
    - Monetary arithmetic using `Decimal`, finite-value validation, and `ROUND_HALF_UP` quantization (`0.01`).
    - Unapplied surplus calculation and reporting (never treated as cash or student stipend).
- **Exit Criteria:** 40 unit tests passing with zero external dependencies (`PYTHONPATH=. python3 -m unittest discover -s tests/unit`).

### Phase 1C — Persistence & Data Layer (Proposed)
- **Status:** **Proposed / Awaiting Implementation Approval** (Audited as `READY WITH BLOCKERS`)
- **Audit Findings:** Dependency environment setup, empty Alembic migration directory, and schema gaps between initial scaffold models and Phase 1B domain contracts.
- **Proposed Sub-Milestones:**
  - **Phase 1C.1 — Persistence Foundation**:
    - Establish isolated Python development environment.
    - Align database models with Phase 1B domain contracts (policy catalog, criteria, award specifications, account summaries).
    - Generate and verify initial Alembic baseline migration against a dedicated disposable PostgreSQL database.
    - Preserve all 40 Phase 1B domain unit tests.
  - **Phase 1C.2 — Domain Persistence Adapters & Repositories**:
    - Build bidirectional mapping between domain dataclasses and ORM models.
    - Implement repository interfaces for policy retrieval and assessment persistence.
    - Persist frozen evaluation snapshots and detailed tuition account balances for reproducibility.
    - Validate persistence round-trips against PostgreSQL.
- **Exit Criteria:** Clean Alembic migration history; schema verification tests passing; persistence round-trips verified without regressions in Phase 1B domain tests.

### Phase 2 — Business API Services & Integration (Planned)
- **Status:** Planned
- **Scope:**
  - Implement FastAPI routers for application submission, scholarship evaluation, and loan assessment.
  - Connect HTTP endpoints to business services and domain repositories.
  - Validate all request payloads using Pydantic schemas.
  - Implement consistent structured error envelopes.
- **Exit Criteria:** Endpoints tested via integration tests; frontend services wired to live backend API.

### Phase 3 — Document Processing & OCR Cross-Checking (Planned)
- **Status:** Planned
- **Scope:**
  - Implement secure document upload endpoint supporting PDFs and images.
  - Integrate server-side OCR service for key field extraction (marksheets, income proofs).
  - Cross-verify extracted fields against self-reported applicant attributes.
  - Flag mismatches and map missing/unverified documents to `PENDING_EVIDENCE` status.
- **Exit Criteria:** OCR pipeline functional; mismatches routed to human review.

### Phase 4 — LLM Explanation Layer & Grounded Reasoning (Planned)
- **Status:** Planned
- **Scope:**
  - Implement `/explanation` backend service implementing the prompt contract in [PROMPTS.md](./PROMPTS.md).
  - Convert pre-computed domain evaluation results and accounting summaries into plain-English explanations.
  - Enforce strict system prompt guardrails: AI never calculates, alters, or overrides numerical scores or eligibility statuses.
- **Exit Criteria:** Schema-valid JSON explanations generated for 100% of assessed applications.

### Phase 5 — Fairness Audit & Proxy Screening (Planned)
- **Status:** Planned
- **Scope:**
  - Implement runtime Fairness Checker auditing generated explanations for indirect proxy bias (pincode, surname, demographic proxies).
  - Route flagged explanations to human reviewer queue.
  - Log all fairness screening events to immutable audit trail.
- **Exit Criteria:** Zero sensitive or proxy attributes leak into published explanations; flagged cases successfully routed to human review.

### Phase 6 — Reporting & PDF Generation (Planned)
- **Status:** Planned
- **Scope:**
  - Build PDF generation service compiling applicant inputs, domain calculations, explanation text, and human-review notices.
  - Embed cryptographic audit checksum and policy versions for reproducibility.
- **Exit Criteria:** Downloadable PDF report generated with complete assessment breakdown.

### Phase 7 — Administrative Review Queue & Analytics Dashboard (Planned)
- **Status:** Planned
- **Scope:**
  - Implement human reviewer queue for institutional and banking officers.
  - Build administrative analytics dashboard tracking cohort volume, eligibility distribution, and fairness flags.
- **Exit Criteria:** Authorized reviewers can inspect, approve, or override recommendations with audit logging.

### Phase 8 — Production Hardening & Release (Planned)
- **Status:** Planned
- **Scope:**
  - Deploy frontend to Vercel and backend to Railway with managed PostgreSQL.
  - Enforce HTTPS, encryption at rest for sensitive financial data, and secure secret management.
  - Perform end-to-end regression and load testing.
- **Exit Criteria:** Full platform operational in production; compliance and security checklist verified.

---

## 3. Engineering Dependencies & Invariants

1. **Deterministic Core Invariant**: `backend/app/domain/` has zero external dependencies and must remain completely decoupled from database models, web frameworks, and external APIs.
2. **Persistence Boundary**: Phase 1C persistence must consume domain models via adapters; domain models must never import ORM entities or database sessions.
3. **AI Boundary**: The LLM Explanation Layer consumes domain outputs; it never provides inputs to the domain core or calculates financial figures.
4. **Human Authority**: The system provides decision-support calculations and explainable recommendations; authorized humans make all binding decisions.
