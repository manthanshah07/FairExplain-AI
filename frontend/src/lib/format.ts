/**
 * FairExplain AI — Precision Formatting Utilities
 * ================================================
 * Pure formatting utilities honoring domain rules:
 * - Money values formatted with Indian numbering system (₹1,20,000.00) without float arithmetic.
 * - Operator translation into plain English phrases ("at least", "must equal").
 * - Cryptographic hash and version truncation.
 */

/**
 * Format an exact decimal string or number into Indian Rupee format (₹1,20,000.00).
 * Does NOT perform float arithmetic; operates strictly on integer/fraction string components.
 */
export function formatINR(val: string | number | null | undefined, showSymbol: boolean = true): string {
  if (val === null || val === undefined || val === "") {
    return showSymbol ? "₹0.00" : "0.00"
  }

  const str = String(val).trim()
  const isNegative = str.startsWith("-")
  const cleanStr = isNegative ? str.slice(1) : str

  // Split into integer and fractional parts
  const parts = cleanStr.split(".")
  let intPart = parts[0] || "0"
  let fracPart = parts[1] || "00"

  // Pad or trim fractional part to 2 decimals
  if (fracPart.length < 2) {
    fracPart = fracPart.padEnd(2, "0")
  } else if (fracPart.length > 2) {
    fracPart = fracPart.slice(0, 2)
  }

  // Remove leading zeros from integer part
  intPart = intPart.replace(/^0+(?=\d)/, "")

  // Indian number grouping: last 3 digits, then groups of 2
  // e.g., 1234567 -> 12,34,567
  let formattedInt = ""
  if (intPart.length <= 3) {
    formattedInt = intPart
  } else {
    const lastThree = intPart.slice(-3)
    const otherDigits = intPart.slice(0, -3)
    const groupedOther = otherDigits.replace(/\B(?=(\d{2})+(?!\d))/g, ",")
    formattedInt = `${groupedOther},${lastThree}`
  }

  const formatted = `${formattedInt}.${fracPart}`
  const prefix = isNegative ? "-" : ""
  return showSymbol ? `${prefix}₹${formatted}` : `${prefix}${formatted}`
}

/**
 * Compact Indian currency formatting for charts and badges (e.g. ₹1.2L, ₹50K).
 */
export function formatCompactINR(val: string | number | null | undefined): string {
  if (!val) return "₹0"
  const num = typeof val === "string" ? parseFloat(val) : val
  if (isNaN(num)) return "₹0"

  const abs = Math.abs(num)
  const sign = num < 0 ? "-" : ""

  if (abs >= 10000000) {
    return `${sign}₹${(abs / 10000000).toFixed(1)} Cr`
  }
  if (abs >= 100000) {
    return `${sign}₹${(abs / 100000).toFixed(1)}L`
  }
  if (abs >= 1000) {
    return `${sign}₹${(abs / 1000).toFixed(0)}K`
  }
  return `${sign}₹${abs.toFixed(0)}`
}

/**
 * Human-readable operator descriptions per Section 3:
 * Show operators in words ("at least", "must equal", "is one of").
 */
export function formatOperator(op: string): string {
  const norm = op.trim().toLowerCase()
  switch (norm) {
    case "gte":
    case ">=":
      return "at least"
    case "gt":
    case ">":
      return "greater than"
    case "lte":
    case "<=":
      return "at most"
    case "lt":
    case "<":
      return "less than"
    case "eq":
    case "==":
    case "=":
      return "must equal"
    case "neq":
    case "!=":
      return "must not equal"
    case "in":
      return "is one of"
    case "not_in":
      return "is not one of"
    default:
      return op
  }
}

/**
 * Format an ISO timestamp for display.
 */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—"
  try {
    const d = new Date(iso)
    return d.toLocaleString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  } catch {
    return iso
  }
}

/**
 * Truncate SHA256 hashes or UUIDs for clean monospace chips.
 */
export function truncateHash(hash: string | null | undefined, length: number = 8): string {
  if (!hash) return "—"
  if (hash.length <= length * 2) return hash
  return `${hash.slice(0, length)}...${hash.slice(-length)}`
}
