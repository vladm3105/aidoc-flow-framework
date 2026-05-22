---
name: doc-cspec-autopilot
description: Automated generation of component-focused SPEC (Layer 6) documents - produces implementation-ready YAML specifications for source-code components from upstream BRD/PRD/EARS/BDD/ADR
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-component-helper
    - automation-workflow
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: component
    deliverable_type: code
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-cspec-autopilot

## Purpose

Automated pipeline that generates **component-focused SPEC** documents — the
component-design specialization of SPEC (Layer 6). It processes upstream
artifacts to produce implementation-ready YAML specifications for source-code
components (interfaces, data models, behavior contracts).

This skill is a **SPEC (Layer 6) specialization**. It authors SPEC documents
with a component-design focus and references the single canonical artifact
contract `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` (see `../doc-spec/`); it
does **not** define a separate artifact, template, or element-code.

**Layer**: 6 (SPEC — component focus)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4),
ADR (Layer 5)

**Downstream**: TDD (Layer 7), IPLAN (Layer 8), Code

---

## When to Use

Use `doc-cspec-autopilot` when:
- Upstream artifacts describe a software component with `deliverable_type: code`
- ADR architecture decisions exist for the component to be specified
- Generating specifications for source code implementation
- Creating YAML specs for services, libraries, modules

---

## Document Type Contract (MANDATORY)

When generating SPEC document instances, the autopilot MUST:

1. **Read** `document_type` from the canonical template:
   - Source: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
   - Field: `metadata.document_type: "spec-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   metadata:
     document_type: spec-document    # NOT "template"
     artifact_type: SPEC
     deliverable_type: code
     layer: 6
   ```

3. **Validation**: Generated documents MUST have `document_type: spec-document`

---

## Skill Dependencies

| Skill | Purpose | Phase |
|-------|---------|-------|
| `../doc-naming/` | Element ID format (`TYPE.NN.SS.xxxx`; SPEC docs use `SPEC-NN`) | All Phases |
| `../doc-spec/` | Canonical SPEC authoring contract (parent skill) | All Phases |
| `../doc-cspec-validator/` | Validation with TDD-Ready scoring | Phase 4 |
| `../doc-cspec-reviewer/` | Content review, quality scoring | Phase 5 |

---

## Execution Phases

### Phase 1: Input Analysis
- Identify upstream artifacts (BRD/PRD/EARS/BDD/ADR) for the component
- Locate the governing ADR architecture decisions
- Extract interface and data-model intent from upstream sources

### Phase 2: Readiness Validation
- Verify upstream SPEC-Ready inputs are present
- Verify ADR decisions are complete
- Check all dependencies are satisfied

### Phase 3: SPEC Generation
- Create SPEC YAML from `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Map upstream requirements to specification elements
- Define interfaces, data models, and behavior contracts
- Add implementation notes (classes, methods, algorithms)

### Phase 4: Validation
- Run `../doc-cspec-validator/`
- Check TDD-Ready score ≥90%
- Verify behavior contracts complete

### Phase 5: Review
- Run `../doc-cspec-reviewer/`
- Generate audit report
- Apply fixes if needed via `../doc-cspec-fixer/`

---

## Output Structure

```
06_SPEC/SPEC-NN_{slug}/
├── SPEC-NN_{slug}.yaml        # Primary SPEC document (component focus)
├── SPEC-NN.0_index.md         # Index (if split needed)
└── SPEC-NN.A_audit_report.md  # Audit report
```

---

## TDD-Ready Score Components

| Component | Weight | Target |
|-----------|--------|--------|
| Interface Completeness | 20% | 100% |
| Behavior Contracts | 20% | 100% |
| Algorithm Specification | 15% | ≥90% |
| Error Handling | 15% | ≥90% |
| TDD Contract Mapping | 15% | ≥90% |
| Traceability | 15% | 100% |

**Target**: TDD-Ready ≥90%

---

## References

- Canonical SPEC artifact contract: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer overview: `framework/layers/06_SPEC/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent SPEC skill: `../doc-spec/`
