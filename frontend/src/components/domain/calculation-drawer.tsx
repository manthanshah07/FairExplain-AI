import { Button } from "@/components/ui/button"
import { CalculatorIcon, XIcon } from "lucide-react"

interface CalculationDrawerProps {
  isOpen: boolean
  onClose: () => void
  title: string
  formula: string
  inputs: Record<string, string | number>
  engineVersion?: string
  policyVersion?: string
  notes?: string
}

export function CalculationDrawer({
  isOpen,
  onClose,
  title,
  formula,
  inputs,
  engineVersion = "1.0.0-phase1b",
  policyVersion = "1.0.0",
  notes,
}: CalculationDrawerProps) {
  if (!isOpen) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex justify-end bg-background/80 backdrop-blur-xs animate-in fade-in-0"
    >
      <div className="w-full max-w-md h-full bg-card border-l border-border p-6 shadow-2xl flex flex-col justify-between overflow-y-auto animate-in slide-in-from-right duration-200">
        <div className="space-y-6">
          <div className="flex items-center justify-between border-b pb-4">
            <div className="flex items-center gap-2">
              <div className="size-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                <CalculatorIcon className="size-4" />
              </div>
              <div>
                <h3 className="text-base font-bold text-foreground">Calculation Transparency</h3>
                <p className="text-xs text-muted-foreground">{title}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              aria-label="Close calculation drawer"
              className="rounded-lg p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
            >
              <XIcon className="size-4" />
            </button>
          </div>

          {/* Formula */}
          <div className="space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Mathematical Formula
            </span>
            <div className="rounded-xl border bg-muted/40 p-4 font-mono text-xs text-foreground leading-relaxed">
              {formula}
            </div>
          </div>

          {/* Frozen Inputs */}
          <div className="space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Evaluated Input Snapshots
            </span>
            <div className="rounded-xl border divide-y overflow-hidden text-xs">
              {Object.entries(inputs).map(([key, val]) => (
                <div key={key} className="flex justify-between p-3 bg-background/60">
                  <span className="text-muted-foreground capitalize">{key.replace(/_/g, " ")}:</span>
                  <span className="font-mono font-bold text-foreground">{String(val)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Notes */}
          {notes && (
            <div className="rounded-xl border border-primary/20 bg-primary/5 p-3.5 text-xs text-muted-foreground leading-relaxed">
              <strong className="text-foreground block mb-1">Domain Precision Rule:</strong>
              {notes}
            </div>
          )}

          {/* Version Provenance */}
          <div className="rounded-xl border bg-card p-3.5 space-y-1.5 text-xs">
            <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
              Provenance &amp; Auditability
            </span>
            <div className="flex justify-between font-mono text-[11px]">
              <span className="text-muted-foreground">Rule Engine:</span>
              <span className="text-foreground font-semibold">{engineVersion}</span>
            </div>
            <div className="flex justify-between font-mono text-[11px]">
              <span className="text-muted-foreground">Policy Spec:</span>
              <span className="text-foreground font-semibold">v{policyVersion}</span>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t mt-6">
          <Button onClick={onClose} className="w-full" size="sm">
            Close Explainer
          </Button>
        </div>
      </div>
    </div>
  )
}
