import { Link, useLocation } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Brand } from "@/components/brand"
import { ThemeToggle } from "@/components/theme-toggle"
import { cn } from "@/lib/utils"

const NAV_LINKS = [
  { label: "How it works", href: "/#how-it-works", type: "hash" as const },
  { label: "Dashboard", href: "/dashboard", type: "route" as const },
  { label: "Sample result", href: "/results", type: "route" as const },
]

export function SiteHeader() {
  const { pathname } = useLocation()

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/70 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <Link to="/" aria-label="FairExplain AI home">
          <Brand />
        </Link>

        <nav aria-label="Primary" className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => {
            const active =
              link.type === "route" && pathname.startsWith(link.href)
            return (
              <Button
                key={link.href}
                asChild
                variant="ghost"
                size="sm"
                className={cn(active && "text-primary")}
              >
                {link.type === "route" ? (
                  <Link to={link.href}>{link.label}</Link>
                ) : (
                  <a href={link.href}>{link.label}</a>
                )}
              </Button>
            )
          })}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button asChild variant="ghost" size="sm" className="hidden sm:inline-flex">
            <Link to="/register">Sign up</Link>
          </Button>
          <Button asChild size="sm">
            <Link to="/apply">New application</Link>
          </Button>
        </div>
      </div>
    </header>
  )
}
