import { SparklesIcon, CheckIcon, GaugeIcon } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import type { ExplanationReport } from "@/types/assessment"

export function ExplanationCard({
  explanation,
}: {
  explanation: ExplanationReport
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <SparklesIcon className="size-5" aria-hidden="true" />
            </span>
            <CardTitle className="text-base">AI explanation</CardTitle>
          </div>
          <Badge variant="outline" className="font-mono text-xs">
            {explanation.llmPromptVersion}
          </Badge>
        </div>
        <CardDescription className="mt-2">
          Generated from the rule-engine output. The model explains — it never
          computes or changes the scores.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        <p className="text-pretty leading-relaxed">
          {explanation.recommendationText}
        </p>

        <div className="flex flex-col gap-3">
          <span className="text-sm font-medium">Key reasons</span>
          <ul className="flex flex-col gap-3">
            {explanation.reasons.map((reason, index) => (
              <li key={index} className="flex gap-3">
                <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-success-muted text-success">
                  <CheckIcon className="size-3.5" aria-hidden="true" />
                </span>
                <span className="text-sm leading-relaxed text-muted-foreground">
                  {reason}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <Separator />

        <div className="flex gap-3 rounded-lg bg-muted/50 px-4 py-3">
          <GaugeIcon
            className="mt-0.5 size-4 shrink-0 text-muted-foreground"
            aria-hidden="true"
          />
          <p className="text-sm leading-relaxed text-muted-foreground">
            {explanation.confidenceNote}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
