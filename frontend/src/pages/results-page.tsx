import { Link } from "react-router-dom"
import {
  ArrowLeftIcon,
  DownloadIcon,
  SendIcon,
  GitCommitVerticalIcon,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { ApplicantSummary } from "@/components/results/applicant-summary"
import { HumanReviewNotice } from "@/components/results/human-review-notice"
import { OutcomeCards } from "@/components/results/outcome-cards"
import { ScoreBreakdown } from "@/components/results/score-breakdown"
import { LoanAffordability } from "@/components/results/loan-affordability"
import { ExplanationCard } from "@/components/results/explanation-card"
import { FairnessCard } from "@/components/results/fairness-card"
import { mockAssessment } from "@/lib/mock-data"

export function ResultsPage() {
  const result = mockAssessment

  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-8 sm:px-6 md:py-12">
          <div className="flex flex-col gap-4">
            <Button
              asChild
              variant="ghost"
              size="sm"
              className="-ml-2 w-fit text-muted-foreground"
            >
              <Link to="/">
                <ArrowLeftIcon data-icon="inline-start" />
                Back to overview
              </Link>
            </Button>

            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-primary">
                  Assessment result
                </span>
                <p className="text-sm text-muted-foreground">
                  Sample output — Phase 1 preview with mock data.
                </p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline">
                  <DownloadIcon data-icon="inline-start" />
                  Download report
                </Button>
                <Button>
                  <SendIcon data-icon="inline-start" />
                  Send to reviewer
                </Button>
              </div>
            </div>
          </div>

          <Separator />

          <ApplicantSummary applicant={result.applicant} />

          <HumanReviewNotice />

          <OutcomeCards
            scholarship={result.scholarship}
            loan={result.loan}
          />

          <div className="grid gap-4 lg:grid-cols-2">
            <ScoreBreakdown scholarship={result.scholarship} />
            <LoanAffordability loan={result.loan} />
          </div>

          <ExplanationCard explanation={result.explanation} />

          <FairnessCard fairness={result.fairness} />

          <AuditMeta
            version={result.scholarship.ruleEngineVersion}
            computedAt={result.scholarship.computedAt}
          />
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}

function AuditMeta({
  version,
  computedAt,
}: {
  version: string
  computedAt: string
}) {
  const formatted = new Date(computedAt).toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })

  return (
    <div className="flex flex-col gap-2 rounded-lg border border-border bg-card/40 px-4 py-3 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
      <span className="flex items-center gap-1.5">
        <GitCommitVerticalIcon className="size-3.5" aria-hidden="true" />
        Rule engine version{" "}
        <span className="font-mono text-foreground">{version}</span>
      </span>
      <span>Computed {formatted} · Reproducible &amp; auditable</span>
    </div>
  )
}
