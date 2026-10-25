import { useState } from "react"
import { Link } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import {
  AlertTriangleIcon,
  CheckCircle2Icon,
  ChevronDownIcon,
  ChevronUpIcon,
  ExternalLinkIcon,
  FileTextIcon,
  FlagIcon,
  Loader2Icon,
  ShieldAlertIcon,
  UserCheckIcon,
  XCircleIcon,
} from "lucide-react"

import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { useReviewQueue } from "@/hooks/use-application"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { api } from "@/services/api"
import type { ReviewQueueItem } from "@/types/api"

export function ReviewPage() {
  const { data: queue, isLoading } = useReviewQueue()
  const queryClient = useQueryClient()
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null)
  const [contextData, setContextData] = useState<any | null>(null)
  const [isLoadingContext, setIsLoadingContext] = useState(false)
  const [decision, setDecision] = useState<"approve" | "override" | "request_evidence" | "reject">("approve")
  const [rationale, setRationale] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null)

  const handleToggleExpand = async (appId: string) => {
    if (selectedAppId === appId) {
      setSelectedAppId(null)
      setContextData(null)
      return
    }

    setSelectedAppId(appId)
    setIsLoadingContext(true)
    setSubmitSuccess(null)
    setRationale("")
    try {
      const data = await api.getReviewContext(appId)
      setContextData(data)
    } catch {
      // ignore
    } finally {
      setIsLoadingContext(false)
    }
  }

  const handleSubmitDecision = async (appId: string) => {
    if (!rationale.trim() || rationale.trim().length < 3) {
      alert("Mandatory justification is required for human reviewer determinations.")
      return
    }

    setIsSubmitting(true)
    try {
      const res = await api.recordReviewDecision(appId, decision, rationale.trim(), "officer_in_charge")
      if (res.success) {
        setSubmitSuccess(`Determination '${decision.toUpperCase()}' recorded successfully. Audit entry logged.`)
        queryClient.invalidateQueries({ queryKey: ["reviewQueue"] })
        queryClient.invalidateQueries({ queryKey: ["dashboardStats"] })
      } else {
        alert("Failed to record determination on the server.")
      }
    } catch {
      alert("An unexpected error occurred while submitting determination.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1 px-4 py-8 sm:px-6 md:py-12">
        <div className="mx-auto max-w-5xl space-y-8">
          <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Review Queue</h1>
              <p className="text-muted-foreground">
                Institutional officer oversight portal for inspect-and-decide governance.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="px-3 py-1 font-mono text-xs">
                Human-in-the-Loop Active
              </Badge>
            </div>
          </div>

          <div className="rounded-xl border bg-card/40 shadow-sm overflow-hidden">
            <div className="grid grid-cols-6 border-b p-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              <div className="col-span-2">Applicant</div>
              <div>Submitted</div>
              <div>Priority</div>
              <div>Status</div>
              <div className="text-right">Action</div>
            </div>

            {isLoading ? (
              <div className="p-12 text-center text-muted-foreground flex items-center justify-center gap-2">
                <Loader2Icon className="size-4 animate-spin" />
                Loading review queue...
              </div>
            ) : !queue || queue.length === 0 ? (
              <div className="p-12 text-center text-muted-foreground">
                No applications currently requiring review.
              </div>
            ) : (
              queue.map((app: ReviewQueueItem) => {
                const isExpanded = selectedAppId === app.id
                return (
                  <div key={app.id} className="border-b last:border-0">
                    <div
                      className={`grid grid-cols-6 items-center p-4 hover:bg-muted/30 transition-colors cursor-pointer ${
                        isExpanded ? "bg-muted/40" : ""
                      }`}
                      onClick={() => handleToggleExpand(app.id)}
                    >
                      <div className="col-span-2 flex flex-col gap-1 pr-2">
                        <span className="font-medium text-foreground">{app.name}</span>
                        <span className="text-xs text-muted-foreground font-mono">{app.id}</span>
                        {app.flags && app.flags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {app.flags.map((flag, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center gap-1 rounded bg-amber-500/10 px-1.5 py-0.5 text-[10px] text-amber-600 dark:text-amber-400 font-medium"
                              >
                                <AlertTriangleIcon className="size-3" />
                                {flag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      <div className="text-xs text-muted-foreground">{app.date}</div>

                      <div>
                        {app.priority === "high" ? (
                          <Badge variant="destructive" className="text-[10px] uppercase font-bold">
                            High
                          </Badge>
                        ) : app.priority === "medium" ? (
                          <Badge variant="secondary" className="text-[10px] uppercase font-bold bg-amber-500/15 text-amber-700 dark:text-amber-300">
                            Medium
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-[10px] uppercase font-medium">
                            Low
                          </Badge>
                        )}
                      </div>

                      <div>
                        <Badge
                          variant="secondary"
                          className={`text-[10px] ${
                            app.status === "ready_for_report"
                              ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400"
                              : app.status === "needs_review"
                              ? "bg-amber-500/15 text-amber-700 dark:text-amber-400"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {app.status}
                        </Badge>
                      </div>

                      <div className="text-right flex items-center justify-end gap-2">
                        <Button
                          size="sm"
                          variant={isExpanded ? "secondary" : "outline"}
                          onClick={(e) => {
                            e.stopPropagation()
                            handleToggleExpand(app.id)
                          }}
                        >
                          {isExpanded ? (
                            <>
                              Close <ChevronUpIcon className="size-3.5" />
                            </>
                          ) : (
                            <>
                              Review <ChevronDownIcon className="size-3.5" />
                            </>
                          )}
                        </Button>
                      </div>
                    </div>

                    {/* Expanded Review Dossier Panel */}
                    {isExpanded && (
                      <div className="p-6 bg-card border-t space-y-6">
                        {isLoadingContext ? (
                          <div className="p-8 text-center text-muted-foreground flex items-center justify-center gap-2">
                            <Loader2Icon className="size-4 animate-spin" />
                            Loading applicant dossier and cross-verification records...
                          </div>
                        ) : contextData ? (
                          <div className="space-y-6">
                            {submitSuccess && (
                              <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-4 text-sm text-emerald-700 dark:text-emerald-300 flex items-center gap-2">
                                <CheckCircle2Icon className="size-5 shrink-0" />
                                <span>{submitSuccess}</span>
                              </div>
                            )}

                            {/* Dossier Grid */}
                            <div className="grid gap-4 md:grid-cols-2">
                              {/* 1. Academic & OCR Cross-Verification */}
                              <div className="rounded-lg border p-4 space-y-3 bg-background/50">
                                <div className="flex items-center justify-between">
                                  <h3 className="text-sm font-semibold flex items-center gap-2">
                                    <FileTextIcon className="size-4 text-primary" />
                                    Academic &amp; Document Data
                                  </h3>
                                  <span className="text-xs text-muted-foreground">
                                    Self-reported vs OCR
                                  </span>
                                </div>
                                <div className="space-y-2 text-xs">
                                  <div className="flex justify-between border-b pb-1">
                                    <span className="text-muted-foreground">CGPA:</span>
                                    <span className="font-semibold">{contextData.academic_record?.cgpa ?? "N/A"}</span>
                                  </div>
                                  <div className="flex justify-between border-b pb-1">
                                    <span className="text-muted-foreground">10th / 12th Percent:</span>
                                    <span>{contextData.academic_record?.tenth_percent}% / {contextData.academic_record?.twelfth_percent}%</span>
                                  </div>
                                  <div className="flex justify-between border-b pb-1">
                                    <span className="text-muted-foreground">Active Backlogs:</span>
                                    <span>{contextData.academic_record?.backlogs ?? 0}</span>
                                  </div>
                                </div>

                                {contextData.ocr_diffs && contextData.ocr_diffs.length > 0 && (
                                  <div className="pt-2">
                                    <span className="text-[11px] font-semibold text-muted-foreground uppercase">Uploaded Documents</span>
                                    <div className="mt-1 space-y-1">
                                      {contextData.ocr_diffs.map((doc: any, i: number) => (
                                        <div key={i} className="flex items-center justify-between text-xs rounded bg-muted/40 px-2 py-1">
                                          <span>{doc.doc_type}</span>
                                          {doc.mismatch_flag ? (
                                            <Badge variant="destructive" className="text-[10px]">Mismatch Flagged</Badge>
                                          ) : (
                                            <Badge variant="secondary" className="text-[10px] text-emerald-600">Verified</Badge>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* 2. Financial Profile & Evaluation */}
                              <div className="rounded-lg border p-4 space-y-3 bg-background/50">
                                <h3 className="text-sm font-semibold flex items-center gap-2">
                                  <UserCheckIcon className="size-4 text-primary" />
                                  Financial Profile &amp; Rules
                                </h3>
                                <div className="space-y-2 text-xs">
                                  <div className="flex justify-between border-b pb-1">
                                    <span className="text-muted-foreground">Annual Household Income:</span>
                                    <span className="font-semibold">₹{Number(contextData.financial_profile?.household_income || 0).toLocaleString("en-IN")}</span>
                                  </div>
                                  <div className="flex justify-between border-b pb-1">
                                    <span className="text-muted-foreground">Gross Tuition Fee:</span>
                                    <span>₹{Number(contextData.financial_profile?.tuition_fee || 0).toLocaleString("en-IN")}</span>
                                  </div>
                                  <div className="flex justify-between border-b pb-1">
                                    <span className="text-muted-foreground">Requested Loan:</span>
                                    <span>₹{Number(contextData.financial_profile?.requested_loan || 0).toLocaleString("en-IN")}</span>
                                  </div>
                                  <div className="flex justify-between border-b pb-1">
                                    <span className="text-muted-foreground">Rule Engine Outcome:</span>
                                    <span className="font-semibold capitalize text-primary">{contextData.scholarship_evaluation?.status || "Pending"}</span>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* 3. AI Explanation & Fairness Note */}
                            {contextData.explanation && (
                              <div className="rounded-lg border p-4 space-y-2 bg-background/50">
                                <h3 className="text-sm font-semibold flex items-center gap-2">
                                  <ShieldAlertIcon className="size-4 text-primary" />
                                  AI Grounded Reasoning &amp; Governance
                                </h3>
                                <p className="text-xs text-foreground font-medium">
                                  {contextData.explanation.recommendation_text}
                                </p>
                                {contextData.explanation.fairness_note && (
                                  <p className="text-[11px] text-muted-foreground italic border-l-2 pl-2 border-primary/40">
                                    {contextData.explanation.fairness_note}
                                  </p>
                                )}
                              </div>
                            )}

                            {/* 4. Human Review Determination Form */}
                            <div className="rounded-xl border border-primary/20 bg-primary/5 p-5 space-y-4">
                              <div className="flex items-center justify-between">
                                <h4 className="text-sm font-bold tracking-tight">Record Human Determination</h4>
                                <span className="text-[11px] text-muted-foreground">Authority Boundary: Human Decision Only</span>
                              </div>

                              <div className="grid gap-3 sm:grid-cols-4">
                                <button
                                  type="button"
                                  onClick={() => setDecision("approve")}
                                  className={`rounded-lg border p-3 text-left transition-colors flex flex-col gap-1 text-xs font-semibold ${
                                    decision === "approve"
                                      ? "border-emerald-600 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
                                      : "border-border bg-card/60 hover:bg-card"
                                  }`}
                                >
                                  <CheckCircle2Icon className="size-4 text-emerald-600" />
                                  <span>Approve</span>
                                  <span className="text-[10px] font-normal text-muted-foreground">Confirm eligibility</span>
                                </button>

                                <button
                                  type="button"
                                  onClick={() => setDecision("override")}
                                  className={`rounded-lg border p-3 text-left transition-colors flex flex-col gap-1 text-xs font-semibold ${
                                    decision === "override"
                                      ? "border-amber-600 bg-amber-500/10 text-amber-700 dark:text-amber-400"
                                      : "border-border bg-card/60 hover:bg-card"
                                  }`}
                                >
                                  <AlertTriangleIcon className="size-4 text-amber-600" />
                                  <span>Override</span>
                                  <span className="text-[10px] font-normal text-muted-foreground">Grant exception</span>
                                </button>

                                <button
                                  type="button"
                                  onClick={() => setDecision("request_evidence")}
                                  className={`rounded-lg border p-3 text-left transition-colors flex flex-col gap-1 text-xs font-semibold ${
                                    decision === "request_evidence"
                                      ? "border-blue-600 bg-blue-500/10 text-blue-700 dark:text-blue-400"
                                      : "border-border bg-card/60 hover:bg-card"
                                  }`}
                                >
                                  <FlagIcon className="size-4 text-blue-600" />
                                  <span>Request Evidence</span>
                                  <span className="text-[10px] font-normal text-muted-foreground">Ask for verification</span>
                                </button>

                                <button
                                  type="button"
                                  onClick={() => setDecision("reject")}
                                  className={`rounded-lg border p-3 text-left transition-colors flex flex-col gap-1 text-xs font-semibold ${
                                    decision === "reject"
                                      ? "border-red-600 bg-red-500/10 text-red-700 dark:text-red-400"
                                      : "border-border bg-card/60 hover:bg-card"
                                  }`}
                                >
                                  <XCircleIcon className="size-4 text-red-600" />
                                  <span>Reject</span>
                                  <span className="text-[10px] font-normal text-muted-foreground">Close application</span>
                                </button>
                              </div>

                              <div className="space-y-1.5">
                                <label className="text-xs font-medium text-foreground flex items-center justify-between">
                                  <span>Mandatory Determination Justification / Rationale:</span>
                                  <span className="text-[10px] text-muted-foreground">* Required for immutable audit log</span>
                                </label>
                                <textarea
                                  value={rationale}
                                  onChange={(e) => setRationale(e.target.value)}
                                  rows={3}
                                  placeholder="Provide detailed institutional reasoning for this determination (e.g., 'Verified income tax returns independently with applicant...')"
                                  className="w-full rounded-md border border-input bg-background p-2.5 text-xs text-foreground shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
                                />
                              </div>

                              <div className="flex items-center justify-between pt-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  render={<Link to={`/results/${app.id}`} target="_blank" />}
                                  className="text-xs text-muted-foreground"
                                >
                                  View full assessment <ExternalLinkIcon className="size-3 ml-1" />
                                </Button>

                                <Button
                                  size="sm"
                                  disabled={isSubmitting || !rationale.trim()}
                                  onClick={() => handleSubmitDecision(app.id)}
                                >
                                  {isSubmitting ? (
                                    <>
                                      <Loader2Icon className="size-3.5 animate-spin mr-1.5" />
                                      Recording...
                                    </>
                                  ) : (
                                    "Submit Determination"
                                  )}
                                </Button>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="p-4 text-center text-xs text-muted-foreground">
                            Unable to load context for this application.
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })
            )}
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}
