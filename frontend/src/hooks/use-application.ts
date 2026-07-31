import { useQuery, useMutation } from "@tanstack/react-query"
import { applicationApi } from "@/services/api"

export function useAssessment(applicationId: string | undefined) {
  return useQuery({
    queryKey: ["assessment", applicationId],
    queryFn: () => applicationApi.getAssessment(applicationId!),
    enabled: !!applicationId,
  })
}

export function useSubmitApplication() {
  return useMutation({
    mutationFn: applicationApi.submitApplication,
  })
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboardStats"],
    queryFn: applicationApi.getDashboardStats,
  })
}

export function useReviewQueue() {
  return useQuery({
    queryKey: ["reviewQueue"],
    queryFn: applicationApi.getReviewQueue,
  })
}

export function useVolumeData() {
  return useQuery({
    queryKey: ["volumeData"],
    queryFn: applicationApi.getVolumeData,
  })
}

export function useOutcomeData() {
  return useQuery({
    queryKey: ["outcomeData"],
    queryFn: applicationApi.getOutcomeData,
  })
}

export function useRecentApplications() {
  return useQuery({
    queryKey: ["recentApplications"],
    queryFn: applicationApi.getRecentApplications,
  })
}
