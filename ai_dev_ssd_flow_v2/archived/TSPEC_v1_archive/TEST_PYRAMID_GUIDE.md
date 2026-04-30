# Test Pyramid Guide

## Overview

This guide defines the SDD testing model, explaining when and where each test type executes in the development lifecycle.

---

## Test Pyramid

```
              /\
             /  \  BDD Acceptance Tests
            /    \     (Staging - Few, Slow)
           /------\
          / FTEST  \  Functional Tests
         /----------\    (Staging)
        /   STEST    \  System Tests
       /--------------\    (Staging)
      /     ITEST      \  Integration Tests
     /------------------\    (CI - Moderate)
    /       UTEST        \  Unit Tests
   /______________________\    (CI - Many, Fast)
```

**Principle**: More tests at the bottom (fast, cheap), fewer at the top (slow, expensive).

---

## Test Types Defined

### UTEST (Unit Tests)

| Aspect | Description |
|--------|-------------|
| **Layer** | TSPEC (Layer 10) |
| **Scope** | Single function/method, isolated |
| **Mocking** | External dependencies mocked |
| **Execution** | CI Pipeline (every PR) |
| **Coverage Target** | >=80% code coverage |
| **Speed** | Fast (<1s per test) |
| **Location** | `tests/unit/` |

**Example TSPEC Entry**:
```yaml
- id: TSPEC-01.UTEST.01
  type: UTEST
  target: src/threshold.py::ThresholdChecker::check
  upstream: "@req: REQ-01:REQ.01.01"
```

### ITEST (Integration Tests)

| Aspect | Description |
|--------|-------------|
| **Layer** | TSPEC (Layer 10) |
| **Scope** | Multiple components together |
| **Mocking** | External services mocked (DB, APIs) |
| **Execution** | CI Pipeline (every PR) |
| **Coverage Target** | >=60% integration paths |
| **Speed** | Moderate (1-10s per test) |
| **Location** | `tests/integration/` |

**Example TSPEC Entry**:
```yaml
- id: TSPEC-01.ITEST.01
  type: ITEST
  target: src/services/budget_service.py
  dependencies: [database, pubsub]
  upstream: "@sys: SYS-01:SYS.01.01"
```

### STEST (System Tests)

| Aspect | Description |
|--------|-------------|
| **Layer** | TSPEC (Layer 10) |
| **Scope** | Full system, end-to-end paths |
| **Mocking** | None - real services |
| **Execution** | QA Workflow (staging only) |
| **Coverage Target** | Critical user paths |
| **Speed** | Slow (10s-1min per test) |
| **Location** | `tests/system/` |

**Example TSPEC Entry**:
```yaml
- id: TSPEC-01.STEST.01
  type: STEST
  target: Full budget alert flow
  environment: staging
  upstream: "@ears: EARS-01:EARS.01.01"
```

### FTEST (Functional Tests)

| Aspect | Description |
|--------|-------------|
| **Layer** | TSPEC (Layer 10) |
| **Scope** | Feature-specific functionality |
| **Mocking** | None - real services |
| **Execution** | QA Workflow (staging only) |
| **Coverage Target** | All feature requirements |
| **Speed** | Moderate-slow |
| **Location** | `tests/functional/` |

**Example TSPEC Entry**:
```yaml
- id: TSPEC-01.FTEST.01
  type: FTEST
  feature: Budget threshold notifications
  upstream: "@prd: PRD-01:PRD.01.01"
```

### BDD (Behavior-Driven Development)

| Aspect | Description |
|--------|-------------|
| **Layer** | BDD (Layer 4) |
| **Scope** | User acceptance scenarios |
| **Format** | Gherkin (Given/When/Then) |
| **Execution** | QA Workflow (staging only) |
| **Coverage Target** | All acceptance criteria |
| **Speed** | Slow (user-facing flows) |
| **Location** | `tests/bdd/features/` |

**Example BDD Scenario**:
```gherkin
@brd: BRD-01:BRD.01.01
@prd: PRD-01:PRD.01.01
Scenario: User receives email when budget exceeds 80%
  Given a budget of $10,000 for project "web-app"
  And alert threshold configured at 80%
  When current spend reaches $8,100
  Then an email alert should be sent within 5 minutes
```

---

## Execution Environments

### CI Pipeline (Development)

**Triggers**: Every PR, every push to feature branches

**Tests Run**:
- UTEST (unit tests)
- ITEST (integration tests)
- NOT: STEST, FTEST, BDD (require staging)

**Workflow**: `.github/workflows/ci.yml`

```
PR Created/Updated
    |
+-- Lint (ruff, mypy)
+-- UTEST (pytest tests/unit/)
|   +-- Coverage gate: >=80% or fail
+-- ITEST (pytest tests/integration/)
|   +-- Coverage gate: >=60% or warn
+-- Security scan
    |
PR Ready for Review
```

### QA Staging (Quality Assurance)

**Triggers**: Phase completion, staging deployment

**Tests Run**:
- NOT: UTEST, ITEST (already passed in CI)
- STEST (system tests)
- FTEST (functional tests)
- BDD (acceptance tests)

**Workflow**: `.github/workflows/execute-qa-testing.yml`

```
Staging Deployment Complete
    |
ai:qa-testing issue created
    |
+-- Smoke tests (health endpoints)
+-- STEST (pytest tests/system/)
+-- FTEST (pytest tests/functional/)
+-- BDD (pytest tests/bdd/ --bdd)
    |
Pass -> ai:qa-passed -> Production Ready
Fail -> Bug issue created (iteration:N)
```

---

## Test Directory Structure

```
tests/
+-- unit/                    # UTEST - Unit tests (CI)
|   +-- conftest.py
|   +-- test_threshold.py
|   +-- test_calculator.py
+-- integration/             # ITEST - Integration tests (CI)
|   +-- conftest.py
|   +-- test_budget_service.py
|   +-- test_notification_service.py
+-- system/                  # STEST - System tests (Staging)
|   +-- conftest.py
|   +-- test_full_alert_flow.py
+-- functional/              # FTEST - Functional tests (Staging)
|   +-- conftest.py
|   +-- test_budget_features.py
+-- bdd/                     # BDD - Acceptance tests (Staging)
    +-- conftest.py
    +-- features/
    |   +-- budget_alerts.feature
    |   +-- user_notifications.feature
    +-- step_defs/
        +-- budget_steps.py
        +-- notification_steps.py
```

---

## Coverage Requirements by SDD Depth

| SDD Depth | UTEST | ITEST | STEST/FTEST | BDD |
|-----------|-------|-------|-------------|-----|
| **Lite** | >=60% | Optional | Optional | No |
| **Standard** | >=80% | >=60% | Critical paths | Optional |
| **Full** | >=80% | >=60% | Full coverage | Required |

---

## Workflow Summary

```
Code Generation (Layer 12)
         |
    +--------------------+
    |    CI PIPELINE     |
    |  +------+  +-----+ |
    |  |UTEST |  |ITEST| |
    |  | >=80%|  | >=60| |
    |  +------+  +-----+ |
    +--------------------+
         |
    PR Merge -> Deploy to Dev
         |
    Phase Complete -> Deploy to Staging
         |
    +--------------------+
    |  QA STAGING        |
    | +-----+ +----+     |
    | |STEST| |FTEST|    |
    | +-----+ +----+     |
    |      +-----+       |
    |      | BDD |       |
    |      +-----+       |
    +--------------------+
         |
    Pass -> Production Ready
    Fail -> Bug Issue (max 3 iterations)
```

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `governance/TSPEC_BDD_QA_BRIDGE.md` | QA workflow integration |
| `governance/templates/qa/01-testing-strategy.md` | Testing strategy details |
| `governance/templates/qa/03-ci-pipeline-spec.md` | CI pipeline configuration |
| `ucx_flow_v3/04_BDD/BDD-TEMPLATE.feature` | BDD scenario template |
| `TSPEC-MVP-TEMPLATE.yaml` | TSPEC format template |
