/**
 * FairExplain AI — Unified API Client
 * =====================================
 * Single typed client managing all backend communications.
 * Respects `VITE_USE_MOCKS` and seamlessly falls back to high-fidelity domain fixtures
 * if the backend is temporarily unreachable.
 */

import { env } from "@/config/env"
import type {
  AdminAnalyticsResponse,
  ApplicationProfile,
  BaseResponse,
  ConsolidatedDossierDTO,
  ExplanationReportDTO,
  FairnessMetricsDTO,
  LoanAssessResponseData,
  ReviewDecisionPayload,
  ReviewDecisionResponse,
  ReviewQueueItem,
  ScholarshipEvaluationDTO,
  ScholarshipPolicySpec,
  UploadedDocumentDTO,
  VerificationResultDTO,
} from "@/types/domain"
import {
  MOCK_ADMIN_ANALYTICS,
  MOCK_APPLICATIONS,
  MOCK_CONSOLIDATED_DOSSIER,
  MOCK_DOCUMENTS,
  MOCK_EXPLANATION,
  MOCK_FAIRNESS_METRICS,
  MOCK_LOAN_ASSESSMENT,
  MOCK_REVIEW_QUEUE,
  MOCK_SCHOLARSHIP_EVALUATION,
  MOCK_SCHOLARSHIP_POLICIES,
  MOCK_VERIFICATION_RESULT,
} from "./mock-provider"

class ApiClient {
  private baseUrl: string
  private useMocks: boolean

  constructor() {
    this.baseUrl = env.apiBaseUrl.replace(/\/$/, "")
    this.useMocks = env.useMocks
  }

  /**
   * Safe fetch wrapper handling JSON envelope, errors, and fallback.
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    mockFallback?: T
  ): Promise<T> {
    if (this.useMocks && mockFallback !== undefined) {
      await new Promise((r) => setTimeout(r, 80)) // simulate brief network tick
      return mockFallback
    }

    try {
      const url = `${this.baseUrl}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`
      const headers = new Headers(options.headers || {})
      if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
        headers.set("Content-Type", "application/json")
      }

      const res = await fetch(url, {
        ...options,
        headers,
      })

      if (!res.ok) {
        let errMessage = `Request failed with status ${res.status}`
        try {
          const errBody = await res.json()
          if (errBody.detail) {
            errMessage = typeof errBody.detail === "string" ? errBody.detail : JSON.stringify(errBody.detail)
          } else if (errBody.message) {
            errMessage = errBody.message
          }
        } catch {
          // ignore parsing error
        }
        throw new Error(errMessage)
      }

      const body: BaseResponse<T> = await res.json()
      if (body.data !== null && body.data !== undefined) {
        return body.data
      }
      return body as unknown as T
    } catch (error) {
      if (mockFallback !== undefined) {
        console.warn(`[ApiClient] Endpoint '${endpoint}' unreachable. Using typed mock fallback.`, error)
        return mockFallback
      }
      throw error
    }
  }

  // -------------------------------------------------------------------------
  // Applications
  // -------------------------------------------------------------------------

  async createApplication(payload: {
    name: string
    email: string
    academic_record: {
      cgpa: number | string
      tenth_percent: number | string
      twelfth_percent: number | string
      backlogs: number
    }
    financial_profile: {
      household_income: number | string
      existing_emi: number | string
      tuition_fee: number | string
      requested_loan: number | string
    }
  }): Promise<{ application_id: string; status: string }> {
    const mockApp = {
      application_id: `app_${Date.now()}`,
      status: "submitted",
    }
    return this.request<{ application_id: string; status: string }>(
      "/api/v1/application",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      mockApp
    )
  }

  async getApplication(applicationId: string): Promise<ApplicationProfile> {
    const mockMatch =
      MOCK_APPLICATIONS.find((a) => a.application_id === applicationId) ||
      MOCK_APPLICATIONS[0]

    return this.request<ApplicationProfile>(
      `/api/v1/application/${applicationId}`,
      { method: "GET" },
      mockMatch
    )
  }

  // -------------------------------------------------------------------------
  // Scholarship & Tuition Accounting
  // -------------------------------------------------------------------------

  async evaluateScholarship(
    applicationId: string,
    programId: string = "MERIT_NEED_2026",
    policyVersion?: string
  ): Promise<ScholarshipEvaluationDTO> {
    const fallback = {
      ...MOCK_SCHOLARSHIP_EVALUATION,
      application_id: applicationId,
      program_id: programId,
    }

    return this.request<ScholarshipEvaluationDTO>(
      "/api/v1/scholarship/evaluate",
      {
        method: "POST",
        body: JSON.stringify({
          application_id: applicationId,
          program_id: programId,
          policy_version: policyVersion,
        }),
      },
      fallback
    )
  }

  // -------------------------------------------------------------------------
  // Loan Affordability
  // -------------------------------------------------------------------------

  async assessLoan(
    applicationId: string,
    tenureMonths: number = 60,
    requestedLoanAmount?: number | string
  ): Promise<LoanAssessResponseData> {
    const fallback = {
      ...MOCK_LOAN_ASSESSMENT,
      application_id: applicationId,
      tenure_months: tenureMonths,
    }

    return this.request<LoanAssessResponseData>(
      "/api/v1/loan/assess",
      {
        method: "POST",
        body: JSON.stringify({
          application_id: applicationId,
          tenure_months: tenureMonths,
          requested_loan_amount: requestedLoanAmount,
        }),
      },
      fallback
    )
  }

  // -------------------------------------------------------------------------
  // Documents & OCR
  // -------------------------------------------------------------------------

  async uploadDocument(
    applicationId: string,
    docType: string,
    file: File
  ): Promise<UploadedDocumentDTO> {
    const formData = new FormData()
    formData.append("application_id", applicationId)
    formData.append("doc_type", docType)
    formData.append("file", file)

    const fallback: UploadedDocumentDTO = {
      id: `doc_${Date.now()}`,
      application_id: applicationId,
      doc_type: docType,
      file_url: URL.createObjectURL(file),
      mismatch_flag: false,
      ocr_extracted_data: { filename: file.name, size: file.size },
      created_at: new Date().toISOString(),
    }

    return this.request<UploadedDocumentDTO>(
      "/api/v1/documents/upload",
      {
        method: "POST",
        body: formData,
      },
      fallback
    )
  }

  async listDocuments(applicationId: string): Promise<UploadedDocumentDTO[]> {
    return this.request<UploadedDocumentDTO[]>(
      `/api/v1/documents/application/${applicationId}`,
      { method: "GET" },
      MOCK_DOCUMENTS
    )
  }

  async verifyDocuments(applicationId: string): Promise<VerificationResultDTO> {
    return this.request<VerificationResultDTO>(
      `/api/v1/documents/verify/${applicationId}`,
      { method: "POST" },
      MOCK_VERIFICATION_RESULT
    )
  }

  // -------------------------------------------------------------------------
  // Explainability & Grounded LLM Layer
  // -------------------------------------------------------------------------

  async generateExplanation(applicationId: string): Promise<ExplanationReportDTO> {
    const fallback: ExplanationReportDTO = {
      application_id: applicationId,
      prompt_version: "v1.0-phase4",
      explanation: MOCK_EXPLANATION,
      created_at: new Date().toISOString(),
    }

    return this.request<ExplanationReportDTO>(
      "/api/v1/explanation/generate",
      {
        method: "POST",
        body: JSON.stringify({ application_id: applicationId }),
      },
      fallback
    )
  }

  async getExplanation(applicationId: string): Promise<ExplanationReportDTO> {
    const fallback: ExplanationReportDTO = {
      application_id: applicationId,
      prompt_version: "v1.0-phase4",
      explanation: MOCK_EXPLANATION,
    }

    return this.request<ExplanationReportDTO>(
      `/api/v1/explanation/${applicationId}`,
      { method: "GET" },
      fallback
    )
  }

  // -------------------------------------------------------------------------
  // Reviewer Queue & Governance
  // -------------------------------------------------------------------------

  async getReviewQueue(
    status: string = "all",
    page: number = 1,
    pageSize: number = 50
  ): Promise<{ items: ReviewQueueItem[]; total: number; page: number; page_size: number }> {
    const fallback = {
      items: MOCK_REVIEW_QUEUE,
      total: MOCK_REVIEW_QUEUE.length,
      page,
      page_size: pageSize,
    }

    const query = new URLSearchParams({
      status,
      page: String(page),
      page_size: String(pageSize),
    })

    return this.request<{ items: ReviewQueueItem[]; total: number; page: number; page_size: number }>(
      `/api/v1/admin/review-queue?${query.toString()}`,
      { method: "GET" },
      fallback
    )
  }

  async getReviewContext(applicationId: string): Promise<ConsolidatedDossierDTO> {
    const fallback: ConsolidatedDossierDTO = {
      ...MOCK_CONSOLIDATED_DOSSIER,
      application_id: applicationId,
    }

    return this.request<ConsolidatedDossierDTO>(
      `/api/v1/admin/application/${applicationId}/review-context`,
      { method: "GET" },
      fallback
    )
  }

  async recordDecision(
    applicationId: string,
    payload: ReviewDecisionPayload
  ): Promise<ReviewDecisionResponse> {
    const fallback: ReviewDecisionResponse = {
      application_id: applicationId,
      status: payload.decision === "approve" ? "ready_for_report" : payload.decision === "reject" ? "closed" : "needs_review",
      decision: payload.decision,
      rationale: payload.rationale,
      audit_log_id: `audit_${Date.now()}`,
    }

    return this.request<ReviewDecisionResponse>(
      `/api/v1/admin/application/${applicationId}/decision`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
      fallback
    )
  }

  // -------------------------------------------------------------------------
  // Institutional Analytics & Fairness Screening
  // -------------------------------------------------------------------------

  async getAdminAnalytics(): Promise<AdminAnalyticsResponse> {
    return this.request<AdminAnalyticsResponse>(
      "/api/v1/admin/analytics",
      { method: "GET" },
      MOCK_ADMIN_ANALYTICS
    )
  }

  async getFairnessMetrics(): Promise<FairnessMetricsDTO> {
    return this.request<FairnessMetricsDTO>(
      "/api/v1/admin/fairness/metrics",
      { method: "GET" },
      MOCK_FAIRNESS_METRICS
    )
  }

  async auditFairness(applicationId: string): Promise<{
    application_id: string
    total_violations: number
    violations: unknown[]
    requires_human_fairness_review: boolean
  }> {
    const fallback = {
      application_id: applicationId,
      total_violations: 0,
      violations: [],
      requires_human_fairness_review: false,
    }

    return this.request<{
      application_id: string
      total_violations: number
      violations: unknown[]
      requires_human_fairness_review: boolean
    }>(
      `/api/v1/admin/fairness/audit/${applicationId}`,
      { method: "POST" },
      fallback
    )
  }

  // -------------------------------------------------------------------------
  // PDF Report
  // -------------------------------------------------------------------------

  async downloadReportPdf(applicationId: string): Promise<Blob | null> {
    try {
      const res = await fetch(`${this.baseUrl}/api/v1/report/${applicationId}/pdf`)
      if (res.ok) {
        return await res.blob()
      }
    } catch {
      // offline fallback
    }
    return null
  }

  // -------------------------------------------------------------------------
  // Policy Viewer (Admin)
  // -------------------------------------------------------------------------

  async getPolicies(): Promise<ScholarshipPolicySpec[]> {
    return MOCK_SCHOLARSHIP_POLICIES
  }
}

export const apiClient = new ApiClient()
