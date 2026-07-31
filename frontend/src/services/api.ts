import { mockAssessment } from "@/lib/mock-data"
import type { AssessmentResult } from "@/types/assessment"

// Mock delay to simulate network latency
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const applicationApi = {
  getAssessment: async (_applicationId: string): Promise<AssessmentResult> => {
    await delay(800)
    // Always return mock data for Phase 1
    return mockAssessment
  },
  
  submitApplication: async (_data: any): Promise<{ applicationId: string }> => {
    await delay(1200)
    return { applicationId: "mock-123" }
  },

  getDashboardStats: async () => {
    await delay(600)
    return {
      totalApplications: 1245,
      approved: 890,
      needsReview: 210,
      rejected: 145,
      fairnessFlagRate: 4.2
    }
  },

  getReviewQueue: async () => {
    await delay(700)
    return [
      { id: "APP-2026-004182", name: "Priya Sharma", status: "needs_review", date: "2026-07-24", score: 85.6 },
      { id: "APP-2026-004183", name: "Rahul Verma", status: "needs_review", date: "2026-07-24", score: 72.1 },
    ]
  }
}
