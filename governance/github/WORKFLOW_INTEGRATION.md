# Workflow Integration Guide

## Overview

This document maps workflows between SDD artifact validation and governance issue/deployment lifecycle.

---

## Workflow Categories

| Category | Workflows | Trigger | Purpose |
|----------|-----------|---------|---------|
| **SDD Validation** | `sdd-artifact-validation.yml` | `docs/**` changes | Validate artifacts, update matrix |
| **CI/CD** | `ci.yml`, `test-pipeline.yml` | PR, push | Lint, test, security scan |
| **Deployment** | `deploy-dev.yml`, `deploy-staging.yml`, `deploy-prod.yml` | Phase completion, manual | Environment deployment |
| **Issue Lifecycle** | `agent-dispatch.yml`, `issue-label-sync.yml` | Issue events | AI agent coordination |
| **QA** | `execute-qa-testing.yml`, `create-qa-testing-issue.yml` | Deploy completion | Test execution |
| **Bug Management** | `create-bug-issue.yml` | Test failure | Bug issue creation |

---

## SDD Layer to Governance Phase Mapping

| SDD Layers | Governance Activity | Workflows Involved |
|------------|--------------------|--------------------|
| L1-L4 (BRD->BDD) | Requirement definition | `sdd-artifact-validation.yml` |
| L5-L8 (ADR->CTR) | Architecture & design | `sdd-artifact-validation.yml` |
| L9-L11 (SPEC->TASKS) | Sprint planning | `sdd-artifact-validation.yml`, `mvp-docs-generation.yml` |
| L12-L14 (IMPL) | Development & QA | `ci.yml`, `deploy-*.yml`, `execute-qa-testing.yml` |

---

## Test Execution Workflow

### CI Pipeline (Development)

```
PR Created
    |
ci.yml triggers
    |
+-- Lint (ruff, mypy)
+-- UTEST (pytest, >=80% coverage)
+-- ITEST (integration tests, >=60% coverage)
+-- Security scan (bandit, pip-audit)
+-- Build validation
    |
PR Ready for Review
```

### QA Pipeline (Staging)

```
All Phase Issues Closed
    |
deploy-staging.yml triggers
    |
Staging deployment complete
    |
create-qa-testing-issue.yml creates ai:qa-testing issue
    |
execute-qa-testing.yml triggers (daily 06:00-08:00 EST)
    |
+-- Smoke tests (health endpoints)
+-- STEST (system tests)
+-- FTEST (functional tests)
+-- BDD (acceptance tests via pytest-bdd)
    |
Pass: ai:qa-passed -> Production Ready
Fail: create-bug-issue.yml -> Bug fix iteration
```

---

## Validation Triggers

| Event | SDD Validation | CI Pipeline | QA Pipeline |
|-------|----------------|-------------|-------------|
| PR to `main` | Yes (docs changes) | Yes (code changes) | - |
| Push to `main` | Yes (matrix update) | - | - |
| Phase complete | - | - | Yes |
| Schedule (weekly) | Yes (drift check) | - | Yes (daily) |

---

## Workflow Execution Order

### Feature Development Lifecycle

```
1. Human creates REF/ document
       |
2. AI generates SDD artifacts (BRD -> TASKS)
       |
   sdd-artifact-validation.yml validates
       |
3. AI creates GitHub issues from TASKS
       |
4. AI picks up issue (ai:ready)
       |
   agent-dispatch.yml dispatches
       |
5. AI implements and creates PR
       |
   ci.yml runs (lint, test, security)
       |
6. PR merged
       |
   create-deployment-issue.yml
   create-qa-testing-issue.yml
       |
7. Phase complete -> deploy-staging.yml
       |
8. execute-qa-testing.yml runs
       |
   Pass: Production ready
   Fail: create-bug-issue.yml -> Loop to step 4
```

---

## No Marketplace Actions Policy

Per `GOVERNANCE_RULES.md` Section 2a, all workflows use inline commands:

| Marketplace Action | Replacement |
|--------------------|-------------|
| `actions/checkout@v4` | `git clone` with token |
| `actions/setup-python@v5` | System `python3` |
| `tj-actions/changed-files@v42` | `git diff --name-only` |
| `stefanzweifel/git-auto-commit-action@v5` | `git add && git commit && git push` |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `GOVERNANCE_RULES.md` | Workflow security rules |
| `AI_ISSUE_LIFECYCLE.md` | Issue state transitions |
| `GITHUB_WORKFLOWS.md` | Individual workflow docs |
| `TSPEC_BDD_QA_BRIDGE.md` | Test execution model |
