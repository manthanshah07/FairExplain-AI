import {
  CalculatorIcon,
  SparklesIcon,
  UserCheckIcon,
  ScaleIcon,
  ShieldCheckIcon,
  LockIcon,
  FileCheck2Icon,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function PrinciplesSection() {
  return (
    <section
      id="principles"
      className="scroll-mt-20 border-y border-border/70 bg-card/40 py-16 sm:py-24"
    >
      <div className="mx-auto w-full max-w-6xl px-4 sm:px-6 space-y-16">
        {/* Section Heading */}
        <div className="flex flex-col gap-3 max-w-2xl">
          <Badge variant="secondary" className="w-fit rounded-full px-3 py-1 text-xs">
            Architectural Guarantees
          </Badge>
          <h2 className="text-balance text-3xl font-bold tracking-tight sm:text-4xl text-foreground">
            The Three-Layer Trust Architecture
          </h2>
          <p className="text-pretty text-muted-foreground text-sm sm:text-base leading-relaxed">
            FairExplain AI enforces absolute boundary separation between deterministic arithmetic, generative explanations, and human authority.
          </p>
        </div>

        {/* 3-Layer Visual Architecture Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Layer 1: Deterministic Facts */}
          <div className="rounded-2xl border-2 border-foreground/15 bg-card p-6 space-y-4 shadow-sm flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="size-8 rounded-lg bg-foreground text-background font-mono font-bold text-sm flex items-center justify-center">
                  L1
                </span>
                <Badge variant="outline" className="text-[10px] font-mono uppercase font-bold">
                  Zero AI Math
                </Badge>
              </div>

              <div>
                <h3 className="text-lg font-bold text-foreground">Deterministic Facts</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Pure Python Rule Engine &amp; Accounting Ledger
                </p>
              </div>

              <p className="text-xs text-muted-foreground leading-relaxed">
                Eligibility status, criterion evaluation, and tuition reduction waterfalls are computed solely by deterministic code without generative approximations or floating-point rounding.
              </p>
            </div>

            <div className="pt-4 border-t border-border/60 text-[11px] font-mono text-muted-foreground flex items-center gap-1.5">
              <CalculatorIcon className="size-3.5 text-foreground" />
              <span>Exact Decimal Arithmetic (0.01 INR)</span>
            </div>
          </div>

          {/* Layer 2: Grounded Explanations */}
          <div className="rounded-2xl border-2 border-primary/30 bg-primary/[0.03] p-6 space-y-4 shadow-sm flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="size-8 rounded-lg bg-primary text-primary-foreground font-mono font-bold text-sm flex items-center justify-center">
                  L2
                </span>
                <Badge variant="outline" className="text-[10px] font-mono uppercase font-bold text-primary border-primary/40">
                  Natural Language
                </Badge>
              </div>

              <div>
                <h3 className="text-lg font-bold text-foreground">Grounded AI Explanation</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  JSON-Enforced Explanation Synthesizer
                </p>
              </div>

              <p className="text-xs text-muted-foreground leading-relaxed">
                The language model only explains what Layer 1 evaluated. It has zero power to alter numbers, reject students, or invent reasons. Factually unfaithful generations are discarded.
              </p>
            </div>

            <div className="pt-4 border-t border-border/60 text-[11px] font-mono text-primary flex items-center gap-1.5 font-medium">
              <SparklesIcon className="size-3.5 text-primary" />
              <span>Strictly Advisory &amp; Explainable</span>
            </div>
          </div>

          {/* Layer 3: Human Officer Governance */}
          <div className="rounded-2xl border-2 border-amber-500/30 bg-amber-500/[0.03] p-6 space-y-4 shadow-sm flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="size-8 rounded-lg bg-amber-500 text-white font-mono font-bold text-sm flex items-center justify-center">
                  L3
                </span>
                <Badge variant="outline" className="text-[10px] font-mono uppercase font-bold text-amber-600 dark:text-amber-400 border-amber-500/40">
                  Legal Authority
                </Badge>
              </div>

              <div>
                <h3 className="text-lg font-bold text-foreground">Human Officer Governance</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Inspect-and-Decide Institutional Oversight
                </p>
              </div>

              <p className="text-xs text-muted-foreground leading-relaxed">
                No scholarship is awarded or denied automatically. An authorized financial aid officer reviews the complete dossier, can override with written statutory justification, and signs off.
              </p>
            </div>

            <div className="pt-4 border-t border-border/60 text-[11px] font-mono text-amber-600 dark:text-amber-400 flex items-center gap-1.5 font-medium">
              <UserCheckIcon className="size-3.5 text-amber-600" />
              <span>Final Accountable Determination</span>
            </div>
          </div>
        </div>

        {/* Responsible AI Transparency Panel */}
        <div className="rounded-2xl border border-border bg-card p-8 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/70 pb-4">
            <div className="flex items-center gap-3">
              <div className="size-10 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                <ScaleIcon className="size-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground">
                  Responsible AI &amp; Non-Discrimination Charter
                </h3>
                <p className="text-xs text-muted-foreground">
                  Algorithmic auditing adhering to international equality and institutional equity standards
                </p>
              </div>
            </div>

            <Badge variant="outline" className="text-xs font-mono text-emerald-600 dark:text-emerald-400 border-emerald-500/40 bg-emerald-500/10">
              Four-Fifths Compliant
            </Badge>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl border border-border/70 bg-muted/20 space-y-1.5">
              <div className="flex items-center gap-2 text-foreground font-semibold text-xs">
                <LockIcon className="size-3.5 text-primary" />
                <span>Protected Token Exclusion</span>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Gender, caste, and religious beliefs are completely absent from model prompts and scoring algorithms.
              </p>
            </div>

            <div className="p-4 rounded-xl border border-border/70 bg-muted/20 space-y-1.5">
              <div className="flex items-center gap-2 text-foreground font-semibold text-xs">
                <ScaleIcon className="size-3.5 text-primary" />
                <span>Four-Fifths Rule Parity</span>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Adverse impact ratios are monitored across demographic cohorts to maintain selection rates between 0.80 and 1.25.
              </p>
            </div>

            <div className="p-4 rounded-xl border border-border/70 bg-muted/20 space-y-1.5">
              <div className="flex items-center gap-2 text-foreground font-semibold text-xs">
                <ShieldCheckIcon className="size-3.5 text-primary" />
                <span>Zero Black-Box Math</span>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                No hidden neural weights calculate eligibility or awards. All calculations are 100% reproducible AST code.
              </p>
            </div>

            <div className="p-4 rounded-xl border border-border/70 bg-muted/20 space-y-1.5">
              <div className="flex items-center gap-2 text-foreground font-semibold text-xs">
                <FileCheck2Icon className="size-3.5 text-primary" />
                <span>Cryptographic Audit Seals</span>
              </div>
              <p className="text-[11px] text-muted-foreground leading-relaxed">
                Every decision, policy version, and OCR extraction is sealed with immutable SHA-256 state fingerprints.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
