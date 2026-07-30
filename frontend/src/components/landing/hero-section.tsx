import { Link } from "react-router-dom"
import {
  ArrowRightIcon,
  CircleCheckIcon,
  ShieldCheckIcon,
  UserCheckIcon,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"

const TRUST_POINTS = [
  { icon: ShieldCheckIcon, label: "Deterministic rule engine" },
  { icon: UserCheckIcon, label: "Human-in-the-loop review" },
  { icon: CircleCheckIcon, label: "Fairness-checked explanations" },
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
            Explainable AI for education finance
          </Badge>

          <h1 className="text-balance text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl">
            Fair scholarships. Smaller loans.{" "}
            <span className="text-primary">Every decision explained.</span>
          </h1>

          <p className="max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
            FairExplain AI evaluates scholarship eligibility, reduces the
            education loan a student actually needs, and generates a transparent,
            plain-language explanation for every outcome — while a human makes
            the final call.
          </p>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Button asChild size="lg">
              <Link to="/results">
                See a sample assessment
                <ArrowRightIcon data-icon="inline-end" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="#how-it-works">How it works</a>
            </Button>
          </div>

          <ul className="mt-2 flex flex-wrap gap-x-6 gap-y-3">
            {TRUST_POINTS.map(({ icon: Icon, label }) => (
              <li
                key={label}
                className="flex items-center gap-2 text-sm text-muted-foreground"
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
      <div className="rounded-2xl border border-border bg-card p-5 shadow-xl shadow-primary/5">
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-xs font-medium text-muted-foreground">
              Application APP-2026-004182
            </span>
            <span className="text-sm font-semibold">Priya Sharma</span>
          </div>
          <Badge className="gap-1 bg-success text-success-foreground">
            <CircleCheckIcon className="size-3.5" aria-hidden />
            Eligible
          </Badge>
        </div>

        <Separator className="my-4" />

        <div className="flex flex-col gap-1.5">
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-muted-foreground">
              Scholarship score
            </span>
            <span className="text-2xl font-semibold tabular-nums">85.6</span>
          </div>
          <Progress value={85.6} />
          <span className="text-xs text-muted-foreground">
            Top band — 75% of tuition covered
          </span>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3">
          <MiniStat label="Scholarship" value="₹2,40,000" />
          <MiniStat label="Loan needed" value="₹5,60,000" hint="was ₹8,00,000" />
        </div>

        <div className="mt-4 rounded-lg border border-border bg-muted/40 p-3">
          <p className="text-xs leading-relaxed text-muted-foreground">
            <span className="font-medium text-foreground">Why: </span>
            Strong academics and genuine financial need place this applicant in
            the top eligibility band.
          </p>
        </div>

        <div className="mt-4 flex items-center gap-2 rounded-lg bg-primary/10 px-3 py-2">
          <UserCheckIcon className="size-4 text-primary" aria-hidden />
          <span className="text-xs font-medium text-primary">
            Pending human reviewer sign-off
          </span>
        </div>
      </div>
    </div>
  )
}

function MiniStat({
  label,
  value,
  hint,
}: {
  label: string
  value: string
  hint?: string
}) {
  return (
    <div className="rounded-lg border border-border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-base font-semibold tabular-nums">{value}</p>
      {hint && (
        <p className="text-[11px] text-muted-foreground line-through">{hint}</p>
      )}
    </div>
  )
}
