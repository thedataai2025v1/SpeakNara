import { test, expect } from "@playwright/test";
import { NavbarPage } from "./pages/navbar.page";

const navbar = new NavbarPage();

test.describe("History page", () => {
  test("history page renders heading", async ({ page }) => {
    await page.goto("/history");
    // Wait for page to hydrate
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
    // The heading is "Your Speaking Sessions"
    await expect(page.getByText("Your Speaking Sessions", { exact: true })).toBeVisible({ timeout: 15000 });
  });
});
