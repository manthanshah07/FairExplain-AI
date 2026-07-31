import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { zodResolver } from "@/lib/resolver"
import { useSubmitApplication } from "@/hooks/use-application"
import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

const applySchema = z.object({
  cgpa: z.coerce.number().min(0).max(10, "CGPA must be between 0 and 10"),
  tenth: z.coerce.number().min(0).max(100, "Percentage must be between 0 and 100"),
  twelfth: z.coerce.number().min(0).max(100, "Percentage must be between 0 and 100"),
  backlogs: z.coerce.number().min(0, "Cannot be negative"),
  income: z.coerce.number().min(0),
  emi: z.coerce.number().min(0),
  tuition: z.coerce.number().min(0),
  loan: z.coerce.number().min(0),
})

type ApplyFormValues = z.infer<typeof applySchema>

export function ApplyPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("academic")
  const { mutateAsync: submitApp, isPending } = useSubmitApplication()

  const { register, handleSubmit, formState: { errors } } = useForm<ApplyFormValues>({
    resolver: zodResolver(applySchema),
  })

  const onSubmit = async (data: ApplyFormValues) => {
    try {
      const result = await submitApp(data)
      navigate(`/results/${result.applicationId}`)
    } catch (error) {
      console.error("Submission failed", error)
    }
  }
  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1 px-4 py-8 sm:px-6 md:py-12">
        <div className="mx-auto max-w-3xl">
          <div className="mb-8 space-y-2">
            <h1 className="text-3xl font-bold tracking-tight">Application Form</h1>
            <p className="text-muted-foreground">
              Please provide your academic and financial details, and upload the required documents.
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)}>
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="academic">1. Academic Profile</TabsTrigger>
                <TabsTrigger value="financial">2. Financial Profile</TabsTrigger>
                <TabsTrigger value="documents">3. Documents</TabsTrigger>
              </TabsList>
            
            <TabsContent value="academic" className="mt-6 rounded-xl border bg-card/40 p-6 shadow-sm">
              <div className="grid gap-6 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="cgpa">CGPA (0-10)</Label>
                  <Input id="cgpa" type="number" step="0.1" placeholder="e.g. 8.5" {...register("cgpa")} />
                  {errors.cgpa && <p className="text-xs text-destructive">{errors.cgpa.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tenth">10th %</Label>
                  <Input id="tenth" type="number" step="0.1" placeholder="e.g. 85.0" {...register("tenth")} />
                  {errors.tenth && <p className="text-xs text-destructive">{errors.tenth.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="twelfth">12th %</Label>
                  <Input id="twelfth" type="number" step="0.1" placeholder="e.g. 88.5" {...register("twelfth")} />
                  {errors.twelfth && <p className="text-xs text-destructive">{errors.twelfth.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="backlogs">Active Backlogs</Label>
                  <Input id="backlogs" type="number" placeholder="e.g. 0" {...register("backlogs")} />
                  {errors.backlogs && <p className="text-xs text-destructive">{errors.backlogs.message}</p>}
                </div>
              </div>
              <div className="mt-8 flex justify-end">
                <Button type="button" onClick={() => setActiveTab("financial")}>Next: Financial Details</Button>
              </div>
            </TabsContent>

            <TabsContent value="financial" className="mt-6 rounded-xl border bg-card/40 p-6 shadow-sm">
              <div className="grid gap-6 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="income">Household Income (INR/year)</Label>
                  <Input id="income" type="number" placeholder="e.g. 500000" {...register("income")} />
                  {errors.income && <p className="text-xs text-destructive">{errors.income.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="emi">Existing EMI (INR/month)</Label>
                  <Input id="emi" type="number" placeholder="e.g. 5000" {...register("emi")} />
                  {errors.emi && <p className="text-xs text-destructive">{errors.emi.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tuition">Tuition Fee (INR/year)</Label>
                  <Input id="tuition" type="number" placeholder="e.g. 200000" {...register("tuition")} />
                  {errors.tuition && <p className="text-xs text-destructive">{errors.tuition.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="loan">Requested Loan (INR)</Label>
                  <Input id="loan" type="number" placeholder="e.g. 400000" {...register("loan")} />
                  {errors.loan && <p className="text-xs text-destructive">{errors.loan.message}</p>}
                </div>
              </div>
              <div className="mt-8 flex justify-between">
                <Button type="button" variant="outline" onClick={() => setActiveTab("academic")}>Back</Button>
                <Button type="button" onClick={() => setActiveTab("documents")}>Next: Documents</Button>
              </div>
            </TabsContent>

            <TabsContent value="documents" className="mt-6 rounded-xl border bg-card/40 p-6 shadow-sm">
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="marksheet">Marksheets (PDF/Image)</Label>
                  <Input id="marksheet" type="file" multiple />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="income-proof">Income Proof (PDF/Image)</Label>
                  <Input id="income-proof" type="file" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="id-proof">ID Proof (PDF/Image)</Label>
                  <Input id="id-proof" type="file" />
                </div>
              </div>
              <div className="mt-8 flex justify-between">
                <Button type="button" variant="outline" onClick={() => setActiveTab("financial")}>Back</Button>
                <Button type="submit" disabled={isPending}>{isPending ? "Submitting..." : "Submit Application"}</Button>
              </div>
            </TabsContent>
          </Tabs>
         </form>
        </div>
      </main>
      <SiteFooter />
    </div>
  )
}
