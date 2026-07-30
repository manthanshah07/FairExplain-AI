import { GraduationCapIcon, BuildingIcon, CalendarIcon } from "lucide-react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import type { Applicant } from "@/types/assessment"

function initials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  })
}

export function ApplicantSummary({ applicant }: { applicant: Applicant }) {
  return (
    <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-4">
        <Avatar className="size-14">
          <AvatarFallback className="bg-primary/10 text-base font-semibold text-primary">
            {initials(applicant.name)}
          </AvatarFallback>
        </Avatar>
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight">
            {applicant.name}
          </h1>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <GraduationCapIcon className="size-4" aria-hidden="true" />
              {applicant.programme}
            </span>
            <span className="flex items-center gap-1.5">
              <BuildingIcon className="size-4" aria-hidden="true" />
              {applicant.institution}
            </span>
          </div>
        </div>
      </div>

      <div className="flex flex-col items-start gap-2 sm:items-end">
        <Badge variant="outline" className="font-mono text-xs">
          {applicant.applicationId}
        </Badge>
        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <CalendarIcon className="size-3.5" aria-hidden="true" />
          Submitted {formatDate(applicant.submittedAt)}
        </span>
      </div>
    </div>
  )
}
