---
title: "EARS-MVP-TEMPLATE: EARS Requirements (MVP)"
tags:
  - ears-template
  - mvp-template
  - layer-3-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: EARS
  layer: 3
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.0"
---

> **🔄 Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `EARS-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `EARS_MVP_SCHEMA.yaml`
> - **Complete Explanation**: See [DUAL_MVP_TEMPLATES_ARCHITECTURE.md](../DUAL_MVP_TEMPLATES_ARCHITECTURE.md) for full comparison of formats, authority hierarchy, and when to use each.
> ---

<!--
AI_CONTEXT_START
Role: AI Logic Engineer
Objective: Create a streamlined MVP Engineering Requirements Document (EARS).
Constraints:
- Focus on pure logic mapping (Event -> Response).
- Use simple EARS syntax: WHEN [trigger] -> THE [system] SHALL [response].
- Omit complex state matrices unless critical.
- Maintain single-file structure.
AI_CONTEXT_END
-->
---
title: "EARS-MVP-TEMPLATE: Engineering Requirements (MVP Version)"
tags:
  - ears-template
  - mvp-template
  - layer-3-artifact
custom_fields:
  document_type: template
  artifact_type: EARS
  layer: 3
  architecture_approaches: [ai-agent-based]
  priority: shared
  development_status: draft
  template_variant: mvp
  template_profile: mvp
  template_source: "EARS-MVP-TEMPLATE.md"
  schema_reference: "EARS_MVP_SCHEMA.yaml"
  schema_version: "1.0"
  schema_status: optional
  creation_rules_reference: "EARS_MVP_CREATION_RULES.md"
  validation_rules_reference: "EARS_MVP_VALIDATION_RULES.md"
  traceability_matrix_template: "EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md"
---

> **MVP Template** — Single-file, streamlined EARS for logic mapping.
> MVP Note: Single flat file; split only if too large for AI assistants; otherwise ignore `DOCUMENT_SPLITTING_RULES.md`.
> Use this template to translate PRD features into Atomic Logic for code generation.

> **Validation Note**: MVP templates are intentionally streamlined and will show validation errors when run against full template validators. This is expected behavior.

> References: Schema `EARS_MVP_SCHEMA.yaml` | Rules `EARS_MVP_CREATION_RULES.md`, `EARS_MVP_VALIDATION_RULES.md` | Matrix `EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md`

# EARS-NN: [Target Component/Feature]

## 1. Document Control

| Item | Details |
|------|---------|
| **Version** | 0.1.0 |
| **Status** | Draft / Review / Approved |
| **Source PRD** | @prd: PRD-NN |

---

## 2. Requirements Logic

### 2.1 Event-Driven (When X then Y)

**EARS-NN-01: [Requirement Name]**
```
WHEN [trigger condition]
THE [system component] SHALL [response action]
WITHIN [timing constraint] (@threshold: PRD.NN.key)
```
**Traceability**: @prd: PRD.NN.feature | @threshold: PRD.NN.key

### 2.2 Unwanted Behavior (Error Handling)

**EARS-NN-05: [Error Scenario]**
```
IF [error condition]
THE [system component] SHALL [recovery action]
```
**Traceability**: @prd: PRD.NN.feature

### 2.3 State-Driven (While X then Y)

**EARS-NN-10: [State Behavior]**
```
WHILE [state condition]
THE [system component] SHALL [continuous behavior]
```
**Traceability**: @prd: PRD.NN.feature

---

---

**Document Version**: 0.1.0 (MVP)
