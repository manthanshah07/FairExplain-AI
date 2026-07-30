import { UserCheckIcon } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export function HumanReviewNotice() {
  return (
    <Alert className="border-primary/30 bg-primary/5">
      <UserCheckIcon className="text-primary" />
      <AlertTitle>This is an AI recommendation, not a final decision</AlertTitle>
      <AlertDescription>
        FairExplain AI produces scores and explanations to support a reviewer. A
        qualified human makes the final, accountable decision on this
        application. Nothing here is auto-approved.
      </AlertDescription>
    </Alert>
  )
}
