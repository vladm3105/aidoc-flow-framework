# =============================================================================
# Reference Document Template
# For supplementary documentation that doesn't participate in formal traceability
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
---

# {TYPE}-REF-NNN: [Document Title]

## Document Control

| Item | Details |
|------|---------|
| **Parent Type** | [BRD/PRD/REQ/ADR/etc.] |
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

## Template Usage Notes

**Naming Convention**: `{TYPE}-REF-NNN_{slug}.md`
- `{TYPE}`: Parent artifact type (BRD, PRD, REQ, ADR, SPEC, etc.)
- `REF`: Reference document indicator
- `NNN`: 3-digit sequence number (independent per TYPE)
- `{slug}`: Descriptive slug in snake_case

**Examples**:
- `BRD-REF-001_project_overview.md`
- `PRD-REF-001_market_research.md`
- `REQ-REF-001_glossary.md`
- `ADR-REF-001_technology_stack_summary.md`

**Use Cases**:
- General project descriptions from business perspective
- Infrastructure requirements documentation
- Strategic vision descriptions
- Dictionaries and glossaries
- Reference material and guides

**Validation**:
- Minimal validation (non-blocking)
- Required: Document Control, Revision History, Introduction, H1 ID match
- Exempted: Cumulative tags, full traceability chain, quality gates
