---
title: "TSPEC-00: Test Specifications Master Index"
tags:
  - layer-10-artifact
  - tspec-index
  - document-index
  - shared-architecture
custom_fields:
  document_type: index
  artifact_type: TSPEC
  layer: 10
  priority: shared
  development_status: active
---

# TSPEC-00: Test Specifications Master Index

## Purpose

Central registry for all TSPEC documents organized by test type. This index provides quick navigation and coverage tracking across unit, integration, smoke, and functional test specifications.

## Document Registry

### Unit Test Specifications (UTEST)

| ID | Document | SPEC Ref | REQ Coverage | Status |
|----|----------|----------|--------------|--------|
| UTEST-01 | [Template] | - | - | Template |

### Integration Test Specifications (ITEST)

| ID | Document | CTR Ref | Component Coverage | Status |
|----|----------|---------|-------------------|--------|
| ITEST-01 | [Template] | - | - | Template |

### Smoke Test Specifications (STEST)

| ID | Document | Deployment Target | Timeout Budget | Status |
|----|----------|-------------------|----------------|--------|
| STEST-01 | [Template] | - | <5min | Template |

### Functional Test Specifications (FTEST)

| ID | Document | SYS Ref | Quality Attributes | Status |
|----|----------|---------|-------------------|--------|
| FTEST-01 | [Template] | - | - | Template |

## Coverage Summary

### By Test Type

| Type | Documents | Test Cases | Coverage % | Quality Gate |
|------|-----------|------------|------------|--------------|
| UTEST | 0 | 0 | - | ≥90% target |
| ITEST | 0 | 0 | - | ≥85% target |
| STEST | 0 | 0 | - | 100% required |
| FTEST | 0 | 0 | - | ≥85% target |

### By Upstream Artifact

| Artifact | Covered Elements | Total Elements | Coverage % |
|----------|-----------------|----------------|------------|
| REQ | 0 | - | - |
| SPEC | 0 | - | - |
| CTR | 0 | - | - |
| SYS | 0 | - | - |
| EARS | 0 | - | - |
| BDD | 0 | - | - |

## Element ID Quick Reference

**Format**: `TSPEC.NN.TT.SS`

| Test Type | Code | Example |
|-----------|------|---------|
| Unit Test | 40 | `TSPEC.01.40.01` |
| Integration Test | 41 | `TSPEC.01.41.01` |
| Smoke Test | 42 | `TSPEC.01.42.01` |
| Functional Test | 43 | `TSPEC.01.43.01` |

## Validation Status

| Validator | Last Run | Pass/Fail | Issues |
|-----------|----------|-----------|--------|
| validate_utest.py | - | - | - |
| validate_itest.py | - | - | - |
| validate_stest.py | - | - | - |
| validate_ftest.py | - | - | - |

## Navigation

### Templates

- [UTEST-MVP-TEMPLATE.md](UTEST/UTEST-MVP-TEMPLATE.md) - Unit test template
- [ITEST-MVP-TEMPLATE.md](ITEST/ITEST-MVP-TEMPLATE.md) - Integration test template
- [STEST-MVP-TEMPLATE.md](STEST/STEST-MVP-TEMPLATE.md) - Smoke test template
- [FTEST-MVP-TEMPLATE.md](FTEST/FTEST-MVP-TEMPLATE.md) - Functional test template

### Rules & Quality Gates

- [UTEST_MVP_QUALITY_GATES.md](UTEST/UTEST_MVP_QUALITY_GATES.md)
- [ITEST_MVP_QUALITY_GATES.md](ITEST/ITEST_MVP_QUALITY_GATES.md)
- [STEST_MVP_QUALITY_GATES.md](STEST/STEST_MVP_QUALITY_GATES.md)
- [FTEST_MVP_QUALITY_GATES.md](FTEST/FTEST_MVP_QUALITY_GATES.md)

### Examples

- [UTEST-01_auth_service.md](examples/UTEST-01_auth_service.md)
- [ITEST-01_auth_service.md](examples/ITEST-01_auth_service.md)
- [STEST-01_auth_service.md](examples/STEST-01_auth_service.md)
- [FTEST-01_auth_service.md](examples/FTEST-01_auth_service.md)

## Cross-Layer References

| Layer | Artifact | Relationship |
|-------|----------|--------------|
| L7 | REQ | Tests validate requirements |
| L8 | CTR | Integration tests verify contracts |
| L9 | SPEC | Tests derived from specifications |
| L11 | TASKS | Test implementation tasks generated |

## Maintenance Notes

- Update this index when adding new TSPEC documents
- Run coverage summary after each sprint
- Archive completed test specs after production release
