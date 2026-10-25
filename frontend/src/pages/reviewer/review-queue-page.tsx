import { useState, useMemo } from "react"
import { Link } from "react-router-dom"
import { useReviewQueue } from "@/hooks/use-queries"
import { StatusBadge } from "@/components/domain/status-badge"
import { VersionChip } from "@/components/domain/version-chip"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  AlertTriangleIcon,
  ArrowRightIcon,
  ClockIcon,
  FilterIcon,
  SearchIcon,
  ShieldAlertIcon,
  UserCheckIcon,
  XIcon,
} from "lucide-react"

export function ReviewQueuePage() {
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [priorityFilter, setPriorityFilter] = useState<string>("all")
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [currentPage, setCurrentPage] = useState<number>(1)
  const pageSize = 10

  const { data: queueData, isLoading } = useReviewQueue(statusFilter, currentPage, pageSize)

  const rawItems = queueData?.items
  const items = useMemo(() => rawItems || [], [rawItems])

  // Filter items locally based on search query & priority
  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      // Status filter
      if (statusFilter !== "all") {
        if (statusFilter === "flagged" && item.flags.length === 0) return false
        if (statusFilter !== "flagged" && item.status !== statusFilter) return false
      }

      // Priority filter
      if (priorityFilter !== "all" && item.priority !== priorityFilter) {
        return false
      }

      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase()
        const matchesName = item.applicant_name.toLowerCase().includes(q)
        const matchesEmail = item.applicant_email.toLowerCase().includes(q)
        const matchesId = item.application_id.toLowerCase().includes(q)
        if (!matchesName && !matchesEmail && !matchesId) return false
      }

      return true
    })
  }, [items, statusFilter, priorityFilter, searchQuery])

  // Aggregate queue metrics
  const totalInQueue = items.length
  const flaggedCount = items.filter((i) => i.flags.length > 0).length
  const highPriorityCount = items.filter((i) => i.priority === "high").length
  const pendingCount = items.filter((i) => i.status === "pending_evidence").length

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Reviewer Oversight Queue
            </h1>
            <Badge variant="outline" className="text-xs font-mono border-primary/40 text-primary">
              NITK Surathkal Aid Directorate
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Inspect-and-decide financial aid determinations. All algorithmic recommendations require human sign-off.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            render={<Link to="/reviewer/history" />}
            variant="outline"
            size="sm"
            className="gap-1.5"
          >
            <ClockIcon className="size-4" />
            Decision History
          </Button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Pending Review</span>
            <UserCheckIcon className="size-4 text-primary" />
          </div>
          <div className="text-2xl font-bold font-mono text-foreground">{totalInQueue}</div>
          <span className="text-[11px] text-muted-foreground">Assigned to aid committee</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Flagged for Audit</span>
            <AlertTriangleIcon className="size-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-600 dark:text-amber-400">
            {flaggedCount}
          </div>
          <span className="text-[11px] text-muted-foreground">Demographic / OCR flags</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">High Priority</span>
            <ShieldAlertIcon className="size-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-rose-600 dark:text-rose-400">
            {highPriorityCount}
          </div>
          <span className="text-[11px] text-muted-foreground">Approaching deadline</span>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5 space-y-1 shadow-2xs">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Pending Evidence</span>
            <ClockIcon className="size-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-blue-600 dark:text-blue-400">
            {pendingCount}
          </div>
          <span className="text-[11px] text-muted-foreground">Awaiting student upload</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="rounded-2xl border border-border bg-card p-4 shadow-2xs space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Search box */}
          <div className="relative flex-1">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search by student name, email, or application ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 text-sm"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <XIcon className="size-4" />
              </button>
            )}
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium mr-1">
              <FilterIcon className="size-3.5" />
              <span>Status:</span>
            </div>

            {["all", "flagged", "submitted", "pending_evidence"].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                  statusFilter === st
                    ? "bg-primary text-primary-foreground shadow-2xs"
                    : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {st.replace(/_/g, " ")}
              </button>
            ))}

            <div className="h-4 w-px bg-border mx-1" />

            <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium mr-1">
              <span>Priority:</span>
            </div>

            {["all", "high", "medium", "low"].map((p) => (
              <button
                key={p}
                onClick={() => setPriorityFilter(p)}
                className={`px-2.5 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                  priorityFilter === p
                    ? "bg-foreground text-background shadow-2xs"
                    : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Queue Table */}
      <div className="rounded-2xl border border-border bg-card shadow-2xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/40 border-b border-border text-xs uppercase tracking-wider text-muted-foreground font-semibold">
              <tr>
                <th className="px-5 py-3.5">Candidate / Dossier ID</th>
                <th className="px-5 py-3.5">Recommendation</th>
                <th className="px-5 py-3.5">Priority</th>
                <th className="px-5 py-3.5">Audit Flags</th>
                <th className="px-5 py-3.5">Submitted</th>
                <th className="px-5 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-muted-foreground animate-pulse">
                    Loading reviewer queue...
                  </td>
                </tr>
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center space-y-2">
                    <p className="text-base font-semibold text-foreground">No cases match the active filter</p>
                    <p className="text-xs text-muted-foreground">
                      Try clearing filters or search query to view all assigned dossiers.
                    </p>
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => {
                  const isHighPriority = item.priority === "high"
                  const hasFlags = item.flags && item.flags.length > 0

                  return (
                    <tr
                      key={item.application_id}
                      className="hover:bg-muted/30 transition-colors group"
                    >
                      {/* Candidate Column */}
                      <td className="px-5 py-4">
                        <div className="space-y-1">
                          <div className="font-semibold text-foreground group-hover:text-primary transition-colors">
                            {item.applicant_name}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {item.applicant_email}
                          </div>
                          <VersionChip
                            value={item.application_id}
                            type="hash"
                            className="text-[10px]"
                          />
                        </div>
                      </td>

                      {/* Status Column */}
                      <td className="px-5 py-4">
                        <StatusBadge status={item.status} size="sm" />
                      </td>

                      {/* Priority Column */}
                      <td className="px-5 py-4">
                        <Badge
                          variant="outline"
                          className={`text-[10px] font-bold uppercase tracking-wider ${
                            isHighPriority
                              ? "border-rose-500/40 text-rose-600 bg-rose-500/10"
                              : item.priority === "medium"
                              ? "border-amber-500/40 text-amber-600 bg-amber-500/10"
                              : "border-border text-muted-foreground"
                          }`}
                        >
                          {item.priority}
                        </Badge>
                      </td>

                      {/* Flags Column */}
                      <td className="px-5 py-4">
                        {hasFlags ? (
                          <div className="flex flex-wrap gap-1.5">
                            {item.flags.map((flag, fIdx) => (
                              <Badge
                                key={fIdx}
                                variant="outline"
                                className="text-[10px] border-amber-500/50 bg-amber-500/10 text-amber-700 dark:text-amber-400 gap-1 font-medium"
                              >
                                <AlertTriangleIcon className="size-3" />
                                {flag.replace(/_/g, " ")}
                              </Badge>
                            ))}
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground font-mono">Clean</span>
                        )}
                      </td>

                      {/* Submitted Column */}
                      <td className="px-5 py-4 text-xs font-mono text-muted-foreground">
                        {item.submission_date
                          ? new Date(item.submission_date).toLocaleDateString("en-IN", {
                              day: "numeric",
                              month: "short",
                              year: "numeric",
                            })
                          : "Today"}
                      </td>

                      {/* Action Column */}
                      <td className="px-5 py-4 text-right">
                        <Button
                          render={<Link to={`/reviewer/case/${item.application_id}`} />}
                          size="sm"
                          className="gap-1 shadow-2xs font-semibold"
                        >
                          <span>Review Case</span>
                          <ArrowRightIcon className="size-3.5" />
                        </Button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="flex items-center justify-between px-5 py-3.5 border-t border-border bg-muted/20 text-xs text-muted-foreground">
          <span>
            Showing <span className="font-semibold text-foreground">{filteredItems.length}</span> of{" "}
            <span className="font-semibold text-foreground">{items.length}</span> candidates
          </span>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => p - 1)}
              className="h-8 text-xs"
            >
              Previous
            </Button>
            <span className="font-mono text-xs font-semibold">Page {currentPage}</span>
            <Button
              variant="outline"
              size="sm"
              disabled={filteredItems.length < pageSize}
              onClick={() => setCurrentPage((p) => p + 1)}
              className="h-8 text-xs"
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
