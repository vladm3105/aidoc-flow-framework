# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of IMPL-TEMPLATE.md
# - Authority: IMPL-TEMPLATE.md is the single source of truth for IMPL structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to IMPL-TEMPLATE.md
# =============================================================================
---
title: "IMPL Creation Rules"
tags:
  - creation-rules
  - layer-8-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: IMPL
  layer: 8
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for IMPL-TEMPLATE.md.
> - **Authority**: `IMPL-TEMPLATE.md` is the single source of truth for IMPL structure
> - **Validation**: Use `IMPL_VALIDATION_RULES.md` after IMPL creation/changes

# IMPL Creation Rules

Rules for creating Implementation Plans (IMPL) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

---

## Table of Contents

1. [When to Create an IMPL Document](#1-when-to-create-an-impl-document)
2. [File Naming Convention](#2-file-naming-convention)
3. [Required Sections](#3-required-sections)
4. [PART 1: Project Context Rules](#4-part-1-project-context-rules)
5. [PART 2: Phased Implementation Rules](#5-part-2-phased-implementation-rules)
6. [PART 3: Project Management Rules](#6-part-3-project-management-rules)
7. [PART 4: Tracking Rules](#7-part-4-tracking-rules)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Scope Boundaries](#9-scope-boundaries)
10. [Quality Checklist](#10-quality-checklist)
11. [Common Anti-Patterns](#11-common-anti-patterns)
12. [Validation](#12-validation)
13. [Upstream Artifact Verification Process](#13-upstream-artifact-verification-process)
14. [Cross-Document Validation](#14-cross-document-validation-mandatory)

---

## 1. When to Create an IMPL Document

### Create IMPL When

- [ ] Multi-component feature requiring 3+ SPEC files
- [ ] Phased rollout over multiple sprints/weeks
- [ ] Multiple teams coordinating on related components
- [ ] Complex dependencies between work packages
- [ ] Large scope spanning multiple iterations
- [ ] Resource coordination needed across teams

### Do NOT Create IMPL When

- [ ] Single SPEC implementation (use TASKS directly)
- [ ] Simple feature with no phase dependencies
- [ ] Work can be completed in one sprint by one team
- [ ] No coordination required between components
- [ ] Documentation-only updates

### Rule of Thumb

If implementing a requirement requires creating **3+ SPEC files** or coordinating **2+ teams**, create an IMPL Plan.

---

## 2. File Naming Convention

### Format

```
IMPL-NNN_{system_name}.md
```

### Rules

1. **IMPL-NNN**: Sequential numbering starting from 001
2. **system_name**: Lowercase with underscores
3. **Extension**: Always `.md`

### Examples

- `IMPL-001_risk_management_system.md`
- `IMPL-002_external_data_integration.md`
- `IMPL-003_order_execution_service.md`
- `IMPL-004_authentication_system.md`

---

## 3. Required Sections

### 3.1 Frontmatter

```yaml
---
title: "IMPL-NNN: [System/Feature Name] Implementation Plan"
tags:
  - impl-plan
  - layer-8-artifact
  - project-management
custom_fields:
  document_type: impl
  artifact_type: IMPL
  layer: 8
  related_reqs: [REQ-NNN, REQ-MMM]
---
```

### 3.2 Document Control Table

| Field | Required | Description |
|-------|----------|-------------|
| IMPL ID | Yes | IMPL-NNN format |
| Title | Yes | System/feature name |
| Status | Yes | Draft/Planned/In Progress/On Hold/Completed/Cancelled |
| Version | Yes | Semantic version (X.Y.Z) |
| Created | Yes | YYYY-MM-DD |
| Author | Yes | Creator name |
| Owner | Yes | Team or person responsible |
| Last Updated | Yes | YYYY-MM-DD |
| Related REQs | Yes | List of REQ-NNN references |
| Deliverables | Yes | List of CTR/SPEC/TASKS to produce |

### 3.3 Mandatory Parts

| Part | Purpose |
|------|---------|
| PART 1: Project Context and Strategy | Overview, objectives, scope, dependencies |
| PART 2: Phased Implementation | Work breakdown by phases with deliverables |
| PART 3: Project Management and Risk | Resources, timeline, risk register |
| PART 4: Tracking and Completion | Deliverables checklist, validation, sign-off |
| Traceability | Upstream and downstream references |

---

## 4. PART 1: Project Context Rules

### 4.1 Overview Section

**Requirements**:
- Brief description of system/feature (2-3 sentences)
- Purpose statement (business value)
- Scope summary (high-level inclusions)

### Good Example

```markdown
## PART 1: Project Context and Strategy

### 1.1 Overview

**What System/Feature Is Being Implemented**:
The Risk Management System provides real-time risk assessment for trading positions,
enforcing position limits and calculating risk metrics.

**Purpose**:
Enable compliance with regulatory requirements while protecting trading capital.

**Scope Summary**:
Position limits, risk calculations, and alerting system.
```

### Bad Example

```markdown
## PART 1: Overview

Build the risk system with all the risk stuff.
```

### 4.2 Scope Section

**Requirements**:
- Explicit "In Scope" list
- Explicit "Out of Scope" list
- Assumptions documented
- Constraints identified (technical, resource, timeline, business)

---

## 5. PART 2: Phased Implementation Rules

### Requirements

- Each phase has clear purpose
- Phases are numbered sequentially
- Each phase includes:
  - Purpose statement
  - Owner/team assignment
  - Timeline (dates or duration)
  - Deliverables (CTR-NNN, SPEC-NNN, TASKS-NNN)
  - Dependencies
  - Success criteria
  - Key risks

### Good Example

```markdown
### Phase 1: Core Risk Engine

| Attribute | Details |
|-----------|---------|
| **Purpose** | Build foundation risk calculation engine |
| **Owner** | Risk Team (3 developers) |
| **Timeline** | Sprint 1-2 (4 weeks) |
| **Deliverables** | CTR-003, SPEC-003, TASKS-003 |
| **Dependencies** | Requires: Database schema (ADR-008) |
| **Success Criteria** | [ ] All deliverables created [ ] Tests passing |

**Key Risks**: Resource availability → Mitigation: Cross-train team
```

### Bad Example

```markdown
### Phase 1
- Build the risk engine
- Make it work
```

### Phase Content Rules

1. **Focus on WHO/WHAT/WHEN** - not technical details (HOW goes in SPEC)
2. **List specific deliverables** - CTR-NNN, SPEC-NNN, TASKS-NNN
3. **Assign ownership** - team or person responsible
4. **Include timeline** - dates or sprint numbers
5. **Identify dependencies** - what blocks this phase

---

## 6. PART 3: Project Management Rules

### 6.1 Resource Allocation

**Required**:
- Team/person assignments
- Role descriptions
- Phase assignments
- Effort estimates

### 6.2 Timeline and Milestones

**Required**:
- Overall timeline (start to end)
- Key milestones with dates
- Critical path identification
- Current blockers

### 6.3 Risk Register

**Project Management Risks Only** (technical risks go in ADR/SPEC):

| Risk ID | Risk Description | Probability | Impact | Mitigation | Owner | Status |
|---------|------------------|-------------|--------|------------|-------|--------|
| R-001 | Resource unavailability | Medium | High | Cross-train team | PM | Open |

**Focus Areas**:
- Resource allocation risks
- Timeline management risks
- Scope control risks
- Dependency coordination risks

---

## 7. PART 4: Tracking Rules

### 7.1 Deliverables Checklist

Every deliverable must be listed with checkbox:

```markdown
### 4.1 Deliverables Checklist

**Phase 1 Deliverables**:
- [ ] CTR-003: Risk API Contract created
- [ ] SPEC-003: Risk Engine Specification created
- [ ] TASKS-003: Risk Engine Tasks created

**Phase 2 Deliverables**:
- [ ] CTR-004: Limits API Contract created
- [ ] SPEC-004: Limits Service Specification created
- [ ] TASKS-004: Limits Service Tasks created
```

### 7.2 Project Validation

**Required Checkboxes**:
- [ ] All phases completed on schedule
- [ ] All deliverable documents created
- [ ] All project risks mitigated or accepted
- [ ] All dependencies resolved
- [ ] Stakeholder sign-off received

### 7.3 Sign-off Table

| Role | Name | Status | Date |
|------|------|--------|------|
| Project Manager | [Name] | Pending | - |
| Product Owner | [Name] | Pending | - |
| Technical Lead | [Name] | Pending | - |

---

## 8. Traceability Requirements

### 8.1 Upstream References (Layer 8 position)

IMPL must reference:
- `@brd: BRD.NNN.NNN` - Business requirements
- `@prd: PRD.NNN.NNN` - Product requirements
- `@ears: EARS.NNN.NNN` - EARS statements
- `@bdd: BDD.NNN.NNN` - BDD scenarios
- `@adr: ADR-NNN` - Architecture decisions
- `@sys: SYS.NNN.NNN` - System requirements
- `@req: REQ.NNN.NNN` - Atomic requirements

### 8.2 Downstream Artifacts

IMPL produces (as deliverables):
- `CTR-NNN` - API contracts
- `SPEC-NNN` - Technical specifications
- `TASKS-NNN` - Code generation plans

### 8.3 Tag Format

```markdown
## Traceability Tags

@brd: BRD.01.01.42
@prd: PRD.01.01.15
@ears: EARS.01.24.03
@bdd: BDD.01.13.05
@adr: ADR-002
@sys: SYS.02.25.01
@req: REQ.01.26.01, REQ.02.26.01
```

---

## 9. Scope Boundaries

### IMPL Contains (Project Management)

- **WHO**: Teams, people, assignments
- **WHAT**: Deliverables (CTR/SPEC/TASKS documents)
- **WHEN**: Timeline, milestones, phases
- **WHY**: Business objectives, success criteria

### IMPL Does NOT Contain (Technical)

- **HOW**: Technical implementation → SPEC
- **Code**: Implementation details → TASKS
- **Tests**: Test specifications → BDD/TASKS
- **Architecture**: System design → ADR

---

## 10. Quality Checklist

### Before Creating

- [ ] Verify multi-component scope (3+ SPECs needed)
- [ ] Check for existing IMPL covering same scope
- [ ] Identify all teams/stakeholders involved
- [ ] Understand timeline constraints

### During Creation

- [ ] Use IMPL-TEMPLATE.md as starting point
- [ ] Complete all 4 PARTS
- [ ] List specific deliverables in each phase
- [ ] Assign owners to phases
- [ ] Include project management risks (not technical)
- [ ] Add traceability tags

### After Creation

- [ ] All upstream references valid
- [ ] Deliverable list complete
- [ ] Timeline realistic
- [ ] Update IMPL-000_index.md
- [ ] Notify stakeholders
- [ ] Run validation script

---

## 11. Common Anti-Patterns

### Avoid

1. **IMPL becomes SPEC** - Move technical details to SPEC documents
2. **IMPL duplicates TASKS** - Don't include code generation steps
3. **IMPL too granular** - Keep phases at 1-2 week level
4. **Missing deliverables** - Always list CTR/SPEC/TASKS IDs
5. **No team allocation** - Assign owners to every phase
6. **Technical risks in IMPL** - Project risks only (technical → ADR)
7. **Vague scope** - Be explicit about in/out of scope

---

## 12. Validation

### Automated Validation

```bash
./scripts/validate_impl.sh /path/to/IMPL-NNN_name.md
```

### Manual Checklist

- [ ] Filename follows convention
- [ ] All 4 PARTS present
- [ ] Phases have deliverables listed
- [ ] Owners assigned to phases
- [ ] Traceability tags complete
- [ ] Registered in IMPL-000_index.md

---

## 13. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/BRD/    # Layer 1
ls -la docs/PRD/    # Layer 2
ls -la docs/EARS/   # Layer 3
ls -la docs/BDD/    # Layer 4
ls -la docs/ADR/    # Layer 5
ls -la docs/SYS/    # Layer 6
ls -la docs/REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-001 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-001 or null | Reference/Create/Skip |
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

Include ONLY if relationships exist between IMPL documents sharing implementation context or dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | IMPL-NNN | [Related IMPL title] | Shared implementation context |
| Depends | IMPL-NNN | [Prerequisite IMPL title] | Must complete before this |

**Tags**:
```markdown
@related-impl: IMPL-NNN
@depends-impl: IMPL-NNN
```


## References

- [IMPL-TEMPLATE.md](./IMPL-TEMPLATE.md) - Implementation plan template
- [IMPL-000_index.md](./IMPL-000_index.md) - Plan registry
- [README.md](./README.md) - Directory overview
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide
- [TRACEABILITY.md](../TRACEABILITY.md) - Traceability hierarchy

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-27

---

## 14. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any IMPL document. Do NOT proceed to downstream artifacts until validation passes.

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
python scripts/validate_cross_document.py --document docs/IMPL/IMPL-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all IMPL documents complete
python scripts/validate_cross_document.py --layer IMPL --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| IMPL (Layer 8) | @brd, @prd, @ears, @bdd, @adr, @sys, @req | 7 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd through @req tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NNN.NNN or TYPE-NNN format |
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

**Blocking**: YES - Cannot proceed to CTR/SPEC creation until Phase 1 validation passes with 0 errors.
