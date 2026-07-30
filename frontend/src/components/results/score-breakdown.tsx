import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import type { ScholarshipAssessment } from "@/types/assessment"

export function ScoreBreakdown({
  scholarship,
}: {
  scholarship: ScholarshipAssessment
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">How the score was calculated</CardTitle>
        <CardDescription>
          Deterministic weighting from the rule engine. The same inputs always
          produce this score.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        <ul className="flex flex-col gap-5">
          {scholarship.factors.map((factor) => (
            <li key={factor.label} className="flex flex-col gap-2">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{factor.label}</span>
                  <Badge variant="secondary" className="tabular-nums">
                    {Math.round(factor.weight * 100)}%
                  </Badge>
                </div>
                <span className="text-sm text-muted-foreground tabular-nums">
                  {factor.rawValue}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <Progress
                  value={factor.normalized}
                  className="h-2 flex-1"
                  aria-label={`${factor.label} normalized score`}
                />
                <span className="w-24 shrink-0 text-right text-xs text-muted-foreground tabular-nums">
                  +{factor.weightedPoints.toFixed(1)} pts
                </span>
              </div>
            </li>
          ))}
        </ul>

        <Separator />

        <div className="flex items-center justify-between rounded-lg bg-muted/50 px-4 py-3">
          <span className="text-sm font-medium">Total scholarship score</span>
          <span className="text-xl font-semibold tabular-nums">
            {scholarship.score.toFixed(1)}
            <span className="text-sm text-muted-foreground">/100</span>
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
