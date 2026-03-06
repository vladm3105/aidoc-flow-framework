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

Comprehensive validation infrastructure for TSPEC (Test Specification) documents. Includes individual validators for 6 test types, pre-commit hooks, batch validation tools, and error code integration.

**Status**: Production-ready (v2.0 - 2026-03-06)
**Features**: Schema validation, error codes, JSON output, pre-commit hooks

## Scripts

| Script | Test Type | Description |
|--------|-----------|-------------|
| `validate_utest.py` | Unit Test | Validates UTEST documents |
| `validate_itest.py` | Integration Test | Validates ITEST documents |
| `validate_stest.py` | Smoke Test | Validates STEST documents |
| `validate_ftest.py` | Functional Test | Validates FTEST documents |
| `validate_ptest.py` | Performance Test | Validates PTEST documents |
| `validate_sectest.py` | Security Test | Validates SECTEST documents |
| `validate_tspec_quality_score.sh` | All | Combined quality score (6 types) |
| `validate_all_tspec.sh` | All | Basic batch validation |
| `validate_all_tspec_enhanced.sh` | All | **Enhanced batch validator (v2.0)** |
| `error_code_helpers.py` | Helper | Error code utilities |
| `tspec_core_validator_hook.sh` | Hook | Pre-commit core validation |
| `tspec_quality_gate_hook.sh` | Hook | Pre-commit quality gate |
| `tspec_tasks_ready_hook.sh` | Hook | Pre-commit TASKS-Ready check |

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
# Basic batch validation
bash validate_all_tspec.sh ../../docs/10_TSPEC/

# Enhanced batch validation (v2.0 - recommended)
bash validate_all_tspec_enhanced.sh ../../docs/10_TSPEC/

# With verbose output and color
bash validate_all_tspec_enhanced.sh --verbose --color ../../docs/10_TSPEC/

# JSON output for CI/CD
bash validate_all_tspec_enhanced.sh --json ../../docs/10_TSPEC/
```

### Pre-Commit Hooks

```bash
# Run specific hook
pre-commit run tspec-core-validator --all-files

# Run all TSPEC hooks
pre-commit run tspec-core-validator tspec-quality-gate tspec-tasks-ready --all-files
```

## Quality Gate Thresholds

| Test Type | Pass Threshold |
|-----------|----------------|
| UTEST | ≥90% |
| ITEST | ≥85% |
| STEST | 100% |
| FTEST | ≥85% |
| PTEST | ≥85% |
| SECTEST | ≥90% |

## Exit Codes

**v2.0 Three-Level System**:

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Pass | All checks passed, no warnings |
| 1 | Warnings | Warnings only, can proceed with caution |
| 2 | Errors | Errors present, must fix before proceeding |

**Legacy** (for compatibility):
- `2`: Also used for file not found or parse errors
- `3`: Schema validation failed (deprecated - now returns 2)

## Output Format

### Summary

```
[PASS] UTEST-01_auth_service.md: PASS (92%)
[FAIL] ITEST-01_data_service.md: FAIL (78%)
[PASS] STEST-01_deployment.md: PASS (100%)
```

### Detailed

```
UTEST-01_auth_service.md
========================
Status: PASS
Overall Score: 92%

Quality Gates:
  GATE-01 REQ Coverage:    95% (30/30)  [PASS]
  GATE-02 I/O Tables:      100% (25/25) [PASS]
  GATE-03 Category Prefix: 100% (25/25) [PASS]
  GATE-04 Pseudocode:      80% (20/25)  [WARN]
  GATE-05 Error Cases:     88% (22/25)  [PASS]

Issues:
  - TSPEC.01.40.15: Missing pseudocode
  - TSPEC.01.40.18: Missing error cases
```

## Error Codes (v2.0)

Validators use standardized error codes from the central registry.

**Format**: `[CODE] Message (context)`

**Examples**:
```
[UTEST-E002] Missing I/O table (TC-001)
[TSPEC-E007] Missing Traceability section (missing @spec reference)
[UTEST-W001] Low pseudocode coverage (TC-003)
```

**Registry**: `ai_dev_ssd_flow/scripts/error_codes.py` (lines 227-281)
**Total Codes**: 38 (33 general TSPEC + 5 type-specific per validator)

## Features (v2.0)

### Schema Validation
- Validates YAML frontmatter against MVP schemas
- Flexible path resolution (nested/flat structures)
- Graceful degradation without jsonschema

### Enhanced Batch Validator
- 6 CLI options: `--verbose`, `--quality-gates`, `--json`, `--color`, `--no-color`, `--help`
- Color-coded output with auto-detection
- Per-type statistics
- Machine-readable JSON mode

### Pre-Commit Integration
- 3 hooks: core validator, quality gate, TASKS-Ready
- Automatic validation before commits
- File pattern matching for TSPEC documents

### File Exclusions
Automatically excludes:
- Templates (`*TEMPLATE*`)
- Fix plans (`*FIX_PLAN*`)
- Reserved IDs (`TYPE-00_*`)
- Report files (`.A_audit_report*`, `.R_review_report*`, `.F_fix_report*`, `.V_validation_report*`)

## Dependencies

- Python 3.9+
- PyYAML
- jsonschema (optional - for schema validation)
- bc (for bash score calculations)

## Documentation

### Implementation Reports
- Gap Analysis: `/opt/data/b-local/b-local-docs/tmp/TSPEC_PLAN_GAP_ANALYSIS_2026-03-06.md`
- Phase 1 Completion: `/opt/data/b-local/b-local-docs/tmp/TSPEC_PHASE1_COMPLETION_REPORT_2026-03-06.md`
- Phase 2 Completion: `/opt/data/b-local/b-local-docs/tmp/TSPEC_PHASE2_COMPLETION_REPORT_2026-03-06.md`
- Final Summary: `/opt/data/b-local/b-local-docs/tmp/TSPEC_IMPLEMENTATION_FINAL_SUMMARY_2026-03-06.md`

### Validation Rules
- [../UTEST/UTEST_MVP_VALIDATION_RULES.md](../UTEST/UTEST_MVP_VALIDATION_RULES.md)
- [../ITEST/ITEST_MVP_VALIDATION_RULES.md](../ITEST/ITEST_MVP_VALIDATION_RULES.md)
- [../STEST/STEST_MVP_VALIDATION_RULES.md](../STEST/STEST_MVP_VALIDATION_RULES.md)
- [../FTEST/FTEST_MVP_VALIDATION_RULES.md](../FTEST/FTEST_MVP_VALIDATION_RULES.md)

---

**Version**: 2.0
**Last Updated**: 2026-03-06
**Status**: Production Ready
