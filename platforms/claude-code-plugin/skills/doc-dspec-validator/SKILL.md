---
name: doc-dspec-validator
description: Validate data-spec SPEC (Layer 6) documents against the framework SPEC contract with a data-design focus
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: data-design
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN, Code]
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-dspec-validator

Validate **data-spec SPEC (Layer 6)** documents against the framework SPEC
contract, with a focus on the data-design aspects of a component specification
(data models, schemas, field definitions). This is a plugin-only authoring
helper: a data-design specialization of SPEC. It validates against the single
SPEC template — it does not define its own template.

## Activation

Invoke when the user requests validation of a data-focused SPEC document, or
after creating/modifying the data-model sections of a SPEC artifact.

## Specialization

- **Parent**: `../doc-spec/` (SPEC, Layer 6)
- **Template**: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` (the single SPEC
  template — reference, do not redefine)
- **Focus**: SPEC Section 4 (Data Models) and the data-design facets of
  Sections 3 (Interfaces) and 5 (Behavior)

## Validation Checklist

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `spec-document` |
| `artifact_type` | Yes | `SPEC` |
| `deliverable_type` | Yes | `code` |
| `layer` | Yes | `6` |

### 2. Component Overview

- [ ] Component purpose and role described
- [ ] `architecture_decision` references an ADR (`@adr: ADR-NN`)
- [ ] Language and dependencies specified

### 3. Data Models (primary focus)

- [ ] Data structures defined with typed fields
- [ ] Field types, required flags, and descriptions present
- [ ] Models map to upstream EARS/BDD data requirements
- [ ] No SQL/ORM implementation detail (specification, not source)

### 4. Interfaces

- [ ] Public exports defined with typed signatures
- [ ] Error conditions documented per export

### 5. Behavior

- [ ] Validation rules sourced from EARS (`@ears: EARS.NN.SS.xxxx`)
- [ ] State transitions sourced from BDD (`@bdd: BDD.NN.SS.xxxx`)
- [ ] Error handling defined

### 6. Downstream TDD Contracts

- [ ] References the downstream TDD document (`@tdd: TDD-NN`)
- [ ] Test files identified for data-model coverage

### 7. Traceability

Required upstream tags (per `framework/governance/ID_NAMING_STANDARDS.md`):
- `@brd: BRD-NN`, `@prd: PRD-NN`
- `@ears: EARS.NN.SS.xxxx`, `@bdd: BDD.NN.SS.xxxx`
- `@adr: ADR-NN` (or element-level `@adr: ADR.NN.SS.xxxx`)
- `@spec: SPEC-NN` (this document)

### 8. TDD-Ready Score

| Component | Weight | Minimum |
|-----------|--------|---------|
| Data-Model Coverage | 25% | 100% |
| Interface Completeness | 20% | 90% |
| Behavior Specification | 20% | 90% |
| Implementation Notes | 15% | 85% |
| Downstream TDD Contract | 10% | 85% |
| Traceability | 10% | 100% |

**Target**: TDD-Ready ≥85%

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| SPEC-E001 | Error | Missing or incomplete data models |
| SPEC-E002 | Error | Missing interface definition |
| SPEC-E003 | Error | Missing `document_type` |
| SPEC-W001 | Warning | Upstream traceability tag missing |
| SPEC-W002 | Warning | TDD-Ready score below threshold |

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guide: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
