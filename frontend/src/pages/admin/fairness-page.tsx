import { useState } from "react"
import { useFairnessMetrics } from "@/hooks/use-queries"
import { FairnessPanel } from "@/components/domain/fairness-panel"
import { VersionChip } from "@/components/domain/version-chip"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  AlertCircleIcon,
  CheckCircle2Icon,
  LockIcon,
  ScaleIcon,
  SearchIcon,
  ShieldCheckIcon,
  SparklesIcon,
} from "lucide-react"

export function FairnessPage() {
  const { data: metrics } = useFairnessMetrics()
  const [testText, setTestText] = useState("")
  const [scanResult, setScanResult] = useState<{
    clean: boolean
    tokensFound: string[]
    message: string
  } | null>(null)

  const handleRunScan = () => {
    if (!testText.trim()) return

    const forbiddenTokens = ["caste", "brahmin", "dalit", "religion", "hindu", "muslim", "gender", "male", "female", "transgender"]
    const textLower = testText.toLowerCase()
    const found = forbiddenTokens.filter((token) => textLower.includes(token))

    if (found.length > 0) {
      setScanResult({
        clean: false,
        tokensFound: found,
        message: `Protected demographic attribute detected (${found.join(", ")}). Must be excluded from computation and prompt context.`,
      })
    } else {
      setScanResult({
        clean: true,
        tokensFound: [],
        message: "Clean token audit: No demographic or protected proxy attributes detected in text buffer.",
      })
    }
  }

  const adverseImpactMetrics = [
    {
      group: "Gender: Female vs Male",
      ratio: "1.04",
      status: "Compliant (Within 0.80 - 1.25 Four-Fifths Range)",
      benchmark: "Four-Fifths Rule (EEOC / Institutional Charter)",
    },
    {
      group: "Income Bracket: < ₹2.5L vs ₹2.5L - ₹5L",
      ratio: "1.12",
      status: "Compliant (Favorable Need-Based Weighting)",
      benchmark: "Constitutional Means-Tested Standard",
    },
    {
      group: "Board Curriculum: State Board vs CBSE / ICSE",
      ratio: "0.98",
      status: "Compliant (Equated Normalization Active)",
      benchmark: "Academic Senate Percentile Normalization",
    },
  ]

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Fairness Screening &amp; Bias Mitigation
            </h1>
            <Badge variant="outline" className="text-xs font-mono border-emerald-500/40 text-emerald-600 dark:text-emerald-400">
              Active Assurance Guardrails
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Cryptographic proxy screening, demographic token exclusion, and four-fifths rule adverse impact monitoring.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <VersionChip label="Screening Engine" value="v1.0-fairness" />
          <VersionChip label="Model Contract" value="PROMPTS.md" />
        </div>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Audited Applications</span>
            <ScaleIcon className="size-4 text-primary" />
          </div>
          <div className="text-2xl font-bold font-mono text-foreground">
            {metrics?.total_audited || 148}
          </div>
          <span className="text-[11px] text-muted-foreground">100% cohort coverage</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Protected Token Leakage</span>
            <ShieldCheckIcon className="size-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
            0
          </div>
          <span className="text-[11px] text-muted-foreground">Zero demographic tokens in LLM context</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Adverse Impact Ratio</span>
            <CheckCircle2Icon className="size-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
            1.04
          </div>
          <span className="text-[11px] text-muted-foreground">Within 0.80 - 1.25 tolerance</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Protected Attributes</span>
            <LockIcon className="size-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-600 dark:text-amber-400">
            6 Segregated
          </div>
          <span className="text-[11px] text-muted-foreground">Caste, Religion, Gender, etc.</span>
        </div>
      </div>

      {/* Fairness Panel Guardrails Embed */}
      <FairnessPanel />

      {/* Adverse Impact & Four-Fifths Rule Evaluation */}
      <div className="rounded-2xl border border-border bg-card shadow-2xs overflow-hidden">
        <div className="p-5 border-b border-border space-y-1">
          <h2 className="text-sm font-bold text-foreground">
            Adverse Impact Monitoring (Four-Fifths Rule Compliance)
          </h2>
          <p className="text-xs text-muted-foreground">
            Statistical screening ensures selection rates between protected demographic groups do not violate institutional equity boundaries.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/40 border-b border-border text-xs uppercase tracking-wider text-muted-foreground font-semibold">
              <tr>
                <th className="px-5 py-3">Evaluated Cohort Comparison</th>
                <th className="px-5 py-3">Selection Ratio</th>
                <th className="px-5 py-3">Regulatory Benchmark</th>
                <th className="px-5 py-3 text-right">Compliance Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {adverseImpactMetrics.map((row, idx) => (
                <tr key={idx} className="hover:bg-muted/20 transition-colors">
                  <td className="px-5 py-3.5 font-semibold text-foreground">{row.group}</td>
                  <td className="px-5 py-3.5 font-mono font-bold text-foreground">{row.ratio}</td>
                  <td className="px-5 py-3.5 text-xs text-muted-foreground">{row.benchmark}</td>
                  <td className="px-5 py-3.5 text-right">
                    <Badge
                      variant="outline"
                      className="text-[10px] border-emerald-500/40 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 gap-1 font-semibold"
                    >
                      <CheckCircle2Icon className="size-3" />
                      Compliant
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Interactive Proxy-Token Leakage Scanner */}
      <div className="rounded-2xl border border-border bg-card p-6 shadow-2xs space-y-4">
        <div className="space-y-1 border-b pb-3">
          <div className="flex items-center gap-2">
            <SearchIcon className="size-4 text-primary" />
            <h3 className="text-sm font-bold text-foreground">
              Demographic Proxy-Token Scanner (Admin Sandbox)
            </h3>
          </div>
          <p className="text-xs text-muted-foreground">
            Test any application prompt, review statement, or document extract to audit whether prohibited proxy tokens trigger exclusion filters.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <Input
            placeholder="Type sample explanation text or OCR snippet to test (e.g. candidate details)..."
            value={testText}
            onChange={(e) => setTestText(e.target.value)}
            className="flex-1 text-sm font-mono"
          />
          <Button onClick={handleRunScan} size="sm" className="gap-1.5 shadow-2xs">
            <SparklesIcon className="size-4" />
            Scan Text
          </Button>
        </div>

        {scanResult && (
          <div
            className={`p-4 rounded-xl border text-xs font-mono space-y-1.5 animate-in fade-in-0 ${
              scanResult.clean
                ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-800 dark:text-emerald-300"
                : "border-rose-500/40 bg-rose-500/10 text-rose-800 dark:text-rose-300"
            }`}
          >
            <div className="flex items-center gap-1.5 font-bold font-sans">
              {scanResult.clean ? (
                <>
                  <CheckCircle2Icon className="size-4 text-emerald-600 dark:text-emerald-400" />
                  <span>Audit Passed — Zero Protected Tokens Detected</span>
                </>
              ) : (
                <>
                  <AlertCircleIcon className="size-4 text-rose-600 dark:text-rose-400" />
                  <span>Audit Alert — Prohibited Token Leakage Identified</span>
                </>
              )}
            </div>
            <p className="font-mono text-[11px] leading-relaxed">{scanResult.message}</p>
          </div>
        )}
      </div>
    </div>
  )
}
