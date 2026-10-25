import { formatINR } from "@/lib/format"

interface MoneyAmountProps {
  amount: string | number | null | undefined
  size?: "sm" | "md" | "lg" | "xl" | "hero"
  className?: string
  hint?: string
  showCurrency?: boolean
  trend?: "positive" | "negative" | "neutral"
}

export function MoneyAmount({
  amount,
  size = "md",
  className = "",
  hint,
  showCurrency = true,
  trend = "neutral",
}: MoneyAmountProps) {
  const formatted = formatINR(amount, showCurrency)

  const sizeClasses = {
    sm: "text-xs font-medium",
    md: "text-sm font-semibold",
    lg: "text-lg font-bold",
    xl: "text-2xl font-bold tracking-tight",
    hero: "text-3xl sm:text-4xl font-extrabold tracking-tight",
  }

  const trendClasses = {
    positive: "text-emerald-600 dark:text-emerald-400",
    negative: "text-rose-600 dark:text-rose-400",
    neutral: "text-foreground",
  }

  return (
    <div className={`inline-flex items-baseline gap-1.5 ${className}`}>
      <span className={`tabular-nums font-mono ${sizeClasses[size]} ${trendClasses[trend]}`}>
        {formatted}
      </span>
      {hint && (
        <span className="text-xs text-muted-foreground font-sans line-through opacity-80">
          {hint}
        </span>
      )}
    </div>
  )
}
