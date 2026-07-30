import { CheckIcon } from "lucide-react"
import { cn } from "@/lib/utils"

export interface Step {
  id: string
  title: string
  description: string
}

export function FormStepper({
  steps,
  current,
}: {
  steps: Step[]
  current: number
}) {
  return (
    <>
      {/* Desktop: vertical rail */}
      <ol className="hidden flex-col gap-1 lg:flex" aria-label="Application progress">
        {steps.map((step, index) => {
          const state =
            index < current ? "complete" : index === current ? "current" : "upcoming"
          return (
            <li key={step.id} className="flex gap-3">
              <div className="flex flex-col items-center">
                <span
                  className={cn(
                    "flex size-8 shrink-0 items-center justify-center rounded-full border text-sm font-medium transition-colors",
                    state === "complete" &&
                      "border-primary bg-primary text-primary-foreground",
                    state === "current" &&
                      "border-primary bg-primary/10 text-primary",
                    state === "upcoming" &&
                      "border-border bg-background text-muted-foreground"
                  )}
                  aria-current={state === "current" ? "step" : undefined}
                >
                  {state === "complete" ? (
                    <CheckIcon className="size-4" aria-hidden="true" />
                  ) : (
                    index + 1
                  )}
                </span>
                {index < steps.length - 1 && (
                  <span
                    className={cn(
                      "my-1 w-px flex-1 transition-colors",
                      index < current ? "bg-primary" : "bg-border"
                    )}
                    aria-hidden="true"
                  />
                )}
              </div>
              <div className="pb-6">
                <p
                  className={cn(
                    "text-sm font-medium transition-colors",
                    state === "upcoming" ? "text-muted-foreground" : "text-foreground"
                  )}
                >
                  {step.title}
                </p>
                <p className="text-xs text-muted-foreground">
                  {step.description}
                </p>
              </div>
            </li>
          )
        })}
      </ol>

      {/* Mobile/tablet: horizontal progress bar */}
      <div className="flex flex-col gap-3 lg:hidden">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium">
            Step {current + 1} of {steps.length}
          </span>
          <span className="text-muted-foreground">{steps[current].title}</span>
        </div>
        <div className="flex gap-1.5" aria-hidden="true">
          {steps.map((step, index) => (
            <span
              key={step.id}
              className={cn(
                "h-1.5 flex-1 rounded-full transition-colors",
                index <= current ? "bg-primary" : "bg-muted"
              )}
            />
          ))}
        </div>
      </div>
    </>
  )
}
