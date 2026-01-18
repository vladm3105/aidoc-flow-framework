---
title: "REF-TEMPLATE: Reference Document"
tags:
  - ref-template
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: REF
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
---

# =============================================================================
# Reference Document Template
# For supplementary documentation that doesn't participate in formal traceability
# =============================================================================
# SCOPE: REF documents are LIMITED to BRD and ADR artifact types ONLY
# - BRD-REF: Business context reference documents
# - ADR-REF: Architecture reference documents
# =============================================================================
---
title: "REF-TEMPLATE: Reference Document"
tags:
  - ref-template
  - supplementary-documentation
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: REF
  layer: null
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  template_for: reference-document
  schema_reference: "none"
  valid_parent_types: [BRD, ADR]
---

# {TYPE}-REF-NN: [Document Title]

> **Scope**: REF documents are limited to **BRD and ADR** types only.
> **Ready-Scores**: NOT APPLICABLE - REF documents use free format with no scores.

## Document Control

| Item | Details |
|------|---------|
| **Parent Type** | [BRD or ADR only] |
| **Document Version** | [e.g., 1.0] |
| **Date** | [Current date] |
| **Author** | [Name] |
| **Status** | [Draft / Final] |

### Document Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.0 | [Date] | [Name] | Initial draft | |
| | | | | |

---

## 1. Introduction

### 1.1 Purpose

[Describe the purpose of this reference document. What information does it provide? Who is the intended audience?]

### 1.2 Scope

[Define what this document covers and what it does not cover.]

---

## 2. Content

[Main content of the reference document. Structure as needed for the specific use case.]

---

## 3. Related Documents (Optional)

> **Note**: Traceability is encouraged but not required for REF documents.

| Document Type | Document ID | Title | Relationship |
|---------------|-------------|-------|--------------|
| [TYPE] | [ID] | [Title] | [Describes/Supports/References] |

---

## 4. Template Usage Notes

**Scope**: REF documents are LIMITED to **BRD and ADR artifact types ONLY**.

**Naming Convention**: `{TYPE}-REF-NN_{slug}.md`
- `{TYPE}`: Parent artifact type (**BRD or ADR only**)
- `REF`: Reference document indicator
- `NN`: 3-digit sequence number (independent per TYPE)
- `{slug}`: Descriptive slug in snake_case

**Examples**:
- `BRD-REF-01_project_overview.md` - Business context
- `BRD-REF-02_strategic_vision.md` - Strategic vision
- `ADR-REF-01_technology_stack_summary.md` - Tech overview
- `ADR-REF-02_infrastructure_guide.md` - Infrastructure reference

**Use Cases**:
- BRD-REF: Project overviews, executive summaries, strategic vision, stakeholder guides
- ADR-REF: Technology stack summaries, architecture overviews, infrastructure guides

### 4.1 Ready-Score Exemptions (NO SCORES)

**REF documents are EXEMPT from ALL ready-scores and quality gates:**

| Aspect | Standard Document | REF Document |
|--------|-------------------|--------------|
| **PRD-Ready Score** (BRD-REF) | Required ≥90% | **NOT APPLICABLE** |
| **SYS-Ready Score** (ADR-REF) | Required ≥90% | **NOT APPLICABLE** |
| **Cumulative Tags** | Required per layer | **NOT REQUIRED** |
| **Quality Gates** | Full validation | **EXEMPT** |
| **Format** | Structured sections | **Free format** |

**Purpose**: REF documents are **reference targets** that other documents link to. They provide supporting information, context, or external references but do not define formal business requirements or architecture decisions.

**Validation** (Reduced - 4 checks only):
1. Document Control fields (required)
2. Document Revision History (required)
3. Status/Context sections (required)
4. H1 ID match with filename (required)

**References**:
- BRD-REF validation: `ai_dev_flow/01_BRD/BRD_VALIDATION_RULES.md`
- ADR-REF validation: `ai_dev_flow/05_ADR/ADR_VALIDATION_RULES.md`
