# Testing Infrastructure Implementation Plan

**Plan ID**: TESTING-INFRA-001
**Created**: 2026-02-06
**Completed**: 2026-02-06
**Status**: Complete
**Priority**: High
**Estimated Phases**: 4
**Target Completion**: 2026-02-06

---

## 1. Executive Summary

This plan addresses critical gaps in the testing infrastructure identified during documentation review. While the AI Dev Flow framework has comprehensive testing *documentation* (TSPEC layer, TESTING_STRATEGY_TDD.md, validation scripts), it lacks the *runtime infrastructure* needed to:

1. Track and catalog all tests
2. Execute tests consistently
3. Compare results between runs
4. Detect regressions after changes
5. Generate coverage reports

---

## 2. Current State Assessment

### 2.1 What Exists (Documentation Layer)

| Component | Location | Status |
|-----------|----------|--------|
| TSPEC Layer Definition | `10_TSPEC/` | Complete |
| 4 Test Type Templates | `10_TSPEC/{UTEST,ITEST,STEST,FTEST}/` | Complete |
| Testing Strategy | `TESTING_STRATEGY_TDD.md` | Complete (1,230 lines) |
| BDD Framework | `04_BDD/` | Complete with Gherkin |
| Validation Scripts | `scripts/`, layer scripts | 30+ scripts |
| Quality Gates | All layers | 90% thresholds |
| CI/CD Pipeline | `.github/workflows/` | GitHub Actions |
| Test Examples | `10_TSPEC/examples/` | 4 reference implementations |

### 2.2 What's Missing (Runtime Layer)

| Component | Impact | Priority |
|-----------|--------|----------|
| Test Registry/Catalog | Cannot inventory tests | P1 |
| Test Result Comparison | Cannot detect regressions | P1 |
| Pytest Configuration | No test runner setup | P1 |
| Test Execution Runner | Cannot run tests uniformly | P1 |
| Coverage Reports | No coverage metrics | P2 |
| Test Metadata Index | Cannot query test-to-requirement mapping | P2 |
| Performance Tests (PTEST) | Reserved code 44, not implemented | P3 |
| Security Tests (SECTEST) | Reserved code 45, not implemented | P3 |

---

## 3. Implementation Phases

### Phase 1: Test Registry and Catalog System

**Duration**: 1 session
**Deliverables**:

#### 3.1.1 Test Registry Schema (`10_TSPEC/test_registry_schema.yaml`)

```yaml
# Schema for test registry entries
test_entry:
  required:
    - test_id          # UTEST-001, ITEST-002, etc.
    - test_type        # UTEST | ITEST | STEST | FTEST
    - name             # Human-readable name
    - file_path        # Path to test file
    - status           # active | deprecated | skipped
    - created_date     # YYYY-MM-DD
  optional:
    - upstream_refs    # List of REQ, SPEC, CTR IDs
    - tags             # pytest markers
    - execution_time   # Last known duration (seconds)
    - last_result      # pass | fail | skip | error
    - last_run_date    # YYYY-MM-DD HH:MM:SS
    - coverage_targets # Files/functions covered
    - dependencies     # Other tests that must run first
```

#### 3.1.2 Test Registry File (`10_TSPEC/test_registry.yaml`)

```yaml
# Central registry of all tests
version: "1.0"
last_updated: "2026-02-06"
statistics:
  total_tests: 0
  by_type:
    UTEST: 0
    ITEST: 0
    STEST: 0
    FTEST: 0
  by_status:
    active: 0
    deprecated: 0
    skipped: 0

tests: []
  # Example entry:
  # - test_id: UTEST-001
  #   test_type: UTEST
  #   name: "Test authentication token generation"
  #   file_path: "tests/unit/test_auth.py::test_token_generation"
  #   status: active
  #   created_date: "2026-02-06"
  #   upstream_refs:
  #     - REQ-001
  #     - SPEC-001
  #   tags: [auth, security, fast]
  #   execution_time: 0.05
  #   last_result: pass
  #   last_run_date: "2026-02-06 10:30:00"
```

#### 3.1.3 Registry Management Script (`10_TSPEC/scripts/manage_test_registry.py`)

Functions:
- `add_test(test_id, metadata)` - Add new test to registry
- `update_test(test_id, updates)` - Update test metadata
- `remove_test(test_id)` - Mark test as deprecated
- `list_tests(filters)` - Query tests by type, status, tags
- `validate_registry()` - Check registry consistency
- `sync_from_filesystem()` - Discover tests and update registry
- `generate_report()` - Create summary statistics

**Acceptance Criteria**:
- [x] Schema validates all registry entries
- [x] Script can add/update/remove tests
- [x] Script can sync from filesystem (pytest collection)
- [x] Registry file is valid YAML
- [x] Statistics auto-update on changes

---

### Phase 2: Pytest Configuration and Test Runner

**Duration**: 1 session
**Deliverables**:

#### 3.2.1 Pytest Configuration (`pytest.ini`)

```ini
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers for test types
markers =
    utest: Unit tests (fast, isolated)
    itest: Integration tests (slower, requires services)
    stest: Smoke tests (post-deployment health checks)
    ftest: Functional tests (end-to-end scenarios)
    slow: Tests that take >5 seconds
    requires_db: Tests requiring database
    requires_api: Tests requiring external API

# Timeouts by test type
timeout = 300
timeout_method = thread

# Coverage configuration
addopts =
    --strict-markers
    -v
    --tb=short
    --color=yes

# Parallel execution
# addopts = -n auto  # Uncomment when pytest-xdist installed

# Output
console_output_style = progress
log_cli = true
log_cli_level = INFO
```

#### 3.2.2 Shared Fixtures (`tests/conftest.py`)

```python
"""
Shared pytest fixtures for AI Dev Flow testing.

Fixtures are organized by test type:
- Unit test fixtures: Mocks, stubs, isolated components
- Integration test fixtures: Database, API clients
- Smoke test fixtures: Deployment verification
- Functional test fixtures: End-to-end scenarios
"""

import pytest
import json
import yaml
from pathlib import Path
from datetime import datetime

# === Configuration ===

@pytest.fixture(scope="session")
def project_root():
    """Return project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_config(project_root):
    """Load test configuration."""
    config_path = project_root / "tests" / "test_config.yaml"
    if config_path.exists():
        return yaml.safe_load(config_path.read_text())
    return {}

# === Test Result Recording ===

@pytest.fixture(scope="session")
def test_results():
    """Accumulate test results for comparison."""
    results = {
        "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "started_at": datetime.now().isoformat(),
        "tests": []
    }
    yield results
    results["completed_at"] = datetime.now().isoformat()

@pytest.fixture(autouse=True)
def record_test_result(request, test_results):
    """Record each test result."""
    yield
    test_results["tests"].append({
        "name": request.node.name,
        "nodeid": request.node.nodeid,
        "outcome": "passed" if not hasattr(request.node, "rep_call")
                   or request.node.rep_call.passed else "failed",
        "duration": getattr(request.node, "rep_call", None)
                   and request.node.rep_call.duration or 0
    })

# === Unit Test Fixtures ===

@pytest.fixture
def mock_config():
    """Provide mock configuration for unit tests."""
    return {
        "environment": "test",
        "debug": True,
        "timeout": 30
    }

# === Integration Test Fixtures ===

@pytest.fixture(scope="module")
def db_connection():
    """Database connection for integration tests."""
    # Placeholder - implement based on actual database
    connection = None  # create_test_database()
    yield connection
    # cleanup_test_database(connection)

# === Smoke Test Fixtures ===

@pytest.fixture
def deployment_url(test_config):
    """Get deployment URL for smoke tests."""
    return test_config.get("deployment_url", "http://localhost:8000")

# === Functional Test Fixtures ===

@pytest.fixture
def api_client(deployment_url):
    """API client for functional tests."""
    # Placeholder - implement based on actual API
    return None  # APIClient(deployment_url)
```

#### 3.2.3 Test Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_config.yaml         # Test configuration
├── pytest.ini               # Pytest configuration (symlink to root)
│
├── unit/                    # UTEST - Unit tests
│   ├── conftest.py          # Unit-specific fixtures
│   ├── test_auth.py
│   ├── test_validation.py
│   └── test_utils.py
│
├── integration/             # ITEST - Integration tests
│   ├── conftest.py          # Integration-specific fixtures
│   ├── test_database.py
│   ├── test_api_client.py
│   └── test_service_integration.py
│
├── smoke/                   # STEST - Smoke tests
│   ├── conftest.py          # Smoke-specific fixtures
│   ├── test_health_endpoints.py
│   ├── test_deployment_status.py
│   └── test_critical_paths.py
│
├── functional/              # FTEST - Functional tests
│   ├── conftest.py          # Functional-specific fixtures
│   ├── test_user_workflows.py
│   ├── test_data_processing.py
│   └── test_end_to_end.py
│
└── results/                 # Test result archives
    └── .gitkeep
```

#### 3.2.4 Unified Test Runner (`scripts/run_tests.py`)

```python
#!/usr/bin/env python3
"""
Unified test runner for AI Dev Flow.

Usage:
    python scripts/run_tests.py --type utest           # Run unit tests
    python scripts/run_tests.py --type itest           # Run integration tests
    python scripts/run_tests.py --type all             # Run all tests
    python scripts/run_tests.py --type all --save      # Run and save results
    python scripts/run_tests.py --compare baseline.json current.json
"""

import argparse
import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

TEST_TYPES = {
    "utest": {"path": "tests/unit", "marker": "utest", "timeout": 120},
    "itest": {"path": "tests/integration", "marker": "itest", "timeout": 600},
    "stest": {"path": "tests/smoke", "marker": "stest", "timeout": 300},
    "ftest": {"path": "tests/functional", "marker": "ftest", "timeout": 900},
}

def run_tests(test_type: str, save_results: bool = False) -> dict:
    """Run tests of specified type and return results."""
    # Implementation details...
    pass

def compare_results(baseline: Path, current: Path) -> dict:
    """Compare two test result files and identify regressions."""
    # Implementation details...
    pass

def main():
    parser = argparse.ArgumentParser(description="Run and compare tests")
    parser.add_argument("--type", choices=["utest", "itest", "stest", "ftest", "all"])
    parser.add_argument("--save", action="store_true", help="Save results to file")
    parser.add_argument("--compare", nargs=2, metavar=("BASELINE", "CURRENT"))
    parser.add_argument("--output", default="tests/results", help="Output directory")

    args = parser.parse_args()
    # Implementation...

if __name__ == "__main__":
    main()
```

**Acceptance Criteria**:
- [x] `pytest` runs with configuration
- [x] All 4 test types have markers
- [x] Fixtures load correctly
- [x] Test directory structure created
- [x] Runner script executes tests by type
- [x] Results saved to JSON format

---

### Phase 3: Test Result Comparison and Regression Detection

**Duration**: 1 session
**Deliverables**:

#### 3.3.1 Test Result Schema (`10_TSPEC/test_result_schema.yaml`)

```yaml
# Schema for test result files
test_run:
  required:
    - run_id           # Unique identifier (timestamp-based)
    - started_at       # ISO 8601 datetime
    - completed_at     # ISO 8601 datetime
    - test_type        # UTEST | ITEST | STEST | FTEST | ALL
    - environment      # test | staging | production
    - summary:
        total: int
        passed: int
        failed: int
        skipped: int
        errors: int
        duration_seconds: float
    - tests: list      # Individual test results
  optional:
    - git_commit       # Git SHA for traceability
    - git_branch       # Branch name
    - triggered_by     # manual | ci | scheduled
    - coverage_percent # Overall coverage
```

#### 3.3.2 Comparison Script (`scripts/compare_test_results.py`)

```python
#!/usr/bin/env python3
"""
Compare test results between runs to detect regressions.

Usage:
    python scripts/compare_test_results.py baseline.json current.json
    python scripts/compare_test_results.py --latest tests/results/
    python scripts/compare_test_results.py --threshold 95 baseline.json current.json

Output:
    - Summary of changes (new tests, removed tests, status changes)
    - Regression report (tests that went from pass to fail)
    - Performance comparison (execution time changes)
    - Exit code: 0 = no regressions, 1 = regressions found
"""

import argparse
import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class TestComparison:
    """Result of comparing two test runs."""
    baseline_run_id: str
    current_run_id: str

    # Test changes
    new_tests: List[str]           # Tests in current but not baseline
    removed_tests: List[str]       # Tests in baseline but not current

    # Status changes
    regressions: List[Dict]        # pass -> fail
    fixes: List[Dict]              # fail -> pass
    flaky: List[Dict]              # Different results, same test

    # Performance changes
    slower_tests: List[Dict]       # >20% slower
    faster_tests: List[Dict]       # >20% faster

    # Summary
    regression_count: int
    pass_rate_change: float        # Current - baseline
    total_duration_change: float   # Seconds

def load_results(path: Path) -> dict:
    """Load test results from JSON file."""
    return json.loads(path.read_text())

def compare_runs(baseline: dict, current: dict) -> TestComparison:
    """Compare two test runs and identify changes."""
    # Build test lookup maps
    baseline_tests = {t["nodeid"]: t for t in baseline.get("tests", [])}
    current_tests = {t["nodeid"]: t for t in current.get("tests", [])}

    comparison = TestComparison(
        baseline_run_id=baseline.get("run_id", "unknown"),
        current_run_id=current.get("run_id", "unknown"),
        new_tests=[],
        removed_tests=[],
        regressions=[],
        fixes=[],
        flaky=[],
        slower_tests=[],
        faster_tests=[],
        regression_count=0,
        pass_rate_change=0.0,
        total_duration_change=0.0
    )

    # Find new and removed tests
    comparison.new_tests = list(set(current_tests.keys()) - set(baseline_tests.keys()))
    comparison.removed_tests = list(set(baseline_tests.keys()) - set(current_tests.keys()))

    # Compare common tests
    common_tests = set(baseline_tests.keys()) & set(current_tests.keys())
    for test_id in common_tests:
        baseline_test = baseline_tests[test_id]
        current_test = current_tests[test_id]

        baseline_outcome = baseline_test.get("outcome", "unknown")
        current_outcome = current_test.get("outcome", "unknown")

        # Detect regressions (pass -> fail)
        if baseline_outcome == "passed" and current_outcome == "failed":
            comparison.regressions.append({
                "test_id": test_id,
                "baseline_outcome": baseline_outcome,
                "current_outcome": current_outcome
            })
            comparison.regression_count += 1

        # Detect fixes (fail -> pass)
        elif baseline_outcome == "failed" and current_outcome == "passed":
            comparison.fixes.append({
                "test_id": test_id,
                "baseline_outcome": baseline_outcome,
                "current_outcome": current_outcome
            })

        # Detect performance changes
        baseline_duration = baseline_test.get("duration", 0)
        current_duration = current_test.get("duration", 0)
        if baseline_duration > 0:
            change_pct = (current_duration - baseline_duration) / baseline_duration * 100
            if change_pct > 20:
                comparison.slower_tests.append({
                    "test_id": test_id,
                    "baseline_duration": baseline_duration,
                    "current_duration": current_duration,
                    "change_percent": change_pct
                })
            elif change_pct < -20:
                comparison.faster_tests.append({
                    "test_id": test_id,
                    "baseline_duration": baseline_duration,
                    "current_duration": current_duration,
                    "change_percent": change_pct
                })

    # Calculate summary statistics
    baseline_passed = sum(1 for t in baseline.get("tests", []) if t.get("outcome") == "passed")
    current_passed = sum(1 for t in current.get("tests", []) if t.get("outcome") == "passed")
    baseline_total = len(baseline.get("tests", []))
    current_total = len(current.get("tests", []))

    baseline_rate = (baseline_passed / baseline_total * 100) if baseline_total > 0 else 0
    current_rate = (current_passed / current_total * 100) if current_total > 0 else 0
    comparison.pass_rate_change = current_rate - baseline_rate

    return comparison

def generate_report(comparison: TestComparison) -> str:
    """Generate human-readable comparison report."""
    lines = [
        "# Test Comparison Report",
        "",
        f"**Baseline Run**: {comparison.baseline_run_id}",
        f"**Current Run**: {comparison.current_run_id}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Regressions | {comparison.regression_count} |",
        f"| Fixes | {len(comparison.fixes)} |",
        f"| New Tests | {len(comparison.new_tests)} |",
        f"| Removed Tests | {len(comparison.removed_tests)} |",
        f"| Pass Rate Change | {comparison.pass_rate_change:+.1f}% |",
        "",
    ]

    if comparison.regressions:
        lines.extend([
            "## Regressions (REQUIRES ATTENTION)",
            "",
            "| Test | Baseline | Current |",
            "|------|----------|---------|",
        ])
        for reg in comparison.regressions:
            lines.append(f"| `{reg['test_id']}` | {reg['baseline_outcome']} | {reg['current_outcome']} |")
        lines.append("")

    if comparison.fixes:
        lines.extend([
            "## Fixes",
            "",
            "| Test | Baseline | Current |",
            "|------|----------|---------|",
        ])
        for fix in comparison.fixes:
            lines.append(f"| `{fix['test_id']}` | {fix['baseline_outcome']} | {fix['current_outcome']} |")
        lines.append("")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Compare test results")
    parser.add_argument("baseline", type=Path, help="Baseline results file")
    parser.add_argument("current", type=Path, help="Current results file")
    parser.add_argument("--threshold", type=float, default=100.0,
                        help="Minimum pass rate to succeed (default: 100)")
    parser.add_argument("--output", type=Path, help="Save report to file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    baseline = load_results(args.baseline)
    current = load_results(args.current)
    comparison = compare_runs(baseline, current)

    if args.json:
        print(json.dumps(comparison.__dict__, indent=2))
    else:
        report = generate_report(comparison)
        print(report)
        if args.output:
            args.output.write_text(report)

    # Exit with error if regressions found
    if comparison.regression_count > 0:
        print(f"\n❌ {comparison.regression_count} regression(s) detected!")
        sys.exit(1)
    else:
        print("\n✅ No regressions detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

#### 3.3.3 Result Archival Script (`scripts/archive_test_results.py`)

Functions:
- Save test results with timestamp
- Maintain rolling history (last N runs)
- Tag results with git commit/branch
- Generate trend reports

**Acceptance Criteria**:
- [x] Comparison script detects regressions
- [x] Report clearly shows pass->fail changes
- [x] Performance changes identified
- [x] Exit code indicates regression status
- [x] Results archived with metadata

---

### Phase 4: Coverage Reports and CI/CD Integration

**Duration**: 1 session
**Deliverables**:

#### 3.4.1 Coverage Configuration (`pyproject.toml` additions)

```toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "tests/*",
    "*/__pycache__/*",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:"
]
fail_under = 80
show_missing = true

[tool.coverage.html]
directory = "tests/coverage_html"

[tool.coverage.json]
output = "tests/results/coverage.json"
```

#### 3.4.2 Coverage Report Generator (`scripts/generate_coverage_report.py`)

```python
#!/usr/bin/env python3
"""
Generate coverage reports and track trends.

Usage:
    python scripts/generate_coverage_report.py --type utest
    python scripts/generate_coverage_report.py --type all --html
    python scripts/generate_coverage_report.py --trend tests/results/
"""

# Implementation for:
# - Run coverage.py during test execution
# - Generate HTML, JSON, and terminal reports
# - Track coverage trends over time
# - Alert on coverage decreases
```

#### 3.4.3 GitHub Actions Workflow Update (`.github/workflows/test-pipeline.yml`)

```yaml
name: Test Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pytest pytest-cov pytest-timeout
          pip install -r requirements.txt

      - name: Run unit tests
        run: |
          python scripts/run_tests.py --type utest --save

      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: unit-test-results
          path: tests/results/

      - name: Compare with baseline
        run: |
          python scripts/compare_test_results.py \
            tests/results/baseline_utest.json \
            tests/results/latest_utest.json
        continue-on-error: true

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run integration tests
        run: |
          python scripts/run_tests.py --type itest --save

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: integration-test-results
          path: tests/results/

  coverage-report:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    steps:
      - uses: actions/checkout@v4

      - name: Download all results
        uses: actions/download-artifact@v4

      - name: Generate coverage report
        run: |
          python scripts/generate_coverage_report.py --type all --html

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: tests/coverage_html/
```

**Acceptance Criteria**:
- [x] Coverage reports generated in HTML/JSON
- [x] Coverage thresholds enforced (80% minimum)
- [x] CI/CD pipeline runs all test types
- [x] Results compared against baseline
- [x] Artifacts archived for each run

---

## 4. File Manifest

### New Files to Create

| Phase | File Path | Type | Purpose |
|-------|-----------|------|---------|
| 1 | `10_TSPEC/test_registry_schema.yaml` | Schema | Registry validation |
| 1 | `10_TSPEC/test_registry.yaml` | Data | Central test catalog |
| 1 | `10_TSPEC/scripts/manage_test_registry.py` | Script | Registry management |
| 2 | `pytest.ini` | Config | Pytest configuration |
| 2 | `tests/conftest.py` | Python | Shared fixtures |
| 2 | `tests/test_config.yaml` | Config | Test environment config |
| 2 | `scripts/run_tests.py` | Script | Unified test runner |
| 3 | `10_TSPEC/test_result_schema.yaml` | Schema | Result validation |
| 3 | `scripts/compare_test_results.py` | Script | Regression detection |
| 3 | `scripts/archive_test_results.py` | Script | Result archival |
| 4 | `scripts/generate_coverage_report.py` | Script | Coverage reports |
| 4 | `.github/workflows/test-pipeline.yml` | YAML | CI/CD integration |

### Directories to Create

```
tests/
├── unit/
├── integration/
├── smoke/
├── functional/
└── results/
```

---

## 5. Dependencies

### Python Packages Required

```txt
# requirements-test.txt
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-timeout>=2.2.0
pytest-xdist>=3.5.0      # Parallel execution
pyyaml>=6.0.1
jsonschema>=4.21.0
```

### Optional Packages

```txt
pytest-html>=4.1.0       # HTML reports
pytest-bdd>=7.0.0        # BDD integration
testcontainers>=3.7.0    # Docker test services
```

---

## 6. Success Criteria

### Phase 1 Complete When:
- [x] Test registry schema defined
- [x] Registry YAML file created
- [x] Management script functional
- [x] Can add/remove/list tests

### Phase 2 Complete When:
- [x] `pytest` runs successfully
- [x] All test markers work
- [x] Fixtures load correctly
- [x] Runner script executes by type

### Phase 3 Complete When:
- [x] Comparison detects regressions
- [x] Reports generated in markdown
- [x] Exit codes indicate status
- [x] Results archived with metadata

### Phase 4 Complete When:
- [x] Coverage reports generated
- [x] CI/CD pipeline runs tests
- [x] Baseline comparison works
- [x] Artifacts archived

---

## 7. Execution Commands

### Phase 1: Registry Setup
```bash
# Create registry files
python scripts/manage_test_registry.py --init

# Sync from filesystem (discover existing tests)
python scripts/manage_test_registry.py --sync

# List all tests
python scripts/manage_test_registry.py --list
```

### Phase 2: Test Execution
```bash
# Run unit tests
python scripts/run_tests.py --type utest

# Run all tests
python scripts/run_tests.py --type all --save

# Run with coverage
pytest tests/unit --cov=src --cov-report=html
```

### Phase 3: Comparison
```bash
# Compare results
python scripts/compare_test_results.py baseline.json current.json

# Generate regression report
python scripts/compare_test_results.py --output report.md baseline.json current.json
```

### Phase 4: CI/CD
```bash
# Generate coverage report
python scripts/generate_coverage_report.py --type all --html

# Check coverage threshold
python scripts/generate_coverage_report.py --check --threshold 80
```

---

## 8. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| No existing tests to register | Low | Registry supports empty state, ready for new tests |
| pytest not installed | Medium | Add to requirements, document installation |
| CI/CD conflicts with existing workflows | Medium | Use separate workflow file, test on branch first |
| Coverage tool compatibility | Low | coverage.py is standard, well-supported |

---

## 9. References

### Internal Documentation
- `TESTING_STRATEGY_TDD.md` - Testing philosophy and workflow
- `10_TSPEC/README.md` - TSPEC layer documentation
- `10_TSPEC/TSPEC-00_index.md` - Test type definitions
- `scripts/SCRIPT_INDEX.md` - Existing validation scripts

### External Resources
- [pytest documentation](https://docs.pytest.org/)
- [coverage.py documentation](https://coverage.readthedocs.io/)
- [GitHub Actions pytest](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

---

## 10. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-06 | Claude | Initial plan creation |
