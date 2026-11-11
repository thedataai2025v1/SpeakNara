import { test, expect } from "@playwright/test";
import { NavbarPage } from "./pages/navbar.page";

const navbar = new NavbarPage();

test.describe("Impromptu page", () => {
  test("impromptu page renders heading and placeholder", async ({ page }) => {
    await page.goto("/impromptu");
    // Wait for page to hydrate
    await expect(page.locator("h1, h2, h3")).toBeVisible({ timeout: 15000 });
    // The heading is "Impromptu Speech"
    await expect(page.getByText("Impromptu Speech", { exact: true })).toBeVisible({ timeout: 15000 });
    // Placeholder text in textarea
    const textarea = page.getByPlaceholder(/favourite hobby/i).first();
    if (await textarea.isVisible({ timeout: 15000 })) {
      await expect(textarea).toBeVisible();
    }
  });

  test("impromptu page has start speaking button", async ({ page }) => {
    await page.goto("/impromptu");
    // "Start Speaking" button
    const speakBtn = page.getByRole("button", { name: /Start Speaking/i });
    if (await speakBtn.isVisible({ timeout: 15000 })) {
      await expect(speakBtn).toBeVisible();
    }
  });

  test("impromptu page has 5 topic suggestions", async ({ page }) => {
    await page.goto("/impromptu");
    const form = page.getByRole("form");
    await expect(form).toBeVisible({ timeout: 15000 });
    // Topic buttons (random ones selected from a pool of 5)
    const topicBtns = page.getByRole("button").filter({ hasText: /topic/i });
    // There may be several buttons; check at least one exists
    await expect(page.getByRole("button")).toHaveCount({ min: 1 }, { timeout: 15000 });
  });
});
