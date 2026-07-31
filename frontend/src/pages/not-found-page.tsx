import { Link } from "react-router-dom"
import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { Button } from "@/components/ui/button"

export function NotFoundPage() {
  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1 flex flex-col items-center justify-center p-4 text-center">
        <h1 className="text-8xl font-bold text-primary mb-4">404</h1>
        <h2 className="text-2xl font-semibold tracking-tight mb-2">Page Not Found</h2>
        <p className="text-muted-foreground mb-8 max-w-md">
          The page you are looking for doesn't exist, has been moved, or is temporarily unavailable.
        </p>
        <div className="flex gap-4">
          <Button render={<Link to="/" />}>
            Return Home
          </Button>
          <Button variant="outline" render={<Link to="/dashboard" />}>
            Go to Dashboard
          </Button>
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}
