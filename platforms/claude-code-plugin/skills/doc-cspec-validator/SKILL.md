---
name: doc-cspec-validator
description: Validate component-focused SPEC (Layer 6) documents against the framework SPEC contract
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-component-helper
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: component
    deliverable_type: code
    architecture_approaches: [ai-agent-based]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC]
    downstream_artifacts: []
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-cspec-validator

Validate component-focused **SPEC (Layer 6)** documents against the framework
SPEC contract.

This skill is a **SPEC (Layer 6) specialization** for the component-design
focus of SPEC. It validates against the single canonical artifact contract and
does **not** define a separate artifact, template, or element-code. The plugin
skill *is* the validator — there is no external validation script.

## Activation

Invoke when the user requests validation of a component-focused SPEC document,
or after creating/modifying such an artifact.

## Validation Contract Reference

- Canonical artifact contract: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer overview: `framework/layers/06_SPEC/README.md`
- Layer: 6 (SPEC — component focus)
- Artifact Type: SPEC
- Deliverable Type: code

## Validation Checklist

### 0. Folder Structure Validation (BLOCKING)

**Required Structure**:

| SPEC Type | Required Location |
|-----------|-------------------|
| YAML | `docs/06_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml` |

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `spec-document` |
| `artifact_type` | Yes | `SPEC` |
| `deliverable_type` | Yes | `code` |
| `layer` | Yes | `6` |

### 2. Behavior Contracts (component focus)

- [ ] Validation rules present and trace to EARS
- [ ] State transitions present and trace to BDD
- [ ] Error-handling responses defined

### 3. Interface Definitions

- [ ] All interfaces have complete signatures
- [ ] Parameter types are specified
- [ ] Return types are specified
- [ ] Error handling is defined

### 4. Implementation Notes

- [ ] Classes/modules are specified
- [ ] Methods have algorithms defined
- [ ] Dependencies are listed
- [ ] Configuration is documented

### 5. TDD Contract Mapping

- [ ] Downstream TDD document referenced (`@tdd: TDD-NN`)
- [ ] Test files mapped to interfaces
- [ ] Coverage requirements specified

### 6. Traceability

Required upstream tags:
- `@brd: BRD-NN`, `@prd: PRD-NN`, `@ears: EARS.NN.SS.xxxx`,
  `@bdd: BDD.NN.SS.xxxx`, `@adr: ADR-NN`
- Document-level self tag: `@spec: SPEC-NN`

### 7. TDD-Ready Score

| Component | Weight | Minimum |
|-----------|--------|---------|
| Interface Completeness | 20% | 100% |
| Behavior Contracts | 20% | 100% |
| Algorithm Specification | 15% | 90% |
| Error Handling | 15% | 90% |
| TDD Contract Mapping | 15% | 90% |
| Traceability | 15% | 100% |

**Target**: TDD-Ready ≥90%

## Validation Procedure (declarative)

This skill performs validation directly — there is no external script. Walk the
checklist above against the document, then:

1. Confirm the folder structure and YAML parse cleanly.
2. Confirm metadata fields match the table in section 1.
3. Confirm behavior contracts, interfaces, and TDD contract mapping are present.
4. Confirm all upstream tags resolve to existing documents.
5. Compute the TDD-Ready score; flag any component below its minimum.

For the authoritative rules, consult `framework/layers/06_SPEC/README.md`,
`framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`, and `framework/governance/`.

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| SPEC-E001 | Error | Missing required upstream tag |
| SPEC-E002 | Error | Incomplete interface definition |
| SPEC-E003 | Error | Missing algorithm specification |
| SPEC-W001 | Warning | TDD contract mapping incomplete |
| SPEC-W002 | Warning | TDD-Ready score below threshold |

## References

- Canonical SPEC artifact contract: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer overview: `framework/layers/06_SPEC/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent SPEC skill: `../doc-spec/`
