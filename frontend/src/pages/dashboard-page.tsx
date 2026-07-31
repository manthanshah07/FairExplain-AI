import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { useDashboardStats } from "@/hooks/use-application"
import { Card } from "@/components/ui/card"
import { UsersIcon, CheckCircleIcon, AlertTriangleIcon, FlagIcon } from "lucide-react"

export function DashboardPage() {
  const { data: stats, isLoading } = useDashboardStats()

  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1 px-4 py-8 sm:px-6 md:py-12">
        <div className="mx-auto max-w-6xl space-y-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Admin Dashboard</h1>
            <p className="text-muted-foreground">Overview of application processing and system health.</p>
          </div>

          {isLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
               {[1,2,3,4].map(i => <div key={i} className="h-32 rounded-xl bg-card animate-pulse border border-border" />)}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <StatCard title="Total Applications" value={stats?.totalApplications} icon={UsersIcon} />
              <StatCard title="Approved" value={stats?.approved} icon={CheckCircleIcon} trend="+12% from last month" />
              <StatCard title="Needs Review" value={stats?.needsReview} icon={AlertTriangleIcon} />
              <StatCard title="Fairness Flag Rate" value={`${stats?.fairnessFlagRate}%`} icon={FlagIcon} trend="Below 5% threshold" />
            </div>
          )}
          
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="p-6 h-64 flex items-center justify-center text-muted-foreground">
              [Outcome Distribution Chart Placeholder]
            </Card>
            <Card className="p-6 h-64 flex items-center justify-center text-muted-foreground">
              [Application Volume Trend Placeholder]
            </Card>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}

function StatCard({ title, value, icon: Icon, trend }: any) {
  return (
    <Card className="p-6 flex flex-col gap-2">
      <div className="flex items-center justify-between text-muted-foreground">
        <span className="text-sm font-medium">{title}</span>
        <Icon className="size-4" />
      </div>
      <div className="text-3xl font-bold">{value}</div>
      {trend && <div className="text-xs text-muted-foreground">{trend}</div>}
    </Card>
  )
}
