import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ThemeProvider } from "@/lib/theme"
import { AuthProvider } from "@/lib/auth"
import { RoleGuard } from "@/components/layout/role-guard"
import { StudentShell } from "@/components/layout/student-shell"
import { LandingPage } from "@/pages/landing-page"
import { ResultsPage } from "@/pages/results-page"
import { AuthPage } from "@/pages/auth-page"
import { ReviewPage } from "@/pages/review-page"
import { NotFoundPage } from "@/pages/not-found-page"
import { StudentDashboard } from "@/pages/student/student-dashboard"
import { ApplyWizard } from "@/pages/student/apply-wizard"
import { DocumentsPage } from "@/pages/student/documents-page"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<AuthPage />} />
              <Route path="/register" element={<AuthPage />} />

              {/* Student Portal */}
              <Route
                path="/student"
                element={
                  <RoleGuard allowedRoles={["student"]}>
                    <StudentShell>
                      <StudentDashboard />
                    </StudentShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/student/apply"
                element={
                  <RoleGuard allowedRoles={["student"]}>
                    <StudentShell>
                      <ApplyWizard />
                    </StudentShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/student/documents"
                element={
                  <RoleGuard allowedRoles={["student"]}>
                    <StudentShell>
                      <DocumentsPage />
                    </StudentShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/student/results"
                element={
                  <RoleGuard allowedRoles={["student", "reviewer", "admin"]}>
                    <StudentShell>
                      <ResultsPage />
                    </StudentShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/student/results/:applicationId"
                element={
                  <RoleGuard allowedRoles={["student", "reviewer", "admin"]}>
                    <StudentShell>
                      <ResultsPage />
                    </StudentShell>
                  </RoleGuard>
                }
              />

              {/* Backwards-compatibility aliases */}
              <Route path="/dashboard" element={<Navigate to="/student" replace />} />
              <Route path="/application" element={<Navigate to="/student/apply" replace />} />
              <Route path="/results" element={<Navigate to="/student/results" replace />} />
              <Route path="/results/:applicationId" element={<ResultsPage />} />
              <Route path="/review" element={<ReviewPage />} />

              {/* 404 */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
