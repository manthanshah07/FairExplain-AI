# FairExplain AI — Master Implementation Roadmap & Autonomous Execution Guide

This document is the authoritative engineering roadmap and autonomous execution specification for **FairExplain AI**. It is designed so that any AI software engineering agent (or human engineer) can take any individual Phase—given **only** the phase name (e.g., *"Implement Phase 1C"* or *"Execute Phase 2"*)—and deliver the phase end-to-end with zero ambiguity, zero regressions, complete Git/GitHub lifecycle management, and maximum software engineering rigor.

---

## 1. System Mission & Core Architectural Invariants

FairExplain AI is an explainable, deterministic education financing platform that evaluates scholarship eligibility, computes post-scholarship tuition balances, screens for proxy bias, generates grounded plain-English explanations, and orchestrates human-in-the-loop decision governance.

Every phase must strictly uphold the following **non-negotiable invariants**:

1. **Deterministic Core Purity**:
   - `backend/app/domain/` has **zero external dependencies** (no FastAPI, no SQLAlchemy, no Pydantic, no OpenAI/Gemini SDKs).
   - All monetary arithmetic uses standard library `Decimal`, finite-value validation (`validate_finite_decimal`), and `ROUND_HALF_UP` quantization to `0.01` (`quantize_currency`). Booleans and floats are strictly rejected in financial math.
2. **Authority & Decision Boundary**:
   - **Calculations**: Owned exclusively by the deterministic domain core. AI models **never** calculate eligibility, award amounts, or affordability scores.
   - **Explanations**: The AI layer translates pre-computed domain outputs into plain English. It cannot override, modify, or invent missing financial or academic facts.
   - **Decisions**: The system provides decision-support calculations and explainable recommendations. Authorized human reviewers (university financial aid officers or bank underwriters) retain sole legal and operational decision authority.
3. **Evidence & Failure Semantics**:
   - Missing or unverified supporting documents produce `PENDING_EVIDENCE`, **never** a failed criterion.
   - OCR extraction is not verification; extracted data requires verified matching against self-reported attributes before transitioning evidence status.
4. **Financial Integrity & Surplus**:
   - Only confirmed awards (`AwardStatus.CONFIRMED`) reduce payable tuition.
   - Award allocations follow strict unique positive integer priorities (`priority >= 1`).
   - Unapplied surplus is tracked for accounting transparency and is **never** treated as cash, living allowances, or cash refunds to students.
5. **Fairness & Demographic Governance**:
   - Sensitive attributes (`caste_category`, `caste`, `gender`, `religion`, `disability_status`) require explicit, non-empty `charter_authorization`.
   - Explanations must never cite protected demographic attributes or known proxy variables (e.g., pincodes, surnames).

---

## 2. Master Roadmap & Milestone Status Matrix

| Phase | Milestone | Status | Key Deliverables | Verification Command & Exit Criteria |
|---|---|---|---|---|
| **Phase 1A** | **Scaffolding & Prototype** | **Completed** | FastAPI async app structure, initial ORM models, React + Vite UI prototype. | Prototype navigable with mock data; `/health` returns `200 OK`. |
| **Phase 1B** | **Deterministic Domain Core** | **Completed & Merged** | Pure Python eligibility filter and tuition accounting engine (`backend/app/domain/`). | **40/40 unit tests passing** via `PYTHONPATH=. python3 -m unittest discover -s tests/unit` (PR #5, Commit `72d0a03`). |
| **Phase 1C** | **Persistence & Data Layer** | **Ready to Execute** | Domain-aligned SQLAlchemy models, Alembic baseline migration, bidirectional mappers, and repository layer. | Clean Alembic migration; persistence round-trip tests passing against PostgreSQL; 40 Phase 1B unit tests untouched and passing. |
| **Phase 2** | **Business API Services & Loan Engine** | **Planned** | Loan affordability domain engine, Pydantic v2 schemas, FastAPI routers (`/application`, `/scholarship`, `/loan`), and frontend API integration. | Pytest integration suite passing; end-to-end HTTP request/response validation with structured error envelopes. |
| **Phase 3** | **OCR & Document Verification** | **Planned** | Secure document upload, pluggable OCR extraction engine, cross-verification matching, and `PENDING_EVIDENCE` transitions. | Document upload tested; cross-check identifies matching and discrepant fields; missing documents route to `PENDING_EVIDENCE`. |
| **Phase 4** | **LLM Explanation Layer** | **Planned** | Grounded explanation service implementing `docs/PROMPTS.md` contract with Gemini/OpenAI, zero-calculation validation, and JSON schemas. | 100% valid JSON explanations generated; domain amounts verified untouched; disclaimer present in all outputs. |
| **Phase 5** | **Fairness Audit & Proxy Screening** | **Planned** | Automated proxy screening engine (pincode, surname, demographic checks), audit telemetry logger, and review queue routing. | Zero sensitive attributes or proxies leak into published explanations; flagged cases successfully routed to `needs_review`. |
| **Phase 6** | **Reporting & Cryptographic PDF** | **Planned** | Downloadable PDF report compilation with ReportLab/WeasyPrint, embedded SHA-256 audit hash, and policy versioning. | Valid PDF generated matching UI assessment; cryptographic checksum verifies against stored audit logs. |
| **Phase 7** | **Admin Review Queue & Analytics** | **Planned** | Officer review queue with override audit logging, institutional analytics aggregations, and live frontend dashboard. | Reviewers can inspect and approve/override determinations; dashboard aggregates real-time cohort volume and fairness metrics. |
| **Phase 8** | **Production Hardening & Release** | **Planned** | Multi-stage Docker packaging, Railway/Vercel configuration, rate limiting, connection pooling, and E2E smoke tests. | Complete platform operational in staging/production environments; security and compliance checklist verified. |

---

## 3. Git & GitHub Engineering Protocol

Every autonomous agent working on FairExplain AI must adhere to standard Git and GitHub workflows to maintain a pristine, bisectable commit history and automated verification trail.

### 3.1 Branching Strategy
- **Never commit directly to `main`**.
- Branch off the latest `origin/main`:
  ```bash
  git checkout main
  git pull origin main
  git checkout -b feature/<phase-id>-<short-slug>
  ```
- **Standard Branch Naming Convention**:
  - Phase 1C: `feature/phase-1c-persistence`
  - Phase 2: `feature/phase-2-business-apis`
  - Phase 3: `feature/phase-3-ocr-verification`
  - Phase 4: `feature/phase-4-llm-explanations`
  - Phase 5: `feature/phase-5-fairness-audit`
  - Phase 6: `feature/phase-6-pdf-reporting`
  - Phase 7: `feature/phase-7-admin-portal`
  - Phase 8: `feature/phase-8-production-release`
  - Bug fixes: `fix/<short-slug>`
  - Documentation/Refactor: `docs/<short-slug>` or `refactor/<short-slug>`

### 3.2 Commit Hygiene & Conventional Commits
- Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
  ```
  <type>(<scope>): <short imperative subject>

  [optional multi-line body detailing context, design decisions, and invariant compliance]
  ```
- **Permitted Types**: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `ci`.
- **Permitted Scopes**: `domain`, `persistence`, `api`, `ocr`, `llm`, `fairness`, `reporting`, `admin`, `infra`, `ui`.
- **Pre-commit Cleanliness Gate**:
  - Never stage secret files (`.env`, `.env.local`), database storage files (`*.db`, `*.sqlite`), bytecode (`__pycache__`, `*.pyc`), test artifacts (`.pytest_cache`), or OS junk (`.DS_Store`).
  - Stage specific files explicitly: `git add <file1> <file2>`, avoiding indiscriminate `git add .`.

### 3.3 GitHub Pull Request (PR) Protocol
When all unit, integration, and lint checks pass, submit the pull request using the GitHub CLI (`gh`):
```bash
# 1. Push branch to remote
git push -u origin <branch-name>

# 2. Open Pull Request with structured template
gh pr create \
  --title "feat(<scope>): implement <Phase ID> — <Milestone Title>" \
  --body "$(cat << 'EOF'
## Phase Overview
- **Phase Milestone**: Phase <X> (<Title>)
- **Status**: Implemented & Verified End-to-End

## Summary of Deliverables
- Key component 1...
- Key component 2...

## Verification & Test Results
- Unit Tests: XX/XX passing (`command`)
- Integration Tests: XX/XX passing (`command`)
- Linter / Typing: Clean (`npm run lint`, `ruff check`)

## Architectural Invariants Verified
- [x] Deterministic core purity maintained (no external dependencies in domain)
- [x] Finite monetary arithmetic with Decimal and ROUND_HALF_UP (0.01)
- [x] Authority boundaries strictly respected (domain calculates, LLM explains, humans decide)
- [x] Zero sensitive/proxy attributes leaked
- [x] No credentials or secrets committed
EOF
)"
```

### 3.4 Merge & Post-Merge Protocol
1. Verify CI status: `gh pr checks`
2. Merge via Squash and Merge (or project standard): `gh pr merge --squash --delete-branch`
3. Return to local `main` and sync:
   ```bash
   git checkout main
   git pull origin main
   ```
4. Update Section 2 Status Matrix in `docs/ROADMAP.md` to reference the merged commit SHA / PR number.

---

## 4. Autonomous Execution Specifications by Phase

Each section below contains the complete, self-contained implementation specification for an agent assigned to that milestone.

---

### Phase 1C: Persistence & Data Layer

#### 1. Objective & Scope
Transition FairExplain AI from in-memory mocks to an enterprise-grade async PostgreSQL persistence layer. You must bridge the gap between the initial scaffold models in `backend/app/models/` and the merged Phase 1B domain contracts (`backend/app/domain/`), create clean Alembic migrations, and provide bidirectional domain-to-ORM repositories.

#### 2. Architecture & File Locations
- **Existing Models to Align**:
  - `backend/app/models/user.py`
  - `backend/app/models/application.py`
  - `backend/app/models/academic_record.py`
  - `backend/app/models/financial_profile.py`
  - `backend/app/models/uploaded_document.py`
  - `backend/app/models/audit_log.py`
- **New Persistence Models to Create**:
  - `backend/app/models/policy.py`: `ScholarshipPolicyModel`, `EligibilityCriterionModel`
  - `backend/app/models/award.py`: `AwardSpecificationModel`, `InstitutionalCapModel`
  - `backend/app/models/evaluation.py`: `ScholarshipEvaluationModel`, `CriterionEvaluationSnapshotModel`, `TuitionAccountSummaryModel`, `AwardAllocationModel`
- **Adapters & Repositories**:
  - `backend/app/repositories/base.py`: Generic async CRUD repository
  - `backend/app/repositories/policy_repository.py`: Policy and criteria queries
  - `backend/app/repositories/application_repository.py`: Application aggregate persistence
  - `backend/app/repositories/evaluation_repository.py`: Evaluation and accounting snapshot persistence
  - `backend/app/repositories/mappers.py`: Pure bidirectional mapping between domain dataclasses and ORM models
- **Database & Migrations**:
  - `backend/alembic/env.py`
  - `backend/alembic/versions/0001_initial_schema.py`

#### 3. Step-by-Step Implementation Tasks
1. **Align & Create ORM Models**:
   - Ensure all models inherit from `Base`, `UUIDPrimaryKeyMixin`, and `TimestampMixin` from `app.db.base`.
   - Use `Numeric(14, 2)` for monetary values (matching `Decimal` precision).
   - Use `VARCHAR` or `Enum` matching domain enums (`EligibilityStatus`, `CriterionOperator`, `AwardStatus`, `AwardType`, `EvidenceStatus`).
   - Add foreign keys, cascading rules, and unique constraints:
     - `scholarship_policies`: `(code, version)` must be unique.
     - `eligibility_criteria`: `policy_id` FK → `scholarship_policies.id` on delete CASCADE.
     - `scholarship_evaluations`: `application_id` FK, `policy_id` FK, frozen input snapshot (`JSONB`), overall status.
     - `criterion_evaluations`: `evaluation_id` FK, `criterion_id`, attribute, operator, target/actual values, status, reason.
     - `tuition_account_summaries`: `application_id` FK, gross tuition, cap applied, net payable tuition, surplus.
     - `award_allocations`: `account_summary_id` FK, award ID, priority rank, nominal amount, effective reduction, unapplied surplus.
2. **Implement Bidirectional Mappers (`backend/app/repositories/mappers.py`)**:
   - `domain_to_orm_policy(policy: ScholarshipPolicy) -> ScholarshipPolicyModel`
   - `orm_to_domain_policy(model: ScholarshipPolicyModel) -> ScholarshipPolicy`
   - `domain_to_orm_evaluation(result: EligibilityEvaluationResult, app_id: UUID) -> ScholarshipEvaluationModel`
   - `domain_to_orm_accounting(summary: TuitionAccountSummary, app_id: UUID) -> TuitionAccountSummaryModel`
   - Ensure `Decimal` conversion is exact and round-trip conversions are loss-free.
3. **Generate Initial Alembic Migration**:
   - Configure `backend/alembic/env.py` to import `Base` and all models from `app.models`.
   - Generate baseline migration `0001_initial_schema.py` covering all tables: `users`, `applications`, `academic_records`, `financial_profiles`, `uploaded_documents`, `scholarship_policies`, `eligibility_criteria`, `award_specifications`, `scholarship_evaluations`, `criterion_evaluations`, `tuition_account_summaries`, `award_allocations`, `audit_log_entries`.
4. **Implement Repository Layer**:
   - Implement `PolicyRepository` to load active policies by code and version.
   - Implement `ApplicationRepository` with methods: `get_with_relations(app_id)`, `create_application(...)`, `update_status(...)`.
   - Implement `EvaluationRepository` to persist evaluation snapshots and tuition summaries in a single transaction.

#### 4. Edge Cases & Constraints
- Database models must **never** be imported inside `backend/app/domain/`.
- Float values are strictly disallowed in monetary database columns (`Numeric(14, 2)` must map to Python `Decimal`).
- Application state transitions must be guarded (`draft` -> `submitted` -> `needs_review` / `ready_for_report` -> `closed`).

#### 5. Verification & Test Commands
```bash
# 1. Verify Phase 1B unit tests remain 100% intact
cd backend && PYTHONPATH=. python3 -m unittest discover -s tests/unit

# 2. Run Alembic migration against PostgreSQL test database
alembic upgrade head

# 3. Execute repository integration tests
pytest tests/integration/test_repositories.py tests/integration/test_mappers.py
```

#### 6. Git & GitHub Lifecycle Execution
- **Branch**: `git checkout -b feature/phase-1c-persistence`
- **Atomic Commits**:
  - `feat(persistence): align orm models with phase 1b domain contracts`
  - `feat(persistence): implement bidirectional domain mappers`
  - `feat(persistence): add alembic baseline migration`
  - `feat(persistence): implement application and evaluation repositories`
  - `test(persistence): add postgres repository round-trip integration tests`
- **PR Submission**: `gh pr create --title "feat(persistence): implement Phase 1C persistence and data layer" --body "..."`

#### 7. Definition of Done
- [ ] All ORM models reflect Phase 1B domain contracts and existing scaffold entities.
- [ ] Alembic baseline migration generates cleanly and executes up/down without errors.
- [ ] Bidirectional mappers cover all domain models with 100% field parity.
- [ ] Integration tests verify repository persistence and retrieval round-trips against PostgreSQL.
- [ ] All 40 Phase 1B unit tests pass with zero modifications.
- [ ] Pull request created and passing all CI checks.

---

### Phase 2: Business API Services & Integration

#### 1. Objective & Scope
Expose the deterministic domain engines and persistence layer via robust, versioned REST endpoints under `/api/v1`. Implement the deterministic **Loan Affordability Engine** (`backend/app/domain/loan.py`), implement Pydantic v2 validation schemas with structured error envelopes, and wire the React frontend services to consume the live API instead of mock data.

#### 2. Architecture & File Locations
- **Domain Addition**:
  - `backend/app/domain/loan.py`: Pure Python loan affordability assessment
- **Schemas**:
  - `backend/app/schemas/common.py`: Standard API envelope, pagination, metadata
  - `backend/app/schemas/application.py`: Application submission, academic/financial input schemas
  - `backend/app/schemas/scholarship.py`: Scholarship evaluation request/response schemas
  - `backend/app/schemas/loan.py`: Loan assessment request/response schemas
- **Routers & Services**:
  - `backend/app/services/application_service.py`
  - `backend/app/services/scholarship_service.py`
  - `backend/app/services/loan_service.py`
  - `backend/app/routers/applications.py`: `POST /api/v1/application`, `GET /api/v1/application/{id}`
  - `backend/app/routers/scholarship.py`: `POST /api/v1/scholarship/evaluate`
  - `backend/app/routers/loan.py`: `POST /api/v1/loan/assess`
  - `backend/app/api/router.py`: Register and activate all feature routers
- **Frontend Integration**:
  - `frontend/src/services/api.ts`: Replace mock delay stubs with configured Axios/Fetch client
  - `frontend/src/hooks/use-application.ts`: Query hooks for application submission and assessment loading

#### 3. Step-by-Step Implementation Tasks
1. **Implement Deterministic Loan Affordability Engine (`backend/app/domain/loan.py`)**:
   - Follow pure Python domain conventions (zero external dependencies, `Decimal` arithmetic).
   - Core mathematical formulas (per `docs/RULE_ENGINE.md` Section 4.2):
     $$\text{monthly\_income} = \frac{\text{household\_income}}{12}$$
     $$\text{available\_monthly\_capacity} = (\text{monthly\_income} \times 0.40) - \text{existing\_emi}$$
     $$\text{estimated\_emi} = \frac{\text{post\_scholarship\_loan\_amount}}{\text{tenure\_months}}$$
   - Decision Logic:
     - If $\text{estimated\_emi} \le \text{available\_monthly\_capacity} \implies \text{ELIGIBLE}$
     - If $\text{estimated\_emi} \le \text{available\_monthly\_capacity} \times 1.20 \implies \text{NEEDS\_REVIEW}$
     - If $\text{estimated\_emi} > \text{available\_monthly\_capacity} \times 1.20 \implies \text{NOT\_RECOMMENDED}$
   - Write unit tests in `tests/unit/test_loan_affordability.py`.
2. **Pydantic v2 Request/Response Schemas**:
   - Define strict validation: `cgpa` (0.0 to 10.0), percentages (0.0 to 100.0), positive monetary amounts.
   - Enforce consistent JSON error envelope:
     ```json
     {
       "success": false,
       "error": {
         "code": "VALIDATION_ERROR",
         "message": "Human readable summary",
         "details": []
       }
     }
     ```
3. **FastAPI Routers & Business Services**:
   - `POST /api/v1/application`: Creates application, academic record, and financial profile in `draft` or `submitted` status.
   - `POST /api/v1/scholarship/evaluate`: Evaluates eligibility via `evaluate_scholarship_eligibility`, executes tuition accounting via `calculate_tuition_accounting`, and persists snapshots.
   - `POST /api/v1/loan/assess`: Takes post-scholarship net balance, evaluates loan affordability via `loan.py`, and records result.
   - Wire all routes into `backend/app/api/router.py` and register with `app.main:create_app`.
4. **Connect Frontend Client**:
   - Update `frontend/src/services/api.ts` with base URL environment variable (`VITE_API_BASE_URL`).
   - Implement real network calls with error handling and loading indicators in `ApplyPage` and `ResultsPage`.

#### 4. Edge Cases & Constraints
- Division by zero in tenure months must be caught by schema validation (`tenure_months >= 1`).
- Negative monthly capacity (when existing EMI exceeds 40% of income) must result in `NOT_RECOMMENDED`.
- All domain exceptions (`DisallowedAttributeError`, `MissingAwardPriorityError`, etc.) must be caught by FastAPI exception handlers and mapped to appropriate HTTP 400/422 responses.

#### 5. Verification & Test Commands
```bash
# 1. Run loan domain unit tests
PYTHONPATH=. python3 -m unittest discover -s tests/unit

# 2. Run API integration tests
pytest tests/integration/test_application_api.py tests/integration/test_scholarship_api.py tests/integration/test_loan_api.py

# 3. Test frontend build and linting
cd frontend && npm run lint && npm run build
```

#### 6. Git & GitHub Lifecycle Execution
- **Branch**: `git checkout -b feature/phase-2-business-apis`
- **Atomic Commits**:
  - `feat(domain): implement loan affordability scoring engine`
  - `feat(api): define pydantic v2 request and response schemas`
  - `feat(api): implement application scholarship and loan routers`
  - `feat(ui): connect frontend api services to live backend endpoints`
  - `test(api): add integration test suite for v1 endpoints`
- **PR Submission**: `gh pr create --title "feat(api): implement Phase 2 business API services and loan engine" --body "..."`

#### 7. Definition of Done
- [ ] Loan affordability domain engine implemented with complete test coverage in standard library unittest.
- [ ] All FastAPI routers active under `/api/v1` and verified via integration tests.
- [ ] Standardized success/error envelopes across all endpoints.
- [ ] Frontend successfully submits application and loads evaluation results from the live backend API.
- [ ] Pull request created and passing all CI checks.

---

### Phase 3: OCR & Document Verification Pipeline

#### 1. Objective & Scope
Provide automated document intake, secure storage, server-side OCR text extraction, and cross-verification against applicant self-reported data. Transition missing evidence to `PENDING_EVIDENCE` and route mismatches to the human review queue.

#### 2. Architecture & File Locations
- **Backend Infrastructure**:
  - `backend/app/core/storage.py`: Pluggable file storage backend (Local disk for dev, S3/MinIO compatible for prod)
  - `backend/app/services/ocr/base.py`: Abstract OCR provider interface
  - `backend/app/services/ocr/tesseract_provider.py`: Tesseract / PyPDF / pdfplumber extraction adapter
  - `backend/app/services/ocr/extractor.py`: Structured key-value parser for marksheet, income proof, and ID proof
  - `backend/app/services/verification_service.py`: Cross-check engine comparing extracted values with self-reported profile
  - `backend/app/routers/documents.py`: `POST /api/v1/documents/upload`, `GET /api/v1/documents/{id}/status`
- **Frontend Components**:
  - `frontend/src/components/document-uploader.tsx`: Multi-file drag-and-drop uploader with progress and status badge
  - `frontend/src/pages/apply-page.tsx`: Integrated file upload step with instant feedback

#### 3. Step-by-Step Implementation Tasks
1. **Document Upload & Storage Service**:
   - Secure upload endpoint supporting `.pdf`, `.png`, `.jpg`, `.jpeg`.
   - File size limits (max 10MB per file), MIME type validation, and SHA-256 hash generation for deduplication.
   - Create `UploadedDocument` record with status `uploaded`.
2. **Pluggable OCR Extraction Engine**:
   - Create `BaseOCRProvider` protocol with method:
     `async def extract_text(file_bytes: bytes, mime_type: str) -> OCRExtractionResult`
   - Implement structured parser that searches for:
     - **Marksheets**: CGPA, percentage, candidate name, roll number, backlogs count.
     - **Income Certificates**: Annual family income, issuing authority, applicant/parent name, issue date.
     - **ID Proofs**: Identity number (Aadhaar/PAN/National ID mask), name, date of birth.
   - Return structured confidence scores per extracted field (0.00 – 1.00).
3. **Deterministic Cross-Verification Engine**:
   - Implement `VerificationService.verify_application_documents(application_id: UUID)`:
     - Compare extracted `cgpa` vs. self-reported `academic_record.cgpa` (tolerance: $\pm 0.05$).
     - Compare extracted `household_income` vs. self-reported `financial_profile.household_income` (tolerance: $\pm 5\%$).
   - Flag evaluation:
     - If matched: Document evidence status = `VERIFIED`.
     - If mismatch: Set `mismatch_flag = True`, record discrepancy diff in `audit_log`, set application status = `needs_review`.
     - If document missing: Set criterion evidence status = `PENDING_EVIDENCE`.
4. **API Endpoints & Integration**:
   - Implement `POST /api/v1/documents/upload` accepting `multipart/form-data`.
   - Implement `GET /api/v1/documents/application/{id}` returning document statuses and verification logs.

#### 4. Edge Cases & Constraints
- Low OCR confidence (< 0.60) must never fail an applicant; it must trigger `needs_review` for manual verification.
- Tampered or corrupted PDFs must be caught gracefully and return a clear user error.
- Raw documents containing PII must not be written to unencrypted public directories.

#### 5. Verification & Test Commands
```bash
# 1. Test OCR extraction and parser
pytest tests/unit/test_ocr_extractor.py

# 2. Test cross-verification logic (exact match, within tolerance, mismatch, missing document)
pytest tests/unit/test_verification_service.py

# 3. Test document upload endpoint
pytest tests/integration/test_documents_api.py
```

#### 6. Git & GitHub Lifecycle Execution
- **Branch**: `git checkout -b feature/phase-3-ocr-verification`
- **Atomic Commits**:
  - `feat(ocr): implement pluggable ocr provider and key field extractor`
  - `feat(ocr): implement cross-verification service against applicant profile`
  - `feat(api): expose document upload and verification endpoints`
  - `feat(ui): add multi-file document upload component`
  - `test(ocr): add unit and integration tests for document extraction`
- **PR Submission**: `gh pr create --title "feat(ocr): implement Phase 3 OCR and document verification pipeline" --body "..."`

#### 7. Definition of Done
- [ ] Document upload endpoint handles PDFs and images securely with size and MIME checks.
- [ ] OCR service extracts key numerical and text fields with confidence metrics.
- [ ] Cross-verification detects discrepancies and transitions missing documents to `PENDING_EVIDENCE`.
- [ ] Mismatches are flagged and recorded in `AuditLogEntry`.
- [ ] Pull request created and passing all CI checks.

---

### Phase 4: LLM Explanation Layer & Grounded Reasoning

#### 1. Objective & Scope
Implement the explainable AI service that translates deterministic domain evaluations into objective, empathetic, plain-English explanations for students and aid officers. Strictly enforce the prompt contract and JSON schema in `docs/PROMPTS.md`. Enforce that the LLM has **zero calculation authority** and cannot modify scores or statuses.

#### 2. Architecture & File Locations
- **Backend Services**:
  - `backend/app/services/llm/base.py`: Abstract LLM provider interface
  - `backend/app/services/llm/gemini_provider.py`: Google Gemini 1.5 / 2.0 implementation
  - `backend/app/services/llm/openai_provider.py`: OpenAI GPT-4o / GPT-4o-mini implementation
  - `backend/app/services/llm/prompt_templates.py`: System and user prompt templates per `docs/PROMPTS.md`
  - `backend/app/services/explanation_service.py`: Telemetry formatter, model invocation, output schema validation, and guardrails
  - `backend/app/routers/explanation.py`: `POST /api/v1/explanation/generate`, `GET /api/v1/explanation/{application_id}`
- **Frontend Components**:
  - `frontend/src/components/explanation-card.tsx`: Rich UI displaying plain-English reasoning, key factors, next steps, and human governance banner
  - `frontend/src/pages/results-page.tsx`: Mount explanation card

#### 3. Step-by-Step Implementation Tasks
1. **Telemetry Serializer**:
   - Serialize domain `EligibilityEvaluationResult` and `TuitionAccountSummary` into the exact JSON telemetry structure specified in `docs/PROMPTS.md` Section 3.
2. **LLM Provider Integration & Structured Output**:
   - Implement provider utilizing Gemini SDK (`google-genai` or `google-generativeai`) and OpenAI SDK.
   - Enforce JSON response mode matching the exact schema:
     ```json
     {
       "summary": "Plain English summary",
       "eligibility_explanation": "Explanation of criteria outcome",
       "financial_breakdown_explanation": "Explanation of tuition accounting",
       "key_positive_factors": ["Factor 1", "Factor 2"],
       "shortfalls_or_pending_items": ["Shortfall or required document"],
       "next_steps_for_applicant": ["Action 1", "Action 2"],
       "human_review_notice": "Standard disclaimer confirming human authority"
     }
     ```
3. **Zero-Calculation & Anti-Hallucination Guardrail Validator**:
   - Implement validation verifying:
     - LLM did not alter numerical values (gross tuition, net payable tuition, surplus).
     - LLM did not contradict the status (`ELIGIBLE` vs `INELIGIBLE` vs `PENDING_EVIDENCE`).
     - LLM output contains the mandatory human review notice.
   - If validation fails, retry up to 2 times; if still invalid, fall back to a deterministic template-based explanation.
4. **Persistence & API Router**:
   - Store generated explanation in `ExplanationReport` model.
   - Mount router at `/api/v1/explanation`.

#### 4. Edge Cases & Constraints
- Sensitive demographic attributes (caste, religion, gender, disability) must never appear in the generated explanation text.
- Network timeouts or API key rate limits must gracefully fall back to deterministic template generation without crashing the request.
- LLM outputs must be parsed strictly as JSON without surrounding markdown ticks.

#### 5. Verification & Test Commands
```bash
# 1. Test telemetry serialization and prompt rendering
pytest tests/unit/test_prompt_templates.py

# 2. Test guardrail validator with valid, modified-number, and hallucinated responses
pytest tests/unit/test_explanation_guardrails.py

# 3. Test explanation endpoint with mocked LLM provider
pytest tests/integration/test_explanation_api.py
```

#### 6. Git & GitHub Lifecycle Execution
- **Branch**: `git checkout -b feature/phase-4-llm-explanations`
- **Atomic Commits**:
  - `feat(llm): implement prompt templates and telemetry serializer`
  - `feat(llm): implement gemini and openai structured response providers`
  - `feat(llm): implement zero-calculation guardrails and fallback templates`
  - `feat(api): expose explanation generation endpoints`
  - `feat(ui): render explainable ai cards in results page`
  - `test(llm): add guardrail validation and mock api integration tests`
- **PR Submission**: `gh pr create --title "feat(llm): implement Phase 4 LLM explanation layer and grounded reasoning" --body "..."`

#### 7. Definition of Done
- [ ] LLM explanation service generates 100% valid schema-compliant JSON.
- [ ] Guardrail validator catches and rejects any altered financial figures or hallucinated statuses.
- [ ] Fallback deterministic template provides 100% availability during external API outages.
- [ ] Mandatory human review disclaimer present in every generated explanation.
- [ ] Pull request created and passing all CI checks.

---

### Phase 5: Fairness Audit & Proxy Screening

#### 1. Objective & Scope
Implement an automated auditing engine that inspects generated explanations and application evaluations for proxy bias, disparate impact indicators, and protected attribute leakage. Route any flagged cases to the human reviewer queue.

#### 2. Architecture & File Locations
- **Backend Components**:
  - `backend/app/domain/fairness.py`: Pure Python proxy screening rules and dictionary registries
  - `backend/app/services/fairness_service.py`: Fairness checker auditing explanation text and input features
  - `backend/app/routers/fairness.py`: `GET /api/v1/admin/fairness/metrics`, `POST /api/v1/admin/fairness/audit`
- **Data & Configuration**:
  - Known proxy registers: Zip/postal code proxies, community surname indicators, gendered phrasing markers
- **Frontend Admin View**:
  - `frontend/src/components/fairness-badge.tsx`: Visual badge for audit status
  - `frontend/src/pages/review-page.tsx`: Audit flag highlights and reviewer reasoning inputs

#### 3. Step-by-Step Implementation Tasks
1. **Proxy Attribute Screening Engine (`backend/app/domain/fairness.py`)**:
   - Implement dictionary-based and regex-based scanning for:
     - Sensitive demographic keywords (`caste`, `dalit`, `brahmin`, `reservation`, `quota`, `religion`, `muslim`, `hindu`, `christian`, `gender`, `female`, `male`, `disabled`).
     - Known socio-economic geographical proxies (specific flagged pincodes or regional tags).
   - If any sensitive term or proxy is detected in the explanation text:
     - Generate `FairnessViolation` with violation type, detected term, and position.
2. **Audit & Routing Workflow (`backend/app/services/fairness_service.py`)**:
   - Intercept explanation before publishing to student.
   - If violations exist:
     - Redact prohibited terms.
     - Set application status = `needs_review`.
     - Create `AuditLogEntry` with event type `fairness_flag` and detailed violation metadata.
     - Send notification/task to human review queue.
3. **Cohort Fairness Telemetry Aggregation**:
   - Calculate acceptance rate parity and demographic parity ratios across cohorts where charter-authorized sensitive attributes are tracked.
   - Expose metrics endpoint for admin analytics.

#### 4. Edge Cases & Constraints
- Benign academic terms (e.g., "General Category" in merit context) must be handled with contextual token rules to avoid false positives.
- The fairness engine must fail closed: if the auditor fails to execute, the application must be routed to human review.

#### 5. Verification & Test Commands
```bash
# 1. Test proxy screening engine on positive, negative, and adversarial text
PYTHONPATH=. python3 -m unittest discover -s tests/unit -p "test_fairness*.py"

# 2. Test fairness service workflow and audit logging
pytest tests/integration/test_fairness_service.py
```

#### 6. Git & GitHub Lifecycle Execution
- **Branch**: `git checkout -b feature/phase-5-fairness-audit`
- **Atomic Commits**:
  - `feat(fairness): implement pure python proxy screening engine`
  - `feat(fairness): implement fairness auditing service and violation logger`
  - `feat(api): expose fairness metrics and audit endpoints`
  - `feat(ui): add fairness audit badges and reviewer alerts`
  - `test(fairness): add test coverage for keyword and proxy detection`
- **PR Submission**: `gh pr create --title "feat(fairness): implement Phase 5 fairness audit and proxy screening" --body "..."`

#### 7. Definition of Done
- [ ] Proxy screening engine detects 100% of defined prohibited terms and proxy patterns.
- [ ] Flagged explanations automatically route applications to `needs_review`.
- [ ] Complete audit trail recorded in `AuditLogEntry`.
- [ ] Zero sensitive attributes leaked to end-user facing explanation payloads.
- [ ] Pull request created and passing all CI checks.

---

### Phase 6: Reporting & Cryptographic PDF Generation

#### 1. Objective & Scope
Construct an automated report generation engine that compiles applicant inputs, verified academic/financial metrics, domain calculations, LLM explanation text, fairness check status, and human review sign-offs into a tamper-evident, downloadable PDF report.

#### 2. Architecture & File Locations
- **Backend Components**:
  - `backend/app/services/reporting/pdf_generator.py`: PDF rendering engine (ReportLab / WeasyPrint)
  - `backend/app/services/reporting/checksum.py`: SHA-256 cryptographic audit seal generator
  - `backend/app/routers/report.py`: `GET /api/v1/report/{application_id}/pdf`
- **Frontend Integration**:
  - `frontend/src/components/download-report-button.tsx`: One-click PDF download with loading spinner
  - `frontend/src/pages/results-page.tsx`: Embedded report preview and download trigger

#### 3. Step-by-Step Implementation Tasks
1. **Cryptographic Checksum & Audit Seal (`backend/app/services/reporting/checksum.py`)**:
   - Compute deterministic SHA-256 hash over canonical JSON payload:
     $$\text{Payload} = \{\text{app\_id}, \text{applicant\_hash}, \text{policy\_version}, \text{engine\_version}, \text{status}, \text{payable\_tuition}, \text{timestamp}\}$$
   - Embed hash string and QR-code/verification slug into report footer.
2. **PDF Layout & Formatting Engine**:
   - Header: FairExplain AI branding, Institution name, Application ID, Generation timestamp, Status badge.
   - Section 1: Applicant Profile & Verified Evidence summary.
   - Section 2: Deterministic Scholarship Eligibility Breakdown (table of criteria, target values, actual values, statuses).
   - Section 3: Tuition Accounting Balance Sheet (Gross tuition, awards allocated with priorities, waiver cap, net payable balance, unapplied surplus).
   - Section 4: Plain-English Assessment Explanation (LLM summary and key factors).
   - Section 5: Legal Disclaimer & Human Review Determination block (Reviewer name, decision date, signature line).
3. **Report API Router**:
   - Implement `GET /api/v1/report/{application_id}/pdf` returning `application/pdf` with `Content-Disposition: attachment; filename="assessment_{id}.pdf"`.

#### 4. Edge Cases & Constraints
- Unapplied surplus must clearly display the disclaimer: *"Unapplied surplus is not a cash payment or student refund."*
- Pending evidence applications must render a prominent watermark: `PRELIMINARY ASSESSMENT — PENDING EVIDENCE`.

#### 5. Verification & Test Commands
```bash
# 1. Test checksum generator reproducibility
pytest tests/unit/test_checksum.py

# 2. Test PDF generator output validity (file size > 0, valid PDF header %PDF-)
pytest tests/unit/test_pdf_generator.py

# 3. Test report endpoint
pytest tests/integration/test_report_api.py
```

#### 6. Git & GitHub Lifecycle Execution
- **Branch**: `git checkout -b feature/phase-6-pdf-reporting`
- **Atomic Commits**:
  - `feat(reporting): implement sha-256 cryptographic audit seal`
  - `feat(reporting): implement pdf layout and generation engine`
  - `feat(api): expose downloadable pdf report endpoint`
  - `feat(ui): add report download button and preview card`
  - `test(reporting): add unit and integration tests for pdf output`
- **PR Submission**: `gh pr create --title "feat(reporting): implement Phase 6 reporting and cryptographic PDF generation" --body "..."`

#### 7. Definition of Done
- [ ] PDF generation service operational and accessible via authenticated API endpoint.
- [ ] Generated PDF contains all 5 required sections with professional typography and layout.
- [ ] Embedded SHA-256 cryptographic hash enables tamper verification.
- [ ] Frontend download button triggers clean PDF delivery.
- [ ] Pull request created and passing all CI checks.

---

### Phase 7: Administrative Review Queue & Analytics Dashboard

#### 1. Objective & Scope
Build the institutional officer and bank underwriter portal. Implement the Human-in-the-Loop review queue for inspecting flagged cases, approving or overriding recommendations with mandatory rationale logging, and visualizing real-time cohort analytics.

#### 2. Architecture & File Locations
- **Backend Components**:
  - `backend/app/routers/admin.py`: Review queue endpoints, override action endpoints, and analytics aggregations
  - `backend/app/services/admin_service.py`: Queue filtering, decision recording, and metrics computation
- **Frontend Components**:
  - `frontend/src/pages/review-page.tsx`: Interactive review interface with diff viewer (self-reported vs OCR), explanation review, and determination form
  - `frontend/src/pages/dashboard-page.tsx`: Executive dashboard with cohort statistics, volume trends, and fairness distribution charts
  - `frontend/src/components/override-modal.tsx`: Modal capturing mandatory human justification for overrides

#### 3. Step-by-Step Implementation Tasks
1. **Review Queue Backend Endpoints**:
   - `GET /api/v1/admin/review-queue`: Returns paginated list of applications in `needs_review` or `pending_evidence` state, sorted by priority and submission timestamp.
   - `GET /api/v1/admin/application/{id}/review-context`: Returns consolidated view (applicant profile, OCR diffs, domain evaluation, explanation, audit flags).
   - `POST /api/v1/admin/application/{id}/decision`: Records final human determination (`approved`, `rejected`, `evidence_requested`), mandatory rationale note, and reviewer ID. Updates application status to `ready_for_report` or `closed`.
2. **Administrative Analytics Service**:
   - Compute real-time aggregations: Total volume, eligibility rate, average tuition reduction, fairness flag incidence rate, and average reviewer turnaround time.
   - `GET /api/v1/admin/analytics`: Exposes metrics for dashboard charts.
3. **Frontend Review Portal Wiring**:
   - Wire `frontend/src/pages/review-page.tsx` to live review endpoints.
   - Wire `frontend/src/pages/dashboard-page.tsx` to live analytics endpoints, replacing mock data points.

#### 4. Edge Cases & Constraints
- Reviewer overrides cannot omit the rationale; submission must be rejected if justification text is empty.
- Once a human reviewer records a determination, the application state becomes immutable unless reopened by an admin.

#### 5. Verification & Test Commands
```bash
# 1. Test review queue and decision recording
pytest tests/integration/test_admin_service.py tests/integration/test_admin_api.py

# 2. Test analytics aggregation accuracy
pytest tests/unit/test_analytics_aggregation.py

# 3. Test frontend build with all admin views wired
cd frontend && npm run build
```

#### 6. Git & GitHub Lifecycle Execution
- **Branch**: `git checkout -b feature/phase-7-admin-portal`
- **Atomic Commits**:
  - `feat(admin): implement review queue and determination service`
  - `feat(admin): implement cohort analytics aggregation service`
  - `feat(api): expose admin review and analytics endpoints`
  - `feat(ui): wire review page and override modal to live api`
  - `feat(ui): wire admin dashboard analytics to live api`
  - `test(admin): add integration tests for review determinations`
- **PR Submission**: `gh pr create --title "feat(admin): implement Phase 7 administrative review queue and analytics dashboard" --body "..."`

#### 7. Definition of Done
- [ ] Officers can view, filter, and inspect pending applications in the review queue.
- [ ] Human determinations (approvals, overrides, evidence requests) record immutable audit log entries with mandatory justifications.
- [ ] Analytics dashboard visualizes live cohort distributions and fairness metrics.
- [ ] Frontend mock data completely retired across all administrative pages.
- [ ] Pull request created and passing all CI checks.

---

### Phase 8: Production Hardening, CI/CD & Release

#### 1. Objective & Scope
Prepare FairExplain AI for secure, high-availability production operation. Containerize services, configure managed PostgreSQL and deployment targets (Railway/Render for backend, Vercel for frontend), enforce SSL/CORS/Rate-limiting, and validate the platform with an end-to-end smoke test suite.

#### 2. Architecture & File Locations
- **Containerization & Deployment**:
  - `Dockerfile.backend`: Multi-stage Python 3.11 slim image
  - `Dockerfile.frontend`: Multi-stage Node.js build with Nginx alpine server
  - `docker-compose.yml`: Local full-stack staging environment with PostgreSQL
  - `.github/workflows/ci.yml`: Automated GitHub Actions pipeline running all unit, integration, and lint checks
- **Security & Infrastructure**:
  - `backend/app/middleware/rate_limit.py`: SlowAPI / Redis-backed rate limiter
  - `backend/app/config/production.py`: Hardened production settings (SSL enforcement, secure cookies, secrets validation)

#### 3. Step-by-Step Implementation Tasks
1. **Docker Packaging**:
   - Create non-root, minimal Dockerfiles for backend and frontend.
   - Verify health check endpoints (`/health`) in container configurations.
2. **Security & Performance Hardening**:
   - Restrict CORS origins strictly to production frontend domains.
   - Implement rate limiting (e.g., 60 requests/minute for standard APIs, 10 requests/minute for explanation generation).
   - Configure async database connection pool (`pool_size=20`, `max_overflow=10`, `pool_pre_ping=True`).
   - Audit environment variables to ensure no secrets or API keys are committed or exposed to the client bundle.
3. **CI/CD Pipeline (`.github/workflows/ci.yml`)**:
   - Job 1: Backend linting (`ruff`, `mypy`) and domain unit tests (`python -m unittest`).
   - Job 2: Backend integration tests with ephemeral PostgreSQL service.
   - Job 3: Frontend linting (`npm run lint`), type checking (`tsc --noEmit`), and production build.
4. **End-to-End Smoke Test Suite**:
   - Automated script executing the full applicant journey against the running environment:
     1. Submit application.
     2. Upload documents.
     3. Trigger scholarship & loan evaluation.
     4. Generate explanation.
     5. Perform fairness audit.
     6. Human reviewer approval.
     7. Download final PDF report.

#### 4. Verification & Test Commands
```bash
# 1. Build and boot local production stack
docker-compose up --build -d

# 2. Wait for health checks
curl -f http://localhost:8000/health

# 3. Execute end-to-end smoke test suite
pytest tests/e2e/test_full_platform_journey.py
```

#### 5. Git & GitHub Lifecycle Execution
- **Branch**: `git checkout -b feature/phase-8-production-release`
- **Atomic Commits**:
  - `ci: create github actions pipeline for linting and test automation`
  - `feat(infra): create multi-stage backend and frontend dockerfiles`
  - `feat(security): implement rate limiting and production cors hardening`
  - `test(e2e): add end-to-end platform smoke test journey`
- **PR Submission**: `gh pr create --title "feat(infra): implement Phase 8 production hardening CI/CD and release" --body "..."`

#### 6. Definition of Done
- [ ] Backend and frontend containers build cleanly and pass automated health checks.
- [ ] GitHub Actions CI pipeline passes all linting, typing, unit, and integration tests.
- [ ] Rate limiting, CORS, and connection pooling verified under concurrent load.
- [ ] Full end-to-end smoke test suite executes with 100% pass rate.
- [ ] Pull request created and passing all CI checks.

---

## 5. Autonomous Agent End-to-End Execution Checklist

When an AI agent is instructed to implement any phase with zero additional context, it must execute this rigorous 8-step protocol from start to finish:

1. **Verify Invariants & Prerequisite State**:
   - Review Section 1 (Core Invariants).
   - Confirm prior phases are merged and operational (e.g., verify Phase 1B passes with `PYTHONPATH=. python3 -m unittest discover -s tests/unit`).
2. **Git Workspace Initialization**:
   - Ensure local `main` is current: `git checkout main && git pull origin main`.
   - Create phase feature branch: `git checkout -b <phase-branch-name>`.
3. **Execute Implementation Tasks**:
   - Implement every file and component specified in the target phase section.
   - Preserve exact signatures, schemas, error codes, and mathematical formulas.
4. **Run Verification & Test Suite**:
   - Execute all listed unit, integration, and linting commands.
   - Fix any failures or warnings before proceeding.
5. **Stage & Commit with Conventional Commits**:
   - Check `git status` to ensure no temporary, secret, or junk files are staged.
   - Create clean, atomic commits following the Conventional Commits format.
6. **Submit Pull Request via GitHub CLI**:
   - Push branch: `git push -u origin <branch-name>`.
   - Create PR using `gh pr create` with the structured template detailing deliverables and test results.
7. **CI & Integration Verification**:
   - Check automated checks: `gh pr checks`.
   - Verify zero build or test regressions.
8. **Update Roadmap Status**:
   - Once merged, update the Milestone Status Matrix in Section 2 with the merge commit SHA or PR reference.
