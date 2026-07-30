import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { outcomeDistribution } from "@/lib/dashboard-data"

const total = outcomeDistribution.reduce((sum, o) => sum + o.count, 0)

export function OutcomeDonut() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Outcome distribution</CardTitle>
        <CardDescription>
          Recommendation split across all assessed applications.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="relative h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={outcomeDistribution}
                dataKey="count"
                nameKey="outcome"
                innerRadius={54}
                outerRadius={78}
                paddingAngle={2}
                strokeWidth={0}
              >
                {outcomeDistribution.map((entry) => (
                  <Cell key={entry.outcome} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "var(--popover)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius)",
                  color: "var(--popover-foreground)",
                  fontSize: 12,
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-semibold tabular-nums">
              {total.toLocaleString("en-IN")}
            </span>
            <span className="text-xs text-muted-foreground">total</span>
          </div>
        </div>

        <ul className="flex flex-col gap-2">
          {outcomeDistribution.map((entry) => {
            const pct = Math.round((entry.count / total) * 100)
            return (
              <li
                key={entry.outcome}
                className="flex items-center justify-between text-sm"
              >
                <span className="flex items-center gap-2">
                  <span
                    className="size-2.5 rounded-full"
                    style={{ backgroundColor: entry.fill }}
                    aria-hidden="true"
                  />
                  {entry.outcome}
                </span>
                <span className="tabular-nums text-muted-foreground">
                  {entry.count.toLocaleString("en-IN")}{" "}
                  <span className="text-foreground">({pct}%)</span>
                </span>
              </li>
            )
          })}
        </ul>
      </CardContent>
    </Card>
  )
}
