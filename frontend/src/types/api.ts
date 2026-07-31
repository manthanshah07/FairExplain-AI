// Shared domain types for API request payloads.
// Mirrors the form schemas in the pages layer without coupling services to UI.

export interface ApplicationFormData {
  cgpa: number
  tenth: number
  twelfth: number
  backlogs: number
  income: number
  emi: number
  tuition: number
  loan: number
}

export interface SubmitApplicationResponse {
  applicationId: string
}

export interface DashboardStats {
  totalApplications: number
  approved: number
  needsReview: number
  rejected: number
  fairnessFlagRate: number
}

export interface ReviewQueueItem {
  id: string
  name: string
  status: string
  date: string
  score: number
}

export interface RecentApplication {
  id: string
  name: string
  date: string
  score: number
  status: string
}

export interface VolumeDataPoint {
  name: string
  applications: number
}

export interface OutcomeDataPoint {
  name: string
  value: number
  color: string
}
