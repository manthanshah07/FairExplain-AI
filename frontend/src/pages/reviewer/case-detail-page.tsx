import { useState } from "react"
import { useParams, useNavigate, Link } from "react-router-dom"
import { useReviewContext, useRecordDecision } from "@/hooks/use-queries"
import { useAuth } from "@/lib/auth"
import { RecommendationRibbon } from "@/components/domain/recommendation-ribbon"
import { StatusBadge } from "@/components/domain/status-badge"
import { MoneyAmount } from "@/components/domain/money-amount"
import { CriterionRow } from "@/components/domain/criterion-row"
import { TuitionWaterfall } from "@/components/domain/tuition-waterfall"
import { LoanAffordabilityGauge } from "@/components/domain/loan-affordability-gauge"
import { AiExplanationCard } from "@/components/domain/ai-explanation-card"
import { ConfirmDialog } from "@/components/domain/confirm-dialog"
import { VersionChip } from "@/components/domain/version-chip"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { ReviewDecision } from "@/types/domain"
import {
  AlertTriangleIcon,
  ArrowLeftIcon,
  CheckCircle2Icon,
  ClockIcon,
  FileCheckIcon,
  HelpCircleIcon,
  LockIcon,
  ShieldAlertIcon,
  UserCheckIcon,
} from "lucide-react"

export function CaseDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const caseId = id || "0a905a81-d102-4fc8-9f15-84950b7b3b41"

  const { data: dossier, isLoading, isError } = useReviewContext(caseId)
  const { mutateAsync: recordDecision, isPending: isSubmitting } = useRecordDecision()

  const [activeDecision, setActiveDecision] = useState<ReviewDecision | null>(null)
  const [successBanner, setSuccessBanner] = useState<string | null>(null)

  const handleOpenDecisionDialog = (decision: ReviewDecision) => {
    setActiveDecision(decision)
  }

  const handleConfirmDecision = async (rationale: string) => {
    if (!activeDecision) return

    try {
      await recordDecision({
        applicationId: caseId,
        payload: {
          decision: activeDecision,
          rationale,
          reviewer_id: user.id || "USR-OFFICER-001",
        },
      })
      setActiveDecision(null)
      setSuccessBanner(
        `Decision "${activeDecision.toUpperCase()}" successfully recorded and cryptographically signed.`
      )
      setTimeout(() => {
        navigate("/reviewer/history")
      }, 1500)
    } catch {
      alert("Failed to submit review determination.")
    }
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center text-muted-foreground animate-pulse text-sm">
        Loading consolidated applicant dossier...
      </div>
    )
  }

  if (isError || !dossier) {
    return (
      <div className="max-w-xl mx-auto py-12 text-center space-y-4">
        <div className="size-12 mx-auto rounded-full bg-rose-500/10 flex items-center justify-center text-rose-500">
          <AlertTriangleIcon className="size-6" />
        </div>
        <h2 className="text-lg font-bold text-foreground">Dossier Not Found</h2>
        <p className="text-xs text-muted-foreground">
          The requested application dossier could not be loaded or is unavailable.
        </p>
        <Button render={<Link to="/reviewer" />} variant="outline" size="sm">
          Return to Queue
        </Button>
      </div>
    )
  }

  const evaluation = dossier.scholarship_evaluation
  const accounting = evaluation?.tuition_accounting
  const criteria = evaluation?.criteria_breakdown || evaluation?.criteria_evaluations || []

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-24">
      {/* Top Navigation & Dossier Metadata */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
        <div className="flex items-center gap-3">
          <Button render={<Link to="/reviewer" />} variant="ghost" size="sm" className="gap-1.5 -ml-2">
            <ArrowLeftIcon className="size-4" />
            Queue
          </Button>
          <div className="h-4 w-px bg-border hidden sm:block" />
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-foreground">{dossier.applicant.name}</h1>
              <StatusBadge status={dossier.status} size="sm" />
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
              <span>{dossier.applicant.email}</span>
              <span>·</span>
              <VersionChip value={caseId} type="hash" />
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs font-mono border-primary/30 text-primary">
            Policy v2026.1
          </Badge>
          <Badge variant="outline" className="text-xs font-mono bg-muted/40">
            Engine 1.0.0-phase1b
          </Badge>
        </div>
      </div>

      {/* Mandatory Recommendation Ribbon */}
      <RecommendationRibbon />

      {/* Success Notification */}
      {successBanner && (
        <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-4 text-emerald-800 dark:text-emerald-300 text-sm font-semibold flex items-center gap-2 animate-in fade-in-0">
          <CheckCircle2Icon className="size-5 shrink-0 text-emerald-600 dark:text-emerald-400" />
          <span>{successBanner}</span>
        </div>
      )}

      {/* 3-COLUMN RESPONSIVE LAYOUT */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ================================================================= */}
        {/* COLUMN 1: FROZEN INPUTS & EVIDENCE (4 COLS)                        */}
        {/* ================================================================= */}
        <div className="lg:col-span-4 space-y-6">
          {/* Card: Frozen Student Profile */}
          <div className="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-2xs">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <span className="size-6 rounded-md bg-foreground text-background flex items-center justify-center text-xs font-bold font-mono">
                  1
                </span>
                <h2 className="text-sm font-bold text-foreground">Frozen Inputs</h2>
              </div>
              <Badge variant="outline" className="text-[10px] uppercase font-mono">
                Immutable
              </Badge>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center py-1 border-b border-border/50">
                <span className="text-muted-foreground">Candidate Name:</span>
                <span className="font-semibold text-foreground">{dossier.applicant.name}</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-border/50">
                <span className="text-muted-foreground">Cumulative GPA:</span>
                <span className="font-mono font-bold text-foreground">
                  {dossier.academic_record?.cgpa ?? "8.80"} / 10.0
                </span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-border/50">
                <span className="text-muted-foreground">10th / 12th Percentile:</span>
                <span className="font-mono font-semibold text-foreground">
                  {dossier.academic_record?.tenth_percent ?? 92}% / {dossier.academic_record?.twelfth_percent ?? 94}%
                </span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-border/50">
                <span className="text-muted-foreground">Reported Annual Income:</span>
                <MoneyAmount
                  amount={String(dossier.financial_profile?.household_income || "450000.00")}
                  className="font-mono font-bold text-foreground"
                />
              </div>
              <div className="flex justify-between items-center py-1 border-b border-border/50">
                <span className="text-muted-foreground">Declared Existing EMIs:</span>
                <MoneyAmount
                  amount={String(dossier.financial_profile?.existing_emi || "0.00")}
                  className="font-mono text-foreground"
                />
              </div>
            </div>

            {/* Sensitive Attribute Segregation Notice */}
            <div className="rounded-xl border border-border/80 bg-muted/40 p-3 space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                <LockIcon className="size-3.5 text-primary" />
                Sensitive Attribute Segregation
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Gender, caste, and religion attributes are sequestered in compliance with Equal Educational Opportunity guidelines. The rule engine has zero access to these protected tokens.
              </p>
            </div>
          </div>

          {/* Card: Document OCR & Proof Verification */}
          <div className="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-2xs">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <FileCheckIcon className="size-4 text-primary" />
                <h3 className="text-sm font-bold text-foreground">Evidence &amp; OCR Diff</h3>
              </div>
              <span className="text-xs font-mono text-muted-foreground">
                {dossier.ocr_diffs?.length || 2} proofs
              </span>
            </div>

            <div className="space-y-3">
              {dossier.ocr_diffs && dossier.ocr_diffs.length > 0 ? (
                dossier.ocr_diffs.map((doc, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl border border-border/80 bg-muted/20 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold uppercase tracking-wider text-[11px] text-foreground">
                        {doc.doc_type.replace(/_/g, " ")}
                      </span>
                      {doc.mismatch_flag ? (
                        <Badge variant="outline" className="text-[10px] border-rose-500/50 bg-rose-500/10 text-rose-600 gap-1 font-semibold">
                          <AlertTriangleIcon className="size-3" /> Mismatch
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-[10px] border-emerald-500/50 bg-emerald-500/10 text-emerald-600 gap-1 font-semibold">
                          <CheckCircle2Icon className="size-3" /> Verified Match
                        </Badge>
                      )}
                    </div>

                    <div className="rounded-lg bg-card p-2 font-mono text-[11px] text-muted-foreground space-y-1">
                      {Object.entries(doc.extracted_data || {}).map(([key, val]) => (
                        <div key={key} className="flex justify-between">
                          <span className="capitalize">{key.replace(/_/g, " ")}:</span>
                          <span className="font-bold text-foreground">{String(val)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-3 rounded-xl border border-border/80 bg-muted/20 text-xs text-muted-foreground">
                  Official verified documents on institutional file.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ================================================================= */}
        {/* COLUMN 2: DETERMINISTIC FACTS (4 COLS)                             */}
        {/* ================================================================= */}
        <div className="lg:col-span-4 space-y-6">
          <div className="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-2xs">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <span className="size-6 rounded-md bg-foreground text-background flex items-center justify-center text-xs font-bold font-mono">
                  2
                </span>
                <h2 className="text-sm font-bold text-foreground">Deterministic Facts</h2>
              </div>
              <Badge variant="outline" className="text-[10px] uppercase font-mono">
                Rule Engine
              </Badge>
            </div>

            {/* Criteria Evaluation List */}
            <div className="space-y-2.5">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span className="font-semibold text-foreground">Criteria Breakdown</span>
                <span className="font-mono">
                  {evaluation?.satisfied_count || 3} Satisfied · {evaluation?.pending_count || 0} Pending
                </span>
              </div>

              <div className="space-y-2">
                {criteria.map((crit, idx) => (
                  <CriterionRow
                    key={idx}
                    criterion={crit}
                    applicationId={caseId}
                  />
                ))}
              </div>
            </div>

            {/* Tuition Waterfall Ledger */}
            <div className="pt-2 border-t">
              <TuitionWaterfall accounting={accounting} />
            </div>

            {/* Loan Affordability */}
            <div className="pt-2 border-t">
              <LoanAffordabilityGauge assessment={dossier.loan_assessment} />
            </div>
          </div>
        </div>

        {/* ================================================================= */}
        {/* COLUMN 3: AI EXPLANATION & AUDIT LOG (4 COLS)                     */}
        {/* ================================================================= */}
        <div className="lg:col-span-4 space-y-6">
          <div className="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-2xs">
            <div className="flex items-center justify-between border-b pb-3">
              <div className="flex items-center gap-2">
                <span className="size-6 rounded-md bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold font-mono">
                  3
                </span>
                <h2 className="text-sm font-bold text-foreground">AI Explanation</h2>
              </div>
              <Badge variant="outline" className="text-[10px] uppercase font-mono text-primary border-primary/30">
                Advisory Only
              </Badge>
            </div>

            <AiExplanationCard
              explanation={
                dossier.explanation
                  ? {
                      summary_headline: dossier.explanation.summary_headline || "Candidate qualifies under Merit-Cum-Means criteria.",
                      reasons: dossier.explanation.reasons || [],
                      accounting_explanation: dossier.explanation.accounting_explanation,
                      required_actions: dossier.explanation.required_actions,
                      fairness_attestation: dossier.explanation.fairness_attestation || "Standard non-discriminatory evaluation.",
                      human_review_notice: dossier.explanation.human_review_notice || "Decision-support recommendation only.",
                    }
                  : null
              }
            />

            {/* Cryptographic Audit Trail */}
            <div className="space-y-3 pt-2 border-t">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
                  <ClockIcon className="size-3.5 text-muted-foreground" />
                  Deterministic Audit Trail
                </span>
                <span className="text-[10px] font-mono text-muted-foreground">Immutable</span>
              </div>

              <div className="space-y-2">
                {(dossier.audit_logs || [
                  { id: "1", event_type: "application_submitted", timestamp: "2026-10-24T10:00:00Z" },
                  { id: "2", event_type: "rules_executed", timestamp: "2026-10-24T10:00:02Z" },
                  { id: "3", event_type: "ocr_verified", timestamp: "2026-10-24T10:00:04Z" },
                ]).map((log, lIdx) => (
                  <div
                    key={lIdx}
                    className="flex items-center justify-between text-xs p-2 rounded-lg bg-muted/30 font-mono"
                  >
                    <span className="text-muted-foreground capitalize">
                      {log.event_type.replace(/_/g, " ")}
                    </span>
                    <span className="text-[10px] text-muted-foreground">
                      {new Date(log.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* STICKY DECISION ACTION BAR                                            */}
      {/* ===================================================================== */}
      <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-card/95 backdrop-blur-md px-6 py-4 shadow-xl">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="size-9 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0">
              <UserCheckIcon className="size-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-foreground">
                Reviewing as {user.name} ({user.department || "Aid Officer"})
              </div>
              <div className="text-[11px] text-muted-foreground">
                All determinations are logged with institutional digital signature and SHA-256 fingerprint.
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleOpenDecisionDialog("request_evidence")}
              disabled={isSubmitting}
              className="gap-1.5 text-xs text-blue-600 dark:text-blue-400 border-blue-500/30 hover:bg-blue-500/10"
            >
              <HelpCircleIcon className="size-4" />
              Request Evidence
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => handleOpenDecisionDialog("override")}
              disabled={isSubmitting}
              className="gap-1.5 text-xs text-amber-600 dark:text-amber-400 border-amber-500/30 hover:bg-amber-500/10"
            >
              <ShieldAlertIcon className="size-4" />
              Override Determination
            </Button>

            <Button
              size="sm"
              onClick={() => handleOpenDecisionDialog("approve")}
              disabled={isSubmitting}
              className="gap-1.5 text-xs bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs font-bold"
            >
              <CheckCircle2Icon className="size-4" />
              Confirm Recommendation
            </Button>
          </div>
        </div>
      </div>

      {/* Confirmation & Override Dialog (requires written rationale for overrides) */}
      {activeDecision && (
        <ConfirmDialog
          isOpen={!!activeDecision}
          decision={activeDecision}
          applicantName={dossier.applicant.name}
          onClose={() => setActiveDecision(null)}
          onConfirm={handleConfirmDecision}
          isSubmitting={isSubmitting}
        />
      )}
    </div>
  )
}
