import { ScaleIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface BrandProps {
  className?: string
  /** Hide the wordmark and show only the logo mark. */
  markOnly?: boolean
}

export function Brand({ className, markOnly = false }: BrandProps) {
  return (
    <span className={cn("flex items-center gap-2.5", className)}>
      <span className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
        <ScaleIcon className="size-5" aria-hidden="true" />
      </span>
      {!markOnly && (
        <span className="flex flex-col leading-none">
          <span className="text-base font-semibold tracking-tight">
            FairExplain <span className="text-primary">AI</span>
          </span>
          <span className="text-[11px] font-medium text-muted-foreground">
            Explainable eligibility
          </span>
        </span>
      )}
    </span>
  )
}
