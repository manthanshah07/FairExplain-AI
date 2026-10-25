import { Button } from "@/components/ui/button"
import { AlertCircleIcon, RotateCcwIcon } from "lucide-react"

interface ErrorStateProps {
  title?: string
  message: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
  className = "",
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className={`rounded-2xl border border-destructive/30 bg-destructive/5 p-8 text-center flex flex-col items-center justify-center space-y-3 ${className}`}
    >
      <div className="size-12 rounded-full bg-destructive/15 flex items-center justify-center text-destructive">
        <AlertCircleIcon className="size-6" />
      </div>
      <h3 className="text-base font-semibold text-foreground tracking-tight">{title}</h3>
      <p className="text-xs sm:text-sm text-muted-foreground max-w-md leading-relaxed">
        {message}
      </p>
      {onRetry && (
        <div className="pt-2">
          <Button variant="outline" size="sm" onClick={onRetry} className="gap-1.5">
            <RotateCcwIcon className="size-3.5" />
            Try Again
          </Button>
        </div>
      )}
    </div>
  )
}
