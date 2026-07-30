import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import {
  ArrowRightIcon,
  CircleCheckIcon,
  Loader2Icon,
  ScaleIcon,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Field } from "@/components/ui/field"
import { Brand } from "@/components/brand"
import { ThemeToggle } from "@/components/theme-toggle"

interface RegisterState {
  name: string
  email: string
  role: string
  password: string
}

type Errors = Partial<Record<keyof RegisterState, string>>

const HIGHLIGHTS = [
  "Deterministic rule engine — same inputs, same outputs.",
  "Every recommendation reviewed by an accountable human.",
  "Fairness-checked, plain-language explanations.",
]

export function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<RegisterState>({
    name: "",
    email: "",
    role: "",
    password: "",
  })
  const [errors, setErrors] = useState<Errors>({})
  const [submitting, setSubmitting] = useState(false)

  const update = (key: keyof RegisterState) => (value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    setErrors((prev) => ({ ...prev, [key]: undefined }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const next: Errors = {}
    if (!form.name.trim()) next.name = "Full name is required."
    if (!form.email.trim()) next.email = "Email is required."
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
      next.email = "Enter a valid email address."
    if (!form.role) next.role = "Select your role."
    if (form.password.length < 8)
      next.password = "Password must be at least 8 characters."

    if (Object.keys(next).length > 0) {
      setErrors(next)
      return
    }
    setSubmitting(true)
    window.setTimeout(() => navigate("/dashboard"), 1000)
  }

  return (
    <div className="grid min-h-dvh lg:grid-cols-2">
      {/* Brand panel */}
      <aside className="relative hidden flex-col justify-between overflow-hidden bg-primary p-10 text-primary-foreground lg:flex">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(60%_60%_at_20%_0%,color-mix(in_oklch,white_16%,transparent),transparent)]"
        />
        <Link to="/" className="relative flex items-center gap-2.5">
          <span className="flex size-9 items-center justify-center rounded-lg bg-primary-foreground/15">
            <ScaleIcon className="size-5" aria-hidden="true" />
          </span>
          <span className="text-base font-semibold tracking-tight">
            FairExplain AI
          </span>
        </Link>

        <div className="relative flex flex-col gap-6">
          <h2 className="text-balance text-3xl font-semibold tracking-tight">
            Transparent eligibility decisions your reviewers can stand behind.
          </h2>
          <ul className="flex flex-col gap-3">
            {HIGHLIGHTS.map((point) => (
              <li key={point} className="flex items-start gap-2.5 text-sm">
                <CircleCheckIcon
                  className="mt-0.5 size-4 shrink-0"
                  aria-hidden="true"
                />
                <span className="text-primary-foreground/90">{point}</span>
              </li>
            ))}
          </ul>
        </div>

        <p className="relative text-xs text-primary-foreground/70">
          The AI recommends. Humans decide.
        </p>
      </aside>

      {/* Form panel */}
      <main className="flex flex-col">
        <div className="flex items-center justify-between p-6">
          <Link to="/" className="lg:hidden" aria-label="FairExplain AI home">
            <Brand />
          </Link>
          <span className="hidden lg:block" />
          <ThemeToggle />
        </div>

        <div className="flex flex-1 items-center justify-center px-6 pb-10">
          <div className="w-full max-w-sm">
            <div className="flex flex-col gap-2">
              <h1 className="text-2xl font-semibold tracking-tight">
                Create your account
              </h1>
              <p className="text-sm text-muted-foreground">
                Set up a reviewer workspace to assess applications.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-5" noValidate>
              <Field label="Full name" htmlFor="reg-name" required error={errors.name}>
                <Input
                  id="reg-name"
                  value={form.name}
                  onChange={(e) => update("name")(e.target.value)}
                  placeholder="Jordan Rivera"
                  autoComplete="name"
                  aria-invalid={!!errors.name}
                />
              </Field>
              <Field
                label="Work email"
                htmlFor="reg-email"
                required
                error={errors.email}
              >
                <Input
                  id="reg-email"
                  type="email"
                  value={form.email}
                  onChange={(e) => update("email")(e.target.value)}
                  placeholder="you@institution.edu"
                  autoComplete="email"
                  aria-invalid={!!errors.email}
                />
              </Field>
              <Field label="Role" htmlFor="reg-role" required error={errors.role}>
                <Select
                  id="reg-role"
                  value={form.role}
                  onChange={(e) => update("role")(e.target.value)}
                  aria-invalid={!!errors.role}
                >
                  <option value="" disabled>
                    Select your role
                  </option>
                  <option value="reviewer">Loan / scholarship reviewer</option>
                  <option value="admin">Programme administrator</option>
                  <option value="analyst">Data analyst</option>
                </Select>
              </Field>
              <Field
                label="Password"
                htmlFor="reg-password"
                required
                error={errors.password}
                hint="Use at least 8 characters."
              >
                <Input
                  id="reg-password"
                  type="password"
                  value={form.password}
                  onChange={(e) => update("password")(e.target.value)}
                  placeholder="••••••••"
                  autoComplete="new-password"
                  aria-invalid={!!errors.password}
                />
              </Field>

              <Button type="submit" size="lg" disabled={submitting}>
                {submitting ? (
                  <>
                    <Loader2Icon data-icon="inline-start" className="animate-spin" />
                    Creating account…
                  </>
                ) : (
                  <>
                    Create account
                    <ArrowRightIcon data-icon="inline-end" />
                  </>
                )}
              </Button>
            </form>

            <p className="mt-6 text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link
                to="/dashboard"
                className="font-medium text-primary underline-offset-4 hover:underline"
              >
                Go to dashboard
              </Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
