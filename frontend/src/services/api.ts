import { 
  mockAssessment, 
  DASHBOARD_STATS, 
  REVIEW_QUEUE, 
  volumeData, 
  outcomeData, 
  RECENT_APPLICATIONS 
} from "@/data/mock-data"
import type { AssessmentResult } from "@/types/assessment"
import type {
  ApplicationFormData,
  DashboardStats,
  OutcomeDataPoint,
  RecentApplication,
  ReviewQueueItem,
  SubmitApplicationResponse,
  VolumeDataPoint,
} from "@/types/api"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

// In-memory cache for live evaluated assessments
const evaluatedAssessmentsCache = new Map<string, AssessmentResult>()

export const applicationApi = {
  getAssessment: async (applicationId: string): Promise<AssessmentResult> => {
    // If we have an evaluated assessment in cache for this session, return it
    if (evaluatedAssessmentsCache.has(applicationId)) {
      return evaluatedAssessmentsCache.get(applicationId)!
    }

    try {
      const appResp = await fetch(`${API_BASE_URL}/api/v1/application/${applicationId}`, {
        headers: { "Content-Type": "application/json" },
      })
      if (appResp.ok) {
        const appData = await appResp.json()
        if (appData.success && appData.data) {
          // Construct assessment view
          const acad = appData.data.academic_record || {}
          const fin = appData.data.financial_profile || {}
          
          return {
            ...mockAssessment,
            applicant: {
              ...mockAssessment.applicant,
              applicationId: appData.data.application_id,
              name: appData.data.name || "Priya Sharma",
              email: appData.data.email || "priya.sharma@example.edu",
              status: appData.data.status,
            },
            academic: {
              cgpa: Number(acad.cgpa ?? 8.85),
              tenthPercent: Number(acad.tenth_percent ?? 91.5),
              twelfthPercent: Number(acad.twelfth_percent ?? 88.0),
              backlogs: Number(acad.backlogs ?? 0),
            },
            financial: {
              householdIncome: Number(fin.household_income ?? 600000),
              existingEmi: Number(fin.existing_emi ?? 5000),
              tuitionFee: Number(fin.tuition_fee ?? 150000),
              requestedLoan: Number(fin.requested_loan ?? 100000),
            },
          }
        }
      }
    } catch {
      // Backend not running or network error, fallback to mock assessment
    }

    return mockAssessment
  },
  
  submitApplication: async (data: ApplicationFormData): Promise<SubmitApplicationResponse> => {
    try {
      const payload = {
        name: "Applicant",
        email: `applicant_${Date.now()}@example.com`,
        academic_record: {
          cgpa: data.cgpa,
          tenth_percent: data.tenth,
          twelfth_percent: data.twelfth,
          backlogs: data.backlogs,
        },
        financial_profile: {
          household_income: data.income,
          existing_emi: data.emi,
          tuition_fee: data.tuition,
          requested_loan: data.loan,
        },
      }

      const res = await fetch(`${API_BASE_URL}/api/v1/application`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (res.ok) {
        const body = await res.json()
        const appId = body.data?.application_id

        if (appId) {
          // Trigger scholarship and loan evaluations
          try {
            const [scholarshipResp, loanResp] = await Promise.all([
              fetch(`${API_BASE_URL}/api/v1/scholarship/evaluate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ application_id: appId }),
              }),
              fetch(`${API_BASE_URL}/api/v1/loan/assess`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ application_id: appId, tenure_months: 60 }),
              }),
            ])

            if (scholarshipResp.ok && loanResp.ok) {
              const sData = (await scholarshipResp.json()).data
              const lData = (await loanResp.json()).data

              const scholarshipOutcome =
                sData.status === "eligible"
                  ? "Eligible"
                  : sData.status === "pending_evidence"
                  ? "Needs Review"
                  : "Not Recommended"

              const loanOutcome =
                lData.outcome === "eligible"
                  ? "Eligible"
                  : lData.outcome === "needs_review"
                  ? "Needs Review"
                  : "Not Recommended"

              const customAssessment: AssessmentResult = {
                ...mockAssessment,
                applicant: {
                  ...mockAssessment.applicant,
                  applicationId: appId,
                },
                academic: {
                  cgpa: data.cgpa,
                  tenthPercent: data.tenth,
                  twelfthPercent: data.twelfth,
                  backlogs: data.backlogs,
                },
                financial: {
                  householdIncome: data.income,
                  existingEmi: data.emi,
                  tuitionFee: data.tuition,
                  requestedLoan: data.loan,
                },
                scholarship: {
                  ...mockAssessment.scholarship,
                  outcome: scholarshipOutcome,
                  scholarshipPercent: sData.tuition_accounting?.allocations?.[0] ? 50 : 0,
                  scholarshipAmount: Number(
                    sData.tuition_accounting?.total_effective_reduction ?? 0
                  ),
                },
                loan: {
                  ...mockAssessment.loan,
                  outcome: loanOutcome,
                  reducedLoanAmount: Number(lData.post_scholarship_loan_amount),
                  availableMonthlyCapacity: Number(lData.available_monthly_capacity),
                  estimatedNewEmi: Number(lData.estimated_emi),
                  tenureMonths: lData.tenure_months,
                  confidence: 100 - Number(lData.dti_ratio_percent) > 0 ? 100 - Number(lData.dti_ratio_percent) : 50,
                },
              }

              evaluatedAssessmentsCache.set(appId, customAssessment)
            }
          } catch {
            // Evaluations fallback gracefully
          }

          return { applicationId: appId }
        }
      }
    } catch {
      // Backend not running, fallback to mock response
    }

    return { applicationId: "mock-123" }
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    return DASHBOARD_STATS
  },

  getReviewQueue: async (): Promise<ReviewQueueItem[]> => {
    return REVIEW_QUEUE
  },

  getVolumeData: async (): Promise<VolumeDataPoint[]> => {
    return volumeData
  },

  getOutcomeData: async (): Promise<OutcomeDataPoint[]> => {
    return outcomeData
  },

  getRecentApplications: async (): Promise<RecentApplication[]> => {
    return RECENT_APPLICATIONS
  },

  uploadDocument: async (
    applicationId: string,
    docType: string,
    file: File
  ): Promise<{ success: boolean; documentId?: string }> => {
    try {
      const formData = new FormData()
      formData.append("application_id", applicationId)
      formData.append("doc_type", docType)
      formData.append("file", file)

      const res = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
        method: "POST",
        body: formData,
      })
      if (res.ok) {
        const body = await res.json()
        return { success: true, documentId: body.data?.document_id }
      }
    } catch {
      // offline fallback
    }
    return { success: true, documentId: "mock-doc-123" }
  },

  verifyDocuments: async (applicationId: string): Promise<{ verified: boolean; discrepancies: unknown[] }> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/documents/verify/${applicationId}`, {
        method: "POST",
      })
      if (res.ok) {
        const body = await res.json()
        return body.data
      }
    } catch {
      // offline fallback
    }
    return { verified: true, discrepancies: [] }
  }
}
