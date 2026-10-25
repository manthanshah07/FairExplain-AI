import React from "react"
import { Badge } from "@/components/ui/badge"
import {
  AlertCircleIcon,
  CheckCircle2Icon,
  ClockIcon,
  HelpCircleIcon,
  XCircleIcon,
} from "lucide-react"
import type { CriterionOutcome, EligibilityStatus, LoanOutcome } from "@/types/domain"

export type StatusType =
  | EligibilityStatus
  | CriterionOutcome
  | LoanOutcome
  | "needs_review"
  | "ready_for_report"
  | "submitted"
  | "closed"
  | "approved"
  | "rejected"
  | "overridden"
  | "draft"

interface StatusBadgeProps {
  status: StatusType | string | undefined | null
  size?: "sm" | "md" | "lg"
  className?: string
  showIcon?: boolean
}

export function StatusBadge({
  status,
  size = "md",
  className = "",
  showIcon = true,
}: StatusBadgeProps) {
  const norm = String(status || "pending_evidence").toLowerCase().trim()

  let label = "Pending Evidence"
  let variantClass = "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30"
  let Icon: React.ComponentType<{ className?: string }> = ClockIcon

  switch (norm) {
    case "eligible":
    case "satisfied":
    case "approved":
    case "ready_for_report":
      label = norm === "satisfied" ? "Satisfied" : norm === "ready_for_report" ? "Report Ready" : "Recommended Eligible"
      variantClass = "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30"
      Icon = CheckCircle2Icon
      break

    case "ineligible":
    case "failed":
    case "not_recommended":
    case "rejected":
    case "closed":
      label = norm === "failed" ? "Failed" : norm === "not_recommended" ? "Not Recommended" : "Recommended Ineligible"
      variantClass = "bg-rose-500/15 text-rose-700 dark:text-rose-400 border-rose-500/30"
      Icon = XCircleIcon
      break

    case "needs_review":
    case "overridden":
      label = norm === "overridden" ? "Officer Override" : "Needs Review"
      variantClass = "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30"
      Icon = AlertCircleIcon
      break

    case "pending_evidence":
    case "pending":
    case "missing":
    case "unverified":
      label = "Awaiting Evidence"
      variantClass = "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30"
      Icon = ClockIcon
      break

    case "submitted":
      label = "Submitted"
      variantClass = "bg-blue-500/15 text-blue-700 dark:text-blue-400 border-blue-500/30"
      Icon = CheckCircle2Icon
      break

    case "draft":
      label = "Draft"
      variantClass = "bg-muted text-muted-foreground border-border"
      Icon = HelpCircleIcon
      break

    default:
      label = norm.replace(/_/g, " ")
      variantClass = "bg-muted text-muted-foreground border-border"
      Icon = HelpCircleIcon
      break
  }

  const sizeClasses = {
    sm: "text-[10px] px-2 py-0.5 gap-1",
    md: "text-xs px-2.5 py-1 gap-1.5",
    lg: "text-sm px-3.5 py-1.5 gap-2 font-semibold",
  }

  const iconSizes = {
    sm: "size-3",
    md: "size-3.5",
    lg: "size-4",
  }

  return (
    <Badge
      variant="outline"
      className={`inline-flex items-center font-medium rounded-full border shadow-2xs ${variantClass} ${sizeClasses[size]} ${className}`}
    >
      {showIcon && <Icon className={`${iconSizes[size]} shrink-0`} />}
      <span className="capitalize">{label}</span>
    </Badge>
  )
}
