import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ThemeProvider } from "@/lib/theme"
import { LandingPage } from "@/pages/landing-page"
import { ResultsPage } from "@/pages/results-page"

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/results/:applicationId" element={<ResultsPage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
