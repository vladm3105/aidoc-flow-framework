---
name: ucx-github-deploy-governance
description: |
  Hermes governance skill for CI/CD, QA, staging/production readiness, and
  post-deployment issue-loop control aligned with governance policies.
version: 1.0.0
category: governance
author: UCX Framework Team
requires: []
---

# UCX GitHub Deploy Governance Skill

## Purpose

Manage deployment and QA governance loop after PR submission/merge using
GitHub workflows, issue automation, and policy checks.

## CI/CD Governance Scope

- CI workflow status verification (required checks)
- QA issue generation and tracking for functional changes
- Staging readiness checks
- Production readiness verification
- Post-deployment outcome validation and issue closure/reopen decisions

## Standard Governance Loop

1. PR submitted with linked issue and traceability.
2. Required CI checks execute.
3. Round-based UCX governance gates execute (up to 2 rounds).
4. If gates pass, merge and create/track deployment + QA issues as required.
5. Validate staging evidence.
6. Validate production readiness evidence.
7. Close issues on success; reopen/create bug issues on regression.

## QA and Deployment Rules

- Create QA issues for functional changes.
- Use bounded bug-fix iterations for staging failures.
- Block production progression when readiness checks fail.
- Preserve evidence links in deployment and QA issues.

## Observability-Driven Reopen Policy

If post-deployment monitoring shows incidents or regressions:

1. Open or reopen GitHub issue with severity, impact, and repro context.
2. Include traceability links to source artifacts and PR/deploy evidence.
3. Route issue back to `ai:ready` queue only after approval policy conditions.

## GitHub Actions Compatibility Rules

- Use reviewed, version-pinned workflow actions.
- Respect branch protection and required checks.
- Treat AI review as gate signal, not required human reviewer substitute.

## UCX V3 Boundaries

- Deployment governance does not bypass UCX document lifecycle gates.
- CLI usage allowed for approved IPLAN implementation execution tasks only.
- Lifecycle source of truth remains UCX MCP stage outputs and governance policies.

## Failure Handling

If deployment governance checks fail:

1. Hold progression to next environment.
2. Record failed checks and evidence paths.
3. Open/update corrective issue and assign next governance action.
