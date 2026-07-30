# Product Requirements Document (PRD)

**Product:** FairExplain AI
**Document Owner:** Project Team
**Status:** Draft — v1.0

---

## 1. Vision

Build an enterprise-grade, explainable student financing assistant that removes the "black box" feeling from scholarship and loan decisions — showing students *why* a recommendation was made, not just *what* it is, while keeping a human decision-maker firmly in control of any final outcome.

## 2. Problem Statement

Students routinely face loan rejections and scholarship denials with little to no explanation, and have no way to see how a scholarship award would reduce the loan they actually need. This opacity erodes trust and makes financial planning for education needlessly difficult. See [CONTEXT.md](./CONTEXT.md) for the full problem framing.

## 3. Target Users

| User | Need |
|---|---|
| **Students** | Understand scholarship eligibility and loan requirement in one flow, with clear reasoning. |
| **Universities** | Verify applicant academic/financial standing and support scholarship disbursement decisions. |
| **Banks / NBFCs** | Receive a pre-screened, explainable loan recommendation to speed up manual underwriting. |
| **Scholarship Providers** | Identify eligible candidates against transparent, auditable criteria. |

## 4. Core Features

| # | Feature | Description | Priority |
|---|---|---|---|
| 1 | Registration | Student account creation (demo auth acceptable for MVP). | Must-have |
| 2 | Academic Details | Capture CGPA, 10th %, 12th %, backlogs. | Must-have |
| 3 | Financial Details | Capture household income, existing EMI, tuition fee, requested loan. | Must-have |
| 4 | Document Verification | Upload + OCR extraction of supporting documents. | Must-have |
| 5 | Scholarship Eligibility | Deterministic scoring against academic + financial criteria. | Must-have |
| 6 | Loan Eligibility Recommendation | Scoring on reduced loan amount post-scholarship. | Must-have |
| 7 | Explainable AI | Plain-English reasoning, confidence, and fairness note per recommendation. | Must-have |
| 8 | What-If Simulator | Let students adjust inputs (e.g., hypothetical CGPA, income) and see recalculated outcomes in real time, without submitting a formal application. | Should-have |
| 9 | PDF Report | Downloadable report summarizing scores, recommendation, and explanation. | Must-have |
| 10 | Admin Analytics | Dashboard for universities/providers: application volume, approval trends, fairness metrics. | Should-have |

## 5. Out of Scope (MVP)

- Real-time bank account/credit bureau integration.
- Automated, legally binding loan approval or disbursal.
- Multi-currency / non-Indian education financing contexts.
- Mobile native apps (responsive web only).

## 6. Success Metrics

| Metric | Target |
|---|---|
| Application completion time | < 2 minutes end-to-end |
| Explanation coverage | 100% of recommendations include a plain-English reason |
| Rule engine reproducibility | 100% — identical inputs always yield identical scores |
| Average response time | < 3 seconds per request |

## 7. Assumptions & Constraints

- Users self-report academic/financial data; OCR is used to cross-verify against uploaded documents, not as the sole source of truth.
- Authentication is demo-grade for the MVP; production deployment would require verified institutional SSO or KYC-grade identity checks.
- The rule engine, not the LLM, is the source of truth for scores — the LLM only explains scores that have already been computed.

## 8. Risks

| Risk | Mitigation |
|---|---|
| LLM explanation drifts from the underlying rule-engine score | LLM prompt is constrained to explain a pre-computed score, never to compute or override it (see [PROMPTS.md](./PROMPTS.md)). |
| Sensitive attributes leak into scoring via proxies (e.g., pincode, surname) | Fairness Checker screens inputs/outputs against a defined proxy-attribute list (see [RULE_ENGINE.md](./RULE_ENGINE.md) §5). |
| Users treat AI recommendation as final | UI and PDF report explicitly label output as "Recommendation — Pending Human Review" on every screen. |
