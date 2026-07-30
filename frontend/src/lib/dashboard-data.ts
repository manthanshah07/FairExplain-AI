import type { ApplicationStatus, Outcome } from "@/types/assessment"

// Phase 1 dashboard mock data. Mirrors the shapes the FastAPI backend will
// return so the UI stays aligned with the eventual API contract.

export interface DashboardApplication {
  applicationId: string
  name: string
  programme: string
  institution: string
  scholarshipScore: number
  requestedLoan: number
  outcome: Outcome
  status: ApplicationStatus
  submittedAt: string
}

export interface DashboardKpi {
  label: string
  value: string
  delta: number // percentage change vs. previous period
  hint: string
}

export const dashboardKpis: DashboardKpi[] = [
  {
    label: "Applications processed",
    value: "1,284",
    delta: 12.4,
    hint: "vs. previous 30 days",
  },
  {
    label: "Awaiting human review",
    value: "37",
    delta: -8.1,
    hint: "queued for reviewers",
  },
  {
    label: "Avg. scholarship score",
    value: "72.6",
    delta: 3.2,
    hint: "across approved applicants",
  },
  {
    label: "Fairness checks passed",
    value: "99.2%",
    delta: 0.4,
    hint: "no proxy attributes detected",
  },
]

export const applicationsTrend: { month: string; processed: number; reviewed: number }[] = [
  { month: "Feb", processed: 142, reviewed: 128 },
  { month: "Mar", processed: 168, reviewed: 151 },
  { month: "Apr", processed: 190, reviewed: 174 },
  { month: "May", processed: 214, reviewed: 205 },
  { month: "Jun", processed: 236, reviewed: 219 },
  { month: "Jul", processed: 284, reviewed: 247 },
]

export const outcomeDistribution: { outcome: Outcome; count: number; fill: string }[] = [
  { outcome: "Eligible", count: 812, fill: "var(--chart-2)" },
  { outcome: "Needs Review", count: 341, fill: "var(--chart-3)" },
  { outcome: "Not Recommended", count: 131, fill: "var(--chart-4)" },
]

export const recentApplications: DashboardApplication[] = [
  {
    applicationId: "APP-2026-004182",
    name: "Priya Sharma",
    programme: "B.Tech, Computer Science",
    institution: "National Institute of Technology",
    scholarshipScore: 85.6,
    requestedLoan: 800000,
    outcome: "Eligible",
    status: "ready_for_report",
    submittedAt: "2026-07-24T09:12:00Z",
  },
  {
    applicationId: "APP-2026-004179",
    name: "Arjun Mehta",
    programme: "B.Com, Finance",
    institution: "Delhi University",
    scholarshipScore: 64.2,
    requestedLoan: 450000,
    outcome: "Needs Review",
    status: "needs_review",
    submittedAt: "2026-07-24T08:47:00Z",
  },
  {
    applicationId: "APP-2026-004176",
    name: "Fatima Khan",
    programme: "M.Sc, Biotechnology",
    institution: "Jamia Millia Islamia",
    scholarshipScore: 91.3,
    requestedLoan: 620000,
    outcome: "Eligible",
    status: "ready_for_report",
    submittedAt: "2026-07-23T18:05:00Z",
  },
  {
    applicationId: "APP-2026-004170",
    name: "Rahul Verma",
    programme: "B.Tech, Mechanical",
    institution: "VIT Vellore",
    scholarshipScore: 48.9,
    requestedLoan: 900000,
    outcome: "Not Recommended",
    status: "closed",
    submittedAt: "2026-07-23T14:33:00Z",
  },
  {
    applicationId: "APP-2026-004168",
    name: "Ananya Iyer",
    programme: "B.Arch",
    institution: "CEPT University",
    scholarshipScore: 77.4,
    requestedLoan: 550000,
    outcome: "Eligible",
    status: "submitted",
    submittedAt: "2026-07-23T11:20:00Z",
  },
  {
    applicationId: "APP-2026-004165",
    name: "Karthik Nair",
    programme: "MBA",
    institution: "IIM Kozhikode",
    scholarshipScore: 69.1,
    requestedLoan: 1200000,
    outcome: "Needs Review",
    status: "needs_review",
    submittedAt: "2026-07-22T16:58:00Z",
  },
]

export const STATUS_LABELS: Record<ApplicationStatus, string> = {
  draft: "Draft",
  submitted: "Submitted",
  needs_review: "Needs review",
  ready_for_report: "Ready for report",
  closed: "Closed",
}
