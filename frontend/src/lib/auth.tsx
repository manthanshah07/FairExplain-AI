import React, { createContext, useContext, useEffect, useState } from "react"
import type { UserProfile, UserRole } from "@/types/domain"

export const DEMO_PROFILES: Record<UserRole, UserProfile> = {
  student: {
    id: "usr_student_01",
    name: "Priya Sharma",
    email: "priya.sharma@nitk.edu.in",
    role: "student",
    institution: "National Institute of Technology Karnataka",
    department: "Computer Science & Engineering",
  },
  reviewer: {
    id: "usr_reviewer_01",
    name: "Dr. Sarah Jenkins",
    email: "s.jenkins@finaid.edu",
    role: "reviewer",
    institution: "Central Financial Aid Committee",
    department: "Underwriting & Appeals Board",
  },
  admin: {
    id: "usr_admin_01",
    name: "Marcus Vance",
    email: "admin@fairexplain.org",
    role: "admin",
    institution: "Higher Education Financing Authority",
    department: "Algorithm Governance & Policy Office",
  },
}

interface AuthContextType {
  user: UserProfile
  role: UserRole
  isAuthenticated: boolean
  switchRole: (newRole: UserRole) => void
  login: (email: string, role?: UserRole) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const STORAGE_KEY = "fairexplain_auth_role"

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [role, setRole] = useState<UserRole>(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as UserRole
    if (saved && (saved === "student" || saved === "reviewer" || saved === "admin")) {
      return saved
    }
    return "student"
  })

  const [user, setUser] = useState<UserProfile>(DEMO_PROFILES[role])

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, role)
    setUser(DEMO_PROFILES[role])
  }, [role])

  const switchRole = (newRole: UserRole) => {
    setRole(newRole)
    setUser(DEMO_PROFILES[newRole])
  }

  const login = (email: string, selectedRole: UserRole = "student") => {
    setRole(selectedRole)
    setUser({
      ...DEMO_PROFILES[selectedRole],
      email,
      name: email.split("@")[0].replace(".", " "),
    })
  }

  const logout = () => {
    // Return to demo student
    switchRole("student")
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isAuthenticated: true,
        switchRole,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
