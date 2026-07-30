import { ShieldCheckIcon, ScanSearchIcon } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { FairnessCheck } from "@/types/assessment"

export function FairnessCard({ fairness }: { fairness: FairnessCheck }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="flex size-9 items-center justify-center rounded-lg bg-success-muted text-success">
              <ShieldCheckIcon className="size-5" aria-hidden="true" />
            </span>
            <CardTitle className="text-base">Fairness check</CardTitle>
          </div>
          <Badge className="gap-1 bg-success text-success-foreground">
            {fairness.passed ? "Passed" : "Flagged"}
          </Badge>
        </div>
        <CardDescription className="mt-2">
          Screens for protected attributes and indirect proxies that could
          reintroduce bias.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        <p className="text-sm leading-relaxed text-muted-foreground">
          {fairness.note}
        </p>

        <div className="flex flex-col gap-3">
          <span className="flex items-center gap-1.5 text-sm font-medium">
            <ScanSearchIcon
              className="size-4 text-muted-foreground"
              aria-hidden="true"
            />
            Proxies screened
          </span>
          <ul className="flex flex-wrap gap-2">
            {fairness.screenedProxies.map((proxy) => (
              <li key={proxy}>
                <Badge variant="secondary" className="font-normal">
                  {proxy}
                </Badge>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}
