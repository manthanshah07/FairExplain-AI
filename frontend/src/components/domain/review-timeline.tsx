import { CheckCircle2Icon, CircleDotIcon, CircleIcon } from "lucide-react"

export interface TimelineStep {
  id: string
  label: string
  description?: string
  status: "completed" | "current" | "pending"
  timestamp?: string
}

interface ReviewTimelineProps {
  steps?: TimelineStep[]
  currentStepId?: string
  className?: string
}

const DEFAULT_TIMELINE: TimelineStep[] = [
  { id: "submitted", label: "Application Submitted", description: "Applicant profile received", status: "completed" },
  { id: "scored", label: "Deterministic Scoring", description: "Rule engine criteria evaluated", status: "completed" },
  { id: "explained", label: "AI Grounded Explanation", description: "Objective reasoning synthesized", status: "completed" },
  { id: "fairness", label: "Fairness Screening", description: "Proxy tokens audited", status: "completed" },
  { id: "review", label: "Human Review", description: "Under financial aid officer review", status: "current" },
  { id: "decision", label: "Final Determination", description: "Official accountable sign-off", status: "pending" },
]

export function ReviewTimeline({
  steps = DEFAULT_TIMELINE,
  className = "",
}: ReviewTimelineProps) {
  return (
    <div className={`rounded-2xl border border-border bg-card p-6 space-y-4 ${className}`}>
      <div className="border-b pb-3">
        <h3 className="text-sm font-semibold text-foreground">
          Governance &amp; Review Lifecycle
        </h3>
        <p className="text-xs text-muted-foreground">
          Transparent multi-stage audit trail from submission to human sign-off
        </p>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-border">
        {steps.map((step) => {
          const isDone = step.status === "completed"
          const isCurrent = step.status === "current"

          return (
            <div key={step.id} className="relative flex items-start gap-3">
              <span
                className={`absolute -left-[23px] flex size-5 items-center justify-center rounded-full bg-card ring-4 ring-card transition-colors ${
                  isDone
                    ? "text-emerald-600 dark:text-emerald-400"
                    : isCurrent
                    ? "text-primary animate-pulse"
                    : "text-muted-foreground/40"
                }`}
              >
                {isDone ? (
                  <CheckCircle2Icon className="size-5 fill-emerald-500/20" />
                ) : isCurrent ? (
                  <CircleDotIcon className="size-5" />
                ) : (
                  <CircleIcon className="size-5" />
                )}
              </span>

              <div className="space-y-0.5 min-w-0">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-semibold ${
                      isDone || isCurrent ? "text-foreground" : "text-muted-foreground"
                    }`}
                  >
                    {step.label}
                  </span>
                  {step.timestamp && (
                    <span className="text-[10px] text-muted-foreground font-mono">
                      {step.timestamp}
                    </span>
                  )}
                </div>
                {step.description && (
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
