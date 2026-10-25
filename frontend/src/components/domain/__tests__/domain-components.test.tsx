import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { BrowserRouter } from "react-router-dom"
import { MoneyAmount } from "@/components/domain/money-amount"
import { StatusBadge } from "@/components/domain/status-badge"
import { CriterionRow } from "@/components/domain/criterion-row"
import type { CriterionEvaluationDTO } from "@/types/domain"

describe("MoneyAmount Component", () => {
  it("renders formatted INR string correctly", () => {
    render(<MoneyAmount amount="120000.00" />)
    expect(screen.getByText("₹1,20,000.00")).toBeDefined()
  })

  it("renders ₹0.00 for empty or null amounts", () => {
    render(<MoneyAmount amount={null} />)
    expect(screen.getByText("₹0.00")).toBeDefined()
  })
})

describe("StatusBadge Component", () => {
  it("renders ELIGIBLE badge with positive styling and semantic text", () => {
    render(<StatusBadge status="ELIGIBLE" />)
    expect(screen.getByText("Recommended Eligible")).toBeDefined()
  })

  it("renders INELIGIBLE badge with explicit non-award label", () => {
    render(<StatusBadge status="INELIGIBLE" />)
    expect(screen.getByText("Recommended Ineligible")).toBeDefined()
  })

  it("renders PENDING_EVIDENCE badge distinctly from ineligible", () => {
    render(<StatusBadge status="PENDING_EVIDENCE" />)
    expect(screen.getByText("Awaiting Evidence")).toBeDefined()
  })
})

describe("CriterionRow Component", () => {
  const sampleCriterion: CriterionEvaluationDTO = {
    criterion_id: "CRIT-001",
    attribute: "cgpa",
    operator: "gte",
    target_value: "7.5",
    actual_value: "8.8",
    status: "satisfied",
    is_mandatory: true,
    evidence_required: "marksheet",
    evidence_status: "verified",
    reason: "Student CGPA meets academic excellence threshold",
  }

  it("renders criterion with plain English operator, target, and mandatory badge", () => {
    render(
      <BrowserRouter>
        <CriterionRow criterion={sampleCriterion} />
      </BrowserRouter>
    )

    expect(screen.getByText("cgpa")).toBeDefined()
    expect(screen.getByText("Mandatory")).toBeDefined()
    expect(screen.getByText(/at least/i)).toBeDefined()
    expect(screen.getByText(/8.8/)).toBeDefined()
  })

  it("renders pending evidence call to action when evidence is missing", () => {
    const pendingCriterion: CriterionEvaluationDTO = {
      ...sampleCriterion,
      status: "pending_evidence",
      evidence_status: "missing",
    }

    render(
      <BrowserRouter>
        <CriterionRow criterion={pendingCriterion} applicationId="app-123" />
      </BrowserRouter>
    )

    expect(screen.getByText(/Awaiting Evidence/i)).toBeDefined()
  })
})
