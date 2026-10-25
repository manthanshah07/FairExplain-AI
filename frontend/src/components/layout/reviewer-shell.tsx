import { Link, useLocation } from "react-router-dom"
import { AppHeader } from "@/components/layout/app-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { Badge } from "@/components/ui/badge"
import {
  FileCheckIcon,
  HistoryIcon,
  ShieldAlertIcon,
} from "lucide-react"

const REVIEWER_NAV = [
  { label: "Review Queue", href: "/reviewer", icon: FileCheckIcon },
  { label: "Recent Determinations", href: "/reviewer/history", icon: HistoryIcon },
]

export function ReviewerShell({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <AppHeader />

      <div className="mx-auto flex w-full max-w-7xl flex-1 flex-col md:flex-row">
        {/* Reviewer Sidebar */}
        <aside className="hidden md:flex w-64 flex-col border-r border-border/70 p-4 shrink-0 bg-card/30">
          <div className="mb-4 px-3 py-2 space-y-1">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Reviewer Portal
              </h2>
              <Badge variant="outline" className="text-[10px] uppercase font-mono px-1.5 py-0 border-primary/40 text-primary">
                Officer
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground/80">
              Inspect-and-Decide Oversight
            </p>
          </div>

          <nav className="space-y-1">
            {REVIEWER_NAV.map((item) => {
              const Icon = item.icon
              const isActive =
                item.href === "/reviewer"
                  ? pathname === "/reviewer" || pathname === "/review"
                  : pathname.startsWith(item.href)

              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-primary text-primary-foreground shadow-xs font-semibold"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <Icon className="size-4 shrink-0" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          <div className="mt-auto border-t pt-4 px-2 space-y-3">
            <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-3 text-xs text-amber-800 dark:text-amber-300">
              <span className="font-semibold flex items-center gap-1 mb-1">
                <ShieldAlertIcon className="size-3.5" />
                Accountability Rule
              </span>
              <p className="leading-relaxed opacity-90">
                Overrides strictly require documented written justification. All determinations are written to an immutable audit trail.
              </p>
            </div>
          </div>
        </aside>

        {/* Reviewer Viewport */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 pb-20 md:pb-8 max-w-full overflow-x-hidden">
          {children}
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <nav
        aria-label="Mobile Navigation"
        className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-background/95 backdrop-blur-md border-t border-border flex justify-around py-2 px-1"
      >
        {REVIEWER_NAV.map((item) => {
          const Icon = item.icon
          const isActive =
            item.href === "/reviewer"
              ? pathname === "/reviewer" || pathname === "/review"
              : pathname.startsWith(item.href)

          return (
            <Link
              key={item.href}
              to={item.href}
              className={`flex flex-col items-center gap-1 py-1 px-3 text-[10px] font-medium transition-colors ${
                isActive ? "text-primary font-bold" : "text-muted-foreground"
              }`}
            >
              <Icon className="size-4" />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <SiteFooter />
    </div>
  )
}
