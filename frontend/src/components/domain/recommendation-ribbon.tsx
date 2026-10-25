import { ShieldCheckIcon, UserCheckIcon } from "lucide-react"

interface RecommendationRibbonProps {
  className?: string
  officerDecision?: string | null
  officerName?: string | null
  decidedAt?: string | null
}

export function RecommendationRibbon({
  className = "",
  officerDecision,
  officerName,
  decidedAt,
}: RecommendationRibbonProps) {
  if (officerDecision) {
    return (
      <div
        className={`flex items-center gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-900 dark:text-emerald-300 shadow-2xs ${className}`}
      >
        <UserCheckIcon className="size-5 shrink-0 text-emerald-600 dark:text-emerald-400" />
        <div className="flex-1">
          <span className="font-semibold">Official Human Determination Recorded:</span>{" "}
          <span className="capitalize font-medium">"{officerDecision}"</span>
          {officerName && <span> by authorized officer {officerName}</span>}
          {decidedAt && (
            <span className="text-xs text-muted-foreground block sm:inline sm:ml-2">
              · Confirmed {new Date(decidedAt).toLocaleDateString()}
            </span>
          )}
        </div>
      </div>
    )
  }

  return (
    <div
      className={`flex items-center gap-3 rounded-xl border border-primary/25 bg-primary/5 px-4 py-3 text-sm text-foreground shadow-2xs ${className}`}
    >
      <ShieldCheckIcon className="size-5 shrink-0 text-primary" />
      <div className="flex-1 leading-snug">
        <span className="font-semibold text-primary">Decision-Support Recommendation:</span>{" "}
        <span className="text-muted-foreground">
          Pending formal review and approval by an authorized institutional financial aid officer. Nothing is auto-awarded or finalized by the AI.
        </span>
      </div>
    </div>
  )
}
