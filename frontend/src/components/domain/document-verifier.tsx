import type { UploadedDocumentDTO, VerificationResultDTO } from "@/types/domain"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  AlertTriangleIcon,
  CheckCircle2Icon,
  ExternalLinkIcon,
  FileTextIcon,
  ShieldCheckIcon,
} from "lucide-react"

interface DocumentVerifierProps {
  document: UploadedDocumentDTO
  reportedData?: Record<string, unknown>
  verification?: VerificationResultDTO | null
  onConfirmMismatch?: (field: string) => void
  onCorrectMismatch?: (field: string, correctValue: unknown) => void
}

export function DocumentVerifier({
  document,
  reportedData = {},
  verification,
  onConfirmMismatch,
  onCorrectMismatch,
}: DocumentVerifierProps) {
  const extracted = (document.ocr_extracted_data || {}) as Record<string, unknown>
  const mismatches = verification?.discrepancies || []

  return (
    <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-sm">
      {/* Header */}
      <div className="p-4 sm:p-5 border-b flex flex-wrap items-center justify-between gap-3 bg-muted/20">
        <div className="flex items-center gap-3">
          <div className="size-9 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
            <FileTextIcon className="size-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold capitalize text-foreground">
                {document.doc_type.replace(/_/g, " ")} Document Verification
              </h3>
              {document.mismatch_flag ? (
                <Badge variant="destructive" className="text-[10px] uppercase font-bold">
                  Mismatch Detected
                </Badge>
              ) : (
                <Badge variant="outline" className="text-[10px] uppercase font-medium text-emerald-600 border-emerald-500/30 bg-emerald-500/10">
                  Verified Match
                </Badge>
              )}
            </div>
            <span className="text-xs text-muted-foreground font-mono">
              ID: {document.id} · SHA256: {document.sha256?.slice(0, 12)}...
            </span>
          </div>
        </div>

        {document.confidence !== undefined && (
          <div className="text-right text-xs">
            <span className="text-muted-foreground block text-[10px] uppercase">OCR Confidence</span>
            <span className="font-semibold font-mono text-foreground">
              {(document.confidence * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>

      {/* Split View: Left = Document Info/Preview, Right = Field Reconciliation */}
      <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border">
        {/* Left Column: Document File & Verification Note */}
        <div className="p-5 space-y-4 bg-muted/10">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Document Intake &amp; Preview
            </span>
            {document.file_url && (
              <a
                href={document.file_url}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-primary hover:underline inline-flex items-center gap-1 font-medium"
              >
                Inspect Original <ExternalLinkIcon className="size-3" />
              </a>
            )}
          </div>

          <div className="rounded-xl border bg-background p-4 space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-border/50">
              <span className="text-muted-foreground">Document Category:</span>
              <span className="font-medium capitalize text-foreground">{document.doc_type}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-border/50">
              <span className="text-muted-foreground">Intake Timestamp:</span>
              <span className="font-mono text-foreground">
                {document.created_at ? new Date(document.created_at).toLocaleString() : "—"}
              </span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-muted-foreground">Cryptographic SHA256:</span>
              <span className="font-mono text-[11px] text-foreground">
                {document.sha256 ? `${document.sha256.slice(0, 16)}...` : "Verified"}
              </span>
            </div>
          </div>

          <div className="rounded-xl border border-primary/20 bg-primary/5 p-3.5 text-xs text-muted-foreground leading-relaxed">
            <strong className="text-foreground font-semibold flex items-center gap-1 mb-1">
              <ShieldCheckIcon className="size-3.5 text-primary" />
              Automated Integrity Cross-Check
            </strong>
            OCR parsed academic and financial figures are compared with 5% allowable variance against self-reported profile fields.
          </div>
        </div>

        {/* Right Column: OCR Extracted Fields vs Self-Reported */}
        <div className="p-5 space-y-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block">
            Extracted Data vs. Student Profile
          </span>

          <div className="space-y-3">
            {Object.keys(extracted).length === 0 ? (
              <p className="text-xs text-muted-foreground py-4">No fields extracted yet.</p>
            ) : (
              Object.entries(extracted).map(([field, extractedVal]) => {
                if (field === "confidence" || field === "filename" || field === "size") return null
                const reportedVal = reportedData[field]
                const isMismatch = mismatches.some((m) => m.field === field)

                return (
                  <div
                    key={field}
                    className={`rounded-xl border p-3.5 text-xs space-y-2 transition-colors ${
                      isMismatch
                        ? "border-amber-500/50 bg-amber-500/10"
                        : "border-border bg-background"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-foreground capitalize">
                        {field.replace(/_/g, " ")}
                      </span>
                      {isMismatch ? (
                        <span className="inline-flex items-center gap-1 font-semibold text-amber-700 dark:text-amber-400">
                          <AlertTriangleIcon className="size-3.5" /> Discrepancy
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                          <CheckCircle2Icon className="size-3.5" /> Matches Profile
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-2 font-mono text-[11px] pt-1 border-t border-border/40">
                      <div>
                        <span className="text-muted-foreground block text-[10px] font-sans">
                          OCR Extracted
                        </span>
                        <span className="text-foreground font-bold">{String(extractedVal)}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground block text-[10px] font-sans">
                          Self-Reported
                        </span>
                        <span className="text-foreground">{reportedVal !== undefined ? String(reportedVal) : "—"}</span>
                      </div>
                    </div>

                    {isMismatch && (
                      <div className="pt-2 flex gap-2 justify-end">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => onConfirmMismatch?.(field)}
                          className="text-[11px] h-7"
                        >
                          Confirm Extracted
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => onCorrectMismatch?.(field, extractedVal)}
                          className="text-[11px] h-7"
                        >
                          Keep Self-Reported
                        </Button>
                      </div>
                    )}
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
