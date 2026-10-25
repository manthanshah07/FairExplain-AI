import { useAuth } from "@/lib/auth"
import type { UserRole } from "@/types/domain"
import { Badge } from "@/components/ui/badge"
import {
  GraduationCapIcon,
  ShieldCheckIcon,
  SlidersHorizontalIcon,
} from "lucide-react"

export function RoleSwitcher() {
  const { role, switchRole, user } = useAuth()

  const roles: Array<{ id: UserRole; label: string; icon: React.ComponentType<{ className?: string }> }> = [
    { id: "student", label: "Student", icon: GraduationCapIcon },
    { id: "reviewer", label: "Reviewer", icon: ShieldCheckIcon },
    { id: "admin", label: "Admin", icon: SlidersHorizontalIcon },
  ]

  return (
    <div className="flex items-center gap-2">
      <div className="hidden lg:flex items-center gap-1 bg-muted/60 p-1 rounded-lg border text-xs">
        {roles.map(({ id, label, icon: Icon }) => {
          const isActive = role === id
          return (
            <button
              key={id}
              onClick={() => switchRole(id)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md font-medium transition-all ${
                isActive
                  ? "bg-card text-foreground shadow-xs font-semibold"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon className="size-3.5" />
              <span>{label}</span>
            </button>
          )
        })}
      </div>

      <div className="lg:hidden">
        <select
          value={role}
          onChange={(e) => switchRole(e.target.value as UserRole)}
          aria-label="Select workspace role"
          className="bg-card border rounded-md text-xs font-medium px-2 py-1 text-foreground"
        >
          <option value="student">Student</option>
          <option value="reviewer">Reviewer</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      <Badge
        variant="outline"
        className="hidden sm:inline-flex text-[11px] font-mono px-2 py-0.5 capitalize text-muted-foreground"
      >
        {user.name.split(" ")[0]}
      </Badge>
    </div>
  )
}
