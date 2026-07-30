import { Brand } from "@/components/brand"

export function SiteFooter() {
  return (
    <footer className="border-t border-border/70 bg-card/40">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-10 sm:px-6 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-col gap-3">
          <Brand />
          <p className="max-w-sm text-sm leading-relaxed text-muted-foreground">
            An explainable AI platform for scholarship and education-loan
            decisions. The AI recommends — humans decide.
          </p>
        </div>
        <p className="text-xs text-muted-foreground">
          {"\u00A9"} {new Date().getFullYear()} FairExplain AI. Built for
          transparent, human-reviewed outcomes.
        </p>
      </div>
    </footer>
  )
}
