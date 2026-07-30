import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ThemeProvider } from "@/lib/theme"
import { LandingPage } from "@/pages/landing-page"
import { ResultsPage } from "@/pages/results-page"
import { DashboardPage } from "@/pages/dashboard-page"
import { ApplyPage } from "@/pages/apply-page"
import { RegisterPage } from "@/pages/register-page"
import { ReviewPage } from "@/pages/review-page"
import { NotFoundPage } from "@/pages/not-found-page"

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/apply" element={<ApplyPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/results/:applicationId" element={<ResultsPage />} />
          <Route path="/review/:applicationId" element={<ReviewPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
