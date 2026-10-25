/**
 * FairExplain AI — Deterministic Mock Fixtures & Provider
 * ========================================================
 * High-fidelity, mathematically consistent mock data adhering to:
 * - Domain three-state eligibility: ELIGIBLE, INELIGIBLE, PENDING_EVIDENCE
 * - Monetary strings (INR) with explicit Indian grouping support
 * - Real prompt-grounded LLM explanation contract
 * - Realistic document OCR extractions and mismatch flags
 */

import type {
  AdminAnalyticsResponse,
  ApplicationProfile,
  ConsolidatedDossierDTO,
  ExplanationContract,
  FairnessMetricsDTO,
  LoanAssessResponseData,
  ReviewQueueItem,
  ScholarshipEvaluationDTO,
  ScholarshipPolicySpec,
  UploadedDocumentDTO,
  VerificationResultDTO,
} from "@/types/domain"

// ---------------------------------------------------------------------------
// 1. Seed Applications
// ---------------------------------------------------------------------------

export const MOCK_APPLICATIONS: ApplicationProfile[] = [
  {
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    user_id: "usr_priya_sharma",
    status: "ready_for_report",
    name: "Priya Sharma",
    email: "priya.sharma@nitk.edu.in",
    institution: "National Institute of Technology Karnataka",
    programme: "B.Tech Computer Science & Engineering",
    academic_record: {
      cgpa: "8.85",
      tenth_percent: "92.40",
      twelfth_percent: "89.60",
      backlogs: 0,
    },
    financial_profile: {
      household_income: "420000.00",
      existing_emi: "3000.00",
      tuition_fee: "240000.00",
      requested_loan: "480000.00",
    },
    created_at: "2026-10-24T10:15:30Z",
    updated_at: "2026-10-25T08:30:00Z",
  },
  {
    application_id: "611767c7-61c8-4f5d-a299-3561bfc28306",
    user_id: "usr_aarav_patel",
    status: "needs_review",
    name: "Aarav Patel",
    email: "aarav.patel@test.edu",
    institution: "Indian Institute of Information Technology",
    programme: "B.Tech Electronics & Communication",
    academic_record: {
      cgpa: "8.70",
      tenth_percent: "90.00",
      twelfth_percent: "88.00",
      backlogs: 0,
    },
    financial_profile: {
      household_income: "450000.00",
      existing_emi: "4000.00",
      tuition_fee: "250000.00",
      requested_loan: "500000.00",
    },
    created_at: "2026-10-25T08:32:14Z",
    updated_at: "2026-10-25T08:32:14Z",
  },
  {
    application_id: "e4c1973b-5778-4389-9dbb-821945da9b33",
    user_id: "usr_rohit_verma",
    status: "needs_review",
    name: "Rohit Verma",
    email: "rohit.verma@delhi.edu",
    institution: "Delhi Technological University",
    programme: "B.Tech Mechanical Engineering",
    academic_record: {
      cgpa: "7.40",
      tenth_percent: "82.50",
      twelfth_percent: "78.00",
      backlogs: 1,
    },
    financial_profile: {
      household_income: "320000.00",
      existing_emi: "2000.00",
      tuition_fee: "180000.00",
      requested_loan: "360000.00",
    },
    created_at: "2026-10-25T09:12:00Z",
  },
]

// ---------------------------------------------------------------------------
// 2. Deterministic Scholarship Evaluation Fixture (Priya Sharma)
// ---------------------------------------------------------------------------

export const MOCK_SCHOLARSHIP_EVALUATION: ScholarshipEvaluationDTO = {
  application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
  program_id: "MERIT_NEED_2026",
  policy_version: "1.0.0",
  status: "eligible",
  reason: "All mandatory criteria satisfied and supporting evidence verified.",
  satisfied_count: 3,
  failed_count: 0,
  pending_count: 0,
  criteria_evaluations: [
    {
      criterion_id: "CRIT_CGPA",
      attribute: "cgpa",
      operator: "gte",
      target_value: "8.00",
      actual_value: "8.85",
      status: "satisfied",
      is_mandatory: true,
      evidence_required: "marksheet",
      evidence_status: "verified",
      reason: "Actual CGPA of 8.85 satisfies mandatory threshold of at least 8.00.",
    },
    {
      criterion_id: "CRIT_BACKLOGS",
      attribute: "active_backlogs",
      operator: "lte",
      target_value: 0,
      actual_value: 0,
      status: "satisfied",
      is_mandatory: true,
      evidence_required: null,
      evidence_status: "not_required",
      reason: "Active backlogs count (0) satisfies requirement of at most 0.",
    },
    {
      criterion_id: "CRIT_INCOME",
      attribute: "household_income",
      operator: "lte",
      target_value: "800000.00",
      actual_value: "420000.00",
      status: "satisfied",
      is_mandatory: false,
      evidence_required: "income_proof",
      evidence_status: "verified",
      reason: "Verified annual household income ₹4,20,000.00 is below need ceiling of ₹8,00,000.00.",
    },
  ],
  tuition_accounting: {
    gross_eligible_tuition: "240000.00",
    institutional_cap_applied: "200000.00",
    total_effective_reduction: "120000.00",
    remaining_payable_tuition: "120000.00",
    remaining_waiver_allowance: "80000.00",
    total_unapplied_surplus: "0.00",
    allocations: [
      {
        award_id: "AWD_MERIT_50",
        program_id: "MERIT_NEED_2026",
        title: "National Merit-cum-Means Grant",
        priority: 1,
        status: "confirmed",
        nominal_amount: "120000.00",
        capped_amount: "120000.00",
        effective_reduction: "120000.00",
        unapplied_surplus: "0.00",
        cap_reason: "Applied within institutional 50% tuition ceiling.",
      },
    ],
  },
}

// ---------------------------------------------------------------------------
// 3. Deterministic Loan Assessment Fixture
// ---------------------------------------------------------------------------

export const MOCK_LOAN_ASSESSMENT: LoanAssessResponseData = {
  application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
  monthly_income: "35000.00",
  available_monthly_capacity: "11000.00",
  estimated_emi: "6400.00",
  post_scholarship_loan_amount: "360000.00",
  tenure_months: 60,
  outcome: "eligible",
  dti_ratio_percent: "26.86",
  capacity_utilization_percent: "58.18",
  reason: "Estimated monthly EMI of ₹6,400.00 sits comfortably within available capacity of ₹11,000.00 (58% utilization).",
}

// ---------------------------------------------------------------------------
// 4. Grounded LLM Explanation Contract Fixture
// ---------------------------------------------------------------------------

export const MOCK_EXPLANATION: ExplanationContract = {
  summary_headline: "Recommended eligible for 50% tuition assistance and conservative education loan.",
  reasons: [
    "Verified CGPA of 8.85 satisfies the merit threshold (at least 8.00) with zero active backlogs.",
    "Verified annual household income of ₹4,20,000.00 confirms eligibility for need-based tuition subsidy.",
    "Confirmed scholarship reduces tuition burden by ₹1,20,000.00, reducing required education loan to ₹3,60,000.00.",
  ],
  accounting_explanation: "From gross eligible tuition of ₹2,40,000.00, the 50% merit grant provides an effective reduction of ₹1,20,000.00, leaving a remaining payable tuition balance of ₹1,20,000.00.",
  required_actions: [],
  fairness_attestation: "This assessment was generated purely from objective academic benchmarks and verified income documentation without reliance on protected demographic attributes.",
  human_review_notice: "This is an automated decision-support recommendation pending formal review and confirmation by an authorized financial aid officer.",
}

// ---------------------------------------------------------------------------
// 5. Document Verification & OCR Fixture
// ---------------------------------------------------------------------------

export const MOCK_DOCUMENTS: UploadedDocumentDTO[] = [
  {
    id: "doc_marksheet_01",
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    doc_type: "marksheet",
    file_url: "/uploads/marksheet_sem4.pdf",
    sha256: "b48c894d3f23a8904719f9d1234abcd5678ef90123456789abcdef0123456789",
    mismatch_flag: false,
    ocr_extracted_data: {
      cgpa: 8.85,
      student_name: "Priya Sharma",
      semester: 4,
      backlogs: 0,
      confidence: 0.96,
    },
    created_at: "2026-10-24T10:20:00Z",
  },
  {
    id: "doc_income_01",
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    doc_type: "income_proof",
    file_url: "/uploads/income_cert_2026.pdf",
    sha256: "9f82d1cba90458e87493201f98d76543210fedcba9876543210abcdef0123456",
    mismatch_flag: false,
    ocr_extracted_data: {
      annual_income: 420000,
      issuing_authority: "Tehsildar Office",
      holder_name: "Ramesh Sharma",
      confidence: 0.94,
    },
    created_at: "2026-10-24T10:22:00Z",
  },
]

export const MOCK_VERIFICATION_RESULT: VerificationResultDTO = {
  verified: true,
  mismatch_flag: false,
  discrepancies: [],
  status: "verified_clean",
}

// ---------------------------------------------------------------------------
// 6. Review Queue Fixture
// ---------------------------------------------------------------------------

export const MOCK_REVIEW_QUEUE: ReviewQueueItem[] = [
  {
    application_id: "611767c7-61c8-4f5d-a299-3561bfc28306",
    applicant_name: "Aarav Patel",
    applicant_email: "aarav.patel@test.edu",
    submission_date: "2026-10-25 08:32",
    status: "needs_review",
    program_id: "MERIT_NEED_2026",
    flags: ["Pending evidence: marksheet", "Pending evidence: income_proof"],
    priority: "medium",
  },
  {
    application_id: "e4c1973b-5778-4389-9dbb-821945da9b33",
    applicant_name: "Rohit Verma",
    applicant_email: "rohit.verma@delhi.edu",
    submission_date: "2026-10-25 09:12",
    status: "needs_review",
    program_id: "MERIT_NEED_2026",
    flags: ["Active backlog detected (1)"],
    priority: "high",
  },
  {
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    applicant_name: "Priya Sharma",
    applicant_email: "priya.sharma@nitk.edu.in",
    submission_date: "2026-10-24 10:15",
    status: "ready_for_report",
    program_id: "MERIT_NEED_2026",
    flags: [],
    priority: "low",
  },
]

// ---------------------------------------------------------------------------
// 7. Consolidated Dossier Fixture (for Reviewer Case Detail)
// ---------------------------------------------------------------------------

export const MOCK_CONSOLIDATED_DOSSIER: ConsolidatedDossierDTO = {
  application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
  status: "ready_for_report",
  created_at: "2026-10-24T10:15:30Z",
  updated_at: "2026-10-25T08:30:00Z",
  applicant: {
    id: "usr_priya_sharma",
    name: "Priya Sharma",
    email: "priya.sharma@nitk.edu.in",
  },
  academic_record: {
    cgpa: "8.85",
    tenth_percent: "92.40",
    twelfth_percent: "89.60",
    backlogs: 0,
  },
  financial_profile: {
    household_income: "420000.00",
    existing_emi: "3000.00",
    tuition_fee: "240000.00",
    requested_loan: "480000.00",
  },
  ocr_diffs: [
    {
      document_id: "doc_marksheet_01",
      doc_type: "marksheet",
      file_url: "/uploads/marksheet_sem4.pdf",
      mismatch_flag: false,
      extracted_data: {
        cgpa: 8.85,
        backlogs: 0,
        student_name: "Priya Sharma",
      },
    },
    {
      document_id: "doc_income_01",
      doc_type: "income_proof",
      file_url: "/uploads/income_cert_2026.pdf",
      mismatch_flag: false,
      extracted_data: {
        household_income: 420000,
        issuing_authority: "Tehsildar",
      },
    },
  ],
  scholarship_evaluation: MOCK_SCHOLARSHIP_EVALUATION,
  loan_assessment: MOCK_LOAN_ASSESSMENT,
  explanation: {
    recommendation_text: MOCK_EXPLANATION.summary_headline,
    summary_headline: MOCK_EXPLANATION.summary_headline,
    reasons: MOCK_EXPLANATION.reasons,
    accounting_explanation: MOCK_EXPLANATION.accounting_explanation,
    confidence_note: "Repayment capacity assessed at healthy 58% utilization under 60-month amortized horizon.",
    fairness_note: MOCK_EXPLANATION.fairness_attestation,
    fairness_attestation: MOCK_EXPLANATION.fairness_attestation,
    human_review_notice: MOCK_EXPLANATION.human_review_notice,
    llm_prompt_version: "v1.0-phase4",
  },
  audit_logs: [
    {
      id: "log_01",
      event_type: "application_submitted",
      detail: { channel: "portal_web", client_ip: "127.0.0.1" },
      timestamp: "2026-10-24T10:15:30Z",
    },
    {
      id: "log_02",
      event_type: "deterministic_evaluation_frozen",
      detail: { policy_version: "1.0.0", engine_version: "1.0.0-phase1b", status: "eligible" },
      timestamp: "2026-10-24T10:16:05Z",
    },
    {
      id: "log_03",
      event_type: "documents_verified",
      detail: { verified_count: 2, mismatches: 0 },
      timestamp: "2026-10-24T10:23:10Z",
    },
  ],
}

// ---------------------------------------------------------------------------
// 8. Institutional Analytics Fixture (Admin)
// ---------------------------------------------------------------------------

export const MOCK_ADMIN_ANALYTICS: AdminAnalyticsResponse = {
  total_applications: 214,
  pending_review_count: 38,
  approved_count: 42,
  rejected_count: 4,
  eligibility_rate_percent: 34.5,
  average_tuition_reduction: 68500.0,
  fairness_flag_incidence_rate: 4.2,
  average_turnaround_hours: 3.2,
  status_distribution: {
    draft: 12,
    submitted: 118,
    needs_review: 38,
    ready_for_report: 42,
    closed: 4,
  },
  recent_activity: [
    {
      id: "act_01",
      application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
      event_type: "officer_approval",
      detail: { decision: "approve", reviewer: "Dr. Sarah Jenkins" },
      timestamp: "2026-10-25T08:30:00Z",
    },
    {
      id: "act_02",
      application_id: "611767c7-61c8-4f5d-a299-3561bfc28306",
      event_type: "evidence_request_queued",
      detail: { requested_evidence: ["marksheet", "income_proof"] },
      timestamp: "2026-10-25T08:32:14Z",
    },
  ],
}

export const MOCK_FAIRNESS_METRICS: FairnessMetricsDTO = {
  total_audited: 214,
  demographic_leakage_flags: 9,
  flag_incidence_rate_percent: 4.2,
  status: "healthy_within_threshold",
}

// ---------------------------------------------------------------------------
// 9. Institutional Policy Specification Fixture (Admin Policy Viewer)
// ---------------------------------------------------------------------------

export const MOCK_SCHOLARSHIP_POLICIES: ScholarshipPolicySpec[] = [
  {
    program_id: "MERIT_NEED_2026",
    policy_version: "1.0.0",
    title: "Institutional Merit & Need Scholarship Program",
    description: "Evaluates academic excellence and household financial need with strict exclusion of demographic proxy tokens.",
    checksum_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    effective_date: "2026-06-01",
    charter_authorizations: {
      caste_category: "GOV-SCHEME-ORD-2024/77B",
      religion: "MINORITY-ENDOWMENT-ACT-SEC-4",
    },
    criteria: [
      {
        criterion_id: "CRIT_CGPA",
        attribute: "cgpa",
        operator: "gte",
        target_value: "8.00",
        is_mandatory: true,
        required_evidence: "marksheet",
        description: "Minimum cumulative grade point average required for academic merit qualification.",
        purpose: "merit_ranking",
      },
      {
        criterion_id: "CRIT_BACKLOGS",
        attribute: "active_backlogs",
        operator: "lte",
        target_value: 0,
        is_mandatory: true,
        description: "Applicant must have cleared all preceding semester coursework without active uncleared papers.",
        purpose: "merit_ranking",
      },
      {
        criterion_id: "CRIT_INCOME",
        attribute: "household_income",
        operator: "lte",
        target_value: "800000.00",
        is_mandatory: false,
        required_evidence: "income_proof",
        description: "Need ceiling for supplemental fee waiver allocation.",
        purpose: "program_eligibility",
      },
      {
        criterion_id: "CRIT_DOMICILE",
        attribute: "state_of_domicile",
        operator: "eq",
        target_value: "Karnataka",
        is_mandatory: false,
        description: "Institutional state residency preference check.",
        purpose: "program_eligibility",
      },
      {
        criterion_id: "CRIT_CASTE_RESERVE",
        attribute: "caste_category",
        operator: "in",
        target_value: ["SC", "ST", "OBC-NCL"],
        is_mandatory: false,
        description: "Statutory affirmative action allocation pursuant to charter endowment.",
        purpose: "restricted_sensitive",
        charter_authorization: "GOV-SCHEME-ORD-2024/77B",
      },
    ],
  },
]
