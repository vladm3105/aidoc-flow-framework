# Architecture & Operational Standard: End-to-End Browser Testing & Visual Verification

**Status:** Approved · **Date:** [YYYY-MM-DD]
**Scope:** Browser Automation, Visual Regression & Headless Testing for `[Project Name]`
**Governing Rules:** `GOVERNANCE_WORKFLOW_STANDARD.md`, `BDD_WORKFLOW_STANDARD.md`, `TDD_WORKFLOW_STANDARD.md`
**Canonical Template:** `framework/governance/aidoc/AIDOC-BROWSER-TESTING-TEMPLATE.md`

---

## 1. Purpose & Scope

Full-stack applications require automated verification of the client-side user experience across modern browsers (Chromium, Firefox, WebKit). Browser automation verifies interactive state transitions, client-side rendering, responsive layouts, accessibility tree attributes, and visual styling.

This standard establishes the **Headless Browser Execution Protocol**, **Port & Container Sandboxing**, and **Artifact Capture Standards**.

---

## 2. Browser Automation Architecture (Playwright Reference)

Browser tests execute in headless mode within local worktrees and CI runners:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Headless Test Runner (Playwright / Chromium Engine)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Launch Browser Context with Fixed Viewport (1280x720)                    │
│ 2. Trace & Video Recording Active (retained on failure)                     │
│ 3. Intercept & Route Network Requests (Real backend, zero fake mocks)        │
│ 4. Execute User Actions (click, fill, navigate, await networkidle)          │
│ 5. Assert Semantic Elements & Accessibility Selectors (getByRole, getByTestId)│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Multi-Worktree Port & Container Sandboxing

When multiple browser test suites execute concurrently across separate git worktrees, hardcoded localhost ports (e.g. `:3000`, `:8080`) cause immediate failure. Projects MUST implement dynamic port sandboxing:

1. **Port Offsets:** Read environment variable `BASE_PORT_OFFSET` or generate a deterministic port from the worktree hash:
   ```bash
   export APP_PORT=3045
   export DB_PORT=5477
   ```
2. **Container Project Isolation:** Prepend worktree slug to Docker Compose project names:
   ```bash
   docker compose -p "app-${WORKTREE_SLUG}" up -d
   ```
3. **Dedicated Base URL:** Configure Playwright `baseURL` dynamically using `http://127.0.0.1:${APP_PORT}`.

---

## 4. Diagnostic Artifact Collection (Traces, Screenshots & Logs)

To enable rapid diagnosis without human re-runs, browser runners MUST configure automatic artifact retention upon failure:

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    baseURL: process.env.APP_BASE_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  outputDir: 'artifacts/test-results/',
});
```

When a test fails:
1. Playwright preserves the `.zip` trace archive and video in `artifacts/test-results/`.
2. The QA agent attaches trace links or extracts frame screenshots into the defect report.
3. Traces can be inspected locally via `npx playwright show-trace artifacts/test-results/<trace>.zip`.

---

## 5. Non-Negotiable Browser Testing Invariants

1. **Zero Flaky Timeouts:** Never use arbitrary sleep calls (e.g. `page.waitForTimeout(5000)`). Always await explicit UI element states (e.g. `page.waitForSelector('[data-testid="checkout-complete"]')` or `page.waitForLoadState('networkidle')`).
2. **Accessible Locators First:** Prefer user-facing locators (`page.getByRole()`, `page.getByLabel()`, `page.getByText()`) over fragile CSS or XPath selectors.
3. **Clean Teardown:** Every test suite must guarantee browser context closure and container termination upon suite conclusion or interruption.
