# FairExplain AI

**An Explainable AI platform for student financing — deterministic scholarship eligibility, tuition accounting, and loan-need evaluation, with a human always in the loop.**

---

## 1. Executive Summary

FairExplain AI addresses a fundamental disconnect in higher-education financing: the separation between scholarship eligibility and education loan assessment. Students often apply for loans without knowing whether they qualify for institutional or program scholarships that could substantially reduce their tuition burden. Furthermore, traditional financing decisions are often delivered as opaque "black boxes" with minimal actionable explanation.

FairExplain AI unites these evaluations under a **deterministic domain core** and an **explainable AI layer**:

1. **Deterministic Scholarship Eligibility**: Evaluates applicant attributes against institution-configured criteria with strict attribute safety and clear three-state outcomes (`ELIGIBLE`, `INELIGIBLE`, `PENDING_EVIDENCE`).
2. **Tuition Accounting Engine**: Allocates confirmed scholarship awards against gross eligible tuition, applies institutional and program caps, tracks remaining payable tuition and waiver allowances independently, and calculates unapplied surplus with monetary precision.
3. **AI-Assisted Explanation (Planned)**: Translates deterministic outcomes into transparent, plain-English explanations with confidence framing and fairness auditing.
4. **Human-in-the-Loop Governance**: The system provides auditable recommendations and accounting calculations; an authorized human reviewer (university financial aid officer or bank underwriter) retains final decision authority.

> **Guiding Principle:** *The deterministic engine calculates. The AI explains. The human decides.*

---

## 2. Implementation Status Summary

The project is structured into verified development phases. source code and executable tests serve as the sole authority for implementation claims.

| Phase | Description | Status | Verified Details |
|---|---|---|---|
| **Phase 1A** | **Scaffolding & Prototype** | **Scaffolded** | FastAPI async backend scaffold, initial SQLAlchemy 2 models, and React + Vite prototype with mock data. |
| **Phase 1B** | **Deterministic Domain Core** | **Implemented & Tested** | Merged into `main` via PR #5 (commit `72d0a03`). Pure Python business logic in `backend/app/domain/` with zero external dependencies. **40/40 unit tests passing** via standard library `unittest`. |
| **Phase 1C** | **Persistence & Data Layer** | **Proposed (Ready with Blockers)** | Audit completed. Proposed sub-milestones: 1C.1 (Persistence foundation & initial Alembic migration) and 1C.2 (Domain persistence adapters & round-trip tests). Awaiting explicit implementation approval. |
| **Phase 2** | **Business API Endpoints** | **Planned** | FastAPI routers for `/application`, `/scholarship`, `/loan` (scaffolded in `backend/app/api/router.py`, currently commented out). |
| **Phase 3** | **OCR & Document Verification** | **Planned** | Server-side document upload, OCR extraction, and automated cross-check against self-reported data. |
| **Phase 4** | **LLM Explanation Layer** | **Planned** | Structured prompt contract translating deterministic domain outputs into plain-English explanations. |
| **Phase 5** | **Fairness Audit & Screening** | **Planned** | Proxy-attribute audit screening explanation outputs for indirect bias. |
| **Phase 6** | **Reporting & PDF Generation** | **Planned** | Downloadable summary reports combining audit logs, domain calculations, and human-review notices. |
| **Phase 7** | **Admin Dashboard & Analytics** | **Planned** | Institutional review queues, application volume metrics, and approval distribution tracking. |
| **Phase 8** | **Production Deployment** | **Planned** | Deployment configurations for Vercel (frontend), Railway (backend), and PostgreSQL. |

---

## 3. Verified Phase 1B Domain Core Architecture

The completed Phase 1B domain core (`backend/app/domain/`) implements deterministic business logic in pure Python without dependencies on database engines, web frameworks, or AI providers:

### 3.1 Scholarship Eligibility Engine (`backend/app/domain/eligibility.py`)
- **Separation of Filtering from Ranking**: Phase 1B implements binary and multi-attribute eligibility filtering against explicit institutional criteria. Merit ranking is a separate downstream process.
- **Three-State Outcomes**:
  - `ELIGIBLE`: All mandatory criteria are satisfied and all required evidence is verified.
  - `INELIGIBLE`: One or more mandatory criteria failed evaluation.
  - `PENDING_EVIDENCE`: No mandatory criteria failed, but one or more criteria require supporting documentation that is unverified or missing. Missing evidence is never prematurely treated as a failure.
- **Attribute Registry & Safety**:
  - All attributes are validated against `SUPPORTED_ATTRIBUTES` categorized into `MERIT_RANKING`, `PROGRAM_ELIGIBILITY`, and `RESTRICTED_SENSITIVE`. Unknown or misspelled attributes fail closed (`UnsupportedAttributeError`).
  - Sensitive attributes (`caste_category`, `gender`, `religion`, `disability_status`) require an explicit, non-empty program-charter authorization reference at the criterion or policy level (`DisallowedAttributeError`). This is a technical prerequisite enforcing governance, not a legal clearance.

### 3.2 Tuition Accounting Engine (`backend/app/domain/accounting.py`)
- **Confirmed Awards Only**: Only awards with lifecycle status `CONFIRMED` reduce payable tuition. Eligibility or provisional awards are never treated as guaranteed funding.
- **Explicit Priority Enforcement**: Confirmed awards must specify an explicit, positive integer priority rank. Missing or tied priorities raise `MissingAwardPriorityError` or `TiedAwardPriorityError` rather than resorting to arbitrary fallback ordering.
- **Incompatibility Enforcement**: Mutually exclusive confirmed awards raise `IncompatibleAwardsError`.
- **Independent Balance Tracking**:
  - `remaining_payable_tuition`: Actual balance the student must pay.
  - `remaining_waiver_allowance`: Institutional allowance remaining under institutional caps.
  - `unapplied_surplus`: Surplus resulting from program or institutional caps; explicitly tracked and never automatically converted to cash, living stipends, or student refunds.
- **Monetary Precision**: All monetary values are validated using `Decimal`, rejection of non-finite values (NaN, infinities, booleans), and quantized using `ROUND_HALF_UP` to two decimal places (`0.01`).

---

## 4. Repository Structure

```
FairExplain-AI/
├── backend/
│   ├── alembic/                 # Database migrations (Alembic environment; revisions pending Phase 1C)
│   ├── app/
│   │   ├── api/                 # API router registry (feature routers scaffolded)
│   │   ├── config/              # Pydantic application settings (settings.py)
│   │   ├── core/                # Logging, exception handlers, dependencies
│   │   ├── db/                  # Async SQLAlchemy session and base models
│   │   ├── domain/              # Pure Python deterministic domain core (Phase 1B completed)
│   │   │   ├── __init__.py      # Public domain exports
│   │   │   ├── accounting.py    # Tuition accounting calculation engine
│   │   │   ├── eligibility.py   # Scholarship eligibility filter engine
│   │   │   ├── enums.py         # Domain enumerations (operators, outcomes, statuses)
│   │   │   ├── exceptions.py    # Domain exception hierarchy
│   │   │   └── models.py        # Immutable domain models, registry & validation
│   │   ├── middleware/          # Request logging and middleware
│   │   ├── models/              # SQLAlchemy 2 ORM models (initial scaffold)
│   │   ├── repositories/        # Database repositories (scaffolded)
│   │   ├── routers/             # Active routers (health.py implemented)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── main.py              # FastAPI application bootstrap and lifespan
│   ├── tests/
│   │   ├── unit/                # Pure Python unit tests (Phase 1B)
│   │   │   ├── test_eligibility_filter.py  # 22 tests for eligibility filtering
│   │   │   └── test_tuition_accounting.py  # 18 tests for tuition accounting
│   │   ├── conftest.py          # Pytest fixtures
│   │   └── test_health.py       # Health endpoint integration test
│   ├── pyproject.toml           # Project configuration
│   └── requirements.txt         # Backend Python dependencies
├── frontend/                    # React + Vite + TypeScript client
│   ├── src/
│   │   ├── components/          # UI components (shadcn/ui, results, forms)
│   │   ├── data/                # Mock data fixtures (mock-data.ts)
│   │   ├── hooks/               # React hooks
│   │   ├── pages/               # Application pages (dashboard, forms, results)
│   │   ├── services/            # Client API services (currently backed by mock data)
│   │   └── types/               # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
├── docs/                        # Comprehensive technical documentation
│   ├── ARCHITECTURE.md          # System architecture and layer boundaries
│   ├── CONTEXT.md               # Problem statement and solution rationale
│   ├── DATA_MODEL.md            # Entity models and Phase 1C persistence design
│   ├── PRD.md                   # Product requirements document
│   ├── PROJECTCONTEXT.md        # AI agent instructions, constraints & conventions
│   ├── PROMPTS.md               # LLM explanation prompt contracts
│   ├── README.md                # Documentation index and overview
│   ├── ROADMAP.md               # Phased development roadmap
│   ├── RULE_ENGINE.md           # Domain logic specifications
│   └── SRS.md                   # Software requirements specification
├── .gitignore
└── README.md                    # Project overview and entry point (this file)
```

---

## 5. Setup and Testing Instructions

### 5.1 Running Domain Unit Tests (Phase 1B)
The Phase 1B domain core has zero external dependencies and runs using standard Python 3.10+ without installing third-party packages:

```bash
# Navigate to backend directory
cd backend

# Execute all 40 unit tests using standard library unittest
PYTHONPATH=. python3 -m unittest discover -s tests/unit
```

Expected result:
```
........................................
----------------------------------------------------------------------
Ran 40 tests in 0.001s

OK
```

### 5.2 Running the Backend Scaffold (Requires Dependencies)
When third-party dependencies are installed:

```bash
cd backend

# Optional: Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access health check
curl http://localhost:8000/health
```

### 5.3 Running the Frontend Prototype
```bash
cd frontend

# Install client packages
npm install

# Start Vite dev server
npm run dev
```

The frontend client launches on `http://localhost:5173/` using mock data.

---

## 6. Documentation Index

For detailed specifications, consult the documents in [`docs/`](./docs/):

| Document | Purpose |
|---|---|
| [`docs/PROJECTCONTEXT.md`](./docs/PROJECTCONTEXT.md) | **Essential for AI agents & contributors** — Architectural rules, non-negotiable constraints, and coding standards. |
| [`docs/ROADMAP.md`](./docs/ROADMAP.md) | Phased implementation plan, verified deliverables, and acceptance criteria. |
| [`docs/RULE_ENGINE.md`](./docs/RULE_ENGINE.md) | Technical specification for deterministic eligibility filtering and tuition accounting. |
| [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) | System components, layer boundaries, and request lifecycle. |
| [`docs/DATA_MODEL.md`](./docs/DATA_MODEL.md) | Entity relationships, database schemas, and Phase 1C persistence mapping. |
| [`docs/SRS.md`](./docs/SRS.md) | Software Requirements Specification and traceability. |
| [`docs/PRD.md`](./docs/PRD.md) | Product Requirements Document, user personas, and target metrics. |
| [`docs/PROMPTS.md`](./docs/PROMPTS.md) | LLM prompt specification, input contracts, and explanation schemas. |
| [`docs/CONTEXT.md`](./docs/CONTEXT.md) | Domain background, financing disconnect, and solution framing. |

---

## 7. Responsible AI and Legal Disclaimer

1. **Non-Binding Recommendations**: FairExplain AI generates recommendations and decision-support calculations only. It does not issue legally binding scholarship grants, loan approvals, or disbursements.
2. **Human Authority**: All financing decisions must be reviewed and executed by authorized human personnel at the relevant educational institution, financial institution, or scholarship agency.
3. **Sensitive Attribute Governance**: Program-charter authorization strings configured in eligibility criteria represent technical compliance flags required by the domain engine. They do not constitute formal legal clearance or statutory compliance declarations.
