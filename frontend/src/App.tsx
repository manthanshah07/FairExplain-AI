import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ThemeProvider } from "@/lib/theme"
import { AuthProvider } from "@/lib/auth"
import { RoleGuard } from "@/components/layout/role-guard"
import { StudentShell } from "@/components/layout/student-shell"
import { ReviewerShell } from "@/components/layout/reviewer-shell"
import { AdminShell } from "@/components/layout/admin-shell"
import { LandingPage } from "@/pages/landing-page"
import { ResultsPage } from "@/pages/results-page"
import { AuthPage } from "@/pages/auth-page"
import { NotFoundPage } from "@/pages/not-found-page"
import { StudentDashboard } from "@/pages/student/student-dashboard"
import { ApplyWizard } from "@/pages/student/apply-wizard"
import { DocumentsPage } from "@/pages/student/documents-page"
import { ReviewQueuePage } from "@/pages/reviewer/review-queue-page"
import { CaseDetailPage } from "@/pages/reviewer/case-detail-page"
import { ReviewHistoryPage } from "@/pages/reviewer/review-history-page"
import { AdminAnalyticsPage } from "@/pages/admin/admin-analytics-page"
import { PolicyViewerPage } from "@/pages/admin/policy-viewer-page"
import { FairnessPage } from "@/pages/admin/fairness-page"
import { AuditPage } from "@/pages/admin/audit-page"

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

              {/* Reviewer Portal */}
              <Route
                path="/reviewer"
                element={
                  <RoleGuard allowedRoles={["reviewer", "admin"]}>
                    <ReviewerShell>
                      <ReviewQueuePage />
                    </ReviewerShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/reviewer/case/:id"
                element={
                  <RoleGuard allowedRoles={["reviewer", "admin"]}>
                    <ReviewerShell>
                      <CaseDetailPage />
                    </ReviewerShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/reviewer/history"
                element={
                  <RoleGuard allowedRoles={["reviewer", "admin"]}>
                    <ReviewerShell>
                      <ReviewHistoryPage />
                    </ReviewerShell>
                  </RoleGuard>
                }
              />

              {/* Admin Portal */}
              <Route
                path="/admin"
                element={
                  <RoleGuard allowedRoles={["admin"]}>
                    <AdminShell>
                      <AdminAnalyticsPage />
                    </AdminShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/admin/policies"
                element={
                  <RoleGuard allowedRoles={["admin"]}>
                    <AdminShell>
                      <PolicyViewerPage />
                    </AdminShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/admin/fairness"
                element={
                  <RoleGuard allowedRoles={["admin"]}>
                    <AdminShell>
                      <FairnessPage />
                    </AdminShell>
                  </RoleGuard>
                }
              />
              <Route
                path="/admin/audit"
                element={
                  <RoleGuard allowedRoles={["admin"]}>
                    <AdminShell>
                      <AuditPage />
                    </AdminShell>
                  </RoleGuard>
                }
              />

              {/* Backwards-compatibility aliases */}
              <Route path="/dashboard" element={<Navigate to="/student" replace />} />
              <Route path="/application" element={<Navigate to="/student/apply" replace />} />
              <Route path="/results" element={<Navigate to="/student/results" replace />} />
              <Route path="/results/:applicationId" element={<ResultsPage />} />
              <Route path="/review" element={<Navigate to="/reviewer" replace />} />

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
