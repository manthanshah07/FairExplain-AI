import { Link } from "react-router-dom"
import { ArrowLeftIcon, CompassIcon, LayoutDashboardIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"

export function NotFoundPage() {
  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex flex-1 items-center justify-center px-4 py-16">
        <div className="flex max-w-md flex-col items-center gap-6 text-center">
          <span className="flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <CompassIcon className="size-7" aria-hidden="true" />
          </span>
          <div className="flex flex-col gap-2">
            <span className="text-sm font-medium text-primary">
              Error 404
            </span>
            <h1 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
              We couldn&apos;t find that page
            </h1>
            <p className="text-pretty leading-relaxed text-muted-foreground">
              The page you&apos;re looking for may have moved or never existed.
              Let&apos;s get you back to a familiar place.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button asChild size="lg">
              <Link to="/dashboard">
                <LayoutDashboardIcon data-icon="inline-start" />
                Go to dashboard
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link to="/">
                <ArrowLeftIcon data-icon="inline-start" />
                Back to home
              </Link>
            </Button>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}
