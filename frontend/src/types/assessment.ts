// Domain types mirror docs/DATA_MODEL.md so the UI stays aligned with the
// backend contract that Phase 2 will implement. Phase 1 renders mock data only.

export type Outcome = "Eligible" | "Needs Review" | "Not Recommended"

export type ApplicationStatus =
  | "draft"
  | "submitted"
  | "needs_review"
  | "ready_for_report"
  | "closed"

export interface Applicant {
  name: string
  email: string
  programme: string
  institution: string
  applicationId: string
  status: ApplicationStatus
  submittedAt: string
}

export interface AcademicRecord {
  cgpa: number // 0–10
  tenthPercent: number // 0–100
  twelfthPercent: number // 0–100
  backlogs: number
}

export interface FinancialProfile {
  householdIncome: number // INR / year
  existingEmi: number // INR / month
  tuitionFee: number // INR / year
  requestedLoan: number // INR
}

/** One weighted line item behind the scholarship score. */
export interface ScoreFactor {
  label: string
  weight: number // 0–1
  rawValue: string // human-readable input, e.g. "8.6 / 10"
  normalized: number // 0–100 contribution before weighting
  weightedPoints: number // normalized × weight
}

export interface ScholarshipAssessment {
  score: number // 0–100
  factors: ScoreFactor[]
  scholarshipPercent: number // % of tuition
  scholarshipAmount: number // INR
  outcome: Outcome
  ruleEngineVersion: string
  computedAt: string
}

export interface LoanAssessment {
  reducedLoanAmount: number // INR
  availableMonthlyCapacity: number // INR / month
  estimatedNewEmi: number // INR / month
  tenureMonths: number
  outcome: Outcome
  confidence: number // 0–100
  ruleEngineVersion: string
  computedAt: string
}

export interface FairnessCheck {
  passed: boolean
  screenedProxies: string[]
  note: string
}

export interface ExplanationReport {
  recommendationText: string
  reasons: string[]
  confidenceNote: string
  fairnessNote: string
  llmPromptVersion: string
  generatedAt: string
}

export interface AssessmentResult {
  applicant: Applicant
  academic: AcademicRecord
  financial: FinancialProfile
  scholarship: ScholarshipAssessment
  loan: LoanAssessment
  fairness: FairnessCheck
  explanation: ExplanationReport
}
