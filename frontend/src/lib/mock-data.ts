import type { AssessmentResult } from "@/types/assessment"

const RULE_ENGINE_VERSION = "1.0.0"

// Mock assessment used across Phase 1 (UI only). Numbers follow the formulas in
// docs/RULE_ENGINE.md so the results screen is representative of real output.
export const mockAssessment: AssessmentResult = {
  applicant: {
    name: "Priya Sharma",
    email: "priya.sharma@example.edu",
    programme: "B.Tech, Computer Science",
    institution: "National Institute of Technology",
    applicationId: "APP-2026-004182",
    status: "ready_for_report",
    submittedAt: "2026-07-24T09:12:00Z",
  },
  academic: {
    cgpa: 8.6,
    tenthPercent: 91,
    twelfthPercent: 89,
    backlogs: 0,
  },
  financial: {
    householdIncome: 420000,
    existingEmi: 3000,
    tuitionFee: 320000,
    requestedLoan: 800000,
  },
  scholarship: {
    score: 85.6,
    factors: [
      {
        label: "CGPA",
        weight: 0.4,
        rawValue: "8.6 / 10",
        normalized: 86,
        weightedPoints: 34.4,
      },
      {
        label: "12th Percentage",
        weight: 0.2,
        rawValue: "89%",
        normalized: 89,
        weightedPoints: 17.8,
      },
      {
        label: "Household Income (need)",
        weight: 0.3,
        rawValue: "₹4.2L / year",
        normalized: 78,
        weightedPoints: 23.4,
      },
      {
        label: "Active Backlogs",
        weight: 0.1,
        rawValue: "0",
        normalized: 100,
        weightedPoints: 10,
      },
    ],
    scholarshipPercent: 75,
    scholarshipAmount: 240000,
    outcome: "Eligible",
    ruleEngineVersion: RULE_ENGINE_VERSION,
    computedAt: "2026-07-24T09:12:04Z",
  },
  loan: {
    reducedLoanAmount: 560000,
    availableMonthlyCapacity: 11000,
    estimatedNewEmi: 6667,
    tenureMonths: 84,
    outcome: "Eligible",
    confidence: 82,
    ruleEngineVersion: RULE_ENGINE_VERSION,
    computedAt: "2026-07-24T09:12:04Z",
  },
  fairness: {
    passed: true,
    screenedProxies: [
      "Pincode / geography",
      "Surname-based inference",
      "Institution as socioeconomic proxy",
    ],
    note: "No protected attributes or indirect proxies influenced this assessment. Caste, religion, gender, disability status, and region are never used as inputs.",
  },
  explanation: {
    recommendationText:
      "This applicant is recommended for a 75% tuition scholarship and is assessed as eligible for the reduced education loan, pending human sign-off.",
    reasons: [
      "Strong academic record (CGPA 8.6/10, 89% in 12th) with zero active backlogs drives a scholarship score of 85.6, placing the applicant in the top eligibility band.",
      "Household income of ₹4.2L/year indicates genuine financial need, contributing 23.4 of the weighted points toward the scholarship.",
      "The 75% scholarship reduces the required loan from ₹8.0L to ₹5.6L, bringing the estimated monthly EMI (₹6,667) comfortably within the assessed repayment capacity (₹11,000).",
    ],
    confidenceNote:
      "Confidence is 82% because the estimated EMI sits well below the repayment-capacity threshold, leaving a healthy affordability margin.",
    fairnessNote:
      "Fairness Checker passed. The explanation references only academic and financial factors — no proxy attributes were detected.",
    llmPromptVersion: "explain-v1",
    generatedAt: "2026-07-24T09:12:07Z",
  },
}

export function formatINR(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value)
}
