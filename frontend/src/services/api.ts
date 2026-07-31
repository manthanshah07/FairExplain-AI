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

// Mock delay to simulate network latency
const delay = (ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms))

export const applicationApi = {
  getAssessment: async (_applicationId: string): Promise<AssessmentResult> => {
    await delay(800)
    return mockAssessment
  },
  
  submitApplication: async (_data: ApplicationFormData): Promise<SubmitApplicationResponse> => {
    await delay(1200)
    return { applicationId: "mock-123" }
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    await delay(600)
    return DASHBOARD_STATS
  },

  getReviewQueue: async (): Promise<ReviewQueueItem[]> => {
    await delay(700)
    return REVIEW_QUEUE
  },

  getVolumeData: async (): Promise<VolumeDataPoint[]> => {
    await delay(400)
    return volumeData
  },

  getOutcomeData: async (): Promise<OutcomeDataPoint[]> => {
    await delay(400)
    return outcomeData
  },

  getRecentApplications: async (): Promise<RecentApplication[]> => {
    await delay(500)
    return RECENT_APPLICATIONS
  }
}
