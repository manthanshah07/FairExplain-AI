/**
 * FairExplain AI — Client Environment & Configuration
 * ====================================================
 * Typed configuration driven by Vite import.meta.env with safe defaults.
 */

export interface AppConfig {
  apiBaseUrl: string
  useMocks: boolean
  featureLoan: boolean
  appVersion: string
  appName: string
}

export const env: AppConfig = {
  apiBaseUrl: (import.meta.env.VITE_API_BASE_URL as string) || "http://localhost:8000",
  useMocks: (import.meta.env.VITE_USE_MOCKS as string) === "true",
  featureLoan: (import.meta.env.VITE_FEATURE_LOAN as string) !== "false", // default enabled
  appVersion: "1.0.0",
  appName: "FairExplain AI",
}
