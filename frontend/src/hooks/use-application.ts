import { useQuery, useMutation } from "@tanstack/react-query"
import { applicationApi } from "@/services/api"
import type {
  DashboardStats,
  OutcomeDataPoint,
  RecentApplication,
  ReviewQueueItem,
  SubmitApplicationResponse,
  VolumeDataPoint,
} from "@/types/api"
import type { AssessmentResult } from "@/types/assessment"

export function useAssessment(applicationId: string | undefined) {
  return useQuery<AssessmentResult>({
    queryKey: ["assessment", applicationId],
    queryFn: () => applicationApi.getAssessment(applicationId!),
    enabled: !!applicationId,
  })
}

export function useSubmitApplication() {
  return useMutation<SubmitApplicationResponse, Error, Parameters<typeof applicationApi.submitApplication>[0]>({
    mutationFn: applicationApi.submitApplication,
  })
}

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ["dashboardStats"],
    queryFn: applicationApi.getDashboardStats,
  })
}

export function useReviewQueue() {
  return useQuery<ReviewQueueItem[]>({
    queryKey: ["reviewQueue"],
    queryFn: applicationApi.getReviewQueue,
  })
}

export function useVolumeData() {
  return useQuery<VolumeDataPoint[]>({
    queryKey: ["volumeData"],
    queryFn: applicationApi.getVolumeData,
  })
}

export function useOutcomeData() {
  return useQuery<OutcomeDataPoint[]>({
    queryKey: ["outcomeData"],
    queryFn: applicationApi.getOutcomeData,
  })
}

export function useRecentApplications() {
  return useQuery<RecentApplication[]>({
    queryKey: ["recentApplications"],
    queryFn: applicationApi.getRecentApplications,
  })
}
