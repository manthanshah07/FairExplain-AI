interface SkeletonCardProps {
  className?: string
  lines?: number
}

export function SkeletonCard({ className = "", lines = 3 }: SkeletonCardProps) {
  return (
    <div
      className={`rounded-2xl border border-border bg-card p-6 space-y-4 animate-pulse ${className}`}
    >
      <div className="flex items-center justify-between">
        <div className="h-5 w-1/3 bg-muted rounded-md" />
        <div className="h-5 w-20 bg-muted rounded-full" />
      </div>
      <div className="space-y-2 pt-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className="h-4 bg-muted/70 rounded-md"
            style={{ width: `${100 - i * 15}%` }}
          />
        ))}
      </div>
    </div>
  )
}
