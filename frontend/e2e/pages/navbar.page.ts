import { Page, Locator } from "@playwright/test";

/**
 * Page object for the Navbar component.
 * The navbar is a client-rendered component so elements hydrate after load.
 */
export class NavbarPage {
  constructor() {}

  /** Logo link (links to /) */
  logo(page: Page): Locator {
    return page.getByRole("link", { name: "SpeakNara" }).first();
  }

  /** Table Topics navigation link */
  tableTopicsLink(page: Page): Locator {
    return page.getByRole("link", { name: /Table Topics/i }).first();
  }

  /** Storytelling navigation link */
  storytellingLink(page: Page): Locator {
    return page.getByRole("link", { name: /Storytelling/i }).first();
  }

  /** Impromptu navigation link */
  impromptuLink(page: Page): Locator {
    return page.getByRole("link", { name: /Impromptu/i }).first();
  }

  /** Prepared Speech navigation link */
  preparedSpeechLink(page: Page): Locator {
    return page.getByRole("link", { name: /Prepared Speech/i }).first();
  }

  /** Sign In link (shown when logged out) */
  signInLink(page: Page): Locator {
    return page.getByRole("link", { name: /Sign In/i }).first();
  }

  /** Sign Up link (shown when logged out) */
  signUpLink(page: Page): Locator {
    return page.getByRole("link", { name: /Sign Up/i }).first();
  }

  /** Sign Out button (shown when logged in) */
  signOutButton(page: Page): Locator {
    return page.getByRole("button", { name: /Sign Out/i }).first();
  }

  /** Wait for navbar to hydrate (client component) */
  async waitForHydration(page: Page, timeout = 15000) {
    await page.waitForTimeout(Math.min(timeout, 5000));
    // Wait for at least the logo link to be visible
    await this.logo(page).waitFor({ state: "visible", timeout });
  }
}
