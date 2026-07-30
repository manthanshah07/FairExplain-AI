import {
  GavelIcon,
  ScaleIcon,
  EyeIcon,
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

const PRINCIPLES = [
  {
    icon: GavelIcon,
    title: "The rule engine is the source of truth",
    description:
      "Scholarship and loan scores come from a deterministic, versioned formula. The same inputs always produce the same outputs — fully auditable.",
  },
  {
    icon: EyeIcon,
    title: "The AI only explains",
    description:
      "The language model never calculates a score or changes a decision. It translates the engine's numbers into a clear, honest rationale.",
  },
  {
    icon: ScaleIcon,
    title: "Fairness is checked, not assumed",
    description:
      "Caste, religion, gender, and region are never inputs. A fairness checker also screens for indirect proxies like pincode or surname inference.",
  },
  {
    icon: UserCheckIcon,
    title: "Humans make the final call",
    description:
      "Every recommendation routes to an accountable reviewer. FairExplain assists the decision — it never automates it away.",
  },
]

export function PrinciplesSection() {
  return (
    <section
      id="principles"
      className="scroll-mt-20 border-y border-border/70 bg-card/40"
    >
      <div className="mx-auto grid w-full max-w-6xl gap-10 px-4 py-16 sm:px-6 md:py-24 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
        <div className="flex flex-col gap-4">
          <Badge variant="secondary" className="w-fit rounded-full">
            Core principles
          </Badge>
          <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
            The AI recommends.{" "}
            <span className="text-primary">Humans decide.</span>
          </h2>
          <p className="text-pretty leading-relaxed text-muted-foreground">
            FairExplain AI is deliberately not a chatbot or an autonomous
            approval engine. It is a transparent decision-support system with
            non-negotiable guardrails baked into its architecture.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {PRINCIPLES.map((principle) => (
            <Card key={principle.title} className="h-full">
              <CardHeader>
                <span className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <principle.icon className="size-5" aria-hidden="true" />
                </span>
                <CardTitle className="mt-3 text-base">
                  {principle.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="leading-relaxed">
                  {principle.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
