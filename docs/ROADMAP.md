# Development Roadmap

| Phase | Focus | Key Deliverables | Exit Criteria |
|---|---|---|---|
| 1 | UI Only | Static React screens for registration, academic/financial forms, document upload, results view — no live backend. | All core screens navigable with mock data. |
| 2 | Backend APIs | FastAPI services for `/auth`, `/application`, `/documents`; PostgreSQL schema live per [DATA_MODEL.md](./DATA_MODEL.md). | Frontend fully wired to real endpoints for application CRUD. |
| 3 | Rule Engine | Deterministic scholarship + loan scoring per [RULE_ENGINE.md](./RULE_ENGINE.md), versioned. | Given a fixed input set, output is reproducible and matches documented formula. |
| 4 | OCR | Document upload triggers extraction; mismatch flagging against self-reported values. | OCR extraction accuracy validated against a test document set; mismatches correctly flagged. |
| 5 | LLM Explanations | `/explanation` service implementing the prompt contract in [PROMPTS.md](./PROMPTS.md); Fairness Checker integrated. | Every assessment produces a schema-valid explanation; fairness flags route correctly to review. |
| 6 | PDF Generation | `/report` service producing the downloadable summary report. | Report includes scores, outcome, explanation, and human-review notice for a completed application. |
| 7 | Dashboard | Admin analytics: application volume, outcome distribution, fairness-flag rate. | Dashboard reflects live data from at least one full test cohort. |
| 8 | Deployment | Frontend on Vercel, backend on Railway, database on Neon. | End-to-end flow functional in production environment. |
| 9 | Portfolio Polish | UX refinement, documentation cleanup, demo dataset, walkthrough recording. | Project presentable as a complete, demonstrable case study. |

## Notes

- Phases are sequential but not strictly blocking — Phase 1 (UI) and early Phase 2 (API scaffolding) can proceed in parallel.
- The Rule Engine (Phase 3) should be finalized and versioned **before** Phase 5, since the Explanation Layer depends on stable score inputs.
- Each phase's deliverables map to the functional requirements in [SRS.md](./SRS.md); see FR-IDs for full traceability.
