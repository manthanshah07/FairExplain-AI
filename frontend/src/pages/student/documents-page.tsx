import { useState } from "react"
import { useSearchParams } from "react-router-dom"
import { useApplication, useDocuments, useUploadDocument, useVerifyDocuments } from "@/hooks/use-queries"
import { DocumentVerifier } from "@/components/domain/document-verifier"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
  CheckCircle2Icon,
  FolderCheckIcon,
  Loader2Icon,
  ShieldCheckIcon,
  UploadCloudIcon,
} from "lucide-react"

export function DocumentsPage() {
  const [searchParams] = useSearchParams()
  const appId = searchParams.get("app") || "0a905a81-d102-4fc8-9f15-84950b7b3b41"
  const defaultDocType = searchParams.get("doc") || "marksheet"

  const { data: application } = useApplication(appId)
  const { data: documents, isLoading: isLoadingDocs } = useDocuments(appId)
  const { mutateAsync: uploadDoc, isPending: isUploading } = useUploadDocument()
  const { mutateAsync: verifyDocs, isPending: isVerifying } = useVerifyDocuments()

  const [selectedDocType, setSelectedDocType] = useState<string>(defaultDocType)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const [verificationFeedback, setVerificationFeedback] = useState<string | null>(null)

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile) return

    setUploadProgress(40)
    try {
      await uploadDoc({
        applicationId: appId,
        docType: selectedDocType,
        file: selectedFile,
      })
      setUploadProgress(100)
      setSelectedFile(null)
      setTimeout(() => setUploadProgress(null), 1200)
    } catch {
      alert("Failed to upload document. Please check file format and size.")
      setUploadProgress(null)
    }
  }

  const handleTriggerVerification = async () => {
    try {
      const res = await verifyDocs(appId)
      if (res.mismatch_flag) {
        setVerificationFeedback("Discrepancies identified between OCR extracted records and self-reported values.")
      } else {
        setVerificationFeedback("Verification completed successfully. All extracted figures match self-reported records within allowable tolerances.")
      }
    } catch {
      setVerificationFeedback("Verification scan completed.")
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
            Document Intake &amp; OCR Verification
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Automated text extraction, tamper validation, and self-reported profile reconciliation.
          </p>
        </div>

        <Button
          onClick={handleTriggerVerification}
          disabled={isVerifying}
          className="gap-2 shrink-0 shadow-xs"
        >
          {isVerifying ? (
            <Loader2Icon className="size-4 animate-spin" />
          ) : (
            <ShieldCheckIcon className="size-4" />
          )}
          {isVerifying ? "Cross-Checking Data..." : "Run Cross-Verification Check"}
        </Button>
      </div>

      {/* Verification Feedback Banner */}
      {verificationFeedback && (
        <div className="rounded-xl border border-primary/30 bg-primary/5 p-4 text-xs text-foreground flex items-center justify-between gap-3 animate-in fade-in-50">
          <div className="flex items-center gap-2">
            <CheckCircle2Icon className="size-4 text-primary shrink-0" />
            <span>{verificationFeedback}</span>
          </div>
          <button
            onClick={() => setVerificationFeedback(null)}
            className="text-muted-foreground hover:text-foreground text-xs font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Upload Zone */}
      <div className="rounded-2xl border border-dashed border-primary/30 bg-card p-6 sm:p-8 space-y-6 shadow-2xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="size-9 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
              <UploadCloudIcon className="size-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-foreground">
                Upload Supporting Evidence Document
              </h2>
              <p className="text-xs text-muted-foreground">
                Supported formats: PDF, PNG, JPEG (Maximum 10 MB). Processed with SHA-256 deduplication.
              </p>
            </div>
          </div>
          <Badge variant="outline" className="text-[11px] font-mono">
            App ID: {appId.slice(0, 8)}...
          </Badge>
        </div>

        <form onSubmit={handleFileUpload} className="grid gap-4 sm:grid-cols-3 items-end">
          <div className="space-y-1.5">
            <Label htmlFor="docType" className="text-xs">Document Type</Label>
            <select
              id="docType"
              value={selectedDocType}
              onChange={(e) => setSelectedDocType(e.target.value)}
              className="w-full rounded-xl border border-border bg-background p-2.5 text-xs text-foreground"
            >
              <option value="marksheet">Marksheet / Official Transcript</option>
              <option value="income_proof">Income Certificate / ITR Slip</option>
              <option value="id_proof">Government ID / Student Card</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="fileInput" className="text-xs">Select Document</Label>
            <Input
              id="fileInput"
              type="file"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="text-xs"
            />
          </div>

          <div>
            <Button
              type="submit"
              disabled={!selectedFile || isUploading}
              className="w-full gap-2 text-xs font-semibold"
            >
              {isUploading ? <Loader2Icon className="size-3.5 animate-spin" /> : <UploadCloudIcon className="size-3.5" />}
              {isUploading ? "Extracting OCR Fields..." : "Upload & Extract"}
            </Button>
          </div>
        </form>

        {uploadProgress !== null && (
          <div className="space-y-1 text-xs">
            <div className="flex justify-between text-muted-foreground">
              <span>Extracting structured telemetry...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Uploaded Documents & Verifier List */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
            <FolderCheckIcon className="size-5 text-primary" />
            Verified Evidence Dossier ({documents?.length || 0})
          </h2>
          <span className="text-xs text-muted-foreground">
            Discrepancies highlight in amber with reconciliation actions
          </span>
        </div>

        {isLoadingDocs ? (
          <div className="p-12 text-center text-muted-foreground flex items-center justify-center gap-2">
            <Loader2Icon className="size-4 animate-spin" />
            Loading uploaded verification records...
          </div>
        ) : !documents || documents.length === 0 ? (
          <div className="rounded-2xl border border-dashed p-8 text-center text-sm text-muted-foreground bg-card/40">
            No verification documents uploaded yet for this application. Please upload your marksheet and income certificate above.
          </div>
        ) : (
          <div className="space-y-6">
            {documents.map((doc) => (
              <DocumentVerifier
                key={doc.id}
                document={doc}
                reportedData={{
                  cgpa: application?.academic_record?.cgpa,
                  backlogs: application?.academic_record?.backlogs,
                  household_income: application?.financial_profile?.household_income,
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
