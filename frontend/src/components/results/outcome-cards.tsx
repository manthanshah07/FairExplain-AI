import { AwardIcon, LandmarkIcon, TrendingDownIcon } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { OutcomeBadge } from "@/components/results/outcome-badge"
import { formatINR } from "@/lib/utils"
import type { LoanAssessment, ScholarshipAssessment } from "@/types/assessment"

export function OutcomeCards({
  scholarship,
  loan,
}: {
  scholarship: ScholarshipAssessment
  loan: LoanAssessment
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <ScholarshipCard scholarship={scholarship} />
      <LoanCard loan={loan} />
    </div>
  )
}

function ScholarshipCard({
  scholarship,
}: {
  scholarship: ScholarshipAssessment
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <AwardIcon className="size-5" aria-hidden="true" />
            </span>
            <CardTitle className="text-base">Scholarship</CardTitle>
          </div>
          <OutcomeBadge outcome={scholarship.outcome} />
        </div>
        <CardDescription className="mt-2">
          Weighted score across academics and financial need.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-muted-foreground">Score</span>
            <span className="text-3xl font-semibold tabular-nums">
              {scholarship.score.toFixed(1)}
              <span className="text-base text-muted-foreground">/100</span>
            </span>
          </div>
          <Progress value={scholarship.score} />
        </div>

        <Separator />

        <div className="grid grid-cols-2 gap-4">
          <Stat
            label="Tuition covered"
            value={`${scholarship.scholarshipPercent}%`}
          />
          <Stat
            label="Scholarship amount"
            value={formatINR(scholarship.scholarshipAmount)}
          />
        </div>
      </CardContent>
    </Card>
  )
}

function LoanCard({ loan }: { loan: LoanAssessment }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <LandmarkIcon className="size-5" aria-hidden="true" />
            </span>
            <CardTitle className="text-base">Education loan</CardTitle>
          </div>
          <OutcomeBadge outcome={loan.outcome} />
        </div>
        <CardDescription className="mt-2">
          Reduced loan and affordability after the scholarship.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-muted-foreground">
              Loan required
            </span>
            <span className="text-3xl font-semibold tabular-nums">
              {formatINR(loan.reducedLoanAmount)}
            </span>
          </div>
          <span className="flex items-center gap-1.5 text-xs font-medium text-success">
            <TrendingDownIcon className="size-3.5" aria-hidden="true" />
            Reduced from {formatINR(loan.reducedLoanAmount + 240000)} by the
            scholarship
          </span>
        </div>

        <Separator />

        <div className="grid grid-cols-2 gap-4">
          <Stat
            label="Est. monthly EMI"
            value={`${formatINR(loan.estimatedNewEmi)}/mo`}
          />
          <Stat label="Confidence" value={`${loan.confidence}%`} />
        </div>
      </CardContent>
    </Card>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-lg font-semibold tabular-nums">{value}</span>
    </div>
  )
}
