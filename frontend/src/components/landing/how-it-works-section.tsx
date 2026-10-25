import { useState } from "react"
import {
  FileTextIcon,
  UploadCloudIcon,
  ScanLineIcon,
  GitCompareIcon,
  CpuIcon,
  CalculatorIcon,
  BanknoteIcon,
  ShieldCheckIcon,
  SparklesIcon,
  UserCheckIcon,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"

const WORKFLOW_STEPS = [
  {
    step: 1,
    stage: "Intake",
    icon: FileTextIcon,
    title: "Application Intake",
    description: "Student submits academic records, fee schedule, and household income details.",
  },
  {
    step: 2,
    stage: "Intake",
    icon: UploadCloudIcon,
    title: "Proof Upload",
    description: "Official income certificates and semester marksheets are securely stored.",
  },
  {
    step: 3,
    stage: "Intake",
    icon: ScanLineIcon,
    title: "Vision OCR Extraction",
    description: "Computer vision parses marksheet percentiles and certificate revenue stamps.",
  },
  {
    step: 4,
    stage: "Intake",
    icon: GitCompareIcon,
    title: "Discrepancy Reconciliation",
    description: "Cross-checks self-reported values against OCR extracts, flagging deviations.",
  },
  {
    step: 5,
    stage: "Deterministic",
    icon: CpuIcon,
    title: "AST Rule Engine",
    description: "Deterministic Python core tests criteria against statutory versioned policies.",
  },
  {
    step: 6,
    stage: "Deterministic",
    icon: CalculatorIcon,
    title: "Tuition Accounting Ledger",
    description: "Allocates awards in priority order, enforces caps, and derives net remaining fee.",
  },
  {
    step: 7,
    stage: "Deterministic",
    icon: BanknoteIcon,
    title: "Loan Affordability Analysis",
    description: "Calculates conservative repayment serviceability and debt-to-income capacity.",
  },
  {
    step: 8,
    stage: "Governance",
    icon: ShieldCheckIcon,
    title: "Sensitive Attribute Segregation",
    description: "Guarantees zero caste, religion, or gender tokens enter prompt or scoring context.",
  },
  {
    step: 9,
    stage: "Governance",
    icon: SparklesIcon,
    title: "Grounded AI Explanation",
    description: "LLM synthesizes plain-English rationale strictly bound to deterministic facts.",
  },
  {
    step: 10,
    stage: "Governance",
    icon: UserCheckIcon,
    title: "Human Officer Sign-Off",
    description: "Authorized institutional officer reviews dossier and issues cryptographically signed determination.",
  },
]

export function HowItWorksSection() {
  const [activeStep, setActiveStep] = useState<number>(5)

  const current = WORKFLOW_STEPS[activeStep - 1]

  return (
    <section
      id="how-it-works"
      className="mx-auto w-full max-w-6xl scroll-mt-20 px-4 py-16 sm:px-6 md:py-24 space-y-12"
    >
      <div className="flex flex-col gap-3 max-w-2xl">
        <Badge variant="secondary" className="w-fit rounded-full px-3 py-1 text-xs">
          10-Step End-to-End Pipeline
        </Badge>
        <h2 className="text-balance text-3xl font-bold tracking-tight sm:text-4xl text-foreground">
          From Application Submission to Accountable Human Sign-Off
        </h2>
        <p className="text-pretty text-muted-foreground text-sm sm:text-base leading-relaxed">
          Every phase is strictly decoupled. Math is calculated deterministically, the AI translates facts into plain English, and humans retain final operational authority.
        </p>
      </div>

      {/* Interactive 10-Step Progress Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2">
        {WORKFLOW_STEPS.map((s) => {
          const Icon = s.icon
          const isSelected = activeStep === s.step

          return (
            <button
              key={s.step}
              onClick={() => setActiveStep(s.step)}
              className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between gap-3 ${
                isSelected
                  ? "border-primary bg-primary/10 shadow-xs ring-2 ring-primary/30"
                  : "border-border/70 bg-card hover:bg-muted/40 hover:border-border"
              }`}
            >
              <div className="flex items-center justify-between w-full">
                <span
                  className={`size-6 rounded-md flex items-center justify-center text-xs font-mono font-bold ${
                    isSelected
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                  }`}
                >
                  {s.step}
                </span>
                <span className="text-[10px] uppercase font-mono tracking-wider text-muted-foreground">
                  {s.stage}
                </span>
              </div>

              <div className="space-y-1">
                <Icon
                  className={`size-4 ${
                    isSelected ? "text-primary" : "text-muted-foreground"
                  }`}
                />
                <div className="text-xs font-bold text-foreground line-clamp-2 leading-tight">
                  {s.title}
                </div>
              </div>
            </button>
          )
        })}
      </div>

      {/* Spotlight Selected Step Card */}
      <div className="rounded-2xl border border-primary/30 bg-gradient-to-br from-card to-primary/[0.03] p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6 mb-6">
          <div className="flex items-center gap-4">
            <div className="size-14 rounded-2xl bg-primary/15 text-primary flex items-center justify-center shrink-0">
              <current.icon className="size-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs font-mono font-bold">
                  Step {current.step} of 10
                </Badge>
                <Badge className="text-xs capitalize font-medium">
                  {current.stage} Phase
                </Badge>
              </div>
              <h3 className="text-xl sm:text-2xl font-bold text-foreground mt-1">
                {current.title}
              </h3>
            </div>
          </div>

          <div className="text-xs font-mono text-muted-foreground">
            Architecture Ref: ARCHITECTURE.md § {current.step}
          </div>
        </div>

        <p className="text-base text-foreground/90 leading-relaxed max-w-3xl">
          {current.description}
        </p>
      </div>
    </section>
  )
}
