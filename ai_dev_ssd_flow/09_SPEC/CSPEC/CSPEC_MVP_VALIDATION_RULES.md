---
title: "CSPEC MVP Validation Rules"
tags:
  - validation-rules
  - layer-9-artifact
  - cspec-subtype
custom_fields:
  document_type: rules
  artifact_type: CSPEC
  layer: 9
  subtype_code: 50
---

# CSPEC MVP Validation Rules

## Purpose

Validation checklist for Code Specification (CSPEC) documents after creation.

## Validation Checklist

### Structure Validation

- [ ] File is valid YAML
- [ ] File name matches `CSPEC-NN_name.yaml` format
- [ ] All required sections present
- [ ] `instance_document_type: cspec-document`
- [ ] `deliverable_type: code`

### Metadata Validation

- [ ] Version is semantic version format (X.Y.Z)
- [ ] Status is valid (draft, review, approved, implemented)
- [ ] Dates are YYYY-MM-DD format
- [ ] At least one author specified
- [ ] `ctr_required: true`

### Traceability Validation

- [ ] REQ reference present (required)
- [ ] CTR reference present (required for CSPEC)
- [ ] All cumulative tags complete (BRD through REQ)
- [ ] Downstream artifacts defined (TASKS, code paths)
- [ ] Element IDs use CSPEC.NN.TT.SS format

### Interface Validation

- [ ] At least one class or API defined
- [ ] Each class has at least one method
- [ ] Method signatures include types
- [ ] External APIs reference CTR schemas
- [ ] Error handling defined for each interface

### Performance Validation

- [ ] latency_targets specified (p50, p95, p99)
- [ ] throughput_targets specified
- [ ] All targets use @threshold references
- [ ] Resource limits defined

### Security Validation

- [ ] Authentication requirements specified
- [ ] Authorization model defined
- [ ] Input validation strategy specified

### Verification Validation

- [ ] At least one BDD scenario referenced
- [ ] Test coverage targets specified
- [ ] Integration test dependencies listed

### Implementation Validation

- [ ] Language specified
- [ ] Module path specified
- [ ] Runtime dependencies listed
- [ ] Environment variables documented

## TASKS-Ready Score Calculation

| Criterion | Weight | Check |
|-----------|--------|-------|
| Interface Completeness | 25% | All interfaces fully specified with types |
| Error Handling | 20% | Error codes and recovery strategies |
| Test Coverage Plan | 20% | BDD, unit, integration references |
| Traceability | 20% | All upstream/downstream links |
| Implementation Guidance | 15% | Language, framework, paths |

**Target**: >= 90%

## Error Codes

| Code | Severity | Message |
|------|----------|---------|
| CSPEC-E001 | Error | File is not valid YAML |
| CSPEC-E002 | Error | Missing required field |
| CSPEC-E003 | Error | deliverable_type must be 'code' |
| CSPEC-E004 | Error | Missing CTR reference |
| CSPEC-E005 | Error | Missing REQ reference |
| CSPEC-E006 | Error | No interfaces defined |
| CSPEC-E007 | Error | No implementation language |
| CSPEC-W001 | Warning | Performance not using @threshold |
| CSPEC-W002 | Warning | Missing method types |
| CSPEC-W003 | Warning | Missing BDD references |

---

**Rules Version**: 1.0
**Last Updated**: 2026-03-01
