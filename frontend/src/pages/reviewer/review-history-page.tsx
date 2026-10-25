import { useState } from "react"
import { Link } from "react-router-dom"
import { VersionChip } from "@/components/domain/version-chip"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  ArrowRightIcon,
  CheckCircle2Icon,
  ClockIcon,
  HistoryIcon,
  ShieldAlertIcon,
  ShieldCheckIcon,
  UserCheckIcon,
} from "lucide-react"

interface ReviewHistoryRecord {
  id: string
  application_id: string
  candidate_name: string
  candidate_email: string
  algorithmic_recommendation: "ELIGIBLE" | "INELIGIBLE" | "PENDING_EVIDENCE"
  final_decision: "confirmed" | "overridden" | "evidence_requested"
  rationale: string
  reviewer_name: string
  reviewer_role: string
  decided_at: string
  signature_hash: string
}

const MOCK_HISTORY: ReviewHistoryRecord[] = [
  {
    id: "DEC-2026-001",
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    candidate_name: "Priya Sharma",
    candidate_email: "priya.sharma@nitk.edu.in",
    algorithmic_recommendation: "ELIGIBLE",
    final_decision: "confirmed",
    rationale:
      "All statutory income certificates and semester transcripts independently verified against state treasury records. Award confirmed in full.",
    reviewer_name: "Dr. Sarah Jenkins",
    reviewer_role: "Senior Aid Officer",
    decided_at: "2026-10-25T11:24:00Z",
    signature_hash: "a4f891b29ce3400d98e8211029cfa90218b0c9502948cbb39d0124881ae01192",
  },
  {
    id: "DEC-2026-002",
    application_id: "1b905a81-d102-4fc8-9f15-84950b7b3b42",
    candidate_name: "Rahul Verma",
    candidate_email: "rahul.verma@nitk.edu.in",
    algorithmic_recommendation: "INELIGIBLE",
    final_decision: "overridden",
    rationale:
      "Discretionary waiver granted under Institutional Calamity Hardship Charter clause 4.2. Recent medical emergency documentation accepted in place of current ITR.",
    reviewer_name: "Dr. Sarah Jenkins",
    reviewer_role: "Senior Aid Officer",
    decided_at: "2026-10-24T16:45:00Z",
    signature_hash: "7c19a842b090df48e028bca192084c810938ffba129849201bd498194a029381",
  },
  {
    id: "DEC-2026-003",
    application_id: "2c905a81-d102-4fc8-9f15-84950b7b3b43",
    candidate_name: "Ananya Patel",
    candidate_email: "ananya.patel@nitk.edu.in",
    algorithmic_recommendation: "PENDING_EVIDENCE",
    final_decision: "evidence_requested",
    rationale:
      "Income certificate submitted was expired by 3 months. Student notified via portal to furnish latest Tehsildar certificate within 14 days.",
    reviewer_name: "Marcus Vance",
    reviewer_role: "Compliance Officer",
    decided_at: "2026-10-23T14:10:00Z",
    signature_hash: "c983018274091abdf83910482094182901384019284019284091283019284901",
  },
]

export function ReviewHistoryPage() {
  const [filter, setFilter] = useState<string>("all")

  const filteredHistory = MOCK_HISTORY.filter((item) => {
    if (filter === "all") return true
    return item.final_decision === filter
  })

  const total = MOCK_HISTORY.length
  const confirmedCount = MOCK_HISTORY.filter((i) => i.final_decision === "confirmed").length
  const overrideCount = MOCK_HISTORY.filter((i) => i.final_decision === "overridden").length

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Determinations &amp; Audit Trail
            </h1>
            <Badge variant="outline" className="text-xs font-mono border-primary/40 text-primary">
              Immutable Ledger
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Complete cryptographic audit trail of all financial aid decisions certified by institutional officers.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            render={<Link to="/reviewer" />}
            variant="outline"
            size="sm"
            className="gap-1.5"
          >
            <HistoryIcon className="size-4" />
            Back to Queue
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Total Determinations</span>
            <UserCheckIcon className="size-4 text-primary" />
          </div>
          <div className="text-2xl font-bold font-mono text-foreground">{total}</div>
          <span className="text-[11px] text-muted-foreground">Signed &amp; archived</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Confirmed Recommendations</span>
            <CheckCircle2Icon className="size-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
            {confirmedCount}
          </div>
          <span className="text-[11px] text-muted-foreground">Algorithmic concordances</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Officer Overrides</span>
            <ShieldAlertIcon className="size-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-600 dark:text-amber-400">
            {overrideCount}
          </div>
          <span className="text-[11px] text-muted-foreground">Discretionary exemptions</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Average Turnaround</span>
            <ClockIcon className="size-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-foreground">18.4 hrs</div>
          <span className="text-[11px] text-muted-foreground">SLA target: 48.0 hrs</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b pb-3">
        <span className="text-xs font-medium text-muted-foreground mr-1">Filter determinations:</span>
        {[
          { id: "all", label: "All Decisions" },
          { id: "confirmed", label: "Confirmed" },
          { id: "overridden", label: "Officer Overrides" },
          { id: "evidence_requested", label: "Evidence Requested" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filter === tab.id
                ? "bg-primary text-primary-foreground shadow-2xs"
                : "bg-muted/40 text-muted-foreground hover:bg-muted hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* History Records List */}
      <div className="space-y-4">
        {filteredHistory.map((record) => {
          const isOverride = record.final_decision === "overridden"
          const isConfirmed = record.final_decision === "confirmed"

          return (
            <div
              key={record.id}
              className="rounded-2xl border border-border bg-card p-6 shadow-2xs space-y-4 hover:border-primary/40 transition-colors"
            >
              {/* Record Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <h2 className="text-base font-bold text-foreground">{record.candidate_name}</h2>
                    <span className="text-xs text-muted-foreground font-mono">
                      {record.candidate_email}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground">
                    <VersionChip value={record.application_id} type="hash" />
                    <span>·</span>
                    <span>Decided {new Date(record.decided_at).toLocaleString("en-IN")}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    render={<Link to={`/reviewer/case/${record.application_id}`} />}
                    variant="outline"
                    size="sm"
                    className="gap-1.5 text-xs font-semibold"
                  >
                    <span>View Dossier</span>
                    <ArrowRightIcon className="size-3.5" />
                  </Button>
                </div>
              </div>

              {/* Decision Comparative Diff */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Algorithmic Baseline */}
                <div className="p-3.5 rounded-xl border border-border/80 bg-muted/20 space-y-1.5">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground block font-bold">
                    Algorithmic System Recommendation
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-foreground">
                      Recommended: {record.algorithmic_recommendation}
                    </span>
                    <Badge variant="outline" className="text-[10px] font-mono">
                      Automated
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Based on AST rule evaluation against official criteria and tuition schedule.
                  </p>
                </div>

                {/* Final Human Determination */}
                <div
                  className={`p-3.5 rounded-xl border space-y-1.5 ${
                    isOverride
                      ? "border-amber-500/40 bg-amber-500/5 text-amber-900 dark:text-amber-200"
                      : isConfirmed
                      ? "border-emerald-500/40 bg-emerald-500/5 text-emerald-900 dark:text-emerald-200"
                      : "border-blue-500/40 bg-blue-500/5 text-blue-900 dark:text-blue-200"
                  }`}
                >
                  <span className="text-[10px] font-mono uppercase tracking-wider block font-bold">
                    Final Human Determination
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm capitalize">
                      {record.final_decision.replace(/_/g, " ")}
                    </span>
                    <Badge
                      variant="outline"
                      className={`text-[10px] font-bold uppercase ${
                        isOverride
                          ? "border-amber-500 text-amber-700 dark:text-amber-300"
                          : "border-emerald-500 text-emerald-700 dark:text-emerald-300"
                      }`}
                    >
                      Official Sign-Off
                    </Badge>
                  </div>
                  <div className="text-xs font-medium">
                    Officer: {record.reviewer_name} ({record.reviewer_role})
                  </div>
                </div>
              </div>

              {/* Written Statutory Rationale */}
              <div className="rounded-xl border border-border/70 bg-card p-4 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                  <ShieldCheckIcon className="size-3.5 text-primary" />
                  <span>Mandatory Statutory Rationale:</span>
                </div>
                <p className="text-xs text-foreground/90 italic leading-relaxed">
                  "{record.rationale}"
                </p>
              </div>

              {/* Cryptographic Digital Signature Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-2 border-t border-border/60 text-[11px] font-mono text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <span>Cryptographic Signature:</span>
                  <span className="font-semibold text-foreground">{record.signature_hash.slice(0, 24)}...</span>
                </div>
                <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2Icon className="size-3.5" />
                  <span>Integrity Verified via SHA-256</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
