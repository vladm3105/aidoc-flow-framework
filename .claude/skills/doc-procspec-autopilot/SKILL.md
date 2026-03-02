---
name: doc-procspec-autopilot
description: Automated PROCSPEC (Process Specification) generation from REQ - generates specifications for SOPs, runbooks, playbooks, and operational procedures
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - procspec-artifact
    - automation-workflow
  custom_fields:
    layer: 9
    subtype_code: 54
    artifact_type: PROCSPEC
    deliverable_type: process
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [REQ]
    downstream_artifacts: [TSPEC, TASKS]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-procspec-autopilot

## Purpose

Automated **Process Specification (PROCSPEC)** generation pipeline that processes REQ documents to generate specifications for operational procedures including SOPs, runbooks, playbooks, and checklists.

**Layer**: 9.54 (PROCSPEC - Process Specifications)

**Upstream**: REQ (Layer 7)

**Downstream**: TSPEC (Layer 10), TASKS (Layer 11)

---

## When to Use

Use `doc-procspec-autopilot` when:
- REQ documents have `deliverable_type: process`
- Creating Standard Operating Procedures (SOPs)
- Generating runbook specifications
- Creating playbook requirements
- Specifying operational checklists

---

## Document Type Contract (MANDATORY)

When generating PROCSPEC document instances, the autopilot MUST:

1. **Read** `instance_document_type` from template:
   - Source: `ai_dev_ssd_flow/09_SPEC/PROCSPEC/PROCSPEC-MVP-TEMPLATE.yaml`
   - Field: `metadata.instance_document_type: "procspec-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: procspec-document
     artifact_type: PROCSPEC
     deliverable_type: process
     layer: 9
     subtype_code: 54
   ```

---

## Process Element Types

| Element Type | Code | Description |
|--------------|------|-------------|
| SOP | 70 | Standard Operating Procedure |
| Runbook | 71 | Operational runbook |
| Playbook | 72 | Response playbook |
| Checklist | 73 | Verification checklist |

---

## PROC-Ready Score Components

| Component | Weight | Target |
|-----------|--------|--------|
| Step Completeness | 25% | 100% |
| Role Assignment | 20% | ≥90% |
| Decision Points | 15% | ≥90% |
| Error Handling | 15% | ≥85% |
| Verification Steps | 15% | ≥85% |
| Traceability | 10% | 100% |

**Target**: PROC-Ready ≥85%

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/PROCSPEC/PROCSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/PROCSPEC/PROCSPEC_MVP_SCHEMA.yaml`
