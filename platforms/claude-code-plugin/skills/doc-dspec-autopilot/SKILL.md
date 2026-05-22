---
name: doc-dspec-autopilot
description: Automated data-spec SPEC (Layer 6) generation - authors component specifications with a data-design focus (data models, schemas, field definitions)
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - automation-workflow
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: data-design
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN, Code]
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-dspec-autopilot

## Purpose

Automated **data-spec SPEC** generation pipeline that authors SPEC (Layer 6)
documents with a data-design focus — data models, schemas, and field
definitions — from the upstream chain (BRD, PRD, EARS, BDD, ADR). This is a
plugin-only authoring helper: a data-design specialization of SPEC. It
generates against the single framework SPEC template; it does not define its
own template or subtype code.

**Layer**: 6 (SPEC — data-design focus)

**Parent**: `../doc-spec/`

**Upstream**: BRD, PRD, EARS, BDD, ADR

**Downstream**: TDD (Layer 7), IPLAN (Layer 8), Code

---

## When to Use

Use `doc-dspec-autopilot` when:
- The component being specified is data-centric (data models, schemas, stores)
- Upstream EARS/BDD define data-shaped state and behavior
- You want a SPEC focused on data structures and field-level contracts
- Defining the data interfaces a downstream TDD will test

---

## Document Type Contract (MANDATORY)

When generating SPEC document instances, the autopilot MUST:

1. **Read** the template at
   `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
   (field `metadata.document_type: "spec-document"`).

2. **Set** `document_type` in the generated document frontmatter:
   ```yaml
   metadata:
     document_type: spec-document    # NOT "template"
     artifact_type: SPEC
     deliverable_type: code
     layer: 6
   ```

3. **Validation**: Generated documents MUST have `document_type: spec-document`.

---

## Data-Design Emphasis

Within the unified SPEC template, this skill concentrates on:

| SPEC Section | Data-Design Emphasis |
|--------------|----------------------|
| Section 4 — Data Models | Primary: typed fields, required flags, constraints |
| Section 3 — Interfaces | Data-carrying signatures and return shapes |
| Section 5 — Behavior | Validation rules over data; data state transitions |
| Section 7 — TDD Contracts | Data-model and schema test coverage |

---

## Skill Dependencies

| Skill | Purpose | Phase |
|-------|---------|-------|
| `../doc-naming/` | Element ID format (`SPEC-NN`, `TYPE.NN.SS.xxxx`) | All Phases |
| `../doc-dspec-validator/` | Validation with TDD-Ready scoring | Phase 4 |
| `../doc-dspec-reviewer/` | Content review, quality scoring | Phase 5 |
| `../doc-dspec-fixer/` | Apply review fixes | Phase 5 |

---

## Execution Phases

### Phase 1: Input Analysis
- Read the upstream chain (BRD, PRD, EARS, BDD, ADR)
- Identify the data-centric component to specify
- Extract data requirements from EARS/BDD

### Phase 2: Readiness Validation
- Verify upstream ADR and BDD are ready
- Check all dependencies are satisfied
- Confirm the architecture decision (`@adr: ADR-NN`) is resolved

### Phase 3: SPEC Generation
- Create the SPEC YAML from `SPEC-TEMPLATE.yaml`
- Map data requirements to Section 4 (Data Models)
- Define interfaces, behavior, and implementation notes
- Populate downstream TDD contract references

### Phase 4: Validation
- Run `../doc-dspec-validator/`
- Check TDD-Ready score ≥85%
- Verify data-model coverage

### Phase 5: Review
- Run `../doc-dspec-reviewer/`
- Generate the audit report
- Apply fixes if needed via `../doc-dspec-fixer/`

---

## Output Structure

```
framework/layers/06_SPEC/SPEC-NN_{slug}/
├── SPEC-NN_{slug}.yaml        # Primary SPEC document
├── SPEC-NN.0_index.md         # Index (if split needed)
└── SPEC-NN.A_audit_report.md  # Audit report
```

---

## TDD-Ready Score Components

| Component | Weight | Target |
|-----------|--------|--------|
| Data-Model Coverage | 25% | 100% |
| Interface Completeness | 20% | ≥90% |
| Behavior Specification | 20% | ≥90% |
| Implementation Notes | 15% | ≥85% |
| Downstream TDD Contract | 10% | ≥85% |
| Traceability | 10% | 100% |

**Target**: TDD-Ready ≥85%

---

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guide: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
