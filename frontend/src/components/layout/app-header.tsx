import { Link } from "react-router-dom"
import { Brand } from "@/components/brand"
import { ThemeToggle } from "@/components/theme-toggle"
import { RoleSwitcher } from "@/components/layout/role-switcher"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/lib/auth"
import { ExternalLinkIcon } from "lucide-react"

export function AppHeader() {
  const { role } = useAuth()

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/80 bg-background/95 backdrop-blur-md supports-[backdrop-filter]:bg-background/80">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
        <div className="flex items-center gap-6">
          <Link to="/" aria-label="FairExplain AI home">
            <Brand />
          </Link>

          {/* Quick Context Indicator */}
          <span className="hidden md:inline-flex items-center gap-1.5 text-xs text-muted-foreground border-l pl-4 font-medium">
            <span className="size-2 rounded-full bg-primary" />
            <span className="capitalize">{role}</span> Workspace
          </span>
        </div>

        <div className="flex items-center gap-3">
          <RoleSwitcher />
          <ThemeToggle />
          <Button
            render={<Link to="/" />}
            variant="ghost"
            size="sm"
            className="hidden xl:inline-flex text-xs text-muted-foreground"
          >
            Public Site
            <ExternalLinkIcon className="size-3" />
          </Button>
        </div>
      </div>
    </header>
  )
}
