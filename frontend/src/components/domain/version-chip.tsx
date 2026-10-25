import { useState } from "react"
import { CheckIcon, CopyIcon, GitCommitIcon } from "lucide-react"

interface VersionChipProps {
  label?: string
  value: string
  type?: "version" | "hash" | "engine"
  copyable?: boolean
  className?: string
}

export function VersionChip({
  label,
  value,
  type = "version",
  copyable = true,
  className = "",
}: VersionChipProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    if (!copyable) return
    navigator.clipboard.writeText(value)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  const isHash = type === "hash" || value.length > 20
  const displayValue = isHash ? `${value.slice(0, 8)}...${value.slice(-6)}` : value

  return (
    <div
      onClick={handleCopy}
      title={copyable ? `Click to copy full ${label || value}` : undefined}
      className={`inline-flex items-center gap-1.5 rounded-md border border-border/70 bg-muted/40 px-2 py-0.5 text-[11px] font-mono text-muted-foreground transition-colors ${
        copyable ? "cursor-pointer hover:bg-muted hover:text-foreground" : ""
      } ${className}`}
    >
      <GitCommitIcon className="size-3 text-primary shrink-0" />
      {label && <span className="font-sans font-medium text-foreground">{label}:</span>}
      <span className="font-semibold text-foreground/90">{displayValue}</span>
      {copyable && (
        <span className="ml-0.5 text-muted-foreground/60 hover:text-foreground">
          {copied ? <CheckIcon className="size-3 text-emerald-500" /> : <CopyIcon className="size-3" />}
        </span>
      )}
    </div>
  )
}
