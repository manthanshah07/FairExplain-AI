import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { useDashboardStats } from "@/hooks/use-application"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { UsersIcon, CheckCircleIcon, AlertTriangleIcon, FlagIcon } from "lucide-react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from "@/components/ui/chart"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Pie, PieChart, Cell } from "recharts"
import { Badge } from "@/components/ui/badge"

const volumeData = [
  { name: "Mon", applications: 120 },
  { name: "Tue", applications: 145 },
  { name: "Wed", applications: 110 },
  { name: "Thu", applications: 180 },
  { name: "Fri", applications: 220 },
  { name: "Sat", applications: 90 },
  { name: "Sun", applications: 75 },
]

const outcomeData = [
  { name: "Approved", value: 890, color: "hsl(var(--primary))" },
  { name: "Needs Review", value: 210, color: "hsl(var(--warning, 38 92% 50%))" },
  { name: "Rejected", value: 145, color: "hsl(var(--destructive))" },
]

const RECENT_APPLICATIONS = [
  { id: "APP-2026-004182", name: "Priya Sharma", date: "2026-07-24", score: 85.6, status: "Approved" },
  { id: "APP-2026-004183", name: "Rahul Verma", date: "2026-07-24", score: 72.1, status: "Needs Review" },
  { id: "APP-2026-004184", name: "Anjali Gupta", date: "2026-07-23", score: 91.2, status: "Approved" },
  { id: "APP-2026-004185", name: "Vikram Singh", date: "2026-07-23", score: 45.0, status: "Rejected" },
  { id: "APP-2026-004186", name: "Sneha Patel", date: "2026-07-22", score: 88.4, status: "Approved" },
]

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
            <Card>
              <CardHeader>
                <CardTitle>Outcome Distribution</CardTitle>
                <CardDescription>Breakdown of AI recommendations</CardDescription>
              </CardHeader>
              <CardContent className="h-72">
                <ChartContainer config={{}}>
                  <PieChart>
                    <Pie
                      data={outcomeData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label
                    >
                      {outcomeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <ChartLegend content={<ChartLegendContent />} />
                  </PieChart>
                </ChartContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Application Volume Trend</CardTitle>
                <CardDescription>Applications received over the last 7 days</CardDescription>
              </CardHeader>
              <CardContent className="h-72">
                <ChartContainer config={{ applications: { label: "Applications", color: "hsl(var(--primary))" } }}>
                  <BarChart data={volumeData} margin={{ top: 20, right: 0, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" tickLine={false} axisLine={false} />
                    <YAxis tickLine={false} axisLine={false} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="applications" fill="var(--color-applications)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Applications</CardTitle>
              <CardDescription>Latest submissions and their current statuses.</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Applicant</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead className="text-right">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {RECENT_APPLICATIONS.map((app) => (
                    <TableRow key={app.id}>
                      <TableCell className="font-medium">
                        <div className="flex flex-col">
                          <span>{app.name}</span>
                          <span className="text-xs text-muted-foreground">{app.id}</span>
                        </div>
                      </TableCell>
                      <TableCell>{app.date}</TableCell>
                      <TableCell>{app.score}</TableCell>
                      <TableCell className="text-right">
                        <Badge 
                          variant={
                            app.status === "Approved" ? "default" :
                            app.status === "Needs Review" ? "secondary" : "destructive"
                          }
                        >
                          {app.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

        </div>
      </main>
      <SiteFooter />
    </div>
  )
}

function StatCard({ title, value, icon: Icon, trend }: any) {
  return (
    <Card className="flex flex-col justify-between">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className="size-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{value}</div>
        {trend && <div className="text-xs text-muted-foreground mt-1">{trend}</div>}
      </CardContent>
    </Card>
  )
}
