import { BrowserRouter, Routes, Route } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ThemeProvider } from "@/lib/theme"
import { AuthProvider } from "@/lib/auth"
import { LandingPage } from "@/pages/landing-page"
import { ResultsPage } from "@/pages/results-page"
import { AuthPage } from "@/pages/auth-page"
import { ApplyPage } from "@/pages/apply-page"
import { DashboardPage } from "@/pages/dashboard-page"
import { ReviewPage } from "@/pages/review-page"
import { NotFoundPage } from "@/pages/not-found-page"

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
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<AuthPage />} />
              <Route path="/register" element={<AuthPage />} />
              <Route path="/application" element={<ApplyPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/review" element={<ReviewPage />} />
              <Route path="/results" element={<ResultsPage />} />
              <Route path="/results/:applicationId" element={<ResultsPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
