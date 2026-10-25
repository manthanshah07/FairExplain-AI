# FairExplain AI — Production Frontend Application

**An auditable, explainable, and accountable web application for higher education scholarships and loan affordability.**

FairExplain AI evaluates scholarship eligibility, reduces the education loan a student actually needs, and synthesizes a plain-language explanation for every outcome — while an authorized institutional officer always retains final operational and legal decision authority.

---

## 1. Architectural Philosophy: The Three-Layer Separation

FairExplain AI strictly segregates computation, natural language synthesis, and legal determination across three distinct visual layers:

1. **Layer 1: Deterministic Facts (Rule Engine & Accounting)**
   - AST rule evaluation and tuition ledger arithmetic computed entirely by deterministic backend code.
   - Zero floating-point math; all monetary amounts formatted in Indian Rupees (`₹1,20,000.00`) using exact integer/fraction strings.
   - Missing evidence results in `PENDING_EVIDENCE`, never criterion failure.
2. **Layer 2: Grounded AI Explanation (Grounded LLM)**
   - Natural language synthesized strictly from Layer 1 evaluation results.
   - Highlighted in soft-tinted cards with explicit disclaimers: *Generative Natural Language Explanation · Zero Authority to Alter Facts*.
   - Segregates sensitive protected attributes (caste, religion, gender) from model prompt context.
3. **Layer 3: Human Officer Governance (Authorized Decision-Support)**
   - Every system output is framed as a **recommendation**, never an automated approval or denial.
   - Persistent `RecommendationRibbon`: *"Decision-support recommendation, pending review and approval by an authorized institutional officer."*
   - Officer overrides mandate written statutory rationale with cryptographic SHA-256 state signatures.

---

## 2. Technology Stack

- **Framework**: React 19 + TypeScript + Vite 8
- **Styling**: Tailwind CSS v4 + Base UI / shadcn/ui design primitives
- **State & Data Fetching**: TanStack Query (React Query v5) + React Hook Form + Zod
- **Data Visualization**: Recharts (Tuition Waterfall & Institutional Distribution)
- **Icons & Typography**: Lucide React + Geist Variable Font
- **Testing & Quality**: Vitest + React Testing Library + Oxlint

---

## 3. Getting Started

### Prerequisites
- **Node.js**: v20.x or higher
- **npm**: v10.x or higher

### Environment Variables
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Type | Default | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | `string` | `http://localhost:8000` | Backend FastAPI service endpoint |
| `VITE_USE_MOCKS` | `boolean` | `false` | When `true`, routes all API calls to typed mock fixtures |
| `VITE_FEATURE_LOAN` | `boolean` | `true` | Feature flag toggling loan affordability gauge |

### Installation & Run

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run unit and component test suite
npm run test

# Run linter
npm run lint

# Build production bundle with typecheck
npm run build
```

---

## 4. Workspaces & Roles

FairExplain AI includes a built-in interactive role switcher in the application header:

### 🎓 1. Student Portal (`/student`)
- **Dashboard (`/student`)**: Journey progress stepper, active dossier status, pending document alerts, and stat cards.
- **Application Wizard (`/student/apply`)**: 4-step wizard (Personal & Academic, Financial Need, Policy Alignment, Review & Submit) with client-side Zod validation and draft auto-saving.
- **Documents & OCR (`/student/documents`)**: Document upload intake with real-time OCR extraction preview and discrepancy cross-verification.
- **Results & Dossier (`/student/results`)**: Full 3-layer dossier with interactive `CalculationDrawer` deriving Gross Tuition, Statutory Cap, Confirmed Awards, and Net Payable fee. Official print stylesheet with cryptographic SHA-256 audit header.

### ⚖️ 2. Reviewer Portal (`/reviewer`)
- **Review Queue (`/reviewer`)**: Sortable and filterable queue (by status, priority, audit flags), search bar, and queue statistics.
- **Case Review (`/reviewer/case/:id`)**: Responsive 3-column split view (Frozen Inputs | Deterministic Facts | AI Explanation) with a sticky decision action bar. Overriding recommendations mandates written statutory rationale.
- **Decision History (`/reviewer/history`)**: Read-only immutable audit log of past determinations with algorithmic vs human comparative diffs and digital signatures.

### 🏛️ 3. Admin Console (`/admin`)
- **Institutional Analytics (`/admin`)**: Throughput metrics, recommendation rates, turnaround SLA compliance (target < 24h), and demographic parity assessment table.
- **Policy Registry (`/admin/policies`)**: Active statutory scholarship policies, criteria classifications (`merit_ranking`, `program_eligibility`, `restricted_sensitive`), and version history.
- **Fairness Screening (`/admin/fairness`)**: Four-Fifths Rule compliance monitor, protected attribute segregation audits, and interactive proxy-token leakage sandbox.
- **Cryptographic Audit (`/admin/audit`)**: Immutable log of all system state events, AST executions, and decision records with expandable JSON payload inspection.

---

## 5. Domain Rules & Precision Guidelines

1. **Exact Currency Representation**:
   All monetary amounts are treated as decimal strings (`"120000.00"`). The frontend never converts currency values into JavaScript IEEE-754 floating-point numbers. Use `formatINR` or `<MoneyAmount />` for display with Indian digit grouping (`₹1,20,000.00`).
2. **Plain-English Operators**:
   Mathematical condition operators are displayed to users in clear words:
   - `gte` &rarr; "at least"
   - `lte` &rarr; "at most"
   - `eq` &rarr; "must equal"
   - `in` &rarr; "is one of"
3. **Surplus is Not Cash**:
   Tuition reductions in excess of eligible tuition (`unapplied_surplus`) are clearly labeled as non-refundable institutional fee adjustments and never represented as cash stipends.
