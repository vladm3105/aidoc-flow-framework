---
title: "ADR MVP Creation Rules"
tags:
  - creation-rules
  - layer-5-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: ADR
  layer: 5
  complexity: 1
  priority: shared
  development_status: active
---

# =============================================================================
# 📋 Document Role: Guides creation of ADR-MVP-TEMPLATE.md (default)
# - Authority: ADR-MVP-TEMPLATE.md is the primary standard for ADR structure; full template is archived
# - Purpose: AI guidance for document creation (derived from MVP template)
# - On conflict: Defer to ADR-MVP-TEMPLATE.md
# =============================================================================
---
title: "ADR MVP Creation Rules"
tags:
  - creation-rules
  - layer-5-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: ADR
  layer: 5
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for ADR-MVP-TEMPLATE.md (default).
> - **Authority**: `ADR-MVP-TEMPLATE.md` is the primary standard for ADR structure; full template archived
> - **Validation**: Use `ADR_MVP_VALIDATION_RULES.md` after ADR creation/changes

# ADR Creation Rules

## Template Selection (MVP Default)

**MVP templates are the framework default.**

| Template | File | When to Use |
|----------|------|-------------|
| **MVP (DEFAULT)** | `ADR-MVP-TEMPLATE.md` | All ADRs |

## Index-Only Generation Workflow

- Maintain `ADR-00_index.md` as the authoritative source of planned and active ADR documents (mark planned items with Status: Planned).
- Generators use: `ADR-00_index.md` + selected template profile (MVP by default; full when explicitly requested in settings or prompt).

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 1.1
**Date**: 2025-11-19
**Last Updated**: 2025-11-30
**Source**: Derived from ADR-MVP-TEMPLATE.md and SPEC_DRIVEN_DEVELOPMENT_GUIDE.md (full template archived)
**Purpose**: Complete reference for creating ADR documents according to AI Dev Flow SDD framework
**Changes**: Added Status/Score mapping table, new common mistakes section. Previous: SYS-ready scoring system

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
2. [Document Structure (Required sections)](#2-document-structure-required-sections)
3. [Document Control Requirements](#3-document-control-requirements)
4. [ID and Naming Standards](#4-id-and-naming-standards)
5. [ADR Decision Categories](#5-adr-decision-categories)
6. [SYS Relationship Guidelines](#6-sys-relationship-guidelines)
7. [SYS-Ready Scoring System](#7-sys-ready-scoring-system)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Quality Attributes](#9-quality-attributes)
10. [Quality Gates](#10-quality-gates)
11. [Additional Requirements](#11-additional-requirements)
12. [Diagram Standards](#12-diagram-standards)
13. [Common Mistakes to Avoid](#13-common-mistakes-to-avoid)
14. [Upstream Artifact Verification Process](#14-upstream-artifact-verification-process)
15. [Cross-Document Validation](#15-cross-document-validation-mandatory)

---

## 1. File Organization and Directory Structure

- Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.
- **Location**: `docs/05_ADR/ADR-NN_{slug}/` within project docs directory (nested folder per document with descriptive slug)
- **Folder Naming**: `ADR-NN_{slug}/` where slug MUST match the index file slug (e.g., `ADR-01_cloud_migration/`)
- **Folder Structure** (DEFAULT): `docs/05_ADR/ADR-NN_{slug}/ADR-NN.S_{slug}.md`
  - Index file: `docs/05_ADR/ADR-NN_{slug}/ADR-NN.0_{slug}_index.md`
  - Section files: `docs/05_ADR/ADR-NN_{slug}/ADR-NN.1_{slug}_context.md`, etc.
- **Section Files**: Section-based structure is DEFAULT for all ADR documents. Use format: `ADR-NN.S_{section_slug}.md` (S = section number). See `ID_NAMING_STANDARDS.md` for metadata tags.
- **Monolithic** (OPTIONAL for <25KB): `docs/05_ADR/ADR-NN_{descriptive_slug}.md` (flat structure)
- **Structure**: One primary ADR document folder per architecture decision

---

## 2. Document Structure (Required sections)

ADR documents follow a comprehensive 4-part structure:

#### **Part 1: Decision Context and Requirements**
- Status, Context, Decision, Requirements Satisfied

#### **Part 2: Impact Analysis and Architecture**
- Consequences, Architecture Flow, Implementation Assessment, Impact Analysis

#### **Part 3: Implementation and Operations**
- security, Related Decisions, Implementation Notes

#### **Part 4: Traceability and Documentation**
- Traceability, References

---

## 3. Document Control Requirements

**Required Fields** (6 mandatory):
- Project Name
- Document Version
- Date
- Document Owner
- Prepared By
- Status
- SYS-Ready Score (⭐ NEW)

**Format**:
```markdown
| Item | Details |
|------|---------|
| **SYS-Ready Score** | ✅ 95% (Target: ≥90%) |
```

### Status and SYS-Ready Score Mapping

| SYS-Ready Score | Required Status |
|-----------------|-----------------|
| >= 90% | Accepted |
| 70-89% | Proposed |
| < 70% | Draft |

---

## 4. ID and Naming Standards

- **Filename**: `ADR-NN_descriptive_architecture_decision.md`
- **H1**: `# ADR-NN: [Architecture Decision Title]`
- **ID Alignment**: ADR-DOC_NUM MUST match parent PRD ID (e.g., `PRD-12` -> `ADR-12`).
- **Status Tags**: Proposed, Accepted, Rejected, Superseded, Deprecated

### 4.1 Element ID Format (MANDATORY)

**Pattern**: `ADR.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| Decision | 10 | ADR.02.10.01 |
| Alternative | 12 | ADR.02.12.01 |
| Consequence | 13 | ADR.02.13.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use legacy formats like `DEC-XXX`, `ALT-XXX`.
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

## 5. ADR Decision Categories

**Technical Decisions**:
- Framework, library, or technology selection
- Architecture patterns and design principles
- Infrastructure and deployment models

**Quality Attribute Decisions**:
- Performance, scalability, and reliability requirements
- security and compliance approaches
- Operational and monitoring strategies

**Integration Decisions**:
- Service interaction patterns
- Data flow and communication protocols
- External system integration approaches

---

## 6. SYS Relationship Guidelines

**ADR → SYS Workflow**:
- ADRs establish the "how" for architecture
- SYS documents translate ADRs into detailed system requirements
- SYS requirements must be implementable within ADR constraints

**SYS Impact Analysis**:
- ADR decisions may necessitate SYS requirement modifications
- Performance targets from ADRs drive SYS quality attribute requirements
- Integration patterns in ADRs define SYS interfaces

---

## 7. SYS-Ready Scoring System ⭐ NEW

### Overview
SYS-ready scoring measures ADR maturity and readiness for progression to System Requirements (SYS) phase.

**Format**: `✅ NN% (Target: ≥90%)`
**Location**: Document Control table
**Validation**: Enforced before SYS creation

### Scoring Criteria

**Decision Completeness (30%)**:
- ADR follows complete decision process (Context, Decision, Consequences, Alternatives): 15%
- Requirements mapping clear and traceable: 10%
- Impact analysis comprehensive (positive/negative consequences): 5%

**Architecture Clarity (35%)**:
- Architecture flow documented with Mermaid diagrams: 15%
- Component responsibilities clearly defined: 10%
- Cross-cutting concerns addressed (security, observability): 10%

**Implementation Readiness (20%)**:
- Complexity assessment and resource estimates provided: 10%
- Dependencies and requirements identified: 5%
- Rollback and migration strategies documented: 5%

**Verification Approach (15%)**:
- Testing strategy aligned with architecture: 5%
- Success metrics and validation criteria defined: 5%
- Operational readiness assessment complete: 5%

### Quality Gate Enforcement
- Score <90% prevents SYS artifact creation
- Format validation requires ✅ emoji and percentage
- Threshold enforcement at pre-commit

---

## 8. Traceability Requirements (MANDATORY - Layer 5)

**Complete Upstream Tag Chain**:
```markdown
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
@ears: EARS.NN.EE.SS
@bdd: BDD.NN.EE.SS
```

**Layer 5 Requirements**: ADR must reference ALL upstream artifacts

**Downstream Linkages**:
- SYS requirements must align with ADR architectural boundaries
- REQ artifacts must respect ADR constraints
- SPEC implementations must follow ADR patterns

---

## 8.1 Cross-Linking Tags (AI-Friendly)

**Purpose**: Establish lightweight, machine-readable hints for AI discoverability and dependency tracing across ADR documents without blocking validation.

**Tags Supported**:
- `@depends: ADR-NN` — Hard prerequisite; this ADR cannot proceed without the referenced ADR
- `@discoverability: ADR-NN (short rationale)` — Related document for AI search and ranking (informational)

**ID Format**: Document-level IDs follow `{DOC_TYPE}-NN` per `ID_NAMING_STANDARDS.md` (e.g., `ADR-01`, `ADR-02`).

**Placement**: Add tags to the Traceability section or inline with decision descriptions.

**Example**:
```markdown
@depends: ADR-01 (Technology Stack)
@discoverability: ADR-02 (Database Strategy - related architecture decision)
```

**Validator Behavior**: Cross-linking tags are recognized and reported as **info-level** findings (non-blocking). They enable AI/LLM tools to infer relationships and improve search ranking without affecting document approval.

**Optional for MVP**: Cross-linking tags are optional in MVP templates and are not required for ADR approval; they are purely informational.

---

## 9. Quality Attributes

**Decision Rationale**: Evidence-based with quantitative trade-off analysis

**Technical Validation**: Architecture must be verifiable through testing

**Business Alignment**: Technical decisions support business objectives

**Implementation Feasibility**: Architecture must be buildable with available resources

**Operational Viability**: Long-term maintenance and scaling considerations

**security Compliance**: security architecture meets regulatory requirements

---

## 10. Quality Gates (Pre-Commit Validation)

- ADR completeness and decision quality validation
- SYS-ready score verification ≥90%
- Architecture diagram validation
- Traceability chain completeness

---

## 11. Additional Requirements

- Business justification for all architectural trade-offs
- Quantitative metrics for performance and cost impacts
- Risk mitigation strategies with probability assessments
- Technical debt and maintenance cost projections

---

**Framework Compliance**: 100% AI Dev Flow SDD framework (Layer 5)
**Integration**: Enforces ADR → SYS progression quality gates

---

## 12. Diagram Standards

All diagrams MUST use Mermaid syntax. Text-based diagrams (ASCII art, box drawings) are prohibited. Directory tree structures (`├── └── │`) are exempted.

**Central Authority**: `ai_dev_flow/DIAGRAM_STANDARDS.md`
**Diagram Skill**: `mermaid-gen` skill

---

## 13. Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| `Status: Accepted` (with <90% SYS-Ready score) | Match status to score threshold |
| Missing Consequences section | Document positive AND negative consequences |
| Alternatives without evaluation | Include trade-off analysis for each option |
| `@sys: SYS-NN` (referencing downstream) | ADR should not reference downstream SYS |
| Decision without context | Provide problem statement and constraints |
| Missing architecture diagrams | Include Mermaid diagrams for architecture flow |

---

## 14. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/01_BRD/    # Layer 1
ls -la docs/02_PRD/    # Layer 2
ls -la docs/03_EARS/   # Layer 3
ls -la docs/04_BDD/    # Layer 4
ls -la docs/05_ADR/    # Layer 5
ls -la docs/06_SYS/    # Layer 6
ls -la docs/07_REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-01 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-01 or null | Reference/Create/Skip |
| ... | ... | ... | ... |

**Step 3: Decision Rules**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | Skip that functionality - do NOT implement |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

### Traceability Tag Rules

- **NEVER** use placeholder IDs like `BRD-XXX` or `TBD`
- **NEVER** reference documents that don't exist
- **ALWAYS** verify document exists before adding reference
- **USE** `null` only when artifact type is genuinely not applicable

### Same-Type References (Conditional)

Include ONLY if relationships exist between ADRs sharing architectural context or implementation dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | ADR-NN | [Related ADR title] | Shared architectural context |
| Depends | ADR-NN | [Prerequisite ADR title] | Must complete before this |

**Tags**:
```markdown
@related-adr: ADR-NN
@depends-adr: ADR-NN
```

---

## 15. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any ADR document. Do NOT proceed to downstream artifacts until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed to next layer
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/05_ADR/ADR-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all ADR documents complete
python scripts/validate_cross_document.py --layer ADR --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| ADR (Layer 5) | @brd, @prd, @ears, @bdd | 4 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears/@bdd tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NN.TT.SS or TYPE-NN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to SYS creation until Phase 1 validation passes with 0 errors.

## 16. ADR Generation Planning

When creating an **ADR Generation Plan** (e.g., `ADR_GENERATION_PLAN.md`), ensure the document includes the following to prevent common issues:

### 16.1 Required Frontmatter
Must include standard fields plus `complexity`:
```yaml
---
type: plan
project: [Project Name]
status: planning
date: YYYY-MM-DD
complexity: [1-5]
---
```

### 16.2 Mandatory Sections
1. **Executive Summary**: Scope assessment and key findings.
2. **Prerequisites & Dependencies**: Upstream requirements (BRD/PRD), and current architecture state.
3. **Risk Assessment**: Identify risks (e.g., conflicting decisions) and failure modes with mitigations.
4. **Phases**: Break down work into P0/P1/P2 phases.
   - **MUST Include**: Tasks with complexity ratings, Acceptance Criteria, Validation Steps, and Deliverables.
5. **Validation Commands**: Explicit commands to run for verification.

### 16.3 Common Pitfalls to Avoid
- **Count Mismatch**: Ensure summary counts match the task list items.
- **Missing Complexity**: Rate every task (1-5) and the overall document.
- **Vague Archives**: Clearly state how legacy/archive files are handled.
