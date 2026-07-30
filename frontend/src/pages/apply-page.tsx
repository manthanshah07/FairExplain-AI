import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  GraduationCapIcon,
  Loader2Icon,
  ShieldCheckIcon,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Field } from "@/components/ui/field"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { FormStepper, type Step } from "@/components/apply/form-stepper"
import { formatINR } from "@/lib/mock-data"

const STEPS: Step[] = [
  { id: "applicant", title: "Applicant details", description: "Who is applying" },
  { id: "academic", title: "Academic record", description: "Marks & backlogs" },
  { id: "financial", title: "Financial profile", description: "Income & loan" },
  { id: "review", title: "Review & submit", description: "Confirm everything" },
]

interface FormState {
  name: string
  email: string
  programme: string
  institution: string
  cgpa: string
  tenthPercent: string
  twelfthPercent: string
  backlogs: string
  householdIncome: string
  existingEmi: string
  tuitionFee: string
  requestedLoan: string
}

const INITIAL: FormState = {
  name: "",
  email: "",
  programme: "",
  institution: "",
  cgpa: "",
  tenthPercent: "",
  twelfthPercent: "",
  backlogs: "0",
  householdIncome: "",
  existingEmi: "0",
  tuitionFee: "",
  requestedLoan: "",
}

type Errors = Partial<Record<keyof FormState, string>>

const PROGRAMMES = [
  "B.Tech, Computer Science",
  "B.Tech, Mechanical",
  "B.Com, Finance",
  "M.Sc, Biotechnology",
  "B.Arch",
  "MBA",
  "Other",
]

function validateStep(step: number, form: FormState): Errors {
  const errors: Errors = {}
  const num = (v: string) => (v.trim() === "" ? Number.NaN : Number(v))

  if (step === 0) {
    if (!form.name.trim()) errors.name = "Full name is required."
    if (!form.email.trim()) errors.email = "Email is required."
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
      errors.email = "Enter a valid email address."
    if (!form.programme) errors.programme = "Select a programme."
    if (!form.institution.trim()) errors.institution = "Institution is required."
  }

  if (step === 1) {
    const cgpa = num(form.cgpa)
    if (Number.isNaN(cgpa) || cgpa < 0 || cgpa > 10)
      errors.cgpa = "CGPA must be between 0 and 10."
    const tenth = num(form.tenthPercent)
    if (Number.isNaN(tenth) || tenth < 0 || tenth > 100)
      errors.tenthPercent = "Enter a percentage between 0 and 100."
    const twelfth = num(form.twelfthPercent)
    if (Number.isNaN(twelfth) || twelfth < 0 || twelfth > 100)
      errors.twelfthPercent = "Enter a percentage between 0 and 100."
    const backlogs = num(form.backlogs)
    if (Number.isNaN(backlogs) || backlogs < 0)
      errors.backlogs = "Backlogs cannot be negative."
  }

  if (step === 2) {
    const income = num(form.householdIncome)
    if (Number.isNaN(income) || income < 0)
      errors.householdIncome = "Enter your annual household income."
    const emi = num(form.existingEmi)
    if (Number.isNaN(emi) || emi < 0) errors.existingEmi = "EMI cannot be negative."
    const tuition = num(form.tuitionFee)
    if (Number.isNaN(tuition) || tuition <= 0)
      errors.tuitionFee = "Enter the annual tuition fee."
    const loan = num(form.requestedLoan)
    if (Number.isNaN(loan) || loan <= 0)
      errors.requestedLoan = "Enter the loan amount you need."
  }

  return errors
}

export function ApplyPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [form, setForm] = useState<FormState>(INITIAL)
  const [errors, setErrors] = useState<Errors>({})
  const [submitting, setSubmitting] = useState(false)

  const update = (key: keyof FormState) => (value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    setErrors((prev) => ({ ...prev, [key]: undefined }))
  }

  const goNext = () => {
    const stepErrors = validateStep(step, form)
    if (Object.keys(stepErrors).length > 0) {
      setErrors(stepErrors)
      return
    }
    setErrors({})
    setStep((s) => Math.min(s + 1, STEPS.length - 1))
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  const goBack = () => {
    setErrors({})
    setStep((s) => Math.max(s - 1, 0))
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  const handleSubmit = () => {
    setSubmitting(true)
    // Phase 1: simulate a submission, then route to the sample assessment.
    window.setTimeout(() => navigate("/results/APP-2026-004182"), 1200)
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-8 sm:px-6 md:py-12">
          <div className="flex flex-col gap-2">
            <Button
              asChild
              variant="ghost"
              size="sm"
              className="-ml-2 w-fit text-muted-foreground"
            >
              <Link to="/dashboard">
                <ArrowLeftIcon data-icon="inline-start" />
                Back to dashboard
              </Link>
            </Button>
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              New eligibility application
            </h1>
            <p className="text-sm text-muted-foreground">
              Provide academic and financial details. Our deterministic rule
              engine scores the application; a human reviewer makes the final
              call.
            </p>
          </div>

          <div className="grid gap-8 lg:grid-cols-[240px_1fr]">
            <aside className="lg:sticky lg:top-24 lg:self-start">
              <FormStepper steps={STEPS} current={step} />
            </aside>

            <div className="flex flex-col gap-6">
              <Card>
                <CardHeader className="border-b [.border-b]:pb-4">
                  <CardTitle>{STEPS[step].title}</CardTitle>
                  <CardDescription>
                    {step === 0 && "Basic information about the applicant."}
                    {step === 1 &&
                      "Academic performance used by the scholarship rule engine."}
                    {step === 2 &&
                      "Financial context used to compute the reduced loan."}
                    {step === 3 &&
                      "Confirm the details below before submitting for assessment."}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {step === 0 && (
                    <div className="grid gap-5 sm:grid-cols-2">
                      <Field
                        label="Full name"
                        htmlFor="name"
                        required
                        error={errors.name}
                        className="sm:col-span-2"
                      >
                        <Input
                          id="name"
                          value={form.name}
                          onChange={(e) => update("name")(e.target.value)}
                          placeholder="Priya Sharma"
                          aria-invalid={!!errors.name}
                        />
                      </Field>
                      <Field
                        label="Email address"
                        htmlFor="email"
                        required
                        error={errors.email}
                      >
                        <Input
                          id="email"
                          type="email"
                          value={form.email}
                          onChange={(e) => update("email")(e.target.value)}
                          placeholder="priya@example.edu"
                          aria-invalid={!!errors.email}
                        />
                      </Field>
                      <Field
                        label="Programme"
                        htmlFor="programme"
                        required
                        error={errors.programme}
                      >
                        <Select
                          id="programme"
                          value={form.programme}
                          onChange={(e) => update("programme")(e.target.value)}
                          aria-invalid={!!errors.programme}
                        >
                          <option value="" disabled>
                            Select a programme
                          </option>
                          {PROGRAMMES.map((p) => (
                            <option key={p} value={p}>
                              {p}
                            </option>
                          ))}
                        </Select>
                      </Field>
                      <Field
                        label="Institution"
                        htmlFor="institution"
                        required
                        error={errors.institution}
                        className="sm:col-span-2"
                      >
                        <Input
                          id="institution"
                          value={form.institution}
                          onChange={(e) =>
                            update("institution")(e.target.value)
                          }
                          placeholder="National Institute of Technology"
                          aria-invalid={!!errors.institution}
                        />
                      </Field>
                    </div>
                  )}

                  {step === 1 && (
                    <div className="grid gap-5 sm:grid-cols-2">
                      <Field
                        label="CGPA (out of 10)"
                        htmlFor="cgpa"
                        required
                        error={errors.cgpa}
                        hint="Current cumulative grade point average."
                      >
                        <Input
                          id="cgpa"
                          type="number"
                          step="0.1"
                          min="0"
                          max="10"
                          value={form.cgpa}
                          onChange={(e) => update("cgpa")(e.target.value)}
                          placeholder="8.6"
                          aria-invalid={!!errors.cgpa}
                        />
                      </Field>
                      <Field
                        label="Active backlogs"
                        htmlFor="backlogs"
                        required
                        error={errors.backlogs}
                      >
                        <Input
                          id="backlogs"
                          type="number"
                          min="0"
                          value={form.backlogs}
                          onChange={(e) => update("backlogs")(e.target.value)}
                          aria-invalid={!!errors.backlogs}
                        />
                      </Field>
                      <Field
                        label="10th percentage"
                        htmlFor="tenth"
                        required
                        error={errors.tenthPercent}
                      >
                        <Input
                          id="tenth"
                          type="number"
                          min="0"
                          max="100"
                          value={form.tenthPercent}
                          onChange={(e) =>
                            update("tenthPercent")(e.target.value)
                          }
                          placeholder="91"
                          aria-invalid={!!errors.tenthPercent}
                        />
                      </Field>
                      <Field
                        label="12th percentage"
                        htmlFor="twelfth"
                        required
                        error={errors.twelfthPercent}
                      >
                        <Input
                          id="twelfth"
                          type="number"
                          min="0"
                          max="100"
                          value={form.twelfthPercent}
                          onChange={(e) =>
                            update("twelfthPercent")(e.target.value)
                          }
                          placeholder="89"
                          aria-invalid={!!errors.twelfthPercent}
                        />
                      </Field>
                    </div>
                  )}

                  {step === 2 && (
                    <div className="grid gap-5 sm:grid-cols-2">
                      <Field
                        label="Annual household income"
                        htmlFor="income"
                        required
                        error={errors.householdIncome}
                        hint="Used to assess genuine financial need."
                      >
                        <Input
                          id="income"
                          type="number"
                          min="0"
                          value={form.householdIncome}
                          onChange={(e) =>
                            update("householdIncome")(e.target.value)
                          }
                          placeholder="420000"
                          aria-invalid={!!errors.householdIncome}
                        />
                      </Field>
                      <Field
                        label="Existing monthly EMI"
                        htmlFor="emi"
                        error={errors.existingEmi}
                      >
                        <Input
                          id="emi"
                          type="number"
                          min="0"
                          value={form.existingEmi}
                          onChange={(e) =>
                            update("existingEmi")(e.target.value)
                          }
                          placeholder="3000"
                          aria-invalid={!!errors.existingEmi}
                        />
                      </Field>
                      <Field
                        label="Annual tuition fee"
                        htmlFor="tuition"
                        required
                        error={errors.tuitionFee}
                      >
                        <Input
                          id="tuition"
                          type="number"
                          min="0"
                          value={form.tuitionFee}
                          onChange={(e) =>
                            update("tuitionFee")(e.target.value)
                          }
                          placeholder="320000"
                          aria-invalid={!!errors.tuitionFee}
                        />
                      </Field>
                      <Field
                        label="Loan amount requested"
                        htmlFor="loan"
                        required
                        error={errors.requestedLoan}
                      >
                        <Input
                          id="loan"
                          type="number"
                          min="0"
                          value={form.requestedLoan}
                          onChange={(e) =>
                            update("requestedLoan")(e.target.value)
                          }
                          placeholder="800000"
                          aria-invalid={!!errors.requestedLoan}
                        />
                      </Field>
                    </div>
                  )}

                  {step === 3 && <ReviewSummary form={form} onEdit={setStep} />}
                </CardContent>
              </Card>

              <div className="flex items-center justify-between gap-3">
                <Button
                  variant="ghost"
                  onClick={goBack}
                  disabled={step === 0 || submitting}
                >
                  <ArrowLeftIcon data-icon="inline-start" />
                  Back
                </Button>

                {step < STEPS.length - 1 ? (
                  <Button onClick={goNext}>
                    Continue
                    <ArrowRightIcon data-icon="inline-end" />
                  </Button>
                ) : (
                  <Button onClick={handleSubmit} disabled={submitting}>
                    {submitting ? (
                      <>
                        <Loader2Icon
                          data-icon="inline-start"
                          className="animate-spin"
                        />
                        Assessing…
                      </>
                    ) : (
                      <>
                        <ShieldCheckIcon data-icon="inline-start" />
                        Submit for assessment
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}

function ReviewSummary({
  form,
  onEdit,
}: {
  form: FormState
  onEdit: (step: number) => void
}) {
  const asINR = (v: string) => (v ? formatINR(Number(v)) : "—") 

  return (
    <div className="flex flex-col gap-6">
      <SummaryGroup
        icon={GraduationCapIcon}
        title="Applicant"
        onEdit={() => onEdit(0)}
        rows={[
          ["Name", form.name || "—"],
          ["Email", form.email || "—"],
          ["Programme", form.programme || "—"],
          ["Institution", form.institution || "—"],
        ]}
      />
      <Separator />
      <SummaryGroup
        icon={GraduationCapIcon}
        title="Academic record"
        onEdit={() => onEdit(1)}
        rows={[
          ["CGPA", form.cgpa ? `${form.cgpa} / 10` : "—"],
          ["10th %", form.tenthPercent ? `${form.tenthPercent}%` : "—"],
          ["12th %", form.twelfthPercent ? `${form.twelfthPercent}%` : "—"],
          ["Active backlogs", form.backlogs || "0"],
        ]}
      />
      <Separator />
      <SummaryGroup
        icon={ShieldCheckIcon}
        title="Financial profile"
        onEdit={() => onEdit(2)}
        rows={[
          ["Household income", asINR(form.householdIncome)],
          ["Existing EMI", asINR(form.existingEmi)],
          ["Tuition fee", asINR(form.tuitionFee)],
          ["Loan requested", asINR(form.requestedLoan)],
        ]}
      />

      <div className="flex items-start gap-2.5 rounded-lg bg-primary/10 px-3.5 py-3">
        <ShieldCheckIcon
          className="mt-0.5 size-4 shrink-0 text-primary"
          aria-hidden="true"
        />
        <p className="text-xs leading-relaxed text-muted-foreground">
          <span className="font-medium text-foreground">
            Protected attributes are never collected.
          </span>{" "}
          Caste, religion, gender, disability status, and region play no part in
          this assessment. A fairness checker screens for indirect proxies too.
        </p>
      </div>
    </div>
  )
}

function SummaryGroup({
  icon: Icon,
  title,
  rows,
  onEdit,
}: {
  icon: typeof GraduationCapIcon
  title: string
  rows: [string, string][]
  onEdit: () => void
}) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="flex size-7 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Icon className="size-4" aria-hidden="true" />
          </span>
          <h3 className="text-sm font-medium">{title}</h3>
        </div>
        <Button variant="ghost" size="xs" onClick={onEdit}>
          Edit
        </Button>
      </div>
      <dl className="grid gap-x-6 gap-y-2 sm:grid-cols-2">
        {rows.map(([label, value]) => (
          <div key={label} className="flex items-center justify-between gap-4 text-sm">
            <dt className="text-muted-foreground">{label}</dt>
            <dd className="truncate font-medium tabular-nums">{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
