---
title: "doc-ref: Create Reference Documents (Supplementary)"
name: doc-ref
description: Create Reference Documents (REF) - supplementary documentation that doesn't participate in formal traceability chain
tags:
  - sdd-workflow
  - supplementary-documentation
  - shared-architecture
custom_fields:
  layer: null
  artifact_type: REF
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: utility
  upstream_artifacts: []
  downstream_artifacts: []
---

# doc-ref

## Purpose

Create **Reference Documents (REF)** - supplementary documentation for any artifact type in the SDD framework. REF documents provide supporting information without participating in the formal traceability chain.

**Layer**: Not applicable (supplementary to any layer)

**Traceability**: Optional (encouraged but not required)

**Validation**: Minimal (non-blocking)

## Naming Convention

**Format**: `{TYPE}-REF-NNN_{slug}.md`

| Component | Description | Example |
|-----------|-------------|---------|
| `{TYPE}` | Parent artifact type | BRD, PRD, REQ, ADR, SPEC, etc. |
| `REF` | Reference document indicator | REF |
| `NNN` | 3-digit sequence number | 001, 002, 003 |
| `{slug}` | Descriptive slug (snake_case) | project_overview |

**Examples**:
- `BRD-REF-001_project_overview.md`
- `PRD-REF-001_market_research.md`
- `REQ-REF-001_glossary.md`
- `ADR-REF-001_technology_stack_summary.md`
- `SPEC-REF-001_api_reference_guide.md`

**Numbering**: Independent sequence per parent TYPE
- BRD-REF-001, BRD-REF-002 (BRD sequence)
- PRD-REF-001, PRD-REF-002 (PRD sequence - separate from BRD)

**Location**: Within parent TYPE directory
- `docs/BRD/BRD-REF-001_project_overview.md`
- `docs/PRD/PRD-REF-001_market_research.md`

## When to Use This Skill

Use `doc-ref` when creating supplementary documentation that:

- Provides general project descriptions from business perspective
- Documents infrastructure requirements outside formal workflow
- Describes strategic vision or roadmap information
- Contains dictionaries, glossaries, or reference material
- Offers guides, tutorials, or educational content
- Summarizes information from multiple artifacts

**Do NOT use `doc-ref` for**:
- Documents that should participate in traceability chain
- Core artifacts (BRD, PRD, REQ, ADR, SPEC, etc.)
- Documents requiring validation gates

## Template Reference

**Template**: `ai_dev_flow/REF-TEMPLATE.md`

### Required Sections (4 Mandatory)

1. **YAML Frontmatter** - Metadata with `artifact_type: REF`
2. **Document Control** - Version, date, author, status
3. **Document Revision History** - Change tracking
4. **Introduction** - Purpose and scope

### Optional Sections

- **Related Documents** - Cross-references (traceability encouraged)
- **Content sections** - As needed for the specific reference material

## Creation Process

### Step 1: Determine Parent Type

Identify which artifact type this reference document supports:
- Business context → BRD-REF-NNN
- Product context → PRD-REF-NNN
- Requirements context → REQ-REF-NNN
- Architecture context → ADR-REF-NNN
- Technical context → SPEC-REF-NNN

### Step 2: Check Existing REF Documents

```bash
# List existing REF documents for the parent type
ls docs/BRD/*-REF-*.md 2>/dev/null    # For BRD references
ls docs/PRD/*-REF-*.md 2>/dev/null    # For PRD references
# ... etc.
```

### Step 3: Allocate Next Number

```bash
# Find highest REF number for parent type
ls docs/BRD/*-REF-*.md 2>/dev/null | sort -V | tail -1
```

### Step 4: Create Document

1. Copy template: `ai_dev_flow/REF-TEMPLATE.md`
2. Rename to: `{TYPE}-REF-NNN_{slug}.md`
3. Update H1 heading: `# {TYPE}-REF-NNN: [Document Title]`
4. Fill Document Control section
5. Write Introduction
6. Add content sections as needed
7. [Optional] Add Related Documents section

### Step 5: Place Document

Save in parent TYPE directory:
```
docs/{TYPE}/{TYPE}-REF-NNN_{slug}.md
```

## Validation Rules

### Required (Blocking)

| Check | Description |
|-------|-------------|
| H1 ID Match | H1 must match pattern `{TYPE}-REF-NNN: Title` |
| Document Control | Must have Document Control section |
| Revision History | Must have Document Revision History |
| Introduction | Must have Introduction section |

### Exempted (Not Checked)

| Check | Reason |
|-------|--------|
| Cumulative Tags | REF docs don't participate in traceability chain |
| Full Traceability | Traceability is optional |
| Quality Gates | Non-blocking validation |
| SPEC-Ready Score | Not applicable |

## Common Use Cases

### 1. Project Overview (BRD-REF)

General project description for stakeholders:
```markdown
# BRD-REF-001: Project Overview

## Document Control
...

## 1. Introduction

This document provides a high-level overview of the project for stakeholder reference...
```

### 2. Glossary (REQ-REF)

Domain terminology reference:
```markdown
# REQ-REF-001: Domain Glossary

## Document Control
...

## 1. Introduction

This glossary defines key terms used across requirements documentation...
```

### 3. Technology Summary (ADR-REF)

Consolidated architecture reference:
```markdown
# ADR-REF-001: Technology Stack Summary

## Document Control
...

## 1. Introduction

This document summarizes the technology decisions documented across ADRs...
```

### 4. API Quick Reference (SPEC-REF)

Simplified API guide:
```markdown
# SPEC-REF-001: API Quick Reference

## Document Control
...

## 1. Introduction

Quick reference guide for the most commonly used API endpoints...
```

## Comparison: REF vs Regular Artifacts

| Aspect | Regular Artifacts | REF Documents |
|--------|-------------------|---------------|
| Traceability | Required (cumulative tags) | Optional |
| Validation | Full (blocking) | Minimal (non-blocking) |
| Quality Gates | Must pass | Exempt |
| Workflow Position | Defined layer | No layer |
| Numbering | TYPE-NNN | {TYPE}-REF-NNN |

## Related Resources

- **Template**: `ai_dev_flow/REF-TEMPLATE.md`
- **Naming Standards**: `ai_dev_flow/ID_NAMING_STANDARDS.md`
- **Validation**: `ai_dev_flow/scripts/validate_artifact.py`

## Quick Reference

- **Format**: `{TYPE}-REF-NNN_{slug}.md`
- **Required Sections**: Document Control, Revision History, Introduction
- **Traceability**: Optional
- **Validation**: Minimal (non-blocking)
