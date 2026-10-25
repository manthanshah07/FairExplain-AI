import { useState } from "react"
import { usePolicies } from "@/hooks/use-queries"
import { VersionChip } from "@/components/domain/version-chip"
import { Badge } from "@/components/ui/badge"
import { formatOperator } from "@/lib/format"
import {
  CheckCircle2Icon,
  FileTextIcon,
  GitCommitIcon,
  HistoryIcon,
  LockIcon,
  ShieldCheckIcon,
} from "lucide-react"

export function PolicyViewerPage() {
  const { data: policies } = usePolicies()
  const [selectedProgramId, setSelectedProgramId] = useState<string>("MERIT_NEED_2026")

  const activePolicy =
    policies?.find((p) => p.program_id === selectedProgramId) || policies?.[0]

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Statutory Policy &amp; Rules Registry
            </h1>
            <Badge variant="outline" className="text-xs font-mono border-primary/40 text-primary">
              Charter Verified
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Version-controlled AST rule specifications governing scholarship allocation and tuition accounting.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {activePolicy && (
            <VersionChip
              label="Policy Hash"
              value={activePolicy.checksum_sha256}
              type="hash"
            />
          )}
        </div>
      </div>

      {/* Program Selector Tabs */}
      <div className="flex items-center gap-2 border-b pb-3">
        <span className="text-xs font-semibold text-muted-foreground mr-1">Select Program:</span>
        {(policies || []).map((policy) => (
          <button
            key={policy.program_id}
            onClick={() => setSelectedProgramId(policy.program_id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              (activePolicy?.program_id || "MERIT_NEED_2026") === policy.program_id
                ? "bg-primary text-primary-foreground shadow-2xs font-bold"
                : "bg-muted/40 text-muted-foreground hover:bg-muted hover:text-foreground"
            }`}
          >
            {policy.title}
          </button>
        ))}
      </div>

      {activePolicy && (
        <div className="space-y-6">
          {/* Policy Overview Metadata Card */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-2xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-bold text-foreground">{activePolicy.title}</h2>
                  <Badge variant="outline" className="text-xs font-mono">
                    {activePolicy.policy_version}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Program ID: <span className="font-mono text-foreground font-semibold">{activePolicy.program_id}</span> · Effective Date: <span className="font-mono text-foreground font-semibold">{activePolicy.effective_date}</span>
                </p>
              </div>

              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs font-mono bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 gap-1 font-semibold">
                  <CheckCircle2Icon className="size-3.5" />
                  Active In Production
                </Badge>
              </div>
            </div>

            <p className="text-xs text-muted-foreground leading-relaxed">
              {activePolicy.description ||
                "Merit-Cum-Means Scholarship Scheme providing targeted fee reductions for undergraduate students with proven academic excellence and demonstrated financial need."}
            </p>

            {/* Statutory Charter Authorizations */}
            <div className="rounded-xl border border-border/80 bg-muted/30 p-4 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-foreground">
                <ShieldCheckIcon className="size-4 text-primary" />
                Statutory Charter Authorizations
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono text-muted-foreground">
                {Object.entries(activePolicy.charter_authorizations || {}).map(([key, val]) => (
                  <div key={key} className="flex justify-between p-2 rounded-lg bg-card border border-border/60">
                    <span className="capitalize font-sans font-medium text-foreground">{key.replace(/_/g, " ")}:</span>
                    <span>{String(val)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Criteria Matrix Table */}
          <div className="rounded-2xl border border-border bg-card shadow-2xs overflow-hidden">
            <div className="p-5 border-b border-border flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-foreground">
                  Eligibility Criteria &amp; AST Logic Specification
                </h3>
                <p className="text-xs text-muted-foreground">
                  Full deterministic condition specifications compiled directly into the rule evaluator
                </p>
              </div>
              <Badge variant="outline" className="text-xs font-mono">
                {activePolicy.criteria.length} Rules Defined
              </Badge>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-muted/40 border-b border-border text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                  <tr>
                    <th className="px-5 py-3">Criterion ID / Attribute</th>
                    <th className="px-5 py-3">Condition Logic</th>
                    <th className="px-5 py-3">Classification</th>
                    <th className="px-5 py-3">Purpose Governance</th>
                    <th className="px-5 py-3">Required Evidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {activePolicy.criteria.map((crit) => {
                    const isSensitive = crit.purpose === "restricted_sensitive"
                    const isMerit = crit.purpose === "merit_ranking"

                    return (
                      <tr key={crit.criterion_id} className="hover:bg-muted/20 transition-colors">
                        <td className="px-5 py-4">
                          <div className="font-semibold text-foreground">
                            {crit.attribute.replace(/_/g, " ")}
                          </div>
                          <div className="text-[11px] font-mono text-muted-foreground">
                            {crit.criterion_id}
                          </div>
                        </td>

                        <td className="px-5 py-4">
                          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-muted/60 font-mono text-xs">
                            <span className="text-muted-foreground">
                              {formatOperator(crit.operator)}
                            </span>
                            <span className="font-bold text-foreground">
                              {Array.isArray(crit.target_value)
                                ? crit.target_value.join(", ")
                                : String(crit.target_value)}
                            </span>
                          </div>
                          {crit.description && (
                            <p className="text-[11px] text-muted-foreground mt-1 max-w-xs">
                              {crit.description}
                            </p>
                          )}
                        </td>

                        <td className="px-5 py-4">
                          {crit.is_mandatory ? (
                            <Badge
                              variant="outline"
                              className="text-[10px] uppercase font-bold text-primary border-primary/40 bg-primary/5"
                            >
                              Mandatory Gate
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-[10px] uppercase text-muted-foreground">
                              Optional Merit
                            </Badge>
                          )}
                        </td>

                        <td className="px-5 py-4">
                          {isSensitive ? (
                            <Badge
                              variant="outline"
                              className="text-[10px] uppercase font-bold text-amber-600 dark:text-amber-400 border-amber-500/40 bg-amber-500/10 gap-1"
                            >
                              <LockIcon className="size-3" />
                              Restricted Sensitive
                            </Badge>
                          ) : isMerit ? (
                            <Badge
                              variant="outline"
                              className="text-[10px] uppercase font-bold text-blue-600 dark:text-blue-400 border-blue-500/40 bg-blue-500/10"
                            >
                              Merit Ranking
                            </Badge>
                          ) : (
                            <Badge
                              variant="outline"
                              className="text-[10px] uppercase font-bold text-emerald-600 dark:text-emerald-400 border-emerald-500/40 bg-emerald-500/10"
                            >
                              Program Eligibility
                            </Badge>
                          )}
                        </td>

                        <td className="px-5 py-4 text-xs font-mono text-muted-foreground">
                          {crit.required_evidence ? (
                            <div className="flex items-center gap-1 text-foreground">
                              <FileTextIcon className="size-3.5 text-primary" />
                              <span className="capitalize">
                                {crit.required_evidence.replace(/_/g, " ")}
                              </span>
                            </div>
                          ) : (
                            <span className="text-muted-foreground/60">—</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Policy Revision History */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-2xs space-y-4">
            <div className="flex items-center gap-2 border-b pb-3">
              <HistoryIcon className="size-4 text-primary" />
              <h3 className="text-sm font-bold text-foreground">Version History &amp; Changelog</h3>
            </div>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="size-7 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0 mt-0.5">
                  <GitCommitIcon className="size-4" />
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-foreground">v2026.1 (Active Release)</span>
                    <span className="text-muted-foreground font-mono">Effective Aug 1, 2026</span>
                  </div>
                  <p className="text-muted-foreground">
                    Updated annual household income ceiling from ₹6,00,000 to ₹8,00,000 in accordance with Ministry of Education Revised Cost-of-Living Guidelines. Added automated OCR proof cross-verification for state income certificates.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 opacity-70">
                <div className="size-7 rounded-full bg-muted flex items-center justify-center text-muted-foreground shrink-0 mt-0.5">
                  <GitCommitIcon className="size-4" />
                </div>
                <div className="space-y-1 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-foreground">v2025.2 (Superseded)</span>
                    <span className="text-muted-foreground font-mono">Effective Jan 1, 2025</span>
                  </div>
                  <p className="text-muted-foreground">
                    Initial launch of deterministic AST rule engine with tuition ledger caps and 5-tier merit ranking.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
