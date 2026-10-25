/**
 * FairExplain AI — Canonical Domain Types
 * =========================================
 * Authoritative client-side TypeScript contracts aligned with:
 * - backend/app/domain/ (enums.py, models.py, eligibility.py, accounting.py)
 * - backend/app/schemas/ (scholarship.py, loan.py, application.py, admin.py)
 * - docs/DATA_MODEL.md, docs/RULE_ENGINE.md, docs/PROMPTS.md
 */

// ---------------------------------------------------------------------------
// 1. Core Domain Enums & Literals
// ---------------------------------------------------------------------------

export type EligibilityStatus = "eligible" | "ineligible" | "pending_evidence"

export type CriterionOperator =
  | "eq"
  | "neq"
  | "gt"
  | "gte"
  | "lt"
  | "lte"
  | "in"
  | "not_in"

export type CriterionOutcome = "satisfied" | "failed" | "pending_evidence"

export type EvidenceStatus = "verified" | "unverified" | "missing" | "not_required"

export type AttributePurpose =
  | "merit_ranking"
  | "program_eligibility"
  | "restricted_sensitive"

export type AwardStatus =
  | "confirmed"
  | "eligible"
  | "applied"
  | "pending"
  | "provisionally_awarded"
  | "rejected"

export type AwardType = "fixed_amount" | "percentage_of_tuition"

export type LoanOutcome = "eligible" | "needs_review" | "not_recommended"

export type ApplicationStatus =
  | "draft"
  | "submitted"
  | "needs_review"
  | "ready_for_report"
  | "closed"

export type ReviewDecision = "approve" | "override" | "reject" | "request_evidence"

export type UserRole = "student" | "reviewer" | "admin"

// ---------------------------------------------------------------------------
// 2. Base Response Envelope
// ---------------------------------------------------------------------------

export interface BaseResponse<T> {
  success: boolean
  data: T | null
  message: string
  errors: string[]
}

// ---------------------------------------------------------------------------
// 3. User & Auth
// ---------------------------------------------------------------------------

export interface UserProfile {
  id: string
  name: string
  email: string
  role: UserRole
  institution?: string
  department?: string
  avatarUrl?: string
}

// ---------------------------------------------------------------------------
// 4. Academic & Financial Profiles
// ---------------------------------------------------------------------------

export interface AcademicRecord {
  cgpa: string | number // strictly formatted decimal string from API
  tenth_percent: string | number
  twelfth_percent: string | number
  backlogs: number
}

export interface FinancialProfile {
  household_income: string | number // in INR decimal string
  existing_emi: string | number
  tuition_fee: string | number
  requested_loan: string | number
}

export interface ApplicationProfile {
  application_id: string
  user_id?: string
  status: ApplicationStatus
  name: string
  email: string
  institution?: string
  programme?: string
  academic_record: AcademicRecord
  financial_profile: FinancialProfile
  created_at?: string
  updated_at?: string
}

// ---------------------------------------------------------------------------
// 5. Deterministic Criteria & Scholarship Evaluation
// ---------------------------------------------------------------------------

export interface CriterionEvaluationDTO {
  criterion_id: string
  attribute: string
  operator: CriterionOperator | string
  target_value: string | number | string[]
  actual_value: string | number | null
  status: CriterionOutcome | string
  is_mandatory: boolean
  evidence_required: string | null
  evidence_status: EvidenceStatus | string
  reason: string
}

export interface AwardAllocationDTO {
  award_id: string
  program_id: string
  title: string
  priority: number
  status: AwardStatus | string
  nominal_amount: string // Decimal string
  capped_amount: string
  effective_reduction: string
  unapplied_surplus: string
  cap_reason?: string | null
}

export interface TuitionAccountingDTO {
  gross_eligible_tuition: string
  institutional_cap_applied: string
  total_effective_reduction: string
  remaining_payable_tuition: string
  remaining_waiver_allowance: string
  total_unapplied_surplus: string
  allocations: AwardAllocationDTO[]
}

export interface ScholarshipEvaluationDTO {
  application_id: string
  program_id: string
  policy_version: string
  status: EligibilityStatus | string
  reason: string
  satisfied_count: number
  failed_count: number
  pending_count: number
  criteria_evaluations: CriterionEvaluationDTO[]
  tuition_accounting?: TuitionAccountingDTO | null
}

// ---------------------------------------------------------------------------
// 6. Deterministic Loan Assessment
// ---------------------------------------------------------------------------

export interface LoanAssessResponseData {
  application_id: string
  monthly_income: string
  available_monthly_capacity: string
  estimated_emi: string
  post_scholarship_loan_amount: string
  tenure_months: number
  outcome: LoanOutcome | string
  dti_ratio_percent: string
  capacity_utilization_percent: string
  reason: string
}

// ---------------------------------------------------------------------------
// 7. Grounded LLM Explanation Contract (PROMPTS.md)
// ---------------------------------------------------------------------------

export interface ExplanationContract {
  summary_headline: string
  reasons: string[]
  accounting_explanation?: string
  required_actions?: string[]
  fairness_attestation: string
  human_review_notice: string
}

export interface ExplanationReportDTO {
  application_id: string
  assessment_id?: string
  prompt_version?: string
  explanation: ExplanationContract
  created_at?: string
}

// ---------------------------------------------------------------------------
// 8. Documents & OCR Cross-Verification
// ---------------------------------------------------------------------------

export interface UploadedDocumentDTO {
  id: string
  application_id: string
  doc_type: "marksheet" | "income_proof" | "id_proof" | string
  file_url: string
  sha256?: string
  mismatch_flag: boolean
  ocr_extracted_data?: Record<string, unknown>
  confidence?: number
  created_at?: string
}

export interface DiscrepancyItem {
  doc_type: string
  field: string
  extracted: string | number
  reported: string | number
  reason: string
}

export interface VerificationResultDTO {
  verified: boolean
  mismatch_flag: boolean
  discrepancies: DiscrepancyItem[]
  status?: string
}

// ---------------------------------------------------------------------------
// 9. Institutional Review Queue & Decision Governance
// ---------------------------------------------------------------------------

export interface ReviewQueueItem {
  application_id: string
  applicant_name: string
  applicant_email: string
  submission_date: string
  status: ApplicationStatus | string
  program_id?: string | null
  flags: string[]
  priority: "high" | "medium" | "low"
}

export interface ReviewDecisionPayload {
  decision: ReviewDecision
  rationale: string
  reviewer_id?: string
  override_details?: Record<string, unknown>
}

export interface ReviewDecisionResponse {
  application_id: string
  status: ApplicationStatus | string
  decision: ReviewDecision | string
  rationale: string
  audit_log_id: string
}

export interface ConsolidatedDossierDTO {
  application_id: string
  status: ApplicationStatus | string
  created_at: string
  updated_at?: string
  applicant: {
    id?: string
    name: string
    email: string
  }
  academic_record: AcademicRecord
  financial_profile: FinancialProfile
  ocr_diffs: Array<{
    document_id: string
    doc_type: string
    file_url: string
    mismatch_flag: boolean
    extracted_data: Record<string, unknown>
  }>
  scholarship_evaluation?: {
    id?: string
    program_id: string
    policy_version: string
    status: EligibilityStatus | string
    reason: string
    satisfied_count: number
    failed_count: number
    pending_count: number
    criteria_breakdown?: CriterionEvaluationDTO[]
    criteria_evaluations?: CriterionEvaluationDTO[]
    tuition_accounting?: TuitionAccountingDTO | null
  } | null
  loan_assessment?: LoanAssessResponseData | null
  explanation?: {
    recommendation_text?: string
    summary_headline?: string
    reasons: string[]
    accounting_explanation?: string
    required_actions?: string[]
    confidence_note?: string
    fairness_note?: string
    fairness_attestation?: string
    human_review_notice?: string
    llm_prompt_version?: string
  } | null
  audit_logs: Array<{
    id: string
    event_type: string
    detail: Record<string, unknown>
    timestamp: string
  }>
}

// ---------------------------------------------------------------------------
// 10. Institutional Analytics & Fairness Metrics
// ---------------------------------------------------------------------------

export interface AdminAnalyticsResponse {
  total_applications: number
  pending_review_count: number
  approved_count: number
  rejected_count: number
  eligibility_rate_percent: number
  average_tuition_reduction: number
  fairness_flag_incidence_rate: number
  average_turnaround_hours: number
  status_distribution: Record<string, number>
  recent_activity: Array<{
    id: string
    application_id?: string
    event_type: string
    detail: Record<string, unknown>
    timestamp: string
  }>
}

export interface FairnessMetricsDTO {
  total_audited: number
  demographic_leakage_flags: number
  flag_incidence_rate_percent: number
  status: string
}

// ---------------------------------------------------------------------------
// 11. Policy & Governance Models (Admin)
// ---------------------------------------------------------------------------

export interface EligibilityCriterionSpec {
  criterion_id: string
  attribute: string
  operator: CriterionOperator
  target_value: string | number | string[]
  is_mandatory: boolean
  required_evidence?: string | null
  description?: string
  charter_authorization?: string | null
  purpose: AttributePurpose
}

export interface ScholarshipPolicySpec {
  program_id: string
  policy_version: string
  title: string
  description?: string
  criteria: EligibilityCriterionSpec[]
  checksum_sha256: string
  effective_date: string
  charter_authorizations: Record<string, string>
}
