import { Link } from "react-router-dom"
import {
  ArrowRightIcon,
  CheckCircle2Icon,
  ShieldCheckIcon,
  UserCheckIcon,
  SparklesIcon,
  Building2Icon,
  FileTextIcon,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { MoneyAmount } from "@/components/domain/money-amount"

const TRUST_POINTS = [
  { icon: ShieldCheckIcon, label: "Deterministic AST Rule Engine" },
  { icon: UserCheckIcon, label: "Authorized Officer Human-in-the-Loop" },
  { icon: CheckCircle2Icon, label: "Four-Fifths Bias Guardrails" },
]

export function HeroSection() {
  return (
    <section className="relative overflow-hidden border-b border-border/70">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_60%_at_75%_0%,color-mix(in_oklch,var(--color-primary)_14%,transparent),transparent)]"
      />
      <div className="mx-auto grid w-full max-w-6xl gap-12 px-4 py-16 sm:px-6 md:py-24 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
        <div className="flex flex-col gap-6">
          <Badge
            variant="secondary"
            className="w-fit gap-1.5 rounded-full px-3 py-1 text-xs font-medium"
          >
            <span className="size-1.5 rounded-full bg-primary" aria-hidden />
            Auditable AI for Higher Education Financing
          </Badge>

          <h1 className="text-balance text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl">
            Fair scholarships. Smaller loans.{" "}
            <span className="text-primary">Every decision explained.</span>
          </h1>

          <p className="max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
            FairExplain AI evaluates scholarship eligibility, reduces the education loan a student actually needs, and synthesizes a plain-language explanation for every outcome — while an authorized institutional officer always makes the final call.
          </p>

          {/* Primary Role CTAs */}
          <div className="flex flex-wrap items-center gap-3">
            <Button render={<Link to="/student/apply" />} size="lg" className="gap-2 shadow-xs">
              <FileTextIcon className="size-4" />
              <span>Apply for Aid</span>
              <ArrowRightIcon className="size-4" />
            </Button>

            <Button render={<Link to="/reviewer" />} size="lg" variant="secondary" className="gap-2">
              <UserCheckIcon className="size-4 text-primary" />
              <span>Reviewer Queue</span>
            </Button>

            <Button render={<Link to="/admin" />} size="lg" variant="outline" className="gap-2">
              <Building2Icon className="size-4 text-muted-foreground" />
              <span>Admin Console</span>
            </Button>
          </div>

          <div className="flex items-center gap-3 pt-1">
            <Button render={<Link to="/student/results" />} variant="ghost" size="sm" className="text-xs text-primary gap-1">
              <SparklesIcon className="size-3.5" />
              <span>Inspect Sample Evaluation Dossier &rarr;</span>
            </Button>
          </div>

          <ul className="mt-2 flex flex-wrap gap-x-6 gap-y-3">
            {TRUST_POINTS.map(({ icon: Icon, label }) => (
              <li
                key={label}
                className="flex items-center gap-2 text-xs sm:text-sm text-muted-foreground"
              >
                <Icon className="size-4 text-primary" aria-hidden="true" />
                {label}
              </li>
            ))}
          </ul>
        </div>

        <HeroPreviewCard />
      </div>
    </section>
  )
}

function HeroPreviewCard() {
  return (
    <div className="relative">
      <div
        aria-hidden="true"
        className="absolute -inset-4 -z-10 rounded-3xl bg-primary/5 blur-2xl"
      />
      <div className="rounded-2xl border border-border bg-card p-6 shadow-xl shadow-primary/5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-xs font-mono text-muted-foreground">
              Dossier #0a905a81 · AY 2026-27
            </span>
            <span className="text-base font-bold text-foreground">Priya Sharma</span>
          </div>
          <Badge className="gap-1 bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 font-semibold">
            <CheckCircle2Icon className="size-3.5" aria-hidden />
            Recommended Eligible
          </Badge>
        </div>

        <Separator />

        <div className="flex flex-col gap-1.5">
          <div className="flex items-baseline justify-between">
            <span className="text-xs text-muted-foreground font-medium">
              Academic &amp; Need Eligibility Matrix
            </span>
            <span className="text-sm font-bold font-mono text-foreground">4 / 4 Satisfied</span>
          </div>
          <Progress value={100} />
          <span className="text-[11px] text-muted-foreground">
            CGPA 8.80 (≥7.50) · Income ₹4.50L (&le;₹8.00L) · Zero Backlogs
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-border bg-background p-3 space-y-1">
            <p className="text-xs text-muted-foreground">Scholarship Award</p>
            <div className="text-base font-bold text-emerald-600 dark:text-emerald-400">
              <MoneyAmount amount="65000.00" />
            </div>
            <p className="text-[10px] text-muted-foreground">Tuition Fee Reduction</p>
          </div>

          <div className="rounded-xl border border-border bg-background p-3 space-y-1">
            <p className="text-xs text-muted-foreground">Net Loan Needed</p>
            <div className="text-base font-bold text-foreground">
              <MoneyAmount amount="60000.00" />
            </div>
            <p className="text-[10px] text-muted-foreground line-through">was ₹1,25,000.00</p>
          </div>
        </div>

        <div className="rounded-xl border border-primary/20 bg-primary/[0.04] p-3 space-y-1 text-xs">
          <div className="flex items-center gap-1.5 text-primary font-semibold">
            <SparklesIcon className="size-3.5" />
            <span>AI Plain-English Summary:</span>
          </div>
          <p className="text-muted-foreground leading-relaxed text-[11px]">
            Candidate demonstrates academic distinction and household income within statutory need thresholds, reducing net semester tuition by 52%.
          </p>
        </div>

        <div className="flex items-center gap-2 rounded-xl bg-amber-500/10 border border-amber-500/20 px-3 py-2 text-xs font-medium text-amber-700 dark:text-amber-400">
          <UserCheckIcon className="size-4 shrink-0" />
          <span>Decision-support recommendation pending officer sign-off.</span>
        </div>
      </div>
    </div>
  )
}
