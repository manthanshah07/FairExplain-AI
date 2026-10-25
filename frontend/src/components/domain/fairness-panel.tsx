import { ShieldCheckIcon, CheckIcon, BanIcon } from "lucide-react"

interface FairnessPanelProps {
  attestationText?: string
  screenedProxies?: string[]
}

const DEFAULT_PROXIES = [
  "Caste category / quota inferences",
  "Religion or belief affiliations",
  "Gender identity",
  "Pincode / residential neighborhood proxy",
  "Surname-based socioeconomic proxy",
  "Disability status",
]

const PERMITTED_INPUTS = [
  "Cumulative Grade Point Average (CGPA)",
  "Verified 10th & 12th board percentiles",
  "Active uncleared backlog count",
  "Annual verified household income",
  "Institutional fee schedule & caps",
]

export function FairnessPanel({
  attestationText,
  screenedProxies = DEFAULT_PROXIES,
}: FairnessPanelProps) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6 space-y-6">
      <div className="flex items-center justify-between border-b pb-4">
        <div className="flex items-center gap-2">
          <div className="size-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <ShieldCheckIcon className="size-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">
              Fairness &amp; Proxy Screening Guardrails
            </h3>
            <p className="text-xs text-muted-foreground">
              Algorithmic bias protection and proxy-attribute exclusion
            </p>
          </div>
        </div>
      </div>

      <p className="text-xs text-muted-foreground leading-relaxed">
        {attestationText ||
          "FairExplain AI operates strictly on merit and economic need criteria. In accordance with institutional ethics guidelines, protected demographic attributes and geographical proxies are systematically excluded from computation and natural language generation."}
      </p>

      <div className="grid gap-4 sm:grid-cols-2 pt-1 text-xs">
        <div className="space-y-2 rounded-xl bg-muted/40 p-3.5 border">
          <span className="font-semibold text-foreground flex items-center gap-1.5 text-xs">
            <CheckIcon className="size-3.5 text-emerald-600 dark:text-emerald-400" />
            Permitted Objective Inputs
          </span>
          <ul className="space-y-1.5 text-muted-foreground">
            {PERMITTED_INPUTS.map((input, idx) => (
              <li key={idx} className="flex items-center gap-1.5">
                <span className="size-1 rounded-full bg-emerald-500" />
                <span>{input}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-2 rounded-xl bg-muted/40 p-3.5 border">
          <span className="font-semibold text-foreground flex items-center gap-1.5 text-xs">
            <BanIcon className="size-3.5 text-rose-600 dark:text-rose-400" />
            Strictly Prohibited &amp; Screened Tokens
          </span>
          <ul className="space-y-1.5 text-muted-foreground">
            {screenedProxies.map((proxy, idx) => (
              <li key={idx} className="flex items-center gap-1.5">
                <span className="size-1 rounded-full bg-rose-500" />
                <span>{proxy}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
