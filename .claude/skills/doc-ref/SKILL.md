---
name: "doc-ref: Create Reference Documents (Supplementary)"
name: doc-ref
description: Create Reference Documents (REF) - supplementary documentation that doesn't participate in formal traceability chain
tags:
  - sdd-workflow
  - supplementary-documentation
  - shared-architecture
  - required-both-approaches
custom_fields:
  layer: "N/A"
  artifact_type: REF
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: utility
  upstream_artifacts: [BRD, ADR]
  downstream_artifacts: []
  valid_parent_types: [BRD, ADR]
---

# doc-ref

## Purpose

Create **Reference Documents (REF)** - supplementary documentation for BRD and ADR artifact types in the SDD framework. REF documents provide supporting information without participating in the formal traceability chain.

**Layer**: Not applicable (supplementary to any layer)

**Traceability**: Optional (encouraged but not required)

**Validation**: Minimal (non-blocking)

## Naming Convention

**Format**: `{TYPE}-REF-NNN_{slug}.md`

| Component | Description | Example |
|-----------|-------------|---------|
| `{TYPE}` | Parent artifact type | **BRD or ADR only** |
| `REF` | Reference document indicator | REF |
| `NNN` | 3-digit sequence number | 001, 002, 003 |
| `{slug}` | Descriptive slug (snake_case) | project_overview |

**Scope**: REF documents are LIMITED to **BRD and ADR artifact types ONLY**.

**Examples**:
- `BRD-REF-001_project_overview.md` - Business context
- `BRD-REF-002_strategic_vision.md` - Strategic vision
- `ADR-REF-001_technology_stack_summary.md` - Tech overview
- `ADR-REF-002_infrastructure_guide.md` - Infrastructure reference

**Numbering**: Independent sequence per parent TYPE
- BRD-REF-001, BRD-REF-002 (BRD sequence)
- ADR-REF-001, ADR-REF-002 (ADR sequence - separate from BRD)

**Location**: Within parent TYPE directory
- `docs/BRD/BRD-REF-001_project_overview.md`
- `docs/ADR/ADR-REF-001_technology_stack_summary.md`

## When to Use This Skill

Use `doc-ref` when creating supplementary documentation that:

- **BRD-REF**: Project overviews, executive summaries, strategic vision, stakeholder guides
- **ADR-REF**: Technology stack summaries, architecture overviews, infrastructure guides

**Do NOT use `doc-ref` for**:
- Documents that should participate in traceability chain
- Core artifacts (BRD, PRD, REQ, ADR, SPEC, etc.)
- Documents requiring validation gates
- **Any parent type other than BRD or ADR** (REF is limited to these two types)

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

Identify which artifact type this reference document supports (**BRD or ADR only**):
- Business context → BRD-REF-NNN
- Architecture context → ADR-REF-NNN

### Step 2: Check Existing REF Documents

```bash
# List existing REF documents for the parent type
ls docs/BRD/*-REF-*.md 2>/dev/null    # For BRD references
ls docs/ADR/*-REF-*.md 2>/dev/null    # For ADR references
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

### 2. Strategic Vision (BRD-REF)

Strategic roadmap and vision:
```markdown
# BRD-REF-002: Strategic Vision

## Document Control
...

## 1. Introduction

This document outlines the strategic vision and roadmap for the project...
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

### 4. Infrastructure Guide (ADR-REF)

Infrastructure reference documentation:
```markdown
# ADR-REF-002: Infrastructure Guide

## Document Control
...

## 1. Introduction

Reference guide for infrastructure components and deployment architecture...
```

## Ready-Score Exemptions

**REF documents are EXEMPT from ALL ready-scores and quality gates:**

| Aspect | Standard Document | REF Document |
|--------|-------------------|--------------|
| **PRD-Ready Score** (BRD-REF) | Required ≥90% | **NOT APPLICABLE** |
| **SYS-Ready Score** (ADR-REF) | Required ≥90% | **NOT APPLICABLE** |
| **Cumulative Tags** | Required per layer | **NOT REQUIRED** |
| **Quality Gates** | Full validation | **EXEMPT** |
| **Format** | Structured sections | **Free format** |

## Comparison: REF vs Regular Artifacts

| Aspect | Regular Artifacts | REF Documents |
|--------|-------------------|---------------|
| Traceability | Required (cumulative tags) | Optional |
| Validation | Full (blocking) | Minimal (4 checks only) |
| Quality Gates | Must pass | Exempt |
| Workflow Position | Defined layer | No layer |
| Numbering | TYPE-NN | {TYPE}-REF-NNN |
| Valid Parent Types | All artifact types | **BRD and ADR only** |

## Related Resources

- **Template**: `ai_dev_flow/REF-TEMPLATE.md`
- **Naming Standards**: `ai_dev_flow/ID_NAMING_STANDARDS.md`
- **Validation**: `ai_dev_flow/scripts/validate_artifact.py`

## Quick Reference

- **Format**: `{TYPE}-REF-NNN_{slug}.md`
- **Valid Parent Types**: **BRD and ADR only**
- **Required Sections**: Document Control, Revision History, Introduction
- **Traceability**: Optional (encouraged but not required)
- **Validation**: Minimal (non-blocking, 4 checks only)
- **Ready-Scores**: NOT APPLICABLE - REF documents use free format with no scores
