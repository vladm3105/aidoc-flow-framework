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
---

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
  template_source: "EARS-TEMPLATE.md"
  schema_reference: "EARS_SCHEMA.yaml"
  schema_version: "1.0"
  schema_status: optional
  creation_rules_reference: "EARS_CREATION_RULES.md"
  validation_rules_reference: "EARS_VALIDATION_RULES.md"
  traceability_matrix_template: "EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md"
---

> **MVP Template** — Single-file, streamlined EARS for logic mapping.
> MVP Note: Single flat file; do not use `DOCUMENT_SPLITTING_RULES.md`.
> Use this template to translate PRD features into Atomic Logic for code generation.

> **Validation Note**: MVP templates are intentionally streamlined and will show validation errors when run against full template validators. This is expected behavior.

> References: Full Template `EARS-TEMPLATE.md` | Schema `EARS_SCHEMA.yaml` | Rules `EARS_CREATION_RULES.md`, `EARS_VALIDATION_RULES.md` | Matrix `EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md`

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

## Migration to Full EARS Template

### When to Migrate
- [ ] Logic becomes too complex for simple list
- [ ] Need detailed State Transition Diagrams
- [ ] Need comprehensive quality attribute mapping

### Migration Steps
1. Create `EARS-TEMPLATE.md`
2. Copy logic statements to Section 3
3. Expand Quality Attributes matrices
4. Archive MVP version

---

**Document Version**: 0.1.0 (MVP)
