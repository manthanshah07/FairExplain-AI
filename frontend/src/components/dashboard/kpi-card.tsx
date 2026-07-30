import { ArrowDownRightIcon, ArrowUpRightIcon } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { DashboardKpi } from "@/lib/dashboard-data"

export function KpiCard({ kpi }: { kpi: DashboardKpi }) {
  const positive = kpi.delta >= 0
  const DeltaIcon = positive ? ArrowUpRightIcon : ArrowDownRightIcon

  return (
    <Card>
      <CardContent className="flex flex-col gap-3">
        <p className="text-sm text-muted-foreground">{kpi.label}</p>
        <div className="flex items-end justify-between gap-2">
          <span className="text-3xl font-semibold tracking-tight tabular-nums">
            {kpi.value}
          </span>
          <span
            className={cn(
              "flex items-center gap-0.5 rounded-full px-1.5 py-0.5 text-xs font-medium",
              positive
                ? "bg-success-muted text-success"
                : "bg-danger-muted text-destructive"
            )}
          >
            <DeltaIcon className="size-3" aria-hidden="true" />
            {Math.abs(kpi.delta)}%
          </span>
        </div>
        <p className="text-xs text-muted-foreground">{kpi.hint}</p>
      </CardContent>
    </Card>
  )
}
