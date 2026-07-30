# System Architecture

## 1. High-Level Architecture

```mermaid
flowchart LR
    subgraph Client
        A[React + Vite + TS<br/>Tailwind, shadcn/ui]
    end

    subgraph API["Backend — FastAPI"]
        B1[/auth]
        B2[/application]
        B3[/documents]
        B4[/scholarship]
        B5[/loan]
        B6[/explanation]
        B7[/report]
    end

    subgraph AI["AI Layer"]
        C1[OCR Extraction]
        C2[Rule Engine]
        C3[LLM Explanation]
        C4[Fairness Checker]
    end

    D[(PostgreSQL)]

    A -->|HTTPS/REST| API
    B3 --> C1
    B4 --> C2
    B5 --> C2
    B6 --> C3
    C3 --> C4
    API --> D
```

## 2. Frontend

| Concern | Choice |
|---|---|
| Framework | React + Vite + TypeScript |
| Styling | Tailwind CSS + shadcn/ui component library |
| Forms | React Hook Form (with schema validation) |
| Data fetching / caching | TanStack Query |
| Charts | Recharts (used in Admin Analytics and What-If Simulator) |

The frontend never calls the LLM or OCR provider directly — all AI-layer calls are proxied through the backend so provider API keys never reach the client.

## 3. Backend

| Concern | Choice |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL (Neon, serverless Postgres) |

### 3.1 Services / API Surface

| Route | Responsibility |
|---|---|
| `/auth` | Registration, login/session (demo-grade for MVP). |
| `/application` | Create/read/update an Application and its status. |
| `/documents` | Upload documents, trigger OCR, store extraction results. |
| `/scholarship` | Run Scholarship Rule Engine, return score + amount. |
| `/loan` | Run Loan Rule Engine on the reduced loan amount, return outcome. |
| `/explanation` | Generate LLM explanation + run Fairness Checker for a given assessment. |
| `/report` | Generate and serve the PDF report for a completed application. |

## 4. AI Layer

| Component | Role |
|---|---|
| **OCR** | Extracts text/fields from uploaded documents; cross-checks against self-reported values; flags mismatches for review rather than silently overriding user input. |
| **Rule Engine** | Deterministic scoring module (scholarship + loan). Source of truth for all scores — versioned so results stay reproducible (see [RULE_ENGINE.md](./RULE_ENGINE.md)). |
| **LLM Explanation** | Converts a pre-computed rule-engine score into plain-English reasoning, confidence framing, and a fairness note. Never computes or overrides a score (see [PROMPTS.md](./PROMPTS.md)). |
| **Fairness Checker** | Audits explanation output (and, where applicable, the inputs feeding the rule engine) for reliance on sensitive attributes or known proxies (e.g., pincode, surname, caste, religion, gender). Flags for human review rather than silently editing text. |

## 5. Data Flow (Single Application)

1. Student submits academic + financial details → stored via `/application`.
2. Documents uploaded → `/documents` → OCR extraction → mismatch flags stored.
3. `/scholarship` runs Rule Engine → Scholarship Score, Scholarship Amount persisted.
4. Reduced Loan Amount computed (Requested Loan − Scholarship Amount).
5. `/loan` runs Rule Engine on reduced amount → Loan Assessment outcome persisted.
6. `/explanation` generates LLM explanation for both assessments → passed through Fairness Checker.
7. Application status set to **Needs Review** if either assessment or the fairness check requires it; otherwise **Ready for Report**.
8. `/report` compiles a PDF combining scores, recommendation, and explanation.

## 6. Deployment

| Component | Platform |
|---|---|
| Frontend | Vercel |
| Backend | Railway |
| Database | Neon (managed PostgreSQL) |

## 7. Security Considerations

- All AI-provider and database credentials are server-side only.
- Uploaded documents and financial fields are encrypted at rest.
- All API traffic served over HTTPS.
- Audit log records every scoring and explanation event with timestamp, rule-engine version, and (where applicable) reviewer action.
