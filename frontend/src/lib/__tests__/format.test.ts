import { describe, it, expect } from "vitest"
import { formatINR, formatCompactINR, formatOperator } from "@/lib/format"

describe("formatINR", () => {
  it("formats decimal strings with Indian digit grouping and currency symbol", () => {
    expect(formatINR("120000.00")).toBe("₹1,20,000.00")
    expect(formatINR("65000.00")).toBe("₹65,000.00")
    expect(formatINR("1000000.00")).toBe("₹10,00,000.00")
  })

  it("handles numbers without floats", () => {
    expect(formatINR(50000)).toBe("₹50,000.00")
    expect(formatINR(0)).toBe("₹0.00")
  })

  it("handles zero, null, and empty string safely", () => {
    expect(formatINR(null)).toBe("₹0.00")
    expect(formatINR(undefined)).toBe("₹0.00")
    expect(formatINR("")).toBe("₹0.00")
  })

  it("hides currency symbol when requested", () => {
    expect(formatINR("125000.00", false)).toBe("1,25,000.00")
  })
})

describe("formatCompactINR", () => {
  it("compacts large values into Lakhs and Crores", () => {
    expect(formatCompactINR("1500000")).toBe("₹15.0L")
    expect(formatCompactINR("20000000")).toBe("₹2.0 Cr")
    expect(formatCompactINR("45000")).toBe("₹45K")
  })
})

describe("formatOperator", () => {
  it("translates code operators into plain English", () => {
    expect(formatOperator("gte")).toBe("at least")
    expect(formatOperator("lte")).toBe("at most")
    expect(formatOperator("eq")).toBe("must equal")
    expect(formatOperator("in")).toBe("is one of")
    expect(formatOperator("neq")).toBe("must not equal")
  })
})
