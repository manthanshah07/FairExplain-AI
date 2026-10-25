import { useState } from "react"
import type { TuitionAccountingDTO } from "@/types/domain"
import { MoneyAmount } from "@/components/domain/money-amount"
import { formatCompactINR, formatINR } from "@/lib/format"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { AlertCircleIcon, TableIcon, BarChart3Icon } from "lucide-react"

interface TuitionWaterfallProps {
  accounting?: TuitionAccountingDTO | null
  className?: string
}

export function TuitionWaterfall({ accounting, className = "" }: TuitionWaterfallProps) {
  const [viewMode, setViewMode] = useState<"chart" | "table">("chart")

  if (!accounting) {
    return (
      <div className="rounded-2xl border border-border p-6 text-center text-sm text-muted-foreground">
        No tuition accounting breakdown available for this application.
      </div>
    )
  }

  const gross = parseFloat(accounting.gross_eligible_tuition || "0")
  const remaining = parseFloat(accounting.remaining_payable_tuition || "0")
  const surplus = parseFloat(accounting.total_unapplied_surplus || "0")

  // Assemble Waterfall Steps
  // 1. Gross Tuition
  // 2. Confirmed Awards (reduction)
  // 3. Remaining Payable Tuition
  // 4. Unapplied Surplus (if > 0)
  const chartData = [
    {
      name: "Gross Tuition",
      amount: gross,
      fill: "oklch(0.5 0.08 210)", // slate neutral
      type: "base",
    },
    ...accounting.allocations.map((a) => ({
      name: a.title,
      amount: parseFloat(a.effective_reduction),
      fill: "oklch(0.6 0.16 150)", // emerald green
      type: "reduction",
    })),
    {
      name: "Remaining Due",
      amount: remaining,
      fill: "oklch(0.45 0.16 265)", // brand indigo
      type: "net",
    },
    ...(surplus > 0
      ? [
          {
            name: "Unapplied Surplus",
            amount: surplus,
            fill: "oklch(0.7 0.15 75)", // amber hatched
            type: "surplus",
          },
        ]
      : []),
  ]

  return (
    <div className={`rounded-2xl border border-border bg-card p-6 space-y-6 ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-4">
        <div>
          <h3 className="text-base font-semibold text-foreground">
            Tuition Accounting &amp; Award Allocation
          </h3>
          <p className="text-xs text-muted-foreground">
            Deterministic allocation order · Applied institutional fee caps
          </p>
        </div>

        {/* View Mode Toggle for Accessibility (Data Table vs Chart) */}
        <div className="flex items-center gap-1 self-start sm:self-center bg-muted/60 p-1 rounded-lg border text-xs">
          <button
            onClick={() => setViewMode("chart")}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md font-medium transition-colors ${
              viewMode === "chart" ? "bg-card text-foreground shadow-2xs font-semibold" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <BarChart3Icon className="size-3.5" />
            Chart
          </button>
          <button
            onClick={() => setViewMode("table")}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md font-medium transition-colors ${
              viewMode === "table" ? "bg-card text-foreground shadow-2xs font-semibold" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <TableIcon className="size-3.5" />
            Table
          </button>
        </div>
      </div>

      {/* KPI Balance Cards */}
      <div className="grid gap-4 grid-cols-2 sm:grid-cols-4">
        <div className="rounded-xl border p-3.5 bg-background/60 space-y-1">
          <span className="text-xs text-muted-foreground">Gross Tuition</span>
          <div>
            <MoneyAmount amount={accounting.gross_eligible_tuition} size="lg" />
          </div>
        </div>

        <div className="rounded-xl border p-3.5 bg-emerald-500/[0.04] border-emerald-500/20 space-y-1">
          <span className="text-xs text-emerald-800 dark:text-emerald-400">Total Scholarship Waiver</span>
          <div>
            <MoneyAmount amount={accounting.total_effective_reduction} size="lg" trend="positive" />
          </div>
        </div>

        <div className="rounded-xl border p-3.5 bg-primary/[0.04] border-primary/20 space-y-1">
          <span className="text-xs text-primary font-medium">Net Payable Tuition</span>
          <div>
            <MoneyAmount amount={accounting.remaining_payable_tuition} size="lg" />
          </div>
        </div>

        <div className="rounded-xl border p-3.5 bg-amber-500/[0.04] border-amber-500/20 space-y-1">
          <span className="text-xs text-amber-800 dark:text-amber-400">Unapplied Surplus</span>
          <div>
            <MoneyAmount amount={accounting.total_unapplied_surplus} size="lg" />
          </div>
        </div>
      </div>

      {/* Visual Chart / Accessible Table Mode */}
      {viewMode === "chart" ? (
        <div className="h-64 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.3} />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} tickLine={false} />
              <YAxis
                tickFormatter={(val) => formatCompactINR(val)}
                tick={{ fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                formatter={(val: any) => [formatINR(val), "Amount"]}
                contentStyle={{
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)",
                  borderRadius: "0.75rem",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="amount" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="rounded-xl border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Accounting Step</TableHead>
                <TableHead>Type</TableHead>
                <TableHead className="text-right">Monetary Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {chartData.map((row, idx) => (
                <TableRow key={idx}>
                  <TableCell className="font-medium text-foreground">{row.name}</TableCell>
                  <TableCell className="capitalize text-xs text-muted-foreground">{row.type}</TableCell>
                  <TableCell className="text-right font-mono">
                    <MoneyAmount amount={row.amount} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Domain Note on Surplus */}
      {surplus > 0 && (
        <div className="rounded-xl border border-amber-500/25 bg-amber-500/5 p-4 text-xs text-amber-900 dark:text-amber-300 flex items-start gap-3">
          <AlertCircleIcon className="size-4 shrink-0 mt-0.5 text-amber-600 dark:text-amber-400" />
          <div className="space-y-1">
            <span className="font-semibold block">Policy Rule: Unapplied Surplus Distinction</span>
            <p className="leading-relaxed opacity-90">
              The unapplied surplus of {formatINR(accounting.total_unapplied_surplus)} represents scholarship entitlement capped by the institutional fee ceiling. By university statute, surplus does not convert to cash, cannot be disbursed as a living stipend, and is not refundable to the student.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
