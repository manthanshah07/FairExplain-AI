import { useState } from "react"
import { Button } from "@/components/ui/button"
import type { ReviewDecision } from "@/types/domain"
import { AlertCircleIcon, ShieldAlertIcon } from "lucide-react"

interface ConfirmDialogProps {
  isOpen: boolean
  decision: ReviewDecision
  applicantName: string
  onClose: () => void
  onConfirm: (rationale: string) => void
  isSubmitting?: boolean
}

export function ConfirmDialog({
  isOpen,
  decision,
  applicantName,
  onClose,
  onConfirm,
  isSubmitting = false,
}: ConfirmDialogProps) {
  const [rationale, setRationale] = useState("")

  if (!isOpen) return null

  const isOverride = decision === "override"
  const isReject = decision === "reject"
  const isRequest = decision === "request_evidence"

  const title =
    isOverride
      ? "Confirm Officer Override"
      : isReject
      ? "Confirm Ineligibility Determination"
      : isRequest
      ? "Request Additional Evidence"
      : "Confirm Algorithm Recommendation"

  const isInvalid = isOverride && rationale.trim().length < 5

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-xs animate-in fade-in-0"
    >
      <div className="w-full max-w-lg rounded-2xl border border-border bg-card p-6 shadow-xl space-y-4 text-card-foreground">
        <div className="flex items-center gap-2.5">
          <div
            className={`size-9 rounded-lg flex items-center justify-center ${
              isOverride ? "bg-amber-500/15 text-amber-600" : "bg-primary/10 text-primary"
            }`}
          >
            <ShieldAlertIcon className="size-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-foreground">{title}</h3>
            <p className="text-xs text-muted-foreground">
              Applicant: <span className="font-semibold text-foreground">{applicantName}</span>
            </p>
          </div>
        </div>

        <div className="text-xs text-muted-foreground space-y-2 bg-muted/40 p-3.5 rounded-xl border">
          <p>
            You are recording an official determination as an authorized institutional reviewer. This action will be permanently sealed into the immutable cryptographic audit log.
          </p>
          {isOverride && (
            <p className="font-semibold text-amber-800 dark:text-amber-400">
              * Overrides strictly mandate a written justification explaining the institutional policy basis.
            </p>
          )}
        </div>

        <div className="space-y-1.5">
          <label htmlFor="rationale" className="text-xs font-semibold text-foreground">
            Justification &amp; Determination Notes {isOverride && <span className="text-destructive">*</span>}
          </label>
          <textarea
            id="rationale"
            rows={3}
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
            placeholder="Document the exact basis for this decision (e.g. verified income certificate directly with registrar)..."
            className="w-full rounded-xl border border-border bg-background p-3 text-xs text-foreground placeholder:text-muted-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
          />
          {isOverride && rationale.trim().length < 5 && (
            <p className="text-[11px] text-destructive flex items-center gap-1">
              <AlertCircleIcon className="size-3" /> Mandatory justification must be at least 5 characters.
            </p>
          )}
        </div>

        <div className="flex items-center justify-end gap-2 pt-2 border-t">
          <Button variant="outline" size="sm" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            size="sm"
            variant={isReject ? "destructive" : "default"}
            disabled={isInvalid || isSubmitting}
            onClick={() => onConfirm(rationale)}
          >
            {isSubmitting ? "Recording Audit Entry..." : "Confirm & Sign Off"}
          </Button>
        </div>
      </div>
    </div>
  )
}
