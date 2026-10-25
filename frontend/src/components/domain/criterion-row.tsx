import { Link } from "react-router-dom"
import type { CriterionEvaluationDTO } from "@/types/domain"
import { StatusBadge } from "@/components/domain/status-badge"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatOperator } from "@/lib/format"
import { ArrowUpRightIcon, FileCheckIcon } from "lucide-react"

interface CriterionRowProps {
  criterion: CriterionEvaluationDTO
  onUploadClick?: (docType: string) => void
  applicationId?: string
}

export function CriterionRow({
  criterion,
  onUploadClick,
  applicationId,
}: CriterionRowProps) {
  const isPending =
    criterion.status === "pending_evidence" ||
    criterion.evidence_status === "missing" ||
    criterion.evidence_status === "unverified"

  const friendlyOperator = formatOperator(criterion.operator)

  const formatValue = (val: unknown) => {
    if (val === null || val === undefined) return "—"
    if (Array.isArray(val)) return val.join(", ")
    return String(val)
  }

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl border border-border/80 bg-card hover:bg-muted/20 transition-colors">
      <div className="space-y-1.5 flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-semibold text-sm capitalize text-foreground">
            {criterion.attribute.replace(/_/g, " ")}
          </span>

          {criterion.is_mandatory ? (
            <Badge variant="outline" className="text-[10px] uppercase font-bold tracking-wider border-primary/40 text-primary">
              Mandatory
            </Badge>
          ) : (
            <Badge variant="outline" className="text-[10px] uppercase font-medium text-muted-foreground">
              Optional / Merit
            </Badge>
          )}

          {criterion.evidence_required && (
            <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground font-mono">
              <FileCheckIcon className="size-3" />
              Evidence: {criterion.evidence_required}
            </span>
          )}
        </div>

        <p className="text-xs text-muted-foreground leading-relaxed">
          {criterion.reason}
        </p>

        {/* Parameter Target vs Actual Comparison */}
        <div className="flex flex-wrap items-center gap-3 pt-1 text-xs">
          <div className="text-muted-foreground">
            Rule benchmark:{" "}
            <span className="font-mono text-foreground font-medium">
              {friendlyOperator} {formatValue(criterion.target_value)}
            </span>
          </div>
          <span className="text-border" aria-hidden="true">•</span>
          <div className="text-muted-foreground">
            Verified actual:{" "}
            <span className="font-mono text-foreground font-semibold">
              {formatValue(criterion.actual_value)}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0 self-start sm:self-center">
        <StatusBadge status={criterion.status} size="md" />

        {isPending && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onUploadClick?.(criterion.evidence_required || "marksheet")}
            render={
              applicationId ? (
                <Link to={`/student/documents?app=${applicationId}&doc=${criterion.evidence_required || "marksheet"}`} />
              ) : undefined
            }
            className="text-xs font-medium border-amber-500/40 hover:bg-amber-500/10 text-amber-800 dark:text-amber-300 gap-1"
          >
            Upload Evidence
            <ArrowUpRightIcon className="size-3.5" />
          </Button>
        )}
      </div>
    </div>
  )
}
