import { Link } from "react-router-dom"
import { PlusIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { KpiCard } from "@/components/dashboard/kpi-card"
import { ApplicationsChart } from "@/components/dashboard/applications-chart"
import { OutcomeDonut } from "@/components/dashboard/outcome-donut"
import { ApplicationsTable } from "@/components/dashboard/applications-table"
import { dashboardKpis } from "@/lib/dashboard-data"

export function DashboardPage() {
  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-8 sm:px-6 md:py-12">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex flex-col gap-1.5">
              <span className="text-sm font-medium text-primary">
                Reviewer dashboard
              </span>
              <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
                Applications overview
              </h1>
              <p className="text-sm text-muted-foreground">
                Monitor assessment volume, outcomes, and the human-review queue.
              </p>
            </div>
            <Button asChild>
              <Link to="/apply">
                <PlusIcon data-icon="inline-start" />
                New application
              </Link>
            </Button>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {dashboardKpis.map((kpi) => (
              <KpiCard key={kpi.label} kpi={kpi} />
            ))}
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            <ApplicationsChart />
            <OutcomeDonut />
          </div>

          <ApplicationsTable />
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}
