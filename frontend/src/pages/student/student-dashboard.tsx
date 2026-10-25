import { Link } from "react-router-dom"
import { useAuth } from "@/lib/auth"
import { useApplication, useDocuments } from "@/hooks/use-queries"
import { Stepper } from "@/components/domain/stepper"
import { StatusBadge } from "@/components/domain/status-badge"
import { RecommendationRibbon } from "@/components/domain/recommendation-ribbon"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  ArrowRightIcon,
  CheckCircle2Icon,
  ClockIcon,
  FileTextIcon,
  FolderCheckIcon,
  SparklesIcon,
} from "lucide-react"

const APPLICATION_STEPS = [
  { id: "registration", title: "Profile", description: "Identity details" },
  { id: "academic", title: "Academic", description: "Grades & records" },
  { id: "financial", title: "Financial", description: "Income & tuition" },
  { id: "documents", title: "Documents", description: "Verified proofs" },
  { id: "results", title: "Results", description: "Evaluation report" },
]

export function StudentDashboard() {
  const { user } = useAuth()
  const activeAppId = "0a905a81-d102-4fc8-9f15-84950b7b3b41"
  const { data: application } = useApplication(activeAppId)
  const { data: documents } = useDocuments(activeAppId)

  const docTypes = [
    { id: "marksheet", label: "Academic Marksheet / Transcript", mandatory: true },
    { id: "income_proof", label: "Income Certificate / ITR Slip", mandatory: true },
    { id: "id_proof", label: "Government ID / Student ID", mandatory: false },
  ]

  const uploadedDocTypes = new Set(documents?.map((d) => d.doc_type) || ["marksheet", "income_proof"])

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Welcome back, {user.name}
            </h1>
            <Badge variant="outline" className="hidden sm:inline-flex text-xs font-mono">
              NITK Surathkal
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Track your higher education scholarship evaluation and loan affordability status.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button render={<Link to="/student/apply" />} size="sm" className="gap-1.5 shadow-xs">
            <FileTextIcon className="size-4" />
            Edit Application
          </Button>
          <Button render={<Link to={`/student/results?app=${activeAppId}`} />} variant="outline" size="sm" className="gap-1.5">
            <SparklesIcon className="size-4 text-primary" />
            View Results
          </Button>
        </div>
      </div>

      {/* Mandatory Recommendation Notice */}
      <RecommendationRibbon />

      {/* Progress Stepper */}
      <div className="rounded-2xl border border-border bg-card p-6 shadow-2xs space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">Application Journey</h2>
          <span className="text-xs text-muted-foreground font-mono">
            Status: <span className="font-semibold text-primary capitalize">{application?.status || "Ready for report"}</span>
          </span>
        </div>
        <Stepper steps={APPLICATION_STEPS} currentStepIndex={4} />
      </div>

      {/* Grid: Next Step Action & Checklist */}
      <div className="grid gap-6 md:grid-cols-5">
        {/* Prominent Next Step Card */}
        <div className="md:col-span-3 rounded-2xl border border-primary/25 bg-gradient-to-br from-primary/[0.04] to-card p-6 space-y-4 flex flex-col justify-between shadow-2xs">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Badge className="bg-primary/10 text-primary border-primary/20 text-[10px] uppercase font-bold tracking-wider">
                Recommended Action
              </Badge>
              <StatusBadge status={application?.status || "ready_for_report"} size="sm" />
            </div>

            <h3 className="text-lg font-bold text-foreground">
              Review Your Official Evaluation &amp; Plain-English Breakdown
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Your deterministic criteria evaluation and tuition accounting calculations are ready for your review. You have been recommended for a 50% tuition reduction.
            </p>
          </div>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <Button render={<Link to={`/student/results?app=${activeAppId}`} />} className="gap-2">
              Inspect Decision Dossier
              <ArrowRightIcon className="size-4" />
            </Button>
            <Button
              render={<Link to={`/student/documents?app=${activeAppId}`} />}
              variant="outline"
              className="gap-2 text-xs"
            >
              <FolderCheckIcon className="size-4" />
              Manage Evidence
            </Button>
          </div>
        </div>

        {/* Verification Checklist */}
        <div className="md:col-span-2 rounded-2xl border border-border bg-card p-6 space-y-4 shadow-2xs">
          <div className="flex items-center justify-between border-b pb-3">
            <h3 className="text-sm font-semibold text-foreground">Document Checklist</h3>
            <span className="text-xs font-mono text-muted-foreground">
              {uploadedDocTypes.size} of 3
            </span>
          </div>

          <ul className="space-y-3">
            {docTypes.map((doc) => {
              const isUploaded = uploadedDocTypes.has(doc.id)
              return (
                <li
                  key={doc.id}
                  className="flex items-center justify-between gap-2 p-2.5 rounded-xl border border-border/60 bg-muted/20 text-xs"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    {isUploaded ? (
                      <CheckCircle2Icon className="size-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                    ) : (
                      <ClockIcon className="size-4 text-amber-600 dark:text-amber-400 shrink-0" />
                    )}
                    <span className="truncate font-medium text-foreground">{doc.label}</span>
                  </div>

                  {isUploaded ? (
                    <Badge variant="outline" className="text-[10px] text-emerald-600 border-emerald-500/30 bg-emerald-500/10">
                      Verified
                    </Badge>
                  ) : (
                    <Link
                      to={`/student/documents?app=${activeAppId}&doc=${doc.id}`}
                      className="text-[11px] font-semibold text-primary hover:underline"
                    >
                      Upload
                    </Link>
                  )}
                </li>
              )
            })}
          </ul>

          <p className="text-[11px] text-muted-foreground leading-relaxed pt-1">
            Missing evidence keeps an application in <span className="font-semibold text-amber-700 dark:text-amber-400">Awaiting Evidence</span> and is never treated as an automatic failure.
          </p>
        </div>
      </div>
    </div>
  )
}
