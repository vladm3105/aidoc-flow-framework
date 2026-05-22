---
name: doc-procspec-validator
description: Validate process-spec SPEC (Layer 6) documents against the framework SPEC contract with a process/workflow-design focus
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: process-design
    deliverable_type: document
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN, Code]
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-procspec-validator

Validate **process-spec SPEC (Layer 6)** documents against the framework SPEC
contract, with a focus on the process/workflow-design aspects of a component
specification (steps, roles, decision points, error handling, verification).
This is a plugin-only authoring helper: a process-design specialization of SPEC.
It validates against the single SPEC template — it does not define its own
template.

## Activation

Invoke when the user requests validation of a process-focused SPEC document, or
after creating/modifying the process/workflow sections of a SPEC artifact.

## Specialization

- **Parent**: `../doc-spec/` (SPEC, Layer 6)
- **Template**: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` (the single SPEC
  template — reference, do not redefine)
- **Focus**: the behavior/workflow facets of a SPEC — process steps, roles,
  decision branches, error handling, and verification

## Validation Checklist

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `spec-document` |
| `artifact_type` | Yes | `SPEC` |
| `spec_focus` | Yes | `process-design` |
| `layer` | Yes | `6` |

### 2. Process Content Validation

- [ ] Process steps numbered with logical sequence
- [ ] Roles/responsibilities defined per step
- [ ] Decision points marked with branch conditions and outcomes
- [ ] Error handling and recovery steps documented
- [ ] Verification/completion criteria included

### 3. Traceability

Required upstream tags (per `framework/governance/ID_NAMING_STANDARDS.md`):
- `@brd: BRD.NN.SS.xxxx`, `@prd: PRD.NN.SS.xxxx`
- `@ears: EARS.NN.SS.xxxx`, `@bdd: BDD.NN.SS.xxxx`
- `@adr: ADR-NN` (or element-level `@adr: ADR.NN.SS.xxxx`)
- `@spec: SPEC-NN` (this document)

### 4. TDD-Ready Score

| Component | Weight | Minimum |
|-----------|--------|---------|
| Step Completeness | 25% | 100% |
| Role Assignment | 20% | 90% |
| Decision Points | 15% | 90% |
| Error Handling | 15% | 85% |
| Verification Steps | 15% | 85% |
| Traceability | 10% | 100% |

**Target**: TDD-Ready ≥85%

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| SPEC-E001 | Error | Missing or incomplete process steps |
| SPEC-E002 | Error | Missing role assignment |
| SPEC-E003 | Error | Missing `document_type` |
| SPEC-W001 | Warning | Upstream traceability tag missing |
| SPEC-W002 | Warning | TDD-Ready score below threshold |

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guide: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
