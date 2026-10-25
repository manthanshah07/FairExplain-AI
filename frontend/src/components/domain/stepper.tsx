import { CheckIcon } from "lucide-react"

export interface StepItem {
  id: string
  title: string
  description?: string
}

interface StepperProps {
  steps: StepItem[]
  currentStepIndex: number
  onStepClick?: (index: number) => void
  className?: string
}

export function Stepper({
  steps,
  currentStepIndex,
  onStepClick,
  className = "",
}: StepperProps) {
  return (
    <nav aria-label="Progress Stepper" className={`w-full ${className}`}>
      <ol className="flex items-center w-full">
        {steps.map((step, idx) => {
          const isDone = idx < currentStepIndex
          const isCurrent = idx === currentStepIndex
          const isClickable = onStepClick && idx <= currentStepIndex

          return (
            <li
              key={step.id}
              className={`flex items-center ${
                idx !== steps.length - 1 ? "w-full" : ""
              }`}
            >
              <div
                onClick={() => isClickable && onStepClick(idx)}
                className={`flex items-center gap-2.5 ${
                  isClickable ? "cursor-pointer" : ""
                }`}
              >
                <span
                  className={`flex size-8 shrink-0 items-center justify-center rounded-full text-xs font-bold transition-colors ${
                    isDone
                      ? "bg-primary text-primary-foreground"
                      : isCurrent
                      ? "border-2 border-primary text-primary bg-primary/10"
                      : "border-2 border-border text-muted-foreground bg-muted/40"
                  }`}
                >
                  {isDone ? <CheckIcon className="size-4" /> : idx + 1}
                </span>

                <div className="hidden sm:block min-w-0 text-left">
                  <span
                    className={`text-xs block font-semibold truncate ${
                      isCurrent
                        ? "text-primary"
                        : isDone
                        ? "text-foreground"
                        : "text-muted-foreground"
                    }`}
                  >
                    {step.title}
                  </span>
                  {step.description && (
                    <span className="text-[10px] text-muted-foreground block truncate">
                      {step.description}
                    </span>
                  )}
                </div>
              </div>

              {idx !== steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-3 sm:mx-4 transition-colors ${
                    idx < currentStepIndex ? "bg-primary" : "bg-border"
                  }`}
                />
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
