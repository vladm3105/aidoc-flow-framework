# TSPEC and BDD to QA Bridge

## Overview

This document bridges SDD test specifications (TSPEC Layer 10, BDD Layer 4) with governance QA execution workflows.

---

## Test Types and Execution Environment

### Test Pyramid

```
           /\
          /  \  BDD Acceptance (Staging)
         /    \
        /------\
       / FTEST  \ Functional (Staging)
      /----------\
     /   STEST    \ System (Staging)
    /--------------\
   /     ITEST      \ Integration (CI)
  /------------------\
 /       UTEST        \ Unit (CI)
/______________________\
```

### Mapping

| Test Type | SDD Layer | Execution | Environment | Coverage Target |
|-----------|-----------|-----------|-------------|-----------------|
| **UTEST** | TSPEC (L10) | CI Pipeline | PR checks | >=80% code coverage |
| **ITEST** | TSPEC (L10) | CI Pipeline | PR checks | >=60% integration |
| **STEST** | TSPEC (L10) | QA Workflow | Staging | Critical paths |
| **FTEST** | TSPEC (L10) | QA Workflow | Staging | Feature coverage |
| **BDD** | BDD (L4) | QA Workflow | Staging | User acceptance |

---

## Workflow Integration

### During Development (CI)

```
Code committed to PR
    |
ci.yml triggers
    |
+-- pytest tests/unit/ (UTEST)
|   +-- Coverage gate: >=80%
+-- pytest tests/integration/ (ITEST)
|   +-- Coverage gate: >=60%
+-- Security scan
    |
PR ready for review
```

### After Staging Deployment (QA)

```
All phase issues closed
    |
deploy-staging.yml deploys to staging
    |
create-qa-testing-issue.yml creates ai:qa-testing issue
    |
execute-qa-testing.yml triggers (daily 06:00-08:00 EST)
    |
+-- Smoke tests (health endpoints)
+-- pytest tests/system/ (STEST)
+-- pytest tests/functional/ (FTEST)
+-- pytest tests/bdd/ --bdd (BDD via pytest-bdd)
    |
Results evaluated:
    +-- Pass: ai:qa-passed label -> Production Ready
    +-- Fail: create-bug-issue.yml -> Bug fix iteration (max 3)
```

---

## TSPEC Registry Integration

### Registry Location

`docs/10_TSPEC/test_registry.yaml`

### Registry Structure

```yaml
# test_registry.yaml
tests:
  - nodeid: "tests/unit/test_threshold.py::test_check_threshold"
    tspec_id: "TSPEC-01.UTEST.01"
    upstream_refs:
      - "@spec: SPEC-01"
      - "@req: REQ-01:REQ.01.01"
    coverage_targets:
      - "src/threshold.py::ThresholdChecker"

  - nodeid: "tests/bdd/features/budget_alerts.feature::Budget threshold exceeded"
    tspec_id: "TSPEC-01.BDD.01"
    bdd_scenario: "BDD-01:BDD.01.01"
    upstream_refs:
      - "@ears: EARS-01:EARS.01.01"
      - "@prd: PRD-01:PRD.01.01"
```

### QA Script Integration

Update `governance/scripts/workflows/execute_qa_tests.py`:

```python
def load_tspec_registry(path: Path = Path("docs/10_TSPEC/test_registry.yaml")) -> dict:
    """Load TSPEC test registry for result mapping."""
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f)
    return {"tests": []}

def map_results_to_tspec(pytest_results: dict, registry: dict) -> list[dict]:
    """Map pytest results to TSPEC entries for traceability."""
    registry_map = {t["nodeid"]: t for t in registry.get("tests", [])}
    mapped = []
    for test in pytest_results.get("tests", []):
        tspec_entry = registry_map.get(test["nodeid"])
        if tspec_entry:
            mapped.append({
                "tspec_id": tspec_entry.get("tspec_id"),
                "bdd_scenario": tspec_entry.get("bdd_scenario"),
                "outcome": test["outcome"],
                "duration": test["duration"],
                "upstream_refs": tspec_entry.get("upstream_refs", [])
            })
    return mapped

def generate_traceability_report(mapped_results: list[dict]) -> str:
    """Generate markdown traceability report for QA issue."""
    lines = ["## Test Traceability Report", "", "| TSPEC ID | Outcome | Duration | Upstream |"]
    lines.append("|----------|---------|----------|----------|")
    for r in mapped_results:
        refs = ", ".join(r.get("upstream_refs", [])[:2])
        lines.append(f"| {r['tspec_id']} | {r['outcome']} | {r['duration']:.2f}s | {refs} |")
    return "\n".join(lines)
```

---

## BDD Execution

### Feature File Location

`tests/bdd/features/*.feature`

### Pytest-BDD Configuration

```python
# tests/bdd/conftest.py
import pytest
from pytest_bdd import scenarios

# Load all scenarios from features directory
scenarios("features/")
```

### Running BDD Tests

```bash
# Run all BDD tests
pytest tests/bdd/ --bdd

# Run with verbose BDD output
pytest tests/bdd/ -v --gherkin-terminal-reporter

# Generate BDD report
pytest tests/bdd/ --bdd --html=reports/bdd_report.html
```

---

## Coverage Requirements

| Test Type | Environment | Minimum Coverage | Gate Type |
|-----------|-------------|------------------|-----------|
| UTEST | CI | >=80% | Block PR |
| ITEST | CI | >=60% | Warning |
| STEST | Staging | Critical paths | Block Production |
| FTEST | Staging | Feature paths | Block Production |
| BDD | Staging | Acceptance | Block Production |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `ai_dev_ssd_flow/10_TSPEC/TSPEC-TEMPLATE.yaml` | TSPEC format |
| `ai_dev_ssd_flow/04_BDD/BDD-TEMPLATE.yaml` | BDD scenario format |
| `governance/templates/qa/01-testing-strategy.md` | Testing strategy |
| `governance/templates/qa/03-ci-pipeline-spec.md` | CI pipeline config |
