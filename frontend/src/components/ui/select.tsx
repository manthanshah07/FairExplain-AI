import * as React from "react"
import { ChevronsUpDownIcon } from "lucide-react"

import { cn } from "@/lib/utils"

function Select({ className, children, ...props }: React.ComponentProps<"select">) {
  return (
    <div className="relative w-full">
      <select
        data-slot="select"
        className={cn(
          "flex h-9 w-full appearance-none rounded-lg border border-input bg-background px-3 pr-9 text-sm text-foreground shadow-xs transition-[color,box-shadow] outline-none",
          "focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/30",
          "disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50",
          "aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20",
          "dark:bg-input/30",
          className
        )}
        {...props}
      >
        {children}
      </select>
      <ChevronsUpDownIcon
        className="pointer-events-none absolute top-1/2 right-3 size-3.5 -translate-y-1/2 text-muted-foreground"
        aria-hidden="true"
      />
    </div>
  )
}

export { Select }
