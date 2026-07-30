import {
  CircleCheckIcon,
  CircleAlertIcon,
  CircleXIcon,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { Outcome } from "@/types/assessment"

const OUTCOME_STYLES: Record<
  Outcome,
  { className: string; icon: typeof CircleCheckIcon }
> = {
  Eligible: {
    className: "bg-success text-success-foreground",
    icon: CircleCheckIcon,
  },
  "Needs Review": {
    className: "bg-warning text-warning-foreground",
    icon: CircleAlertIcon,
  },
  "Not Recommended": {
    className: "bg-destructive text-destructive-foreground",
    icon: CircleXIcon,
  },
}

export function OutcomeBadge({
  outcome,
  className,
}: {
  outcome: Outcome
  className?: string
}) {
  const { className: styles, icon: Icon } = OUTCOME_STYLES[outcome]
  return (
    <Badge className={cn("gap-1", styles, className)}>
      <Icon className="size-3.5" aria-hidden="true" />
      {outcome}
    </Badge>
  )
}
