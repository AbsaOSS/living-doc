/* =============================================================================
 * LIVING DOC — FEAT-001 · Login Page
 * =============================================================================
 * surface_type:          UI
 * route:                 /login
 * owners:                Identity Team
 * status:                candidate
 * stub-reason:           Login template carries no test-id attributes yet; surface
 *                        documented from the interface spec. discovered 2026-09-08
 * purpose:               Screen where a registered customer enters an email and password to sign in.
 * user_stories:          US-001
 * functionalities:       FUNC-001
 * external_dependencies: auth-api
 * page-object:           LoginPage.ts
 * ============================================================================= */

// Minimal PageObject body. Locators are added once the template is instrumented
// (status: candidate -> active, and stub-reason removed at that point).
export class LoginPage {
  constructor(private readonly page: import("@playwright/test").Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/login");
  }
}
