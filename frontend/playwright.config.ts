import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright e2e test configuration for SpeakNara frontend.
 *
 * Runs against the Next.js dev server on http://localhost:3000.
 * The backend (FastAPI) should be running on http://localhost:8000.
 *
 * Usage:
 *   npx playwright test                      # run all tests in Chromium (headed)
 *   npx playwright test --project=firefox    # run in Firefox
 *   npx playwright test --ui                 # open Playwright UI mode
 *   npx playwright test --headed             # run headed
 *   npx playwright test --project=chromium home.spec.ts  # run specific file
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Run your local dev server before the tests.
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
