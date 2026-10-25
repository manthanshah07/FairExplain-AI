import { env } from "@/config/env"
import type { LoanAssessResponseData } from "@/types/domain"
import { MoneyAmount } from "@/components/domain/money-amount"
import { StatusBadge } from "@/components/domain/status-badge"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import {
  BanknoteIcon,
  PercentIcon,
} from "lucide-react"

interface LoanAffordabilityGaugeProps {
  assessment?: LoanAssessResponseData | null
  className?: string
}

export function LoanAffordabilityGauge({
  assessment,
  className = "",
}: LoanAffordabilityGaugeProps) {
  // Respect feature flag
  if (!env.featureLoan) {
    return (
      <div className={`rounded-2xl border border-dashed border-border p-6 bg-muted/20 space-y-3 ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="size-8 rounded-lg bg-muted flex items-center justify-center text-muted-foreground">
              <BanknoteIcon className="size-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-foreground">
                Education Loan Need &amp; Affordability Assessment
              </h3>
              <p className="text-xs text-muted-foreground">
                Institutional repayment capacity underwriting
              </p>
            </div>
          </div>
          <Badge variant="outline" className="text-[10px] uppercase font-mono">
            Feature Flagged
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          The education loan serviceability module is currently in institutional pilot review. Check back after pilot launch or speak to an aid officer.
        </p>
      </div>
    )
  }

  if (!assessment) {
    return (
      <div className={`rounded-2xl border border-border p-6 text-center text-sm text-muted-foreground ${className}`}>
        Loan serviceability assessment pending evaluation.
      </div>
    )
  }

  const capacityUtil = parseFloat(assessment.capacity_utilization_percent || "0")
  const emi = parseFloat(assessment.estimated_emi || "0")
  const capacity = parseFloat(assessment.available_monthly_capacity || "0")

  return (
    <div className={`rounded-2xl border border-border bg-card p-6 space-y-6 ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-4">
        <div className="flex items-center gap-2">
          <div className="size-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
            <BanknoteIcon className="size-4" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-foreground">
              Education Loan Affordability (Post-Scholarship)
            </h3>
            <p className="text-xs text-muted-foreground">
              Evaluates actual loan needed after confirmed scholarship reductions
            </p>
          </div>
        </div>

        <StatusBadge status={assessment.outcome} size="md" />
      </div>

      {/* Loan Financial Metrics */}
      <div className="grid gap-4 grid-cols-2 sm:grid-cols-4">
        <div className="rounded-xl border p-3.5 bg-background/60 space-y-1">
          <span className="text-xs text-muted-foreground">Post-Scholarship Loan</span>
          <div>
            <MoneyAmount amount={assessment.post_scholarship_loan_amount} size="lg" />
          </div>
        </div>

        <div className="rounded-xl border p-3.5 bg-background/60 space-y-1">
          <span className="text-xs text-muted-foreground">Monthly Capacity</span>
          <div>
            <MoneyAmount amount={assessment.available_monthly_capacity} size="lg" />
          </div>
        </div>

        <div className="rounded-xl border p-3.5 bg-background/60 space-y-1">
          <span className="text-xs text-muted-foreground">Estimated Monthly EMI</span>
          <div>
            <MoneyAmount amount={assessment.estimated_emi} size="lg" />
          </div>
        </div>

        <div className="rounded-xl border p-3.5 bg-background/60 space-y-1">
          <span className="text-xs text-muted-foreground">Tenure Horizon</span>
          <div className="text-lg font-bold font-mono">
            {assessment.tenure_months}{" "}
            <span className="text-xs font-sans text-muted-foreground font-normal">Months</span>
          </div>
        </div>
      </div>

      {/* Affordability Gauge Bar */}
      <div className="space-y-2 rounded-xl bg-muted/40 p-4 border">
        <div className="flex items-center justify-between text-xs">
          <span className="font-semibold text-foreground flex items-center gap-1.5">
            <PercentIcon className="size-3.5 text-primary" />
            Monthly Capacity Utilization: {capacityUtil.toFixed(1)}%
          </span>
          <span className="text-muted-foreground font-mono">
            EMI ₹{emi.toLocaleString()} / Capacity ₹{capacity.toLocaleString()}
          </span>
        </div>

        <Progress
          value={Math.min(100, capacityUtil)}
          className="h-2.5 bg-muted"
        />

        <div className="flex justify-between text-[11px] text-muted-foreground pt-1">
          <span>0% (No Debt)</span>
          <span className="text-emerald-600 font-medium">Safe Margin (&lt;80%)</span>
          <span className="text-amber-600 font-medium">Threshold (100%)</span>
          <span className="text-rose-600 font-medium">&gt;120% (Overburdened)</span>
        </div>
      </div>

      <p className="text-xs text-muted-foreground leading-relaxed">
        <strong>Affordability Rationale: </strong>
        {assessment.reason}
      </p>
    </div>
  )
}
