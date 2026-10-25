import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { zodResolver } from "@/lib/resolver"
import { useCreateApplication } from "@/hooks/use-queries"
import { Stepper } from "@/components/domain/stepper"
import { MoneyAmount } from "@/components/domain/money-amount"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  InfoIcon,
  LockIcon,
  SaveIcon,
  SparklesIcon,
} from "lucide-react"

const WIZARD_STEPS = [
  { id: "personal", title: "Personal & Academic", description: "Identity & grades" },
  { id: "financial", title: "Financial Need", description: "Income & tuition" },
  { id: "policy", title: "Policy Alignment", description: "Governance checks" },
  { id: "review", title: "Review & Submit", description: "Audit verification" },
]

const formSchema = z.object({
  name: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.string().email("Valid institutional or personal email required"),
  institution: z.string().min(2, "Institution name required").default("National Institute of Technology"),
  programme: z.string().min(2, "Degree programme required").default("B.Tech Computer Science"),
  cgpa: z.coerce.number().min(0).max(10, "CGPA must be between 0.0 and 10.0"),
  tenth: z.coerce.number().min(0).max(100, "10th percentage must be between 0 and 100"),
  twelfth: z.coerce.number().min(0).max(100, "12th percentage must be between 0 and 100"),
  backlogs: z.coerce.number().min(0, "Active backlogs cannot be negative"),
  income: z.coerce.number().min(0, "Annual household income must be positive"),
  emi: z.coerce.number().min(0, "Existing monthly EMI must be positive"),
  tuition: z.coerce.number().min(0, "Annual tuition fee must be positive"),
  loan: z.coerce.number().min(0, "Requested education loan must be positive"),
  casteCategory: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

const DRAFT_STORAGE_KEY = "fairexplain_application_draft"

export function ApplyWizard() {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(0)
  const [savedAt, setSavedAt] = useState<string | null>(null)
  const { mutateAsync: createApplication, isPending } = useCreateApplication()

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "Priya Sharma",
      email: "priya.sharma@nitk.edu.in",
      institution: "National Institute of Technology Karnataka",
      programme: "B.Tech Computer Science & Engineering",
      cgpa: 8.85,
      tenth: 92.4,
      twelfth: 89.6,
      backlogs: 0,
      income: 420000,
      emi: 3000,
      tuition: 240000,
      loan: 480000,
    },
  })

  const formValues = watch()

  // Load Draft from LocalStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(DRAFT_STORAGE_KEY)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        Object.keys(parsed).forEach((k) => {
          setValue(k as keyof FormValues, parsed[k])
        })
        setSavedAt("Loaded from draft")
      } catch {
        // ignore
      }
    }
  }, [setValue])

  // Autosave Draft
  const handleSaveDraft = () => {
    localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(formValues))
    setSavedAt(new Date().toLocaleTimeString())
  }

  const onSubmit = async (data: FormValues) => {
    try {
      const result = await createApplication({
        name: data.name,
        email: data.email,
        academic_record: {
          cgpa: data.cgpa,
          tenth_percent: data.tenth,
          twelfth_percent: data.twelfth,
          backlogs: data.backlogs,
        },
        financial_profile: {
          household_income: data.income,
          existing_emi: data.emi,
          tuition_fee: data.tuition,
          requested_loan: data.loan,
        },
      })

      localStorage.removeItem(DRAFT_STORAGE_KEY)
      navigate(`/student/results?app=${result.application_id}`)
    } catch (err) {
      console.error("Submission failed", err)
      alert("Failed to submit application to rule engine. Please try again.")
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
            Higher Education Financing Application
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Deterministic eligibility evaluation under institutional merit &amp; need policy.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {savedAt && (
            <span className="text-xs text-muted-foreground font-mono">
              Draft saved {savedAt}
            </span>
          )}
          <Button variant="outline" size="sm" onClick={handleSaveDraft} className="gap-1.5 text-xs">
            <SaveIcon className="size-3.5" />
            Save Draft
          </Button>
        </div>
      </div>

      {/* Stepper */}
      <div className="rounded-2xl border bg-card p-6 shadow-2xs">
        <Stepper
          steps={WIZARD_STEPS}
          currentStepIndex={currentStep}
          onStepClick={(idx) => setCurrentStep(idx)}
        />
      </div>

      {/* Main Wizard Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Step 0: Personal & Academic Profile */}
        {currentStep === 0 && (
          <div className="rounded-2xl border border-border bg-card p-6 sm:p-8 space-y-6 shadow-2xs animate-in fade-in-50">
            <div className="border-b pb-4">
              <h2 className="text-base font-bold text-foreground">
                Step 1: Personal &amp; Academic Identity
              </h2>
              <p className="text-xs text-muted-foreground">
                Enter your student credentials and verified cumulative academic performance.
              </p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">Full Legal Name</Label>
                <Input id="name" placeholder="Priya Sharma" {...register("name")} />
                {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input id="email" type="email" placeholder="priya.sharma@nitk.edu.in" {...register("email")} />
                {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="institution">Enrolled Institution / University</Label>
                <Input id="institution" placeholder="National Institute of Technology" {...register("institution")} />
                {errors.institution && <p className="text-xs text-destructive">{errors.institution.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="programme">Degree Programme</Label>
                <Input id="programme" placeholder="B.Tech Computer Science" {...register("programme")} />
                {errors.programme && <p className="text-xs text-destructive">{errors.programme.message}</p>}
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="cgpa">Cumulative GPA (0.00 – 10.00)</Label>
                  <span className="text-[11px] text-muted-foreground">Target: &ge; 8.00</span>
                </div>
                <Input id="cgpa" type="number" step="0.01" placeholder="8.85" {...register("cgpa")} />
                {errors.cgpa && <p className="text-xs text-destructive">{errors.cgpa.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="backlogs">Active Uncleared Backlogs</Label>
                <Input id="backlogs" type="number" placeholder="0" {...register("backlogs")} />
                <p className="text-[11px] text-muted-foreground">
                  Uncleared courses from preceding semesters requiring examination. (Must be 0 for merit).
                </p>
                {errors.backlogs && <p className="text-xs text-destructive">{errors.backlogs.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="tenth">10th Board Examination Percentage</Label>
                <Input id="tenth" type="number" step="0.1" placeholder="92.4" {...register("tenth")} />
                {errors.tenth && <p className="text-xs text-destructive">{errors.tenth.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="twelfth">12th Board Examination Percentage</Label>
                <Input id="twelfth" type="number" step="0.1" placeholder="89.6" {...register("twelfth")} />
                {errors.twelfth && <p className="text-xs text-destructive">{errors.twelfth.message}</p>}
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t">
              <Button type="button" onClick={() => setCurrentStep(1)} className="gap-2">
                Next: Financial Profile
                <ArrowRightIcon className="size-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Step 1: Financial Need Profile */}
        {currentStep === 1 && (
          <div className="rounded-2xl border border-border bg-card p-6 sm:p-8 space-y-6 shadow-2xs animate-in fade-in-50">
            <div className="border-b pb-4">
              <h2 className="text-base font-bold text-foreground">
                Step 2: Financial Need &amp; Fee Details
              </h2>
              <p className="text-xs text-muted-foreground">
                All amounts are in Indian Rupees (₹). Used to compute tuition accounting and debt capacity.
              </p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="income">Annual Household Income (INR/year)</Label>
                  <span className="text-[11px] text-muted-foreground">Ceiling: ₹8.0L</span>
                </div>
                <Input id="income" type="number" placeholder="420000" {...register("income")} />
                <p className="text-[11px] text-muted-foreground">
                  Combined gross income of parents/guardians as verified on ITR or income certificate.
                </p>
                {errors.income && <p className="text-xs text-destructive">{errors.income.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="emi">Existing Monthly Family EMI Obligations (INR/month)</Label>
                <Input id="emi" type="number" placeholder="3000" {...register("emi")} />
                <p className="text-[11px] text-muted-foreground">
                  Active monthly loan installments across all ongoing bank facilities.
                </p>
                {errors.emi && <p className="text-xs text-destructive">{errors.emi.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="tuition">Annual Tuition Fee (INR/year)</Label>
                <Input id="tuition" type="number" placeholder="240000" {...register("tuition")} />
                <p className="text-[11px] text-muted-foreground">
                  Approved institutional gross tuition schedule before any waivers.
                </p>
                {errors.tuition && <p className="text-xs text-destructive">{errors.tuition.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="loan">Requested Education Loan Amount (INR)</Label>
                <Input id="loan" type="number" placeholder="480000" {...register("loan")} />
                <p className="text-[11px] text-muted-foreground">
                  Gross loan amount requested prior to scholarship reduction.
                </p>
                {errors.loan && <p className="text-xs text-destructive">{errors.loan.message}</p>}
              </div>
            </div>

            <div className="flex justify-between pt-4 border-t">
              <Button type="button" variant="outline" onClick={() => setCurrentStep(0)} className="gap-2">
                <ArrowLeftIcon className="size-4" /> Back
              </Button>
              <Button type="button" onClick={() => setCurrentStep(2)} className="gap-2">
                Next: Policy Alignment
                <ArrowRightIcon className="size-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Step 2: Policy Alignment & Sensitive Governance */}
        {currentStep === 2 && (
          <div className="rounded-2xl border border-border bg-card p-6 sm:p-8 space-y-6 shadow-2xs animate-in fade-in-50">
            <div className="border-b pb-4">
              <h2 className="text-base font-bold text-foreground">
                Step 3: Policy Alignment &amp; Governance Notice
              </h2>
              <p className="text-xs text-muted-foreground">
                Verification of demographic safety rules and statutory scheme compliance.
              </p>
            </div>

            <div className="rounded-xl border border-primary/20 bg-primary/5 p-4 space-y-3 text-xs leading-relaxed">
              <div className="flex items-center gap-2 font-semibold text-primary">
                <LockIcon className="size-4" />
                Charter Authorization Protection (Section 3 Governance)
              </div>
              <p className="text-muted-foreground">
                FairExplain AI systematically isolates sensitive attributes (caste, religion, gender, disability) from general merit evaluations. Such attributes are only evaluated if a specific affirmative endowment legally mandates them via an explicit charter order.
              </p>
            </div>

            <div className="space-y-4 pt-2">
              <div className="space-y-2">
                <Label htmlFor="casteCategory" className="flex items-center justify-between">
                  <span>Affirmative Action Endowment Category (Optional)</span>
                  <Badge variant="outline" className="text-[10px] font-mono">
                    Charter: GOV-SCHEME-ORD-2024/77B
                  </Badge>
                </Label>
                <select
                  id="casteCategory"
                  {...register("casteCategory")}
                  className="w-full rounded-xl border border-border bg-background p-2.5 text-xs text-foreground focus:ring-2 focus:ring-primary"
                >
                  <option value="General">General Category / Non-Reserved</option>
                  <option value="OBC-NCL">OBC Non-Creamy Layer</option>
                  <option value="SC">Scheduled Caste (SC)</option>
                  <option value="ST">Scheduled Tribe (ST)</option>
                  <option value="EWS">Economically Weaker Section (EWS)</option>
                </select>
                <p className="text-[11px] text-muted-foreground">
                  Providing this information is voluntary and solely used for statutory reserve grant eligibility.
                </p>
              </div>
            </div>

            <div className="flex justify-between pt-4 border-t">
              <Button type="button" variant="outline" onClick={() => setCurrentStep(1)} className="gap-2">
                <ArrowLeftIcon className="size-4" /> Back
              </Button>
              <Button type="button" onClick={() => setCurrentStep(3)} className="gap-2">
                Next: Review &amp; Submit
                <ArrowRightIcon className="size-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Review & Submit */}
        {currentStep === 3 && (
          <div className="rounded-2xl border border-border bg-card p-6 sm:p-8 space-y-6 shadow-2xs animate-in fade-in-50">
            <div className="border-b pb-4">
              <h2 className="text-base font-bold text-foreground">
                Step 4: Audit Verification &amp; Final Submission
              </h2>
              <p className="text-xs text-muted-foreground">
                Confirm your submitted profile figures before triggering deterministic evaluation.
              </p>
            </div>

            {/* Confirmation Summary Cards */}
            <div className="grid gap-4 sm:grid-cols-2 text-xs">
              <div className="rounded-xl border p-4 bg-background space-y-2.5">
                <span className="font-semibold text-foreground uppercase tracking-wider text-[11px] block text-primary">
                  Academic Record
                </span>
                <div className="flex justify-between py-1 border-b">
                  <span className="text-muted-foreground">Full Name:</span>
                  <span className="font-medium text-foreground">{formValues.name}</span>
                </div>
                <div className="flex justify-between py-1 border-b">
                  <span className="text-muted-foreground">Institution:</span>
                  <span className="font-medium text-foreground">{formValues.institution}</span>
                </div>
                <div className="flex justify-between py-1 border-b">
                  <span className="text-muted-foreground">Cumulative GPA:</span>
                  <span className="font-mono font-bold text-foreground">{formValues.cgpa} / 10.0</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-muted-foreground">Active Backlogs:</span>
                  <span className="font-mono font-bold text-foreground">{formValues.backlogs}</span>
                </div>
              </div>

              <div className="rounded-xl border p-4 bg-background space-y-2.5">
                <span className="font-semibold text-foreground uppercase tracking-wider text-[11px] block text-primary">
                  Financial Profile
                </span>
                <div className="flex justify-between py-1 border-b">
                  <span className="text-muted-foreground">Annual Household Income:</span>
                  <MoneyAmount amount={formValues.income} size="sm" />
                </div>
                <div className="flex justify-between py-1 border-b">
                  <span className="text-muted-foreground">Existing Monthly EMI:</span>
                  <MoneyAmount amount={formValues.emi} size="sm" />
                </div>
                <div className="flex justify-between py-1 border-b">
                  <span className="text-muted-foreground">Annual Tuition Fee:</span>
                  <MoneyAmount amount={formValues.tuition} size="sm" />
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-muted-foreground">Requested Loan:</span>
                  <MoneyAmount amount={formValues.loan} size="sm" />
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-primary/25 bg-primary/5 p-4 text-xs text-foreground leading-relaxed flex items-start gap-3">
              <InfoIcon className="size-4 text-primary shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold block">Deterministic Rule Guarantee</span>
                FairExplain AI will evaluate your submission against verified institutional criteria. Output will be generated with a cryptographic audit signature for full reproducibility.
              </div>
            </div>

            <div className="flex justify-between pt-4 border-t">
              <Button type="button" variant="outline" onClick={() => setCurrentStep(2)} className="gap-2">
                <ArrowLeftIcon className="size-4" /> Back
              </Button>
              <Button type="submit" disabled={isPending} className="gap-2 font-semibold">
                {isPending ? (
                  "Evaluating via Rule Engine..."
                ) : (
                  <>
                    <SparklesIcon className="size-4" />
                    Submit Application for Evaluation
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </form>
    </div>
  )
}
