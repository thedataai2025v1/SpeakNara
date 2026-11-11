import { test, expect } from "@playwright/test";
import { NavbarPage } from "./pages/navbar.page";

const navbar = new NavbarPage();

test.describe("Home page", () => {
  test("home page loads", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/SpeakNara/);
    // Wait for navbar to hydrate
    await navbar.waitForHydration(page, 15000);
  });

  test("home page shows SpeakNara heading", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("SpeakNara", { exact: true })).toBeVisible({ timeout: 15000 });
  });

  test("home page has navigation links", async ({ page }) => {
    await page.goto("/");
    await navbar.waitForHydration(page, 15000);
    // Links to Sign In / Register should be on the page (navbar or home page)
    const signIn = page.getByRole("link", { name: /Sign In/i }).first();
    await expect(signIn).toBeVisible({ timeout: 15000 });
    const register = page.getByRole("link", { name: /Register|Sign Up/i }).first();
    await expect(register).toBeVisible({ timeout: 15000 });
  });
});
