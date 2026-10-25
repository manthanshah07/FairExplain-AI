# FairExplain AI — Shared Component Library Reference

This document catalogs the 17 shared domain components defined in `src/components/domain/`.

---

## 1. `StatusBadge`
- **File**: `src/components/domain/status-badge.tsx`
- **Purpose**: Displays deterministic eligibility, individual criterion outcomes, and review determinations. Always pairs color with an icon and label (never color alone).
- **Props**:
  - `status`: `"eligible" | "ineligible" | "pending_evidence" | "satisfied" | "failed" | "needs_review" | "ready_for_report" | ...`
  - `size?`: `"sm" | "md" | "lg"` (default: `"md"`)
  - `showIcon?`: boolean (default: `true`)
- **Usage**:
  ```tsx
  <StatusBadge status="eligible" size="lg" />
  <StatusBadge status="pending_evidence" size="sm" />
  ```

---

## 2. `MoneyAmount`
- **File**: `src/components/domain/money-amount.tsx`
- **Purpose**: Displays exact financial figures in Indian Rupee format (`₹1,20,000.00`) using Indian digit grouping (`12,34,567.00`). **Zero floating-point arithmetic**; operates strictly on integer/fraction string components.
- **Props**:
  - `amount`: `string | number | null | undefined` (raw decimal string from API)
  - `size?`: `"sm" | "md" | "lg" | "xl" | "hero"` (default: `"md"`)
  - `hint?`: optional strike-through baseline (e.g. was ₹8,00,000.00)
  - `trend?`: `"positive" | "negative" | "neutral"`
- **Usage**:
  ```tsx
  <MoneyAmount amount="120000.00" size="xl" trend="positive" />
  <MoneyAmount amount="560000.00" hint="was ₹8,00,000" size="lg" />
  ```

---

## 3. `RecommendationRibbon`
- **File**: `src/components/domain/recommendation-ribbon.tsx`
- **Purpose**: Persistent governance banner establishing that all calculations are decision-support recommendations until signed off by an authorized human officer.
- **Props**:
  - `officerDecision?`: string | null (e.g. `"approve" | "override"`)
  - `officerName?`: string | null
  - `decidedAt?`: string | null
- **Usage**:
  ```tsx
  <RecommendationRibbon />
  <RecommendationRibbon officerDecision="approve" officerName="Dr. Sarah Jenkins" decidedAt="2026-10-25T10:00:00Z" />
  ```

---

## 4. `CriterionRow`
- **File**: `src/components/domain/criterion-row.tsx`
- **Purpose**: Renders one evaluated eligibility criterion with operators in words ("at least", "must equal"), parameter comparison, mandatory tag, and an "Upload Evidence" button for pending states.
- **Props**:
  - `criterion`: `CriterionEvaluationDTO`
  - `onUploadClick?`: `(docType: string) => void`
  - `applicationId?`: string
- **Usage**:
  ```tsx
  <CriterionRow criterion={evalDto} onUploadClick={(doc) => handleUpload(doc)} />
  ```

---

## 5. `AiExplanationCard`
- **File**: `src/components/domain/ai-explanation-card.tsx`
- **Purpose**: Renders grounded natural-language explanations following the strict JSON schema in `docs/PROMPTS.md`. Features a softer tinted background and clear label that AI text cannot compute or alter results.
- **Props**:
  - `explanation?`: `ExplanationContract | null`
  - `isLoading?`: boolean
  - `isError?`: boolean
  - `onRetry?`: `() => void`
  - `promptVersion?`: string
- **Usage**:
  ```tsx
  <AiExplanationCard explanation={expData} promptVersion="v1.0-phase4" />
  ```

---

## 6. `FairnessPanel`
- **File**: `src/components/domain/fairness-panel.tsx`
- **Purpose**: Displays the fairness attestation, permitted merit/need inputs, and explicit list of screened demographic proxy tokens.
- **Props**:
  - `attestationText?`: string
  - `screenedProxies?`: string[]
- **Usage**:
  ```tsx
  <FairnessPanel attestationText="No proxy tokens used..." />
  ```

---

## 7. `TuitionWaterfall`
- **File**: `src/components/domain/tuition-waterfall.tsx`
- **Purpose**: Waterfall chart and data table toggle showing gross tuition, confirmed awards in ascending priority order, institutional cap, remaining payable tuition, and unapplied surplus.
- **Props**:
  - `accounting?`: `TuitionAccountingDTO | null`
- **Usage**:
  ```tsx
  <TuitionWaterfall accounting={tuitionAccounting} />
  ```

---

## 8. `LoanAffordabilityGauge`
- **File**: `src/components/domain/loan-affordability-gauge.tsx`
- **Purpose**: Underwriting gauge showing post-scholarship loan balance, monthly capacity utilization, and estimated EMI. Respects `VITE_FEATURE_LOAN` flag.
- **Props**:
  - `assessment?`: `LoanAssessResponseData | null`
- **Usage**:
  ```tsx
  <LoanAffordabilityGauge assessment={loanData} />
  ```

---

## 9. `ReviewTimeline`
- **File**: `src/components/domain/review-timeline.tsx`
- **Purpose**: Shows the multi-step lifecycle: Submitted -> Scored -> Explained -> Fairness-checked -> Under human review -> Final decision.
- **Props**:
  - `steps?`: `TimelineStep[]`
  - `currentStepId?`: string
- **Usage**:
  ```tsx
  <ReviewTimeline currentStepId="review" />
  ```

---

## 10. `DocumentVerifier`
- **File**: `src/components/domain/document-verifier.tsx`
- **Purpose**: Split-screen view comparing OCR-extracted document values against self-reported student inputs, highlighting mismatches with reconciliation action buttons.
- **Props**:
  - `document`: `UploadedDocumentDTO`
  - `reportedData?`: `Record<string, unknown>`
  - `verification?`: `VerificationResultDTO | null`
  - `onConfirmMismatch?`: `(field: string) => void`
  - `onCorrectMismatch?`: `(field: string, val: unknown) => void`
- **Usage**:
  ```tsx
  <DocumentVerifier document={doc} reportedData={academic} verification={verifyRes} />
  ```

---

## 11. `Stepper`
- **File**: `src/components/domain/stepper.tsx`
- **Purpose**: Horizontal multi-step progress bar for application intake.
- **Props**:
  - `steps`: `StepItem[]`
  - `currentStepIndex`: number
  - `onStepClick?`: `(idx: number) => void`
- **Usage**:
  ```tsx
  <Stepper steps={appSteps} currentStepIndex={step} onStepClick={setStep} />
  ```

---

## 12. `EmptyState`
- **File**: `src/components/domain/empty-state.tsx`
- **Purpose**: Friendly empty view with icon, title, description, and primary CTA.
- **Props**:
  - `icon?`: React component
  - `title`: string
  - `description`: string
  - `actionLabel?`: string
  - `onAction?`: `() => void`
- **Usage**:
  ```tsx
  <EmptyState title="No applications in queue" description="All submissions have been reviewed." />
  ```

---

## 13. `ErrorState`
- **File**: `src/components/domain/error-state.tsx`
- **Purpose**: Accessible error card translating backend failures with retry support.
- **Props**:
  - `title?`: string
  - `message`: string
  - `onRetry?`: `() => void`
- **Usage**:
  ```tsx
  <ErrorState message="Could not connect to decision engine." onRetry={refetch} />
  ```

---

## 14. `SkeletonCard`
- **File**: `src/components/domain/skeleton-card.tsx`
- **Purpose**: Loading placeholder pulse cards preserving layout stability.
- **Props**:
  - `lines?`: number (default: 3)
- **Usage**:
  ```tsx
  <SkeletonCard lines={4} />
  ```

---

## 15. `ConfirmDialog`
- **File**: `src/components/domain/confirm-dialog.tsx`
- **Purpose**: Modal confirmation for human decisions; enforces mandatory written justification for overrides.
- **Props**:
  - `isOpen`: boolean
  - `decision`: `"approve" | "override" | "reject" | "request_evidence"`
  - `applicantName`: string
  - `onClose`: `() => void`
  - `onConfirm`: `(rationale: string) => void`
  - `isSubmitting?`: boolean
- **Usage**:
  ```tsx
  <ConfirmDialog isOpen={show} decision="override" applicantName="Aarav Patel" onConfirm={handleConfirm} onClose={() => setShow(false)} />
  ```

---

## 16. `CalculationDrawer`
- **File**: `src/components/domain/calculation-drawer.tsx`
- **Purpose**: Slide-over drawer answering "How was this calculated?" with explicit mathematical formulas, frozen inputs, and policy provenance.
- **Props**:
  - `isOpen`: boolean
  - `onClose`: `() => void`
  - `title`: string
  - `formula`: string
  - `inputs`: `Record<string, string | number>`
  - `engineVersion?`: string
  - `policyVersion?`: string
  - `notes?`: string
- **Usage**:
  ```tsx
  <CalculationDrawer isOpen={open} onClose={() => setOpen(false)} title="Net Payable Tuition" formula="Gross Tuition - SUM(Confirmed Awards)" inputs={{ gross: 240000, award: 120000 }} />
  ```

---

## 17. `VersionChip`
- **File**: `src/components/domain/version-chip.tsx`
- **Purpose**: Monospace badge for policy versions, engine versions, and SHA-256 hashes with 1-click clipboard copying.
- **Props**:
  - `label?`: string
  - `value`: string
  - `type?`: `"version" | "hash" | "engine"`
  - `copyable?`: boolean
- **Usage**:
  ```tsx
  <VersionChip label="Policy" value="1.0.0" />
  <VersionChip type="hash" value="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" />
  ```
