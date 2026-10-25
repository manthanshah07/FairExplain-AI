import { Link, useLocation } from "react-router-dom"
import { AppHeader } from "@/components/layout/app-header"
import { SiteFooter } from "@/components/layout/site-footer"
import {
  FileTextIcon,
  FolderCheckIcon,
  LayoutDashboardIcon,
  SparklesIcon,
} from "lucide-react"

const NAV_ITEMS = [
  { label: "Dashboard", href: "/student", icon: LayoutDashboardIcon },
  { label: "Application Form", href: "/student/apply", icon: FileTextIcon },
  { label: "Documents & OCR", href: "/student/documents", icon: FolderCheckIcon },
  { label: "Results & Decision", href: "/student/results", icon: SparklesIcon },
]

export function StudentShell({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <AppHeader />

      <div className="mx-auto flex w-full max-w-7xl flex-1 flex-col md:flex-row">
        {/* Desktop Sidebar */}
        <aside className="hidden md:flex w-64 flex-col border-r border-border/70 p-4 shrink-0 bg-card/30">
          <div className="mb-4 px-3 py-2">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Student Portal
            </h2>
            <p className="text-xs text-muted-foreground/80 mt-0.5">
              Financing &amp; Aid Management
            </p>
          </div>

          <nav className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon
              const isActive =
                item.href === "/student"
                  ? pathname === "/student" || pathname === "/dashboard"
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

          <div className="mt-auto border-t pt-4 px-2 space-y-2">
            <div className="rounded-lg bg-primary/5 border border-primary/15 p-3 text-xs">
              <span className="font-semibold text-primary block mb-1">Human-in-the-Loop</span>
              <p className="text-muted-foreground leading-relaxed">
                All scholarship &amp; loan figures are decision-support recommendations. An authorized officer confirms final awards.
              </p>
            </div>
          </div>
        </aside>

        {/* Main Content Viewport */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 pb-20 md:pb-8 max-w-full overflow-x-hidden">
          {children}
        </main>
      </div>

      {/* Mobile Bottom Navigation Bar */}
      <nav
        aria-label="Mobile Navigation"
        className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-background/95 backdrop-blur-md border-t border-border flex justify-around py-2 px-1"
      >
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          const isActive =
            item.href === "/student"
              ? pathname === "/student" || pathname === "/dashboard"
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
              <span>{item.label.split(" ")[0]}</span>
            </Link>
          )
        })}
      </nav>

      <SiteFooter />
    </div>
  )
}
