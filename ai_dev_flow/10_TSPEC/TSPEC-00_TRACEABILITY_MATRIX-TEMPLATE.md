---
title: "TSPEC-00: Test Specification Traceability Matrix Template"
tags:
  - layer-10-artifact
  - tspec-matrix
  - traceability-template
  - shared-architecture
custom_fields:
  document_type: traceability-matrix-template
  artifact_type: TSPEC
  layer: 10
  priority: shared
  development_status: active
---

# TSPEC-00: Test Specification Traceability Matrix Template

## Purpose

Template for creating combined traceability matrices that map test specifications to upstream requirements and downstream implementation artifacts.

---

## 1. REQ → UTEST Coverage Matrix

Maps requirements to unit test specifications.

| REQ ID | REQ Title | UTEST ID | Test Name | Category | Status |
|--------|-----------|----------|-----------|----------|--------|
| REQ.01.10.01 | [Requirement title] | TSPEC.01.40.01 | [Test name] | [Logic] | Planned |
| REQ.01.10.02 | [Requirement title] | TSPEC.01.40.02 | [Test name] | [Validation] | Planned |

**Coverage Summary**:
- Total REQ elements: [N]
- Covered by UTEST: [N] ([XX]%)
- Missing coverage: [List REQ IDs]

---

## 2. CTR → ITEST Coverage Matrix

Maps API contracts to integration test specifications.

| CTR Endpoint | Method | ITEST ID | Test Name | Components | Status |
|--------------|--------|----------|-----------|------------|--------|
| /api/v1/auth | POST | TSPEC.01.41.01 | [Test name] | Auth, DB | Planned |
| /api/v1/users | GET | TSPEC.01.41.02 | [Test name] | Users, Cache | Planned |

**Coverage Summary**:
- Total CTR endpoints: [N]
- Covered by ITEST: [N] ([XX]%)
- Missing coverage: [List endpoints]

---

## 3. EARS/BDD → STEST Coverage Matrix

Maps behavioral requirements to smoke test specifications.

| EARS/BDD ID | Scenario | STEST ID | Critical Path | Timeout | Status |
|-------------|----------|----------|---------------|---------|--------|
| EARS.01.25.01 | [Scenario] | TSPEC.01.42.01 | Auth Flow | 30s | Planned |
| BDD.01.01.01 | [Feature] | TSPEC.01.42.02 | Data Load | 45s | Planned |

**Coverage Summary**:
- Total critical paths: [N]
- Covered by STEST: [N] ([XX]%)
- Total timeout budget: [N]s / 300s max

---

## 4. SYS → FTEST Coverage Matrix

Maps system requirements to functional test specifications.

| SYS ID | Quality Attribute | FTEST ID | Test Name | Threshold | Status |
|--------|-------------------|----------|-----------|-----------|--------|
| SYS.01.01.01 | Performance | TSPEC.01.43.01 | [Test name] | <200ms | Planned |
| SYS.01.02.01 | Reliability | TSPEC.01.43.02 | [Test name] | 99.9% | Planned |

**Coverage Summary**:
- Total SYS quality attributes: [N]
- Covered by FTEST: [N] ([XX]%)
- Missing coverage: [List SYS IDs]

---

## 5. SPEC → Test Type Distribution

Maps specifications to appropriate test types.

| SPEC ID | Component | UTEST | ITEST | STEST | FTEST | Total |
|---------|-----------|-------|-------|-------|-------|-------|
| SPEC-01 | Auth Service | 5 | 3 | 2 | 1 | 11 |
| SPEC-02 | Data Service | 8 | 4 | 1 | 2 | 15 |

---

## 6. TSPEC → TASKS Forward Traceability

Maps test specifications to implementation tasks.

| TSPEC ID | Test Type | TASKS ID | Task Description | Status |
|----------|-----------|----------|------------------|--------|
| TSPEC.01.40.01 | UTEST | TASKS.01.01.01 | Implement auth unit tests | Planned |
| TSPEC.01.41.01 | ITEST | TASKS.01.02.01 | Implement auth integration tests | Planned |

---

## 7. Gap Analysis

### Uncovered Requirements

| REQ ID | REQ Title | Reason | Action |
|--------|-----------|--------|--------|
| [ID] | [Title] | [Why not covered] | [Planned action] |

### Uncovered Contracts

| CTR Endpoint | Reason | Action |
|--------------|--------|--------|
| [Endpoint] | [Why not covered] | [Planned action] |

### Missing Quality Attribute Tests

| SYS ID | Attribute | Reason | Action |
|--------|-----------|--------|--------|
| [ID] | [Attribute] | [Why not covered] | [Planned action] |

---

## 8. Quality Gate Summary

| Test Type | Document | Target | Actual | Status |
|-----------|----------|--------|--------|--------|
| UTEST | UTEST-01 | ≥90% | [XX]% | ✅/❌ |
| ITEST | ITEST-01 | ≥85% | [XX]% | ✅/❌ |
| STEST | STEST-01 | 100% | [XX]% | ✅/❌ |
| FTEST | FTEST-01 | ≥85% | [XX]% | ✅/❌ |

**Overall TASKS-Ready**: [YES/NO]

---

## Usage Instructions

1. Copy this template to project `docs/10_TSPEC/`
2. Replace placeholders with actual artifact references
3. Update coverage percentages after creating test specs
4. Run gap analysis before TASKS generation
5. Validate quality gates before proceeding to implementation
