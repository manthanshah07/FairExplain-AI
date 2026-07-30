import { Link } from "react-router-dom"
import { ArrowRightIcon } from "lucide-react"
import { Button } from "@/components/ui/button"

export function CtaSection() {
  return (
    <section className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6 md:py-24">
      <div className="relative overflow-hidden rounded-2xl border border-border bg-primary px-6 py-12 text-primary-foreground sm:px-12">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(50%_80%_at_100%_0%,color-mix(in_oklch,white_18%,transparent),transparent)]"
        />
        <div className="relative flex max-w-2xl flex-col gap-4">
          <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
            See exactly how a decision is explained
          </h2>
          <p className="text-pretty leading-relaxed text-primary-foreground/80">
            Explore a complete sample assessment — scholarship score, reduced
            loan, plain-language rationale, fairness check, and the human-review
            notice that accompanies every outcome.
          </p>
          <div className="mt-2">
            <Button
              render={<Link to="/results" />}
              size="lg"
              variant="secondary"
            >
              View the sample result
              <ArrowRightIcon data-icon="inline-end" />
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
