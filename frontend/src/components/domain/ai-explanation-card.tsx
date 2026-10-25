import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { ExplanationContract } from "@/types/domain"
import {
  AlertTriangleIcon,
  CheckCircle2Icon,
  InfoIcon,
  RotateCwIcon,
  ScaleIcon,
  SparklesIcon,
  UserCheckIcon,
} from "lucide-react"

interface AiExplanationCardProps {
  explanation?: ExplanationContract | null
  isLoading?: boolean
  isError?: boolean
  onRetry?: () => void
  promptVersion?: string
}

export function AiExplanationCard({
  explanation,
  isLoading = false,
  isError = false,
  onRetry,
  promptVersion = "v1.0-phase4",
}: AiExplanationCardProps) {
  if (isLoading) {
    return (
      <div className="rounded-2xl border border-primary/20 bg-primary/[0.03] p-6 space-y-4 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-5 w-48 bg-primary/10 rounded-md" />
          <div className="h-4 w-24 bg-primary/10 rounded-md" />
        </div>
        <div className="h-6 w-3/4 bg-primary/10 rounded-md" />
        <div className="space-y-2">
          <div className="h-4 w-full bg-primary/5 rounded-md" />
          <div className="h-4 w-5/6 bg-primary/5 rounded-md" />
          <div className="h-4 w-2/3 bg-primary/5 rounded-md" />
        </div>
      </div>
    )
  }

  if (isError || !explanation) {
    return (
      <div className="rounded-2xl border border-border bg-card/60 p-6 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
            <SparklesIcon className="size-4 text-muted-foreground" />
            AI Explanation
          </span>
          <Badge variant="outline" className="text-[10px]">
            Unavailable
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          Explanation service is currently unavailable. Deterministic rule calculations and accounting above remain fully verified and unaffected.
        </p>
        {onRetry && (
          <Button size="sm" variant="outline" onClick={onRetry} className="gap-1.5 text-xs">
            <RotateCwIcon className="size-3.5" />
            Retry Generating Explanation
          </Button>
        )}
      </div>
    )
  }

  const requiresHumanFairnessReview =
    explanation.summary_headline?.toLowerCase().includes("fairness review") ||
    explanation.fairness_attestation?.toLowerCase().includes("human review required")

  return (
    <section
      aria-label="AI Generated Explanation"
      className="rounded-2xl border border-indigo-500/25 dark:border-indigo-500/30 bg-gradient-to-br from-indigo-500/[0.04] via-background to-teal-500/[0.03] p-6 sm:p-8 space-y-6 shadow-sm"
    >
      {/* Visual Header Identifying AI Nature */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/60 pb-4">
        <div className="flex items-center gap-2">
          <span className="flex size-7 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-600 dark:text-indigo-400">
            <SparklesIcon className="size-4" />
          </span>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-foreground">
                Plain-English Recommendation Explanation
              </h2>
              <Badge variant="secondary" className="text-[10px] uppercase font-mono tracking-wider bg-indigo-500/10 text-indigo-700 dark:text-indigo-300">
                AI-Grounded
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Explains deterministic findings · Cannot calculate scores or alter determinations
            </p>
          </div>
        </div>

        <span className="text-[11px] font-mono text-muted-foreground shrink-0">
          Prompt Spec: <span className="text-foreground">{promptVersion}</span>
        </span>
      </div>

      {/* Fairness Escalation Alert if detected */}
      {requiresHumanFairnessReview && (
        <div className="rounded-xl border border-amber-500/40 bg-amber-500/15 p-4 text-xs text-amber-900 dark:text-amber-200 flex items-start gap-3">
          <AlertTriangleIcon className="size-5 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
          <div className="space-y-1">
            <span className="font-semibold block">Human Fairness Screening Flagged</span>
            <p>
              This explanation triggered an algorithmic caution. A human fairness officer must review this case before any final determination is confirmed.
            </p>
          </div>
        </div>
      )}

      {/* 1. Summary Headline */}
      <div className="space-y-1.5">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Executive Summary
        </span>
        <p className="text-base sm:text-lg font-medium text-foreground leading-snug">
          {explanation.summary_headline}
        </p>
      </div>

      {/* 2. Structured Reasons */}
      {explanation.reasons && explanation.reasons.length > 0 && (
        <div className="space-y-2.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Key Decision Factors
          </span>
          <ul className="space-y-2">
            {explanation.reasons.map((reason, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2.5 text-sm text-foreground/90 leading-relaxed rounded-lg bg-card/60 p-3 border border-border/50"
              >
                <CheckCircle2Icon className="size-4 shrink-0 text-primary mt-0.5" />
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 3. Tuition Accounting Explanation */}
      {explanation.accounting_explanation && (
        <div className="rounded-xl border border-border/80 bg-background/60 p-4 space-y-1.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <InfoIcon className="size-3.5 text-primary" />
            Financial Accounting Context
          </span>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {explanation.accounting_explanation}
          </p>
        </div>
      )}

      {/* 4. Required Applicant Actions */}
      {explanation.required_actions && explanation.required_actions.length > 0 && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 space-y-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-amber-800 dark:text-amber-400 flex items-center gap-1.5">
            <AlertTriangleIcon className="size-3.5" />
            Next Actions Required From You
          </span>
          <ul className="space-y-1.5 text-xs text-foreground">
            {explanation.required_actions.map((act, idx) => (
              <li key={idx} className="flex items-center gap-2">
                <span className="size-1.5 rounded-full bg-amber-500" />
                <span>{act}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 5. Attestation & Governance Disclaimers */}
      <div className="grid gap-3 pt-2 text-xs sm:grid-cols-2 border-t border-border/60">
        <div className="flex items-start gap-2 text-muted-foreground">
          <ScaleIcon className="size-4 shrink-0 text-primary mt-0.5" />
          <span>
            <strong className="text-foreground font-medium">Fairness Attestation: </strong>
            {explanation.fairness_attestation}
          </span>
        </div>
        <div className="flex items-start gap-2 text-muted-foreground">
          <UserCheckIcon className="size-4 shrink-0 text-primary mt-0.5" />
          <span>
            <strong className="text-foreground font-medium">Human Governance: </strong>
            {explanation.human_review_notice}
          </span>
        </div>
      </div>
    </section>
  )
}
