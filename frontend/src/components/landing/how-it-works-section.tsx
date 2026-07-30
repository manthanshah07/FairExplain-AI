import {
  FileTextIcon,
  ScanLineIcon,
  CalculatorIcon,
  MessageSquareTextIcon,
  UserCheckIcon,
} from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const STEPS = [
  {
    icon: FileTextIcon,
    title: "Submit application",
    description:
      "Students provide academic and financial details along with supporting documents.",
  },
  {
    icon: ScanLineIcon,
    title: "Verify with OCR",
    description:
      "Uploaded marksheets and income proofs are extracted and cross-checked against self-reported values.",
  },
  {
    icon: CalculatorIcon,
    title: "Score with the rule engine",
    description:
      "A deterministic, versioned engine computes the scholarship score and reduced-loan eligibility. No AI guesswork.",
  },
  {
    icon: MessageSquareTextIcon,
    title: "Explain the outcome",
    description:
      "An LLM turns the engine's numbers into a clear rationale, then a fairness checker screens it for bias.",
  },
  {
    icon: UserCheckIcon,
    title: "Human decides",
    description:
      "A reviewer sees the score, explanation, and fairness note — and makes the final, accountable decision.",
  },
]

export function HowItWorksSection() {
  return (
    <section
      id="how-it-works"
      className="mx-auto w-full max-w-6xl scroll-mt-20 px-4 py-16 sm:px-6 md:py-24"
    >
      <div className="flex max-w-2xl flex-col gap-3">
        <Badge variant="secondary" className="w-fit rounded-full">
          How it works
        </Badge>
        <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
          From application to accountable decision
        </h2>
        <p className="text-pretty text-muted-foreground">
          Every step is separated by design. The rule engine owns the math, the
          AI only explains, and a human owns the outcome.
        </p>
      </div>

      <ol className="mt-10 grid gap-4 md:grid-cols-3 lg:grid-cols-5">
        {STEPS.map((step, index) => (
          <li key={step.title}>
            <Card className="h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <span className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <step.icon className="size-5" aria-hidden="true" />
                  </span>
                  <span className="text-sm font-semibold text-muted-foreground tabular-nums">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>
                <CardTitle className="mt-3 text-base">{step.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="leading-relaxed">
                  {step.description}
                </CardDescription>
              </CardContent>
            </Card>
          </li>
        ))}
      </ol>
    </section>
  )
}
