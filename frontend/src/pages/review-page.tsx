import { useState } from "react"
import { Link, useParams } from "react-router-dom"
import {
  ArrowLeftIcon,
  CheckIcon,
  ClockIcon,
  MessageSquareTextIcon,
  UserCheckIcon,
  XIcon,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { ApplicantSummary } from "@/components/results/applicant-summary"
import { OutcomeCards } from "@/components/results/outcome-cards"
import { ExplanationCard } from "@/components/results/explanation-card"
import { FairnessCard } from "@/components/results/fairness-card"
import { mockAssessment } from "@/lib/mock-data"
import { cn } from "@/lib/utils"

type Decision = "approve" | "reject" | null

const TIMELINE = [
  { label: "Application submitted", time: "24 Jul, 09:12", done: true },
  { label: "OCR verification passed", time: "24 Jul, 09:12", done: true },
  { label: "Rule engine scored", time: "24 Jul, 09:12", done: true },
  { label: "Explanation generated", time: "24 Jul, 09:12", done: true },
  { label: "Fairness check passed", time: "24 Jul, 09:12", done: true },
  { label: "Awaiting reviewer decision", time: "Pending", done: false },
]

export function ReviewPage() {
  const { applicationId } = useParams()
  const result = mockAssessment
  const [decision, setDecision] = useState<Decision>(null)
  const [notes, setNotes] = useState("")

  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-8 sm:px-6 md:py-12">
          <div className="flex flex-col gap-4">
            <Button
              asChild
              variant="ghost"
              size="sm"
              className="-ml-2 w-fit text-muted-foreground"
            >
              <Link to="/dashboard">
                <ArrowLeftIcon data-icon="inline-start" />
                Back to dashboard
              </Link>
            </Button>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-col gap-1">
                <span className="text-sm font-medium text-primary">
                  Human review
                </span>
                <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
                  Review application
                </h1>
                <p className="text-sm text-muted-foreground">
                  {applicationId ?? result.applicant.applicationId} · The AI
                  recommendation is advisory. Your decision is final.
                </p>
              </div>
              <Badge
                variant="secondary"
                className="w-fit gap-1.5 rounded-full px-3 py-1"
              >
                <ClockIcon className="size-3.5" aria-hidden="true" />
                Awaiting decision
              </Badge>
            </div>
          </div>

          <Separator />

          <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
            <div className="flex flex-col gap-6">
              <ApplicantSummary applicant={result.applicant} />
              <OutcomeCards
                scholarship={result.scholarship}
                loan={result.loan}
              />
              <ExplanationCard explanation={result.explanation} />
              <FairnessCard fairness={result.fairness} />
            </div>

            <aside className="flex flex-col gap-6 lg:sticky lg:top-24 lg:self-start">
              <DecisionPanel
                decision={decision}
                setDecision={setDecision}
                notes={notes}
                setNotes={setNotes}
              />
              <TimelineCard />
            </aside>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}

function DecisionPanel({
  decision,
  setDecision,
  notes,
  setNotes,
}: {
  decision: Decision
  setDecision: (d: Decision) => void
  notes: string
  setNotes: (n: string) => void
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <span className="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <UserCheckIcon className="size-4" aria-hidden="true" />
          </span>
          <CardTitle>Reviewer decision</CardTitle>
        </div>
        <CardDescription className="mt-1">
          Confirm or override the AI recommendation.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => setDecision("approve")}
            aria-pressed={decision === "approve"}
            className={cn(
              "flex flex-col items-center gap-1 rounded-lg border px-3 py-3 text-sm font-medium transition-colors outline-none focus-visible:ring-3 focus-visible:ring-ring/40",
              decision === "approve"
                ? "border-success bg-success-muted text-success"
                : "border-border text-muted-foreground hover:bg-muted"
            )}
          >
            <CheckIcon className="size-4" aria-hidden="true" />
            Approve
          </button>
          <button
            type="button"
            onClick={() => setDecision("reject")}
            aria-pressed={decision === "reject"}
            className={cn(
              "flex flex-col items-center gap-1 rounded-lg border px-3 py-3 text-sm font-medium transition-colors outline-none focus-visible:ring-3 focus-visible:ring-ring/40",
              decision === "reject"
                ? "border-destructive bg-danger-muted text-destructive"
                : "border-border text-muted-foreground hover:bg-muted"
            )}
          >
            <XIcon className="size-4" aria-hidden="true" />
            Reject
          </button>
        </div>

        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="review-notes"
            className="flex items-center gap-1.5 text-sm font-medium"
          >
            <MessageSquareTextIcon className="size-3.5" aria-hidden="true" />
            Decision notes
          </label>
          <Textarea
            id="review-notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Record your reasoning for the audit trail…"
            rows={4}
          />
        </div>

        <Button className="w-full" disabled={!decision}>
          Record decision
        </Button>
        <p className="text-center text-xs text-muted-foreground">
          Decisions are logged with your identity for accountability.
        </p>
      </CardContent>
    </Card>
  )
}

function TimelineCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Assessment timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="flex flex-col">
          {TIMELINE.map((event, index) => (
            <li key={event.label} className="flex gap-3">
              <div className="flex flex-col items-center">
                <span
                  className={cn(
                    "flex size-5 shrink-0 items-center justify-center rounded-full",
                    event.done
                      ? "bg-primary text-primary-foreground"
                      : "border-2 border-dashed border-border bg-background"
                  )}
                >
                  {event.done && (
                    <CheckIcon className="size-3" aria-hidden="true" />
                  )}
                </span>
                {index < TIMELINE.length - 1 && (
                  <span
                    className={cn(
                      "my-1 w-px flex-1",
                      event.done ? "bg-primary/40" : "bg-border"
                    )}
                    aria-hidden="true"
                  />
                )}
              </div>
              <div className={cn("pb-4", index === TIMELINE.length - 1 && "pb-0")}>
                <p
                  className={cn(
                    "text-sm font-medium",
                    !event.done && "text-muted-foreground"
                  )}
                >
                  {event.label}
                </p>
                <p className="text-xs text-muted-foreground">{event.time}</p>
              </div>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  )
}
