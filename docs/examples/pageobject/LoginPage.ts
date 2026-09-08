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

// The FEAT-001 entity is `active` (delivered), but this *surface* is `candidate`:
// the login template has no test-id attributes yet. Locators and the promotion to
// `status: active` (dropping stub-reason) follow once it is instrumented.
export class LoginPage {
  constructor(private readonly page: import("@playwright/test").Page) {}

  async goto(): Promise<void> {
    await this.page.goto("/login");
  }
}
