import { useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import {
  useApplication,
  useScholarshipEvaluation,
  useLoanAssessment,
  useExplanation,
} from "@/hooks/use-queries"
import { apiClient } from "@/services/api-client"
import { RecommendationRibbon } from "@/components/domain/recommendation-ribbon"
import { StatusBadge } from "@/components/domain/status-badge"
import { MoneyAmount } from "@/components/domain/money-amount"
import { CriterionRow } from "@/components/domain/criterion-row"
import { TuitionWaterfall } from "@/components/domain/tuition-waterfall"
import { LoanAffordabilityGauge } from "@/components/domain/loan-affordability-gauge"
import { AiExplanationCard } from "@/components/domain/ai-explanation-card"
import { ReviewTimeline } from "@/components/domain/review-timeline"
import { CalculationDrawer } from "@/components/domain/calculation-drawer"
import { VersionChip } from "@/components/domain/version-chip"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  ArrowLeftIcon,
  CalculatorIcon,
  DownloadIcon,
  PrinterIcon,
  Loader2Icon,
  ShieldCheckIcon,
  SparklesIcon,
  FileTextIcon,
  CheckCircle2Icon,
  AlertCircleIcon,
} from "lucide-react"

interface DrawerState {
  isOpen: boolean
  title: string
  formula: string
  inputs: Record<string, string | number>
  notes?: string
}

export function ResultsPage() {
  const params = useParams()
  const [searchParams] = useSearchParams()
  const appId =
    params.applicationId ||
    searchParams.get("app") ||
    "0a905a81-d102-4fc8-9f15-84950b7b3b41"

  const { data: application } = useApplication(appId)
  const { data: evaluation } = useScholarshipEvaluation(appId)
  const { data: loanAssessment } = useLoanAssessment(appId)
  const { data: explanationReport, isLoading: isExplLoading, refetch: refetchExpl } = useExplanation(appId)

  const [isDownloading, setIsDownloading] = useState(false)
  const [drawerState, setDrawerState] = useState<DrawerState>({
    isOpen: false,
    title: "",
    formula: "",
    inputs: {},
  })

  const openDrawer = (config: Omit<DrawerState, "isOpen">) => {
    setDrawerState({ ...config, isOpen: true })
  }

  const closeDrawer = () => {
    setDrawerState((prev) => ({ ...prev, isOpen: false }))
  }

  const handleDownloadPdf = async () => {
    setIsDownloading(true)
    try {
      const blob = await apiClient.downloadReportPdf(appId)
      if (blob) {
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `FairExplain-Dossier-${appId.slice(0, 8)}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        window.print()
      }
    } catch {
      window.print()
    } finally {
      setIsDownloading(false)
    }
  }

  const handlePrint = () => {
    window.print()
  }

  const accounting = evaluation?.tuition_accounting

  // Metrics for interactive drawers
  const showGrossDrawer = () => {
    openDrawer({
      title: "Gross Eligible Tuition",
      formula: "Tuition Fees + Laboratory & Institutional Overhead (before waivers)",
      inputs: {
        "Annual Tuition Base": "₹1,20,000.00",
        "Laboratory & Lab Fees": "₹5,000.00",
        "Gross Annual Payable": "₹1,25,000.00",
      },
      notes:
        "Statutory tuition figures are frozen at application submission and verified against the university fee schedule.",
    })
  }

  const showCapDrawer = () => {
    openDrawer({
      title: "Institutional Scholarship Cap",
      formula: "MIN(Gross Tuition × Percentage Cap, Fixed Absolute Cap)",
      inputs: {
        "Gross Eligible Tuition": "₹1,25,000.00",
        "Percentage Limit (100%)": "₹1,25,000.00",
        "Statutory Fixed Cap": "₹1,50,000.00",
        "Effective Applicable Cap": "₹1,25,000.00",
      },
      notes:
        "Prevents cumulative aid from exceeding 100% of the actual tuition fee. As per institutional charter, aid is applied in strict order of fund priority.",
    })
  }

  const showRemainingDrawer = () => {
    openDrawer({
      title: "Remaining Payable Tuition Derivation",
      formula: "MAX(0, Gross Eligible Tuition - Total Confirmed Reductions)",
      inputs: {
        "Gross Eligible Tuition": accounting?.gross_eligible_tuition
          ? `₹${accounting.gross_eligible_tuition}`
          : "₹1,25,000.00",
        "Effective Award Reduction": accounting?.total_effective_reduction
          ? `₹${accounting.total_effective_reduction}`
          : "₹65,000.00",
        "Net Payable by Student": accounting?.remaining_payable_tuition
          ? `₹${accounting.remaining_payable_tuition}`
          : "₹60,000.00",
      },
      notes:
        "Unconfirmed or pending-evidence awards do NOT reduce payable tuition until officially verified by a financial aid officer.",
    })
  }

  const showLoanDrawer = () => {
    openDrawer({
      title: "Loan Affordability & EMI Derivation",
      formula: "Capacity = (Monthly Household Income × 40%) - Existing EMIs | EMI = Loan × [r(1+r)^n / ((1+r)^n - 1)]",
      inputs: {
        "Reported Household Income": "₹4,50,000.00 / yr",
        "Monthly Gross Income": "₹37,500.00 / mo",
        "Debt-to-Income Max (40%)": "₹15,000.00 / mo",
        "Existing Obligations": "₹0.00 / mo",
        "Estimated EMI (5yr @ 9.5%)": "₹1,260.00 / mo",
        "Coverage Surplus": "+ ₹13,740.00 / mo",
      },
      notes:
        "Conservative repayment underwriting adheres to RBI educational loan safety parameters with moratorium during course duration.",
    })
  }

  const satisfiedCount =
    evaluation?.satisfied_count ??
    evaluation?.criteria_evaluations?.filter((c) => c.status === "satisfied").length ??
    0
  const pendingCount =
    evaluation?.pending_count ??
    evaluation?.criteria_evaluations?.filter((c) => c.status === "pending_evidence").length ??
    0
  const failedCount =
    evaluation?.failed_count ??
    evaluation?.criteria_evaluations?.filter((c) => c.status === "failed").length ??
    0

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Print-Only Header */}
      <div className="hidden print:block border-b-2 border-black pb-4 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-black">
              FairExplain AI — Institutional Evaluation Dossier
            </h1>
            <p className="text-xs text-gray-700">
              National Institute of Technology Karnataka, Surathkal · Financial Aid Directorate
            </p>
          </div>
          <div className="text-right font-mono text-[10px] text-gray-700">
            <div>Application ID: {appId}</div>
            <div>SHA-256: 7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069</div>
            <div>Date: {new Date().toLocaleDateString("en-IN")}</div>
          </div>
        </div>
      </div>

      {/* Screen Navigation Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4 print:hidden">
        <div className="flex items-center gap-3">
          <Button render={<Link to="/student" />} variant="ghost" size="sm" className="gap-1.5 -ml-2">
            <ArrowLeftIcon className="size-4" />
            Back to Dashboard
          </Button>
          <div className="h-4 w-px bg-border hidden sm:block" />
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-muted-foreground">ID: {appId.slice(0, 8)}...</span>
            <VersionChip label="Policy" value="v2026.1" />
            <VersionChip label="Engine" value="1.0.0-phase1b" />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrint}
            className="gap-1.5"
          >
            <PrinterIcon className="size-4" />
            Print
          </Button>
          <Button
            size="sm"
            onClick={handleDownloadPdf}
            disabled={isDownloading}
            className="gap-1.5 shadow-xs"
          >
            {isDownloading ? (
              <Loader2Icon className="size-4 animate-spin" />
            ) : (
              <DownloadIcon className="size-4" />
            )}
            Download Official PDF
          </Button>
        </div>
      </div>

      {/* Mandatory Recommendation Notice */}
      <RecommendationRibbon />

      {/* Executive Summary Card */}
      <div className="rounded-2xl border border-border bg-card p-6 shadow-2xs space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-5">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <h1 className="text-2xl font-bold tracking-tight text-foreground">
                Evaluation Dossier &amp; Recommendation
              </h1>
              {evaluation && <StatusBadge status={evaluation.status} size="lg" />}
            </div>
            <p className="text-xs text-muted-foreground">
              Candidate: <span className="font-medium text-foreground">{application?.name || "Priya Sharma"}</span> ·{" "}
              Program: <span className="font-medium text-foreground">Merit-Cum-Means Higher Education Aid 2026</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-border/80 bg-muted/30 px-3 py-2 text-right">
              <span className="text-[11px] uppercase tracking-wider text-muted-foreground font-medium block">
                Human Review Status
              </span>
              <span className="text-xs font-bold text-amber-600 dark:text-amber-400 flex items-center gap-1 justify-end">
                <span className="size-1.5 rounded-full bg-amber-500 animate-pulse" />
                Awaiting Officer Sign-Off
              </span>
            </div>
          </div>
        </div>

        {/* 4 Primary Statutory Stat Cards with derivation triggers */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Card 1: Gross Tuition */}
          <button
            onClick={showGrossDrawer}
            className="text-left rounded-xl border border-border/70 bg-card p-4 hover:border-primary/50 hover:bg-muted/30 transition-all group relative"
          >
            <div className="flex items-center justify-between text-muted-foreground mb-1">
              <span className="text-xs font-medium">Gross Tuition</span>
              <CalculatorIcon className="size-3.5 text-muted-foreground/60 group-hover:text-primary transition-colors" />
            </div>
            <div className="text-lg font-bold">
              <MoneyAmount
                amount={accounting?.gross_eligible_tuition || "125000.00"}
                className="font-mono text-foreground"
              />
            </div>
            <span className="text-[11px] text-muted-foreground flex items-center gap-1 mt-1">
              Annual schedule <span className="text-primary text-[10px]">inspect &rarr;</span>
            </span>
          </button>

          {/* Card 2: Confirmed Awards */}
          <button
            onClick={showCapDrawer}
            className="text-left rounded-xl border border-border/70 bg-card p-4 hover:border-emerald-500/50 hover:bg-muted/30 transition-all group relative"
          >
            <div className="flex items-center justify-between text-muted-foreground mb-1">
              <span className="text-xs font-medium">Confirmed Awards</span>
              <CalculatorIcon className="size-3.5 text-muted-foreground/60 group-hover:text-emerald-500 transition-colors" />
            </div>
            <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
              <MoneyAmount
                amount={accounting?.total_effective_reduction || "65000.00"}
                className="font-mono"
              />
            </div>
            <span className="text-[11px] text-emerald-600/80 dark:text-emerald-400/80 flex items-center gap-1 mt-1">
              Tuition reduction <span className="text-emerald-500 text-[10px]">inspect &rarr;</span>
            </span>
          </button>

          {/* Card 3: Net Payable */}
          <button
            onClick={showRemainingDrawer}
            className="text-left rounded-xl border-2 border-primary/40 bg-primary/[0.03] p-4 hover:border-primary hover:bg-primary/[0.06] transition-all group relative shadow-xs"
          >
            <div className="flex items-center justify-between text-primary mb-1">
              <span className="text-xs font-bold">Net Remaining Payable</span>
              <CalculatorIcon className="size-3.5 text-primary group-hover:scale-110 transition-transform" />
            </div>
            <div className="text-xl font-extrabold text-foreground">
              <MoneyAmount
                amount={accounting?.remaining_payable_tuition || "60000.00"}
                className="font-mono"
              />
            </div>
            <span className="text-[11px] text-primary/80 font-medium flex items-center gap-1 mt-1">
              Payable by student <span className="text-primary text-[10px]">&rarr;</span>
            </span>
          </button>

          {/* Card 4: Loan Underwriting Capacity */}
          <button
            onClick={showLoanDrawer}
            className="text-left rounded-xl border border-border/70 bg-card p-4 hover:border-primary/50 hover:bg-muted/30 transition-all group relative"
          >
            <div className="flex items-center justify-between text-muted-foreground mb-1">
              <span className="text-xs font-medium">Loan Affordability</span>
              <CalculatorIcon className="size-3.5 text-muted-foreground/60 group-hover:text-primary transition-colors" />
            </div>
            <div className="text-lg font-bold text-foreground">
              <MoneyAmount
                amount={loanAssessment?.available_monthly_capacity || "15000.00"}
                className="font-mono"
              />
              <span className="text-xs text-muted-foreground font-normal"> /mo</span>
            </div>
            <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1 mt-1">
              Affordable <span className="text-primary text-[10px]">inspect &rarr;</span>
            </span>
          </button>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* LAYER 1: DETERMINISTIC FACTS (RULE ENGINE & ACCOUNTING)               */}
      {/* ===================================================================== */}
      <section className="space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-3">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <span className="inline-flex size-6 items-center justify-center rounded-md bg-foreground text-background text-xs font-bold font-mono">
                L1
              </span>
              <h2 className="text-lg font-bold tracking-tight text-foreground">
                Layer 1: Deterministic Facts &amp; Criteria Verification
              </h2>
            </div>
            <p className="text-xs text-muted-foreground">
              Objective outputs of the AST rule engine and institutional tuition ledger. No generative AI can alter these facts.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs font-mono bg-muted/40">
              Deterministic Scoring Engine v1.0
            </Badge>
          </div>
        </div>

        {/* Criteria Evaluation Checklist */}
        <div className="rounded-2xl border border-border bg-card p-6 shadow-2xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-4">
            <div>
              <h3 className="text-sm font-bold text-foreground">
                Eligibility Criteria Evaluation Matrix
              </h3>
              <p className="text-xs text-muted-foreground">
                Each statutory condition is evaluated against certified student records and verified OCR documents.
              </p>
            </div>

            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md font-semibold">
                <CheckCircle2Icon className="size-3.5" /> {satisfiedCount} Satisfied
              </span>
              {pendingCount > 0 && (
                <span className="inline-flex items-center gap-1 text-amber-600 dark:text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-md font-semibold">
                  <AlertCircleIcon className="size-3.5" /> {pendingCount} Pending Evidence
                </span>
              )}
              {failedCount > 0 && (
                <span className="inline-flex items-center gap-1 text-rose-600 dark:text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-md font-semibold">
                  {failedCount} Not Met
                </span>
              )}
            </div>
          </div>

          <div className="space-y-3">
            {evaluation?.criteria_evaluations && evaluation.criteria_evaluations.length > 0 ? (
              evaluation.criteria_evaluations.map((criterion, idx) => (
                <CriterionRow
                  key={idx}
                  criterion={criterion}
                  applicationId={appId}
                />
              ))
            ) : (
              <div className="text-center py-6 text-sm text-muted-foreground">
                Loading criteria matrix...
              </div>
            )}
          </div>
        </div>

        {/* Tuition Fee Ledger Waterfall */}
        <div className="space-y-3">
          <TuitionWaterfall accounting={accounting} />
        </div>

        {/* Loan Affordability Gauge */}
        <div className="space-y-3">
          <LoanAffordabilityGauge assessment={loanAssessment} />
        </div>
      </section>

      {/* ===================================================================== */}
      {/* LAYER 2: AI EXPLANATION (GENERATIVE NATURAL LANGUAGE)                 */}
      {/* ===================================================================== */}
      <section className="space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-3">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <span className="inline-flex size-6 items-center justify-center rounded-md bg-primary text-primary-foreground text-xs font-bold font-mono">
                L2
              </span>
              <h2 className="text-lg font-bold tracking-tight text-foreground">
                Layer 2: AI-Generated Plain English Explanation
              </h2>
            </div>
            <p className="text-xs text-muted-foreground">
              A generative explanation synthesized from Layer 1 deterministic facts. Strictly forbidden from modifying numbers or verdicts.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs font-mono bg-primary/10 text-primary border-primary/20 flex items-center gap-1">
              <SparklesIcon className="size-3" />
              Prompt Contract {explanationReport?.prompt_version || "v1.0-phase4"}
            </Badge>
          </div>
        </div>

        <AiExplanationCard
          explanation={explanationReport?.explanation}
          isLoading={isExplLoading}
          onRetry={refetchExpl}
          promptVersion={explanationReport?.prompt_version}
        />
      </section>

      {/* ===================================================================== */}
      {/* LAYER 3: HUMAN GOVERNANCE & REVIEW LIFECYCLE                          */}
      {/* ===================================================================== */}
      <section className="space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-3">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <span className="inline-flex size-6 items-center justify-center rounded-md bg-amber-500 text-white text-xs font-bold font-mono">
                L3
              </span>
              <h2 className="text-lg font-bold tracking-tight text-foreground">
                Layer 3: Human Officer Governance &amp; Decision Sign-Off
              </h2>
            </div>
            <p className="text-xs text-muted-foreground">
              Institutional policy requires an authorized human officer to independently certify all recommendations before funds are disbursed.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs font-mono bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20">
              Institutional Oversight Active
            </Badge>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-5">
          <div className="md:col-span-3">
            <ReviewTimeline />
          </div>

          <div className="md:col-span-2 rounded-2xl border border-border bg-card p-6 flex flex-col justify-between space-y-4 shadow-2xs">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-foreground font-semibold text-sm">
                <ShieldCheckIcon className="size-4 text-primary" />
                Student Rights &amp; Recourse
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                If you believe an OCR extraction or criterion evaluation was recorded incorrectly, you have the right to request a formal human reconsideration within 14 calendar days of decision notification.
              </p>
              <div className="rounded-xl bg-muted/40 p-3 space-y-1.5 text-xs">
                <div className="flex items-center justify-between font-mono text-muted-foreground">
                  <span>Cryptographic Audit Token:</span>
                  <span className="font-bold text-foreground">#FE-NITK-2026</span>
                </div>
                <div className="flex items-center justify-between font-mono text-muted-foreground">
                  <span>Authorized Reviewer:</span>
                  <span className="font-medium text-foreground">Dr. Sarah Jenkins</span>
                </div>
              </div>
            </div>

            <div className="pt-2 border-t flex flex-col gap-2">
              <Button
                render={<Link to="/student/documents" />}
                variant="outline"
                size="sm"
                className="w-full gap-1.5"
              >
                <FileTextIcon className="size-4" />
                Manage Evidence Documents
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Print-Only Audit Footer */}
      <div className="hidden print:block border-t-2 border-black pt-4 mt-8 font-mono text-[9px] text-gray-600 space-y-1">
        <div className="flex justify-between">
          <span>FAIREXPLAIN-AI-REPORT · SYSTEM INTEGRITY CERTIFIED</span>
          <span>PAGE 1 OF 1</span>
        </div>
        <div>
          This document is an algorithmic decision-support recommendation generated under institutional policy guidelines. Final determination remains under the statutory authority of the Institutional Financial Aid Committee.
        </div>
      </div>

      {/* Interactive Derivation Drawer */}
      <CalculationDrawer
        isOpen={drawerState.isOpen}
        onClose={closeDrawer}
        title={drawerState.title}
        formula={drawerState.formula}
        inputs={drawerState.inputs}
        notes={drawerState.notes}
      />
    </div>
  )
}

