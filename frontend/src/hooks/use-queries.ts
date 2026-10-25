/**
 * FairExplain AI — TanStack Query Hooks
 * =======================================
 * Declarative data fetching, cache invalidation, and mutations.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/services/api-client"
import type { ReviewDecisionPayload } from "@/types/domain"

// ---------------------------------------------------------------------------
// Student Queries & Mutations
// ---------------------------------------------------------------------------

export function useApplication(applicationId: string | undefined) {
  return useQuery({
    queryKey: ["application", applicationId],
    queryFn: () => apiClient.getApplication(applicationId!),
    enabled: !!applicationId,
  })
}

export function useScholarshipEvaluation(
  applicationId: string | undefined,
  programId: string = "MERIT_NEED_2026"
) {
  return useQuery({
    queryKey: ["scholarship_evaluation", applicationId, programId],
    queryFn: () => apiClient.evaluateScholarship(applicationId!, programId),
    enabled: !!applicationId,
  })
}

export function useLoanAssessment(
  applicationId: string | undefined,
  tenureMonths: number = 60
) {
  return useQuery({
    queryKey: ["loan_assessment", applicationId, tenureMonths],
    queryFn: () => apiClient.assessLoan(applicationId!, tenureMonths),
    enabled: !!applicationId,
  })
}

export function useExplanation(applicationId: string | undefined) {
  return useQuery({
    queryKey: ["explanation", applicationId],
    queryFn: () => apiClient.getExplanation(applicationId!),
    enabled: !!applicationId,
    retry: 1,
  })
}

export function useDocuments(applicationId: string | undefined) {
  return useQuery({
    queryKey: ["documents", applicationId],
    queryFn: () => apiClient.listDocuments(applicationId!),
    enabled: !!applicationId,
  })
}

export function useCreateApplication() {
  const queryClient = useQueryClient()
  return useMutation<{ application_id: string; status: string }, Error, Parameters<typeof apiClient.createApplication>[0]>({
    mutationFn: (payload) => apiClient.createApplication(payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["application", data.application_id] })
      queryClient.invalidateQueries({ queryKey: ["review_queue"] })
    },
  })
}

export function useUploadDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      applicationId,
      docType,
      file,
    }: {
      applicationId: string
      docType: string
      file: File
    }) => apiClient.uploadDocument(applicationId, docType, file),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ["documents", vars.applicationId] })
    },
  })
}

export function useVerifyDocuments() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (applicationId: string) => apiClient.verifyDocuments(applicationId),
    onSuccess: (_, applicationId) => {
      queryClient.invalidateQueries({ queryKey: ["documents", applicationId] })
      queryClient.invalidateQueries({ queryKey: ["review_context", applicationId] })
    },
  })
}

// ---------------------------------------------------------------------------
// Reviewer Queries & Mutations
// ---------------------------------------------------------------------------

export function useReviewQueue(status: string = "all", page: number = 1, pageSize: number = 50) {
  return useQuery({
    queryKey: ["review_queue", status, page, pageSize],
    queryFn: () => apiClient.getReviewQueue(status, page, pageSize),
  })
}

export function useReviewContext(applicationId: string | undefined) {
  return useQuery({
    queryKey: ["review_context", applicationId],
    queryFn: () => apiClient.getReviewContext(applicationId!),
    enabled: !!applicationId,
  })
}

export function useRecordDecision() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      applicationId,
      payload,
    }: {
      applicationId: string
      payload: ReviewDecisionPayload
    }) => apiClient.recordDecision(applicationId, payload),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ["review_context", vars.applicationId] })
      queryClient.invalidateQueries({ queryKey: ["review_queue"] })
      queryClient.invalidateQueries({ queryKey: ["admin_analytics"] })
    },
  })
}

// ---------------------------------------------------------------------------
// Admin Queries
// ---------------------------------------------------------------------------

export function useAdminAnalytics() {
  return useQuery({
    queryKey: ["admin_analytics"],
    queryFn: () => apiClient.getAdminAnalytics(),
  })
}

export function useFairnessMetrics() {
  return useQuery({
    queryKey: ["fairness_metrics"],
    queryFn: () => apiClient.getFairnessMetrics(),
  })
}

export function usePolicies() {
  return useQuery({
    queryKey: ["admin_policies"],
    queryFn: () => apiClient.getPolicies(),
  })
}
