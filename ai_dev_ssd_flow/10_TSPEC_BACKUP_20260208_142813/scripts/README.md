---
title: "TSPEC Validation Scripts"
tags:
  - scripts
  - validation
  - layer-10-artifact
custom_fields:
  document_type: scripts-readme
  artifact_type: TSPEC
  layer: 10
  development_status: active
---

# TSPEC Validation Scripts

## Overview

Validation scripts for TSPEC (Test Specification) documents. Each script validates a specific test type and calculates quality gate scores.

## Scripts

| Script | Test Type | Description |
|--------|-----------|-------------|
| `validate_utest.py` | Unit Test | Validates UTEST documents |
| `validate_itest.py` | Integration Test | Validates ITEST documents |
| `validate_stest.py` | Smoke Test | Validates STEST documents |
| `validate_ftest.py` | Functional Test | Validates FTEST documents |
| `validate_tspec_quality_score.sh` | All | Combined quality score |
| `validate_all_tspec.sh` | All | Batch validation |
| `run_tests.py` | All | Unified test runner |
| `compare_test_results.py` | All | Regression detection |
| `archive_test_results.py` | All | Result archival |
| `generate_coverage_report.py` | All | Coverage reporting |
| `manage_test_registry.py` | All | Test registry management |

## Usage

### Individual Validators

```bash
# Validate unit test specification
python validate_utest.py ../../docs/10_TSPEC/UTEST/UTEST-01_*.md

# Validate integration test specification
python validate_itest.py ../../docs/10_TSPEC/ITEST/ITEST-01_*.md

# Validate smoke test specification
python validate_stest.py ../../docs/10_TSPEC/STEST/STEST-01_*.md

# Validate functional test specification
python validate_ftest.py ../../docs/10_TSPEC/FTEST/FTEST-01_*.md
```

### Options

| Option | Description |
|--------|-------------|
| `--verbose` | Show detailed validation output |
| `--quality-gates` | Show quality gate breakdown |
| `--json` | Output results as JSON |
| `--fix` | Attempt auto-fix for common issues |

### Combined Score

```bash
# Calculate combined quality score for all TSPEC types
bash validate_tspec_quality_score.sh ../../docs/10_TSPEC/
```

### Batch Validation

```bash
# Validate all TSPEC documents
bash validate_all_tspec.sh ../../docs/10_TSPEC/
```

## Quality Gate Thresholds

| Test Type | Pass Threshold |
|-----------|----------------|
| UTEST | ≥90% |
| ITEST | ≥85% |
| STEST | 100% |
| FTEST | ≥85% |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All validations passed |
| 1 | Validation errors found |
| 2 | File not found or parse error |
| 3 | Schema validation failed |

## Output Format

### Summary

```
✅ UTEST-01_auth_service.md: PASS (92%)
❌ ITEST-01_data_service.md: FAIL (78%)
✅ STEST-01_deployment.md: PASS (100%)
```

### Detailed

```
UTEST-01_auth_service.md
========================
Status: PASS
Overall Score: 92%

Quality Gates:
  GATE-01 REQ Coverage:    95% (30/30)  ✅
  GATE-02 I/O Tables:      100% (25/25) ✅
  GATE-03 Category Prefix: 100% (25/25) ✅
  GATE-04 Pseudocode:      80% (20/25)  ⚠️
  GATE-05 Error Cases:     88% (22/25)  ✅

Issues:
  - TSPEC.01.40.15: Missing pseudocode
  - TSPEC.01.40.18: Missing error cases
```

## Dependencies

- Python 3.9+
- PyYAML
- jsonschema (for schema validation)

## See Also

- [../UTEST/UTEST_MVP_VALIDATION_RULES.md](../UTEST/UTEST_MVP_VALIDATION_RULES.md)
- [../ITEST/ITEST_MVP_VALIDATION_RULES.md](../ITEST/ITEST_MVP_VALIDATION_RULES.md)
- [../STEST/STEST_MVP_VALIDATION_RULES.md](../STEST/STEST_MVP_VALIDATION_RULES.md)
- [../FTEST/FTEST_MVP_VALIDATION_RULES.md](../FTEST/FTEST_MVP_VALIDATION_RULES.md)
