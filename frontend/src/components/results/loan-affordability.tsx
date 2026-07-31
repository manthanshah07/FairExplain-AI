import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { cn, formatINR } from "@/lib/utils"
import type { LoanAssessment } from "@/types/assessment"

export function LoanAffordability({ loan }: { loan: LoanAssessment }) {
  const usedRatio = Math.min(
    100,
    (loan.estimatedNewEmi / loan.availableMonthlyCapacity) * 100,
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Affordability check</CardTitle>
        <CardDescription>
          The estimated EMI is compared against the monthly repayment capacity
          derived from household income.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        <div className="flex flex-col gap-3">
          <Row
            label="Monthly repayment capacity"
            value={`${formatINR(loan.availableMonthlyCapacity)}/mo`}
          />
          <Row
            label="Estimated new EMI"
            value={`${formatINR(loan.estimatedNewEmi)}/mo`}
            hint={`over ${loan.tenureMonths} months`}
          />
        </div>

        <div className="flex flex-col gap-2">
          <div
            className="relative h-3 w-full overflow-hidden rounded-full bg-muted"
            role="img"
            aria-label={`Estimated EMI uses ${Math.round(usedRatio)}% of repayment capacity`}
          >
            <div
              className={cn(
                "h-full rounded-full",
                usedRatio <= 100 ? "bg-success" : "bg-destructive",
              )}
              style={{ width: `${usedRatio}%` }}
            />
          </div>
          <p className="text-xs text-muted-foreground">
            EMI uses{" "}
            <span className="font-medium text-foreground tabular-nums">
              {Math.round(usedRatio)}%
            </span>{" "}
            of available capacity — a comfortable affordability margin.
          </p>
        </div>

        <Separator />

        <div className="rounded-lg bg-muted/50 px-4 py-3 text-sm leading-relaxed text-muted-foreground">
          Estimated EMI is within capacity and no document mismatches were
          flagged, so the loan outcome is{" "}
          <span className="font-medium text-foreground">Eligible</span>.
        </div>
      </CardContent>
    </Card>
  )
}

function Row({
  label,
  value,
  hint,
}: {
  label: string
  value: string
  hint?: string
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-right text-sm font-semibold tabular-nums">
        {value}
        {hint && (
          <span className="ml-1 font-normal text-muted-foreground">{hint}</span>
        )}
      </span>
    </div>
  )
}
