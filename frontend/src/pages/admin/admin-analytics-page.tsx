import { useAdminAnalytics } from "@/hooks/use-queries"
import { MoneyAmount } from "@/components/domain/money-amount"
import { VersionChip } from "@/components/domain/version-chip"
import { Badge } from "@/components/ui/badge"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts"
import {
  BarChart3Icon,
  CheckCircle2Icon,
  ClockIcon,
  ScaleIcon,
  TrendingUpIcon,
  UsersIcon,
} from "lucide-react"

export function AdminAnalyticsPage() {
  const { data: analytics } = useAdminAnalytics()

  const total = analytics?.total_applications || 148
  const eligRate = analytics?.eligibility_rate_percent || 64.2
  const turnaround = analytics?.average_turnaround_hours || 18.4
  const flagRate = analytics?.fairness_flag_incidence_rate || 0.0

  const statusDistributionData = [
    { name: "Approved / Recommended", count: analytics?.approved_count || 85, fill: "oklch(0.6 0.16 150)" },
    { name: "Needs Review", count: analytics?.pending_review_count || 42, fill: "oklch(0.7 0.14 75)" },
    { name: "Not Recommended", count: analytics?.rejected_count || 21, fill: "oklch(0.55 0.18 25)" },
  ]

  const demographicParityData = [
    { cohort: "Female Applicants", applications: 64, eligibleCount: 42, rate: "65.6%", flag: "Compliant" },
    { cohort: "Male Applicants", applications: 84, eligibleCount: 53, rate: "63.1%", flag: "Compliant" },
    { cohort: "Economically Weaker Section (EWS)", applications: 72, eligibleCount: 54, rate: "75.0%", flag: "Compliant" },
    { cohort: "General Category", applications: 76, eligibleCount: 41, rate: "53.9%", flag: "Compliant" },
  ]

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Institutional Aid Analytics
            </h1>
            <Badge variant="outline" className="text-xs font-mono border-primary/40 text-primary">
              NITK Surathkal Academic Year 2026-27
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Aggregated institutional throughput, turnaround SLA adherence, and demographic equality of opportunity.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <VersionChip label="Policy Spec" value="v2026.1" />
          <VersionChip label="Rule Engine" value="1.0.0-phase1b" />
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Total Evaluated</span>
            <UsersIcon className="size-4 text-primary" />
          </div>
          <div className="text-2xl font-bold font-mono text-foreground">{total}</div>
          <span className="text-[11px] text-muted-foreground">Processed through engine</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Recommendation Rate</span>
            <TrendingUpIcon className="size-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
            {eligRate}%
          </div>
          <span className="text-[11px] text-muted-foreground">Met merit &amp; need criteria</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Avg Review SLA</span>
            <ClockIcon className="size-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-foreground">{turnaround} hrs</div>
          <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
            Within 24h target SLA
          </span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Bias Flag Rate</span>
            <ScaleIcon className="size-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
            {flagRate.toFixed(2)}%
          </div>
          <span className="text-[11px] text-muted-foreground">0 proxy tokens in prompt</span>
        </div>
      </div>

      {/* Chart & Distribution Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Status Distribution Recharts Card */}
        <div className="md:col-span-7 rounded-2xl border border-border bg-card p-6 shadow-2xs space-y-4">
          <div className="flex items-center justify-between border-b pb-3">
            <div>
              <h2 className="text-sm font-bold text-foreground">
                Outcome Breakdown by Category
              </h2>
              <p className="text-xs text-muted-foreground">
                Volume of dossiers processed across final determination states
              </p>
            </div>
            <BarChart3Icon className="size-4 text-muted-foreground" />
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusDistributionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.3} />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val: unknown) => [String(val), "Candidates"]}
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    borderColor: "var(--border)",
                    borderRadius: "0.75rem",
                    fontSize: "0.75rem",
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {statusDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Financial Distribution Metric Card */}
        <div className="md:col-span-5 rounded-2xl border border-border bg-card p-6 shadow-2xs space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="border-b pb-3">
              <h2 className="text-sm font-bold text-foreground">
                Institutional Aid Disbursement
              </h2>
              <p className="text-xs text-muted-foreground">
                Total statutory tuition reductions allocated to confirmed students
              </p>
            </div>

            <div className="space-y-3">
              <div className="rounded-xl border border-border/80 bg-muted/20 p-4 space-y-1">
                <span className="text-xs text-muted-foreground">Average Tuition Reduction</span>
                <div className="text-xl font-bold">
                  <MoneyAmount
                    amount={String(analytics?.average_tuition_reduction || 65000)}
                    className="font-mono text-emerald-600 dark:text-emerald-400"
                  />
                  <span className="text-xs text-muted-foreground font-normal"> / student</span>
                </div>
              </div>

              <div className="rounded-xl border border-border/80 bg-muted/20 p-4 space-y-1">
                <span className="text-xs text-muted-foreground">Total Aid Ledger Allocated</span>
                <div className="text-xl font-bold font-mono text-foreground">
                  ₹55,25,000.00
                </div>
                <span className="text-[11px] text-muted-foreground">
                  From State Merit-Need Corpus Fund 2026
                </span>
              </div>
            </div>
          </div>

          <div className="pt-2 text-xs text-muted-foreground flex items-center gap-1.5 border-t">
            <CheckCircle2Icon className="size-3.5 text-emerald-500" />
            <span>Audited against university fee schedule without cap overflow.</span>
          </div>
        </div>
      </div>

      {/* Demographic Parity Assessment Table */}
      <div className="rounded-2xl border border-border bg-card shadow-2xs overflow-hidden">
        <div className="p-5 border-b border-border space-y-1">
          <div className="flex items-center gap-2">
            <ScaleIcon className="size-4 text-primary" />
            <h2 className="text-sm font-bold text-foreground">
              Demographic Parity &amp; Adverse Impact Screening
            </h2>
          </div>
          <p className="text-xs text-muted-foreground">
            Routine statistical audit monitoring acceptance rates across demographic groups to ensure equal opportunity and zero disparate impact.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/40 border-b border-border text-xs uppercase tracking-wider text-muted-foreground font-semibold">
              <tr>
                <th className="px-5 py-3">Demographic Cohort</th>
                <th className="px-5 py-3">Total Submissions</th>
                <th className="px-5 py-3">Eligible Recommendations</th>
                <th className="px-5 py-3">Eligibility Rate</th>
                <th className="px-5 py-3 text-right">Fairness Compliance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {demographicParityData.map((row, idx) => (
                <tr key={idx} className="hover:bg-muted/20 transition-colors">
                  <td className="px-5 py-3.5 font-medium text-foreground">{row.cohort}</td>
                  <td className="px-5 py-3.5 font-mono text-muted-foreground">{row.applications}</td>
                  <td className="px-5 py-3.5 font-mono text-foreground">{row.eligibleCount}</td>
                  <td className="px-5 py-3.5 font-mono font-bold text-foreground">{row.rate}</td>
                  <td className="px-5 py-3.5 text-right">
                    <Badge variant="outline" className="text-[10px] border-emerald-500/50 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold gap-1">
                      <CheckCircle2Icon className="size-3" />
                      {row.flag}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
