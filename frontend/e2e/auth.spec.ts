import { test, expect } from "@playwright/test";
import { NavbarPage } from "./pages/navbar.page";

const navbar = new NavbarPage();

test.describe("Auth pages", () => {
  test("login page renders sign in form", async ({ page }) => {
    await page.goto("/login");
    // Wait for page to hydrate
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
    // The heading is "Sign In"
    await expect(page.getByText("Sign In", { exact: true })).toBeVisible({ timeout: 15000 });
    // Form with email and password inputs
    const form = page.getByRole("form");
    await expect(form).toBeVisible({ timeout: 15000 });
    const emailInput = page.getByLabel(/email/i).first();
    await expect(emailInput).toBeVisible({ timeout: 15000 });
    const passwordInput = page.getByLabel(/password/i).first();
    await expect(passwordInput).toBeVisible({ timeout: 15000 });
  });

  test("register page renders register form", async ({ page }) => {
    await page.goto("/register");
    // Wait for page to hydrate
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
    // The heading is "Register"
    await expect(page.getByText("Register", { exact: true })).toBeVisible({ timeout: 15000 });
    // Form with email and password inputs
    const form = page.getByRole("form");
    await expect(form).toBeVisible({ timeout: 15000 });
    const emailInput = page.getByLabel(/email/i).first();
    await expect(emailInput).toBeVisible({ timeout: 15000 });
    const passwordInput = page.getByLabel(/password/i).first();
    await expect(passwordInput).toBeVisible({ timeout: 15000 });
  });
});
