import { 
  mockAssessment, 
  DASHBOARD_STATS, 
  REVIEW_QUEUE, 
  volumeData, 
  outcomeData, 
  RECENT_APPLICATIONS 
} from "@/data/mock-data"
import type { AssessmentResult } from "@/types/assessment"

// Mock delay to simulate network latency
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const applicationApi = {
  getAssessment: async (_applicationId: string): Promise<AssessmentResult> => {
    await delay(800)
    return mockAssessment
  },
  
  submitApplication: async (_data: any): Promise<{ applicationId: string }> => {
    await delay(1200)
    return { applicationId: "mock-123" }
  },

  getDashboardStats: async () => {
    await delay(600)
    return DASHBOARD_STATS
  },

  getReviewQueue: async () => {
    await delay(700)
    return REVIEW_QUEUE
  },

  getVolumeData: async () => {
    await delay(400)
    return volumeData
  },

  getOutcomeData: async () => {
    await delay(400)
    return outcomeData
  },

  getRecentApplications: async () => {
    await delay(500)
    return RECENT_APPLICATIONS
  }
}
