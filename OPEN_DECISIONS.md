# FairExplain AI — Open Architecture, Product & Strategic Decisions

**Document Version:** 1.1.0  
**Effective Date:** October 25, 2026  
**Auditor / Architect:** Senior Staff Software Engineer, Security Auditor & Product Architect  
**Repository:** `https://github.com/manthanshah/FairExplain-AI`

---

## 1. Governance & Decision Framework

This document records the foundational product, security, architecture, commercial, and compliance decisions required to transition FairExplain AI from a prototype to an enterprise-grade platform.

For each decision, this document specifies:
1. **Context & Problem Statement:** Why this decision is necessary.
2. **Available Options:** Concrete alternative paths.
3. **Reconciled Decision & Engineering Contract:** The adopted path with technical and economic rationale.
4. **Trade-offs:** What is sacrificed or gained.
5. **Decision Owner:** The accountable role.
6. **Blocker Status:** Whether implementation can proceed before this decision is formally approved.

---

## 2. Decision Register

### DEC-01: Primary Customer Segment & Core Scope Boundaries
* **Context:** Legacy documentation claimed to serve three disparate audiences simultaneously: Students, University Financial Aid Offices, and Commercial Bank Lenders. Commercial banks require credit underwriting and RBI Non-Banking Financial Company (NBFC) compliance; universities require scholarship governance and tuition accounting; students require application transparency.
* **Options:**
  - *Option A (Status Quo / Diluted):* Build features for universities, banks, and students concurrently.
  - *Option B (Adopted Engineering Contract):* Narrow the primary Ideal Customer Profile (ICP) exclusively to **Higher Education Institution (HEI) Financial Aid Offices and CSR Scholarship Foundations**. Position the student view as a downstream transparency portal and drop commercial bank lending from core scope.
  - *Option C (Direct-to-Consumer):* Pivot to a B2C student marketplace monetized via lead generation.
* **Rationale & Trade-offs:** Option B aligns engineering resources with a single institutional buyer with a validated administrative pain point (the "72-Hour Audit-Proof Aid Determination" workflow). Option A leads to feature dilution and unmeetable regulatory burdens. Option C faces intense competition from established high-traffic consumer portals (e.g. Buddy4Study).
* **Decision Owner:** Chief Product Officer / Founder
* **Approval Status:** **FORMALLY RESOLVED & ADOPTED**. Implementation proceeds under Option B.

---

### DEC-02: Identity, Authentication & Complete Session Security Contract
* **Context:** Preliminary documents conflicted: `EXECUTIVE_PRODUCT_REVIEW.md` called for enterprise SAML 2.0 / Google Workspace SSO, while `PRODUCT_ROADMAP.md` proposed OAuth2 password authentication. Furthermore, `OPEN_DECISIONS.md v1.0` erroneously stated implementation was blocked waiting for approval, creating planning deadlock.
* **Options:**
  - *Option A (Enterprise SAML/SSO Only):* Require institutional SAML 2.0 / Shibboleth integration before any user can log in.
  - *Option B (Adopted Engineering Contract):* **Email/Password authentication using direct `bcrypt` password hashing + RFC 7519 JWT with rotating HttpOnly refresh cookies**, restricted to verified institutional email domains (e.g. `@nitk.edu.in`, `@*.ac.in`, `@*.edu`). Enterprise SAML/Google SSO is formally scheduled as an enterprise adapter in Milestone 7.
* **Complete Session Security Contract Specification:**
  1. **Password Hashing:** Direct `bcrypt` with work factor (salt rounds) = 12 (`bcrypt.hashpw(password, bcrypt.gensalt(12))`). *Verification Note:* Bypasses the known Python 3.12 compatibility defect between legacy `passlib 1.7.4` and `bcrypt 4.x`.
  2. **Access Token:**
     - *Transport:* `Authorization: Bearer <access_token>` HTTP header.
     - *Lifetime:* Exactly 15 minutes (900 seconds).
     - *Algorithm:* HMAC-SHA256 (`HS256`) signed with rotating `JWT_SECRET_KEY` (minimum 256-bit entropy).
     - *Claims:* `sub` (User UUID), `email` (string), `role` (`student` | `reviewer` | `admin`), `institution_id` (UUID), `type: "access"`, `iat` (epoch seconds), `exp` (iat + 900), `jti` (unique UUIDv4 token identifier).
  3. **Refresh Token & Cookie Security:**
     - *Transport:* Strictly transmitted via HTTP response cookie. Never accessible to JavaScript.
     - *Lifetime:* 7 days (604,800 seconds).
     - *Cookie Attributes:* `HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth; Max-Age=604800`.
     - *Claims:* `sub` (User UUID), `type: "refresh"`, `jti` (UUIDv4), `iat`, `exp`.
  4. **Refresh Token Rotation (RTR) & Token Family Revocation:**
     - When `POST /api/v1/auth/refresh` is invoked, the presented refresh token is immediately invalidated. A new access token and a new refresh token are issued atomically.
     - If an already-invalidated refresh token is presented (replay attack), the system detects a token family compromise and immediately revokes all active refresh tokens for that `sub`.
  5. **Rate Limiting & Brute-Force Defense:**
     - `POST /api/v1/auth/login` is strictly rate-limited via `slowapi` to 5 attempts per minute per IP + email address. Failed attempts trigger exponential backoff.
* **Decision Owner:** Lead Backend Architect & Security Officer
* **Approval Status:** **FORMALLY RESOLVED & APPROVED**. Implementation proceeds immediately in Milestone 1 without blocking.

---

### DEC-03: Multi-Tenancy Architecture (Reconciling Pilot vs. Target Architecture)
* **Context:** Earlier reports presented a conflicting strategy: `TARGET_ARCHITECTURE.md` proposed a shared database with PostgreSQL Row-Level Security (RLS), whereas `OPEN_DECISIONS.md v1.0` proposed separate physical databases for the pilot, risking throwaway code and post-pilot schema divergence.
* **Options:**
  - *Option A (Throwaway Isolated Databases for Pilot):* Deploy separate physical databases without `institution_id` columns, deferring multi-tenancy code to Phase 2.
  - *Option B (Adopted Engineering Contract):* **Unified Multi-Tenant Schema with Dual-Layer Isolation from Milestone 2 Forward.**
* **Reconciled Architecture Specification:**
  1. **Single Schema Definition:** Every tenant-scoped table (`users`, `applications`, `policies`, `uploaded_documents`, `scholarship_funds`) includes an indexed, non-nullable `institution_id UUID REFERENCES institutions(id)` column added in Milestone 2.
  2. **Layer 1 — Application-Level Scoping:** Every repository query and ORM mutation injects `WHERE institution_id = :current_tenant_id` via a scoped FastAPI dependency (`TenantContext`) extracted from the validated JWT claims.
  3. **Layer 2 — Database-Level Defense-in-Depth (RLS):** PostgreSQL Row-Level Security policies are activated across all tenant tables:
     ```sql
     ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
     CREATE POLICY tenant_isolation_policy ON applications
       USING (institution_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
     ```
  4. **Unified Deployment Model:**
     - *Standard Multi-Tenant SaaS (Default for Pilot & GA):* Single PostgreSQL cluster (Neon / RDS); institutions partitioned by `institution_id` + RLS.
     - *Sovereign Single-Tenant Campus (Contractual Requirement):* If a state university contractually mandates physical isolation, the exact same Docker container and schema is deployed to a dedicated database with a single record in `institutions`.
  5. **Outcome:** Zero throwaway code, zero schema divergence, and zero post-pilot rewrites.
* **Decision Owner:** Lead Database Architect & Lead Backend Engineer
* **Approval Status:** **FORMALLY RECONCILED & ADOPTED**. Schema migration scheduled for Milestone 2.

---

### DEC-04: Provider-Specific Object Storage & Key Management Architecture
* **Context:** Previous reports cited "AWS S3 or Cloudflare R2 with customer-managed SSE-KMS encryption". Code inspection reveals Cloudflare R2 does NOT support AWS KMS (`SSE-KMS`). A precise provider-specific specification is required.
* **Provider-Specific Analysis:**
  | Dimension | AWS S3 | Cloudflare R2 | Local Development (MinIO) |
  | :--- | :--- | :--- | :--- |
  | **Server-Side Encryption** | `aws:kms` using Customer Managed Key (CMK) ARN. | Managed AES-256 (`SSE-S3` equivalent). KMS **unsupported**. | Local filesystem / MinIO SSE-S3. |
  | **Key Rotation** | Automated annual rotation via AWS KMS Key Policy. | Cloudflare internal key lifecycle; no user-auditable rotation. | N/A (Test credentials). |
  | **Pre-Signed URLs** | Supported (`s3:PutObject`, `s3:GetObject` with 15-min TTL). | Supported via S3-compatible API (15-min TTL). | Supported via MinIO S3 API. |
  | **Audit Logging** | Full API access logging via AWS CloudTrail. | Cloudflare Logpush (Enterprise tier only). | Local console logs. |
  | **Institutional Compliance** | Meets rigorous government/UGC audit mandates for CMEK. | Cost-effective ($0 egress), but lacks CMEK auditability. | Development & CI only. |
* **Adopted Engineering Contract:**
  1. **Primary Production Provider:** **AWS S3** with Customer Managed Keys in AWS KMS (`SSE-KMS`). Bucket policy mandates `aws:SecureTransport: true` (TLS 1.3) and denies unencrypted PUTs.
  2. **Storage Abstraction:** Implement `S3StorageBackend` using `aioboto3` adhering to a strict `StorageService` protocol (`save_file`, `get_presigned_download_url`, `get_presigned_upload_url`, `delete_file`).
  3. **Local & CI Testing:** Use containerized **MinIO** in Docker Compose (`docker-compose.test.yml`), maintaining 100% API parity with S3 without external cloud credentials.
* **Decision Owner:** Infrastructure SRE & Security Officer
* **Approval Status:** **FORMALLY RESOLVED & ADOPTED**. Implementation scheduled in Milestone 1.

---

### DEC-05: PDF Audit Verifiability & Digital Signatures
* **Context:** Current code generates an unauthenticated SHA-256 hash printed on the PDF footer without database persistence or digital signature.
* **Options:**
  - *Option A (Unsigned Hash):* Retain current unstored, unsigned hash.
  - *Option B (Adopted Engineering Contract):* **Server-Side Cryptographic Signatures (Ed25519) with Database Persistence.** Store the computed audit digest in `audit_log_entries`. Sign the hash using the institution's or platform's Ed25519 private key. Expose `POST /api/v1/report/verify` allowing auditors to upload a PDF and verify authenticity, signature validity, and database match.
* **Decision Owner:** Security Officer & Cryptographic Lead
* **Approval Status:** **FORMALLY ADOPTED**. Implementation scheduled in Milestone 4.

---

### DEC-06: Commercial Pricing & Campus Procurement Strategy
* **Context:** Indian universities operate on fixed annual departmental budgets. Charging per-application creates continuous procurement friction.
* **Adopted Contract:** **Annual Flat Campus License with Volume Tiers.**
  - *Pilot Edition:* ₹1,50,000 / year (up to 1,000 dossiers; 5 officer seats). Priced deliberately below institutional tender thresholds (< ₹2,50,000) for direct Dean discretionary approval.
  - *Campus Standard:* ₹4,50,000 / year (up to 5,000 dossiers; unlimited reviewers).
* **Decision Owner:** Commercial Director / Founder
* **Approval Status:** **FORMALLY ADOPTED**. Guided by [`VALIDATION_PLAN.md`](file:///Users/manthanshah/Documents/FairExplain/FairExplain-AI/VALIDATION_PLAN.md).

---

### DEC-07: PII Document Retention vs. Legal Compliance Verification
* **Context:** Previous reports conflated an operational proposal ("180-day document purge") with statutory compliance under India's Digital Personal Data Protection (DPDP) Act, 2023. A rigorous distinction between statutory law, engineering policy, and unresolved legal claims is required.
* **Reconciled Classification:**
  1. **Statutory Principles under DPDP Act 2023 (Verified Indian Law):**
     - Section 6: Notice and consent must be unconditional, itemized, and available in English and 22 scheduled languages.
     - Section 8(6): Mandatory notification of personal data breaches to the Data Protection Board of India (DPBI) and affected individuals without delay.
     - Section 8(7): Data Fiduciary **must erase personal data** as soon as the specified purpose is no longer served or upon consent withdrawal. *The statute contains NO explicit 180-day figure.*
     - Aadhaar Act 2016 (Section 29) & UIDAI Regulations: Raw, unmasked 12-digit Aadhaar numbers and photocopies must never be stored on uncertified servers.
  2. **Proposed Operational Engineering Policy (FairExplain AI Rule):**
     - Retain student income proofs and marksheets during the active admission semester (120 days) plus a 60-day appeal window (total: 180 days post-award).
     - At Day 180, an automated background worker permanently deletes physical PDF documents from S3.
     - The platform permanently retains: (a) anonymized calculation inputs, (b) eligibility outcome booleans, (c) immutable audit log entries, and (d) cryptographic SHA-256 hashes of the deleted files.
  3. **Specific Claims Requiring Qualified Legal Counsel & DPO Review:**
     - *Claim 1:* "Purging tax records after 180 days satisfies all regulatory requirements." -> **Requires Legal Review** against General Financial Rules (GFR, 2017) and UGC/AICTE accounting norms, which require financial disbursement vouchers to be retained for 3 to 8 years.
     - *Claim 2:* "Cryptographic SHA-256 digests of erased student documents do not constitute personal data." -> **Requires Legal Review** to confirm whether high-entropy hashes of student documents are legally deemed anonymized under DPDP Act rules.
     - *Claim 3:* "Cloud hosting on AWS Mumbai (ap-south-1) satisfies all data sovereignty rules." -> **Requires Legal Review** regarding multi-region backup replication and institutional government contracts.
     - *Claim 4:* "Collecting parent ITR income certificates is covered by applicant student consent." -> **Requires Legal Review** regarding third-party non-applicant data principals (parents/guardians) under DPDP Act Section 6.
* **Decision Owner:** Compliance Officer & External Legal Counsel
* **Approval Status:** **ENGINEERING POLICY ADOPTED FOR IMPLEMENTATION; LEGAL CLAIMS FORMALLY FLAGGED AS PENDING COUNSEL REVIEW.**
