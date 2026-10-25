import React from "react"
import { useAuth } from "@/lib/auth"
import type { UserRole } from "@/types/domain"
import { Button } from "@/components/ui/button"
import { ShieldAlertIcon } from "lucide-react"

interface RoleGuardProps {
  children: React.ReactNode
  allowedRoles: UserRole[]
}

export function RoleGuard({ children, allowedRoles }: RoleGuardProps) {
  const { role, switchRole } = useAuth()

  if (!allowedRoles.includes(role)) {
    // Determine suggested role
    const primaryAllowed = allowedRoles[0]

    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-background">
        <div className="max-w-md w-full border rounded-xl p-6 bg-card text-card-foreground shadow-sm space-y-4 text-center">
          <div className="size-12 mx-auto rounded-full bg-warning/15 flex items-center justify-center text-warning">
            <ShieldAlertIcon className="size-6" />
          </div>
          <h2 className="text-xl font-bold tracking-tight">Access Restricted</h2>
          <p className="text-sm text-muted-foreground">
            This workspace requires the <span className="font-semibold uppercase">{primaryAllowed}</span> role.
            You are currently signed in as <span className="font-semibold uppercase">{role}</span>.
          </p>
          <div className="pt-2 flex flex-col gap-2">
            <Button
              onClick={() => switchRole(primaryAllowed)}
              className="w-full"
            >
              Switch to {primaryAllowed.toUpperCase()} Workspace
            </Button>
            <Button
              variant="outline"
              onClick={() => window.history.back()}
              className="w-full"
            >
              Go Back
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
