import { test, expect } from "@playwright/test";
import { NavbarPage } from "./pages/navbar.page";

const navbar = new NavbarPage();

test.describe("Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("navigate to table-topics page", async ({ page }) => {
    await page.getByRole("link", { name: /Table Topics/i }).first().click();
    await expect(page).toHaveURL(/.*table-topics/);
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
  });

  test("navigate to storytelling page", async ({ page }) => {
    await page.getByRole("link", { name: /Storytelling/i }).first().click();
    await expect(page).toHaveURL(/.*storytelling/);
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
  });

  test("navigate to impromptu page", async ({ page }) => {
    await page.getByRole("link", { name: /Impromptu/i }).first().click();
    await expect(page).toHaveURL(/.*impromptu/);
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
  });

  test("navigate to prepared-speech page", async ({ page }) => {
    await page.getByRole("link", { name: /Prepared Speech/i }).first().click();
    await expect(page).toHaveURL(/.*prepared-speech/);
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
  });

  test("navigate to youtube page", async ({ page }) => {
    // YouTube link may not be in the navbar; navigate directly
    await page.goto("/youtube");
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
  });

  test("navigate to history page", async ({ page }) => {
    // History link may not be in the navbar; navigate directly
    await page.goto("/history");
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
  });
});
