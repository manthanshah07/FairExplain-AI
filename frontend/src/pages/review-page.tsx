import { Link } from "react-router-dom"
import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { useReviewQueue } from "@/hooks/use-application"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export function ReviewPage() {
  const { data: queue, isLoading } = useReviewQueue()

  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1 px-4 py-8 sm:px-6 md:py-12">
        <div className="mx-auto max-w-5xl space-y-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Review Queue</h1>
            <p className="text-muted-foreground">Applications requiring human reviewer sign-off.</p>
          </div>

          <div className="rounded-xl border bg-card/40 shadow-sm overflow-hidden">
            <div className="grid grid-cols-5 border-b p-4 text-sm font-medium text-muted-foreground">
              <div className="col-span-2">Applicant</div>
              <div>Date</div>
              <div>Score</div>
              <div className="text-right">Action</div>
            </div>
            
            {isLoading ? (
               <div className="p-8 text-center text-muted-foreground">Loading queue...</div>
            ) : queue?.length === 0 ? (
               <div className="p-8 text-center text-muted-foreground">No applications need review.</div>
            ) : (
               queue?.map((app) => (
                 <div key={app.id} className="grid grid-cols-5 items-center border-b p-4 last:border-0 hover:bg-muted/20">
                   <div className="col-span-2 flex flex-col gap-1">
                     <span className="font-medium">{app.name}</span>
                     <span className="text-xs text-muted-foreground">{app.id}</span>
                   </div>
                   <div className="text-sm">{app.date}</div>
                   <div className="flex items-center gap-2">
                     <span className="font-medium">{app.score}</span>
                     <Badge variant="secondary" className="text-[10px]">Needs Review</Badge>
                   </div>
                   <div className="text-right">
                     <Button size="sm" render={<Link to={`/results/${app.id}`} />}>
                       Review
                     </Button>
                   </div>
                 </div>
               ))
            )}
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}
