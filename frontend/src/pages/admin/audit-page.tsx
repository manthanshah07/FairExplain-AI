import { useState } from "react"
import { VersionChip } from "@/components/domain/version-chip"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  ChevronDownIcon,
  ChevronUpIcon,
  FilterIcon,
  FingerprintIcon,
  SearchIcon,
  ShieldCheckIcon,
  TerminalIcon,
} from "lucide-react"

interface AuditLogEntry {
  id: string
  application_id: string
  event_type: "application_submitted" | "rules_executed" | "ocr_verified" | "decision_recorded" | "explanation_generated"
  actor: string
  actor_role: string
  timestamp: string
  state_sha256: string
  payload: Record<string, unknown>
}

const MOCK_AUDIT_LOGS: AuditLogEntry[] = [
  {
    id: "LOG-2026-9011",
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    event_type: "decision_recorded",
    actor: "USR-OFFICER-001 (Dr. Sarah Jenkins)",
    actor_role: "Senior Aid Officer",
    timestamp: "2026-10-25T11:24:00Z",
    state_sha256: "a4f891b29ce3400d98e8211029cfa90218b0c9502948cbb39d0124881ae01192",
    payload: {
      action: "CONFIRM_RECOMMENDATION",
      decision: "approve",
      rationale: "Statutory income certificates verified against state treasury records.",
      effective_reduction: "65000.00",
      payable_tuition: "60000.00",
    },
  },
  {
    id: "LOG-2026-9010",
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    event_type: "explanation_generated",
    actor: "SYS-EXPLAINER-v1.0",
    actor_role: "Deterministic LLM Explainer",
    timestamp: "2026-10-25T10:00:06Z",
    state_sha256: "b182049182903182039182390182390128390128301928301928301928301928",
    payload: {
      prompt_version: "v1.0-phase4",
      tokens_processed: 642,
      protected_tokens_detected: 0,
      grounding_verification: "PASS",
    },
  },
  {
    id: "LOG-2026-9009",
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    event_type: "ocr_verified",
    actor: "SYS-OCR-VISION-2.1",
    actor_role: "Automated OCR Verification Service",
    timestamp: "2026-10-25T10:00:04Z",
    state_sha256: "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    payload: {
      document_type: "income_proof",
      extracted_income: 450000,
      reported_income: 450000,
      confidence_score: 0.98,
      mismatch_flag: false,
    },
  },
  {
    id: "LOG-2026-9008",
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    event_type: "rules_executed",
    actor: "SYS-RULE-ENGINE-1.0.0",
    actor_role: "AST Deterministic Rule Evaluator",
    timestamp: "2026-10-25T10:00:02Z",
    state_sha256: "3d91028301928301928301928301928301928301928301928301928301928301",
    payload: {
      policy_id: "MERIT_NEED_2026",
      policy_version: "v2026.1",
      rules_evaluated: 5,
      rules_satisfied: 4,
      rules_pending: 0,
      status: "ELIGIBLE",
    },
  },
  {
    id: "LOG-2026-9007",
    application_id: "0a905a81-d102-4fc8-9f15-84950b7b3b41",
    event_type: "application_submitted",
    actor: "Priya Sharma (Student)",
    actor_role: "Applicant",
    timestamp: "2026-10-25T10:00:00Z",
    state_sha256: "e091283019283019283019283019283019283019283019283019283019283019",
    payload: {
      applicant_name: "Priya Sharma",
      cgpa: 8.8,
      annual_income: 450000,
      tuition_fee: 125000,
      documents_attached: 2,
    },
  },
]

export function AuditPage() {
  const [eventTypeFilter, setEventTypeFilter] = useState<string>("all")
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null)

  const filteredLogs = MOCK_AUDIT_LOGS.filter((log) => {
    if (eventTypeFilter !== "all" && log.event_type !== eventTypeFilter) {
      return false
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const matchesId = log.id.toLowerCase().includes(q)
      const matchesApp = log.application_id.toLowerCase().includes(q)
      const matchesActor = log.actor.toLowerCase().includes(q)
      if (!matchesId && !matchesApp && !matchesActor) return false
    }

    return true
  })

  const toggleExpand = (logId: string) => {
    setExpandedLogId(expandedLogId === logId ? null : logId)
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Cryptographic Audit &amp; Reproducibility
            </h1>
            <Badge variant="outline" className="text-xs font-mono border-primary/40 text-primary">
              Immutable SHA-256 Ledger
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Complete cryptographic audit trail of all AST rule evaluations, OCR extractions, and human officer sign-offs.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs font-mono bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-1 font-semibold">
            <ShieldCheckIcon className="size-3.5" />
            Hash Chain Intact
          </Badge>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="rounded-2xl border border-border bg-card p-4 shadow-2xs space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="relative flex-1">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Search by Log ID, Application ID, or Actor..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 text-sm"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium mr-1">
              <FilterIcon className="size-3.5" />
              <span>Event:</span>
            </div>

            {[
              { id: "all", label: "All Events" },
              { id: "decision_recorded", label: "Decisions" },
              { id: "rules_executed", label: "Rule AST" },
              { id: "ocr_verified", label: "OCR Proofs" },
              { id: "application_submitted", label: "Submissions" },
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setEventTypeFilter(f.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  eventTypeFilter === f.id
                    ? "bg-primary text-primary-foreground shadow-2xs font-bold"
                    : "bg-muted/40 text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Audit Log Entries List */}
      <div className="space-y-3">
        {filteredLogs.map((log) => {
          const isExpanded = expandedLogId === log.id

          return (
            <div
              key={log.id}
              className="rounded-2xl border border-border bg-card shadow-2xs overflow-hidden transition-all"
            >
              <div
                onClick={() => toggleExpand(log.id)}
                className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer hover:bg-muted/20 transition-colors select-none"
              >
                <div className="flex items-start md:items-center gap-3">
                  <div className="size-9 rounded-xl bg-primary/10 flex items-center justify-center text-primary shrink-0 mt-0.5 md:mt-0">
                    <FingerprintIcon className="size-4" />
                  </div>

                  <div className="space-y-0.5">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-bold text-sm text-foreground">
                        {log.event_type.replace(/_/g, " ").toUpperCase()}
                      </span>
                      <span className="text-xs font-mono text-muted-foreground">
                        {log.id}
                      </span>
                      <Badge variant="outline" className="text-[10px] font-mono">
                        {log.actor_role}
                      </Badge>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-muted-foreground">
                      <span>Actor: <span className="text-foreground">{log.actor}</span></span>
                      <span>·</span>
                      <span>App: <span className="text-foreground">{log.application_id.slice(0, 8)}...</span></span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end md:self-auto">
                  <div className="text-right font-mono text-xs text-muted-foreground">
                    <div>{new Date(log.timestamp).toLocaleDateString("en-IN")}</div>
                    <div className="text-[11px]">{new Date(log.timestamp).toLocaleTimeString("en-IN")}</div>
                  </div>

                  <VersionChip
                    value={log.state_sha256}
                    type="hash"
                    className="hidden sm:inline-flex"
                  />

                  <button
                    className="p-1 rounded-md text-muted-foreground hover:bg-muted"
                    aria-label="Toggle details"
                  >
                    {isExpanded ? (
                      <ChevronUpIcon className="size-4" />
                    ) : (
                      <ChevronDownIcon className="size-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Expandable JSON Detail View */}
              {isExpanded && (
                <div className="border-t border-border bg-muted/30 p-5 space-y-3 animate-in fade-in-0">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5 font-semibold text-foreground">
                      <TerminalIcon className="size-3.5 text-primary" />
                      <span>Cryptographic Payload State Inspection</span>
                    </div>
                    <span className="font-mono text-[11px]">
                      SHA-256: {log.state_sha256}
                    </span>
                  </div>

                  <pre className="p-4 rounded-xl bg-card border border-border text-xs font-mono text-foreground overflow-x-auto leading-relaxed">
                    {JSON.stringify(log.payload, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
