---
name: doc-procspec-autopilot
description: Automated process-spec SPEC (Layer 6) generation - produces process/workflow specifications (SOPs, runbooks, playbooks, checklists) against the framework SPEC template
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - automation-workflow
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: process-design
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

# doc-procspec-autopilot

## Purpose

Automated **process-spec SPEC** generation pipeline that produces SPEC documents
with a process/workflow-design focus — operational procedures such as SOPs,
runbooks, playbooks, and checklists. This is a plugin-only authoring helper: a
process-design specialization of SPEC (Layer 6) that generates against the
single framework SPEC template — it does not define its own template.

**Layer**: 6 (SPEC — process/workflow design)

**Parent**: `../doc-spec/`

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5)

**Downstream**: TDD (Layer 7), IPLAN (Layer 8), Code

---

## When to Use

Use `doc-procspec-autopilot` when:
- A SPEC's focus is an operational process or workflow
- Creating Standard Operating Procedures (SOPs)
- Generating runbook specifications
- Creating playbook specifications
- Specifying operational checklists

---

## Document Type Contract (MANDATORY)

When generating process-spec SPEC instances, the autopilot MUST:

1. **Read** the canonical SPEC template:
   - Source: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`

2. **Set** the artifact fields in the generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: spec-document
     artifact_type: SPEC
     spec_focus: process-design
     layer: 6
   ```

---

## Process Specification Facets

The process focus shapes the SPEC content (not separate ID codes — the
8-layer model has no element-type-code scheme):

| Facet | Description |
|-------|-------------|
| SOP | Standard Operating Procedure |
| Runbook | Operational runbook |
| Playbook | Response playbook |
| Checklist | Verification checklist |

---

## TDD-Ready Score Components

| Component | Weight | Target |
|-----------|--------|--------|
| Step Completeness | 25% | 100% |
| Role Assignment | 20% | ≥90% |
| Decision Points | 15% | ≥90% |
| Error Handling | 15% | ≥85% |
| Verification Steps | 15% | ≥85% |
| Traceability | 10% | 100% |

**Target**: TDD-Ready ≥85%

---

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guide: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
