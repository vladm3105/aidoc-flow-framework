# Architecture & Operational Standard: CI Smart Routing & Anti-Deadlock Protocol

**Status:** Approved · **Date:** [YYYY-MM-DD]
**Scope:** Continuous Integration & Status Check Orchestration for `[Project Name]`
**Governing Rules:** `CI_AUTONOMOUS_PR_STANDARD.md`, `GOVERNANCE_WORKFLOW_STANDARD.md`
**Canonical Template:** `framework/governance/aidoc/AIDOC-CI-SMART-ROUTING-TEMPLATE.md`

---

## 1. Purpose & Motivation

In autonomous pull-request workflows, required status checks gate pull request merges. A frequent and fatal failure mode in CI configuration is placing path-filtering directives (such as `paths:` or `paths-ignore:`) at the workflow trigger level. When a PR modifies only documentation, governance, or assets, a workflow with trigger-level filtering never triggers; consequently, GitHub/GitLab marks the required check as pending forever, deadlocking autonomous auto-merge.

This standard establishes the **Anti-Deadlock Invariant** and **Internal Smart Routing Architecture**: workflows trigger unconditionally on every push/PR, while internal jobs detect changed paths to execute heavy suites conditionally and emit clean green status for unaffected paths.

---

## 2. Core Invariants

1. **Anti-Deadlock Invariant (HARD BLOCK):** Required CI status checks MUST trigger on every push and pull request targeting integration branches (`dev`, `main`). Workflow definitions MUST NEVER declare top-level `paths:` or `paths-ignore:` trigger filters.
2. **Internal Smart Routing:** Path-based optimization MUST execute inside the workflow via dedicated change-detection jobs (e.g., `dorny/paths-filter`, `git diff`, or task runners).
3. **Fail-Closed Change Detection:** If the change-detection step fails, produces indeterminate output, or encounters unexpected git states, all test suites MUST execute by default.
4. **Concentric Latency Budgets:**
   - Pre-flight / Static Analysis (formatting, linting, secrets): < 15 seconds.
   - Core Unit & Schema Tests: < 45 seconds.
   - Comprehensive Integration & Acceptance Suites: 2 to 4 minutes.
5. **Zero-Mock Rule:** Integration test jobs MUST execute against authentic containerized services (PostgreSQL, Redis, MinIO) rather than synthetic in-memory mock frameworks.

---

## 3. Reference Workflow Implementation (GitHub Actions)

```yaml
name: CI Suite

on:
  pull_request:
    branches: [dev, main]
  push:
    branches: [dev, main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  changes:
    name: Change Detection
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
      docs: ${{ steps.filter.outputs.docs }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'src/backend/**'
              - 'migrations/**'
              - 'go.mod'
              - 'go.sum'
            frontend:
              - 'src/frontend/**'
              - 'package.json'
              - 'pnpm-lock.yaml'
            docs:
              - 'docs/**'
              - 'seed/**'
              - '*.md'

  backend-tests:
    name: Backend Test Suite
    needs: changes
    runs-on: ubuntu-latest
    if: ${{ needs.changes.outputs.backend == 'true' || github.event_name == 'push' }}
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Setup Go
        uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'
      - name: Run Unit & Integration Tests
        run: |
          go test -v -race -cover ./...

  frontend-tests:
    name: Frontend Test Suite
    needs: changes
    runs-on: ubuntu-latest
    if: ${{ needs.changes.outputs.frontend == 'true' || github.event_name == 'push' }}
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm test

  ci-gate:
    name: Required CI Gate
    needs: [changes, backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Verify All Dependent Jobs Succeeded or Skipped Cleanly
        run: |
          backend_res="${{ needs.backend-tests.result }}"
          frontend_res="${{ needs.frontend-tests.result }}"

          for res in "" ""; do
            if [ "" != "success" ] && [ "" != "skipped" ]; then
              echo "❌ CI Gate Failure: Dependent job result was "
              exit 1
            fi
          done
          echo "✅ All required CI components passed or cleanly skipped."
```

---

## 4. Verification & Operational Checks

1. **Verify No Trigger Filters:** Run `grep -E "paths:|paths-ignore:" .github/workflows/*.yml` — MUST yield 0 matches at the root `on:` level.
2. **Verify Required Check Registration:** In repository branch protection rules, the single required check MUST be the aggregating gate (e.g., `Required CI Gate`).
3. **Verify Pure Docs PR:** Open a test PR with only a markdown edit; verify that the aggregated check completes GREEN in under 30 seconds.
