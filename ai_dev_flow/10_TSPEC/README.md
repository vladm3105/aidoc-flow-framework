---
title: "TSPEC Layer Overview - Test Specifications"
tags:
  - layer-10-artifact
  - tspec-overview
  - tdd-workflow
  - shared-architecture
custom_fields:
  document_type: layer-readme
  artifact_type: TSPEC
  layer: 10
  priority: shared
  development_status: active
  upstream_artifacts: [REQ, SPEC, CTR, SYS, EARS, BDD]
  downstream_artifacts: [TASKS]
---

# Layer 10: TSPEC (Test Specifications)

## Purpose

TSPEC formalizes test specifications between SPEC (L9) and TASKS (L11) to enable Test-Driven Development (TDD) workflow. This layer defines test cases, coverage matrices, and quality gates before implementation begins.

## Test Type Categories

| Code | Type | Abbreviation | Directory | Source Artifacts | Purpose |
|------|------|--------------|-----------|------------------|---------|
| 40 | Unit Test | UT | `UTEST/` | REQ (L7), SPEC (L9) | Individual function tests |
| 41 | Integration Test | IT | `ITEST/` | CTR (L8), SYS (L6), SPEC (L9) | Component interaction |
| 42 | Smoke Test | ST | `STEST/` | EARS (L3), BDD (L4), REQ (L7) | Post-deployment health |
| 43 | Functional Test | FT | `FTEST/` | SYS (L6) | System behavior validation |
| 44-45 | Reserved | - | - | - | Future (performance, security) |

**Note**: Acceptance tests remain in BDD (L4), not duplicated here.

## Directory Structure

```
10_TSPEC/
├── README.md                              # This file
├── TSPEC-00_index.md                      # Master index
├── TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md
│
├── UTEST/                                 # Unit Test Specifications
│   ├── UTEST-MVP-TEMPLATE.md
│   ├── UTEST-MVP-TEMPLATE.yaml
│   ├── UTEST_MVP_SCHEMA.yaml
│   ├── UTEST_MVP_CREATION_RULES.md
│   ├── UTEST_MVP_VALIDATION_RULES.md
│   └── UTEST_MVP_QUALITY_GATES.md
│
├── ITEST/                                 # Integration Test Specifications
│   ├── ITEST-MVP-TEMPLATE.md
│   ├── ITEST-MVP-TEMPLATE.yaml
│   ├── ITEST_MVP_SCHEMA.yaml
│   ├── ITEST_MVP_CREATION_RULES.md
│   ├── ITEST_MVP_VALIDATION_RULES.md
│   └── ITEST_MVP_QUALITY_GATES.md
│
├── STEST/                                 # Smoke Test Specifications
│   ├── STEST-MVP-TEMPLATE.md
│   ├── STEST-MVP-TEMPLATE.yaml
│   ├── STEST_MVP_SCHEMA.yaml
│   ├── STEST_MVP_CREATION_RULES.md
│   ├── STEST_MVP_VALIDATION_RULES.md
│   └── STEST_MVP_QUALITY_GATES.md
│
├── FTEST/                                 # Functional Test Specifications
│   ├── FTEST-MVP-TEMPLATE.md
│   ├── FTEST-MVP-TEMPLATE.yaml
│   ├── FTEST_MVP_SCHEMA.yaml
│   ├── FTEST_MVP_CREATION_RULES.md
│   ├── FTEST_MVP_VALIDATION_RULES.md
│   └── FTEST_MVP_QUALITY_GATES.md
│
├── scripts/
│   ├── README.md
│   ├── validate_utest.py
│   ├── validate_itest.py
│   ├── validate_stest.py
│   ├── validate_ftest.py
│   ├── validate_tspec_quality_score.sh
│   └── validate_all_tspec.sh
│
└── examples/
    ├── README.md
    ├── UTEST-01_auth_service.md
    ├── ITEST-01_auth_service.md
    ├── STEST-01_auth_service.md
    └── FTEST-01_auth_service.md
```

## Element ID Format

**Format**: `TSPEC.NN.TT.SS`

| Component | Description | Range |
|-----------|-------------|-------|
| `NN` | Document number | 01-99+ |
| `TT` | Test type code | 40-45 |
| `SS` | Sequential test case | 01-99+ |

**Test Type Codes**:

| Code | Type | Prefix |
|------|------|--------|
| 40 | Unit Test | UTEST |
| 41 | Integration Test | ITEST |
| 42 | Smoke Test | STEST |
| 43 | Functional Test | FTEST |
| 44 | Reserved | PTEST (Performance) |
| 45 | Reserved | SECTEST (Security) |

**Examples**:
- `TSPEC.01.40.01` = Document 1, Unit Test #1
- `TSPEC.01.41.03` = Document 1, Integration Test #3
- `TSPEC.01.42.01` = Document 1, Smoke Test #1
- `TSPEC.01.43.02` = Document 1, Functional Test #2

## Traceability Requirements

### Required Upstream Tags (9 total)

```
@brd, @prd, @ears, @bdd, @adr, @sys, @req, @ctr, @spec
```

Plus: `@threshold` for quantitative values

### Downstream Tags

```
@tasks: TASKS-NN
@code: tests/unit/, tests/integration/, etc.
```

### Test Type Specific Tags

| Test Type | Required Tags |
|-----------|---------------|
| UTEST | `@req`, `@spec` |
| ITEST | `@ctr`, `@sys`, `@spec` |
| STEST | `@ears`, `@bdd`, `@req` |
| FTEST | `@sys`, `@threshold` |

## Quality Gates Summary

| Test Type | Target Score | Key Criteria |
|-----------|--------------|--------------|
| UTEST | ≥90% | REQ coverage, I/O tables, pseudocode |
| ITEST | ≥85% | CTR coverage, sequence diagrams |
| STEST | 100% | Critical paths, timeout <5min, rollback |
| FTEST | ≥85% | SYS coverage, threshold refs |

## TDD Workflow Position

```
SPEC (L9) → TSPEC (L10) → TASKS (L11) → Code
    │           │              │
    │           └──────────────┼─── Tests written first
    │                          │
    └──────────────────────────┴─── Implementation follows tests
```

## Usage

1. After SPEC approval, create TSPEC documents for each test type needed
2. Define test cases with I/O tables and pseudocode
3. Validate coverage matrices against upstream artifacts
4. Run quality gate validators
5. Pass TASKS-Ready threshold before creating TASKS

## Validation Commands

```bash
# Validate specific test type
python scripts/validate_utest.py docs/10_TSPEC/UTEST/UTEST-01_*.md
python scripts/validate_itest.py docs/10_TSPEC/ITEST/ITEST-01_*.md
python scripts/validate_stest.py docs/10_TSPEC/STEST/STEST-01_*.md
python scripts/validate_ftest.py docs/10_TSPEC/FTEST/FTEST-01_*.md

# Combined quality score
bash scripts/validate_tspec_quality_score.sh docs/10_TSPEC/

# Batch all types
bash scripts/validate_all_tspec.sh docs/10_TSPEC/
```

## Runtime Test Infrastructure

The TSPEC layer includes runtime infrastructure for test execution, tracking, and regression detection.

### Test Registry System

Central catalog for all tests with metadata and traceability:

| File | Purpose |
|------|---------|
| `test_registry_schema.yaml` | JSON Schema for registry validation |
| `test_registry.yaml` | Central test catalog |
| `test_result_schema.yaml` | Schema for test result files |
| `scripts/manage_test_registry.py` | Registry management CLI |

**Registry Commands**:
```bash
# Initialize empty registry
python scripts/manage_test_registry.py --init

# Sync tests from filesystem
python scripts/manage_test_registry.py --sync

# Add test manually
python scripts/manage_test_registry.py --add UTEST-001 UTEST "Test name" "tests/unit/test_file.py::test_func"

# List all tests
python scripts/manage_test_registry.py --list

# Filter by type
python scripts/manage_test_registry.py --list --type UTEST

# Validate registry consistency
python scripts/manage_test_registry.py --validate

# Generate registry report
python scripts/manage_test_registry.py --report
```

### Test Execution

Project-level test runner with unified configuration:

| File | Location | Purpose |
|------|----------|---------|
| `pytest.ini` | Project root | Pytest configuration |
| `pyproject.toml` | Project root | Coverage and tool config |
| `tests/conftest.py` | tests/ | Shared fixtures |
| `scripts/run_tests.py` | scripts/ | Unified test runner |

**Test Execution Commands**:
```bash
# Run by type
python scripts/run_tests.py --type utest
python scripts/run_tests.py --type itest
python scripts/run_tests.py --type stest
python scripts/run_tests.py --type ftest
python scripts/run_tests.py --type all

# Save results for comparison
python scripts/run_tests.py --type utest --save

# Run with coverage
python scripts/run_tests.py --type all --coverage
```

### Regression Detection

Compare test results between runs to detect regressions:

| File | Purpose |
|------|---------|
| `scripts/compare_test_results.py` | Regression detection |
| `scripts/archive_test_results.py` | Result archival |

**Comparison Commands**:
```bash
# Compare two result files
python scripts/compare_test_results.py baseline.json current.json

# Compare latest results in directory
python scripts/compare_test_results.py --latest tests/results/

# Output as JSON
python scripts/compare_test_results.py --json baseline.json current.json
```

### Coverage Reports

Track and enforce coverage thresholds:

| File | Purpose |
|------|---------|
| `scripts/generate_coverage_report.py` | Coverage generation |
| `tests/coverage_html/` | HTML reports |
| `tests/results/coverage.json` | JSON coverage data |

**Coverage Commands**:
```bash
# Generate coverage report
python scripts/generate_coverage_report.py --type all --html

# Check threshold
python scripts/generate_coverage_report.py --check --threshold 80

# View trend
python scripts/generate_coverage_report.py --trend
```

### CI/CD Integration

GitHub Actions workflow at `.github/workflows/test-pipeline.yml`:

- Unit tests run on every push
- Integration tests run after unit tests pass
- Smoke tests run on main branch deployments
- Coverage reports generated and archived
- Regression detection on pull requests

### Test Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_config.yaml         # Test environment config
├── unit/                    # UTEST (Code 40)
│   ├── conftest.py
│   └── test_*.py
├── integration/             # ITEST (Code 41)
│   ├── conftest.py
│   └── test_*.py
├── smoke/                   # STEST (Code 42)
│   ├── conftest.py
│   └── test_*.py
├── functional/              # FTEST (Code 43)
│   ├── conftest.py
│   └── test_*.py
└── results/                 # Test result archives
```

---

## See Also

- [TSPEC-00_index.md](TSPEC-00_index.md) - Master index of all test specifications
- [TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md](TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md) - Combined matrix template
- [TESTING_STRATEGY_TDD.md](../TESTING_STRATEGY_TDD.md) - TDD workflow overview
- [TRACEABILITY.md](../TRACEABILITY.md) - Full traceability chain
- [tests/README.md](../../tests/README.md) - Test directory documentation
