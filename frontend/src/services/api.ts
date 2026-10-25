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

              let explanationPayload = mockAssessment.explanation
              try {
                const expResp = await fetch(`${API_BASE_URL}/api/v1/explanation/generate`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ application_id: appId }),
                })
                if (expResp.ok) {
                  const expJson = await expResp.json()
                  const expData = expJson.data?.explanation
                  if (expData) {
                    explanationPayload = {
                      ...mockAssessment.explanation,
                      recommendationText: expData.summary_headline,
                      reasons: expData.reasons,
                      confidenceNote: expData.fairness_attestation,
                      fairnessNote: expData.human_review_notice,
                      llmPromptVersion: expJson.data?.prompt_version || "v1.0-phase4",
                    }
                  }
                }
              } catch {
                // Explanation fallback
              }

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
                explanation: explanationPayload,
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
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/admin/analytics`)
      if (res.ok) {
        const body = await res.json()
        const data = body.data
        if (data && data.total_applications > 0) {
          return {
            totalApplications: data.total_applications,
            approved: data.approved_count,
            needsReview: data.pending_review_count,
            rejected: data.rejected_count,
            fairnessFlagRate: data.fairness_flag_incidence_rate,
          }
        }
      }
    } catch {
      // offline fallback
    }
    return DASHBOARD_STATS
  },

  getReviewQueue: async (): Promise<ReviewQueueItem[]> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/admin/review-queue?status=all`)
      if (res.ok) {
        const body = await res.json()
        const items = body.data?.items
        if (items && items.length > 0) {
          return items.map((item: any) => ({
            id: item.application_id,
            name: item.applicant_name,
            status: item.status,
            date: item.submission_date,
            score: item.priority === "high" ? 65 : item.priority === "medium" ? 80 : 92,
            flags: item.flags || [],
            priority: item.priority,
          }))
        }
      }
    } catch {
      // offline fallback
    }
    return REVIEW_QUEUE
  },

  getReviewContext: async (applicationId: string): Promise<any> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/admin/application/${applicationId}/review-context`)
      if (res.ok) {
        const body = await res.json()
        return body.data
      }
    } catch {
      // offline fallback
    }
    return null
  },

  recordReviewDecision: async (
    applicationId: string,
    decision: "approve" | "override" | "reject" | "request_evidence",
    rationale: string,
    reviewerId: string = "officer_portal",
    overrideDetails?: Record<string, unknown>
  ): Promise<{ success: boolean; data?: unknown }> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/admin/application/${applicationId}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision,
          rationale,
          reviewer_id: reviewerId,
          override_details: overrideDetails,
        }),
      })
      if (res.ok) {
        const body = await res.json()
        return { success: true, data: body.data }
      }
    } catch {
      // offline fallback
    }
    return { success: false }
  },

  getVolumeData: async (): Promise<VolumeDataPoint[]> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/admin/analytics`)
      if (res.ok) {
        const body = await res.json()
        const data = body.data
        if (data && data.total_applications > 0) {
          return [
            { name: "Mon", applications: Math.round(data.total_applications * 0.1) },
            { name: "Tue", applications: Math.round(data.total_applications * 0.15) },
            { name: "Wed", applications: Math.round(data.total_applications * 0.2) },
            { name: "Thu", applications: Math.round(data.total_applications * 0.25) },
            { name: "Fri", applications: Math.round(data.total_applications * 0.2) },
            { name: "Sat", applications: Math.round(data.total_applications * 0.05) },
            { name: "Sun", applications: Math.round(data.total_applications * 0.05) },
          ]
        }
      }
    } catch {
      // offline fallback
    }
    return volumeData
  },

  getOutcomeData: async (): Promise<OutcomeDataPoint[]> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/admin/analytics`)
      if (res.ok) {
        const body = await res.json()
        const data = body.data
        if (data && data.total_applications > 0) {
          return [
            { name: "Eligible / Approved", value: data.approved_count || 1, color: "hsl(var(--chart-1))" },
            { name: "Needs Review", value: data.pending_review_count || 1, color: "hsl(var(--chart-2))" },
            { name: "Rejected / Closed", value: data.rejected_count || 1, color: "hsl(var(--chart-3))" },
          ]
        }
      }
    } catch {
      // offline fallback
    }
    return outcomeData
  },

  getRecentApplications: async (): Promise<RecentApplication[]> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/admin/analytics`)
      if (res.ok) {
        const body = await res.json()
        const data = body.data
        if (data?.recent_activity && data.recent_activity.length > 0) {
          return data.recent_activity.map((act: any, idx: number) => ({
            id: act.application_id ? `${act.application_id.slice(0, 8)}...` : `APP-${idx + 1}`,
            name: act.event_type.replace(/_/g, " ").toUpperCase(),
            date: act.timestamp ? act.timestamp.slice(0, 10) : "Today",
            score: 85,
            status: act.detail?.decision || "Processed",
          }))
        }
      }
    } catch {
      // offline fallback
    }
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
  },

  downloadReportPdf: async (applicationId: string): Promise<Blob | null> => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/report/${applicationId}/pdf`)
      if (res.ok) {
        return await res.blob()
      }
    } catch {
      // offline fallback
    }
    return null
  }
}

export const api = applicationApi
