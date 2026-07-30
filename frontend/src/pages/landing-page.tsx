import { SiteHeader } from "@/components/layout/site-header"
import { SiteFooter } from "@/components/layout/site-footer"
import { HeroSection } from "@/components/landing/hero-section"
import { HowItWorksSection } from "@/components/landing/how-it-works-section"
import { PrinciplesSection } from "@/components/landing/principles-section"
import { CtaSection } from "@/components/landing/cta-section"

export function LandingPage() {
  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <main className="flex-1">
        <HeroSection />
        <HowItWorksSection />
        <PrinciplesSection />
        <CtaSection />
      </main>
      <SiteFooter />
    </div>
  )
}
