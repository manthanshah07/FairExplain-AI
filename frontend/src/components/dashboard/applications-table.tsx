import { useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { ArrowRightIcon, SearchIcon } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { OutcomeBadge } from "@/components/results/outcome-badge"
import { formatINR } from "@/lib/mock-data"
import { recentApplications } from "@/lib/dashboard-data"
import type { Outcome } from "@/types/assessment"

const OUTCOME_FILTERS: (Outcome | "All")[] = [
  "All",
  "Eligible",
  "Needs Review",
  "Not Recommended",
]

export function ApplicationsTable() {
  const [query, setQuery] = useState("")
  const [outcome, setOutcome] = useState<Outcome | "All">("All")

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase()
    return recentApplications.filter((app) => {
      const matchesQuery =
        q === "" ||
        app.name.toLowerCase().includes(q) ||
        app.applicationId.toLowerCase().includes(q) ||
        app.institution.toLowerCase().includes(q)
      const matchesOutcome = outcome === "All" || app.outcome === outcome
      return matchesQuery && matchesOutcome
    })
  }, [query, outcome])

  return (
    <Card>
      <CardHeader className="border-b [.border-b]:pb-4">
        <div className="flex flex-col gap-4 @2xl/card-header:flex-row @2xl/card-header:items-end @2xl/card-header:justify-between">
          <div className="flex flex-col gap-1">
            <CardTitle>Recent applications</CardTitle>
            <CardDescription>
              Every application routes to a human reviewer before a decision.
            </CardDescription>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <div className="relative">
              <SearchIcon
                className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
                aria-hidden="true"
              />
              <Input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search name, ID, institution"
                aria-label="Search applications"
                className="pl-9 sm:w-64"
              />
            </div>
            <Select
              value={outcome}
              onChange={(e) => setOutcome(e.target.value as Outcome | "All")}
              aria-label="Filter by outcome"
              className="sm:w-44"
            >
              {OUTCOME_FILTERS.map((o) => (
                <option key={o} value={o}>
                  {o === "All" ? "All outcomes" : o}
                </option>
              ))}
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent className="px-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs font-medium text-muted-foreground">
                <th className="px-4 py-2.5 font-medium">Applicant</th>
                <th className="px-4 py-2.5 font-medium">Score</th>
                <th className="px-4 py-2.5 font-medium">Requested loan</th>
                <th className="px-4 py-2.5 font-medium">Outcome</th>
                <th className="px-4 py-2.5 font-medium">Submitted</th>
                <th className="px-4 py-2.5" />
              </tr>
            </thead>
            <tbody>
              {rows.map((app) => (
                <tr
                  key={app.applicationId}
                  className="border-b border-border/60 transition-colors last:border-0 hover:bg-muted/40"
                >
                  <td className="px-4 py-3">
                    <div className="flex flex-col">
                      <span className="font-medium text-foreground">
                        {app.name}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {app.applicationId} · {app.institution}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 tabular-nums">
                    {app.scholarshipScore.toFixed(1)}
                  </td>
                  <td className="px-4 py-3 tabular-nums">
                    {formatINR(app.requestedLoan)}
                  </td>
                  <td className="px-4 py-3">
                    <OutcomeBadge outcome={app.outcome} />
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-muted-foreground">
                    {new Date(app.submittedAt).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "short",
                    })}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button asChild variant="ghost" size="sm">
                      <Link
                        to={`/results/${app.applicationId}`}
                        aria-label={`View ${app.name}'s assessment`}
                      >
                        View
                        <ArrowRightIcon data-icon="inline-end" />
                      </Link>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {rows.length === 0 && (
            <div className="flex flex-col items-center gap-1 px-4 py-12 text-center">
              <p className="text-sm font-medium">No applications found</p>
              <p className="text-sm text-muted-foreground">
                Try a different search term or clear the outcome filter.
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
