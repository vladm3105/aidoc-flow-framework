# Implementation Plan - Add Same-Type Document Traceability Rules

**Created**: 2025-11-29 11:59:06 EST
**Status**: Ready for Implementation

## Objective

Add documentation for two types of same-type traceability across all SDD framework documents:
1. **Same-type supporting references** - Documents of the same type that provide context or supplementary information
2. **Implementation priority ordering** - Dependencies between same-type documents where one must be implemented before another

## Context

- **Relationship types**: Both (supporting/related AND implementation priority)
- **Requirement level**: Conditional (mandatory only when relationships exist, can omit if none)
- **Direction**: Forward-only (no reverse `@dependent-` tags for maintainability)
- Reverse relationships derived via grep scripts, not stored in documents

## Task List

### Pending
- [ ] Update TRACEABILITY.md with new "Same-Type Document Relationships" section
- [ ] Update Tag Format Specification in TRACEABILITY.md
- [ ] Update Traceability Section Template in TRACEABILITY.md
- [ ] Update 13 templates with Same-Type References subsection
- [ ] Update 13 creation rules with same-type guidance
- [ ] Update 12 skills with same-type traceability info
- [ ] Validate all changes

## Implementation Guide

### Prerequisites
- Working directory: `/opt/data/docs_flow_framework`
- Files to modify: ~40 files total

### Content to Add

#### New Section for TRACEABILITY.md (~line 598)

```markdown
## Same-Type Document Relationships

### Overview

In addition to upstream/downstream layer traceability, documents may have relationships with other documents of the **same artifact type**. These relationships are **conditional** - required only when they exist.

### Relationship Types

| Relationship | Tag Format | Purpose | When Required |
|--------------|------------|---------|---------------|
| **Related** | `@related-{type}:` | Supporting context, shared domain knowledge | When documents share concepts |
| **Depends** | `@depends-{type}:` | Implementation prerequisite, must complete first | When implementation order matters |

### Tag Formats

**Related Documents** (informational, no ordering):
```
@related-req: REQ-001, REQ-005
@related-spec: SPEC-002
@related-tasks: TASKS-003
```

**Dependency Documents** (implementation order):
```
@depends-req: REQ-001  # Must implement REQ-001 before this
@depends-spec: SPEC-001, SPEC-002  # Prerequisites
@depends-tasks: TASKS-001  # Depends on TASKS-001 completion
```

### Decision Rules

| Situation | Action |
|-----------|--------|
| No same-type relationships exist | Omit section entirely |
| Related documents exist | Add `@related-{type}:` tags |
| Implementation dependencies exist | Add `@depends-{type}:` tags |
| Both exist | Include both tag types |

### Examples

**REQ-003 with same-type relationships**:
```markdown
## Traceability Tags

### Upstream (Cross-Layer)
@brd: BRD-001:FR-030
@prd: PRD-003:FEATURE-002
@sys: SYS-008:PERF-001

### Same-Type References
@related-req: REQ-001, REQ-002  # Shared risk management domain
@depends-req: REQ-001  # Connection must exist before validation
```

### Validation Rules

1. **Format Check**: Same-type tags use `@related-{type}:` or `@depends-{type}:` format
2. **Document Exists**: Referenced document must exist in docs/{TYPE}/
3. **No Circular Dependencies**: `@depends-` cannot create cycles
4. **Conditional Presence**: Section optional if no relationships exist

### Impact Analysis (Script-Based)

**Forward-only approach**: Reverse relationships derived via scripts, not stored in documents.

```bash
# Find all documents that depend on REQ-001
grep -r "@depends-req:.*REQ-001" docs/REQ/

# Find all documents related to SPEC-003
grep -r "@related-spec:.*SPEC-003" docs/SPEC/
```
```

#### Tag Format Specification Addition (~lines 479-529)

```markdown
**Same-Type Relationship Tags** (Forward-Only):

| Tag Type | Format | Purpose |
|----------|--------|---------|
| Related | `@related-{type}:` | Supporting context, shared domain knowledge |
| Depends | `@depends-{type}:` | Implementation prerequisite (must complete first) |

**Supported Types**: req, spec, tasks, adr, bdd, sys, ears, prd, ctr, impl, iplan

**Examples**:
```markdown
@related-req: REQ-001, REQ-005
@depends-req: REQ-001
@related-spec: SPEC-002, SPEC-004
@depends-spec: SPEC-001
@related-tasks: TASKS-002
@depends-tasks: TASKS-001
```
```

#### Template Subsection Addition

Add after Downstream Artifacts in traceability section:

```markdown
### Same-Type References (Conditional)

**Include this section only if same-type relationships exist.**

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | [REQ-001](../REQ/.../REQ-001_...md) | [Related requirement] | Shared domain context |
| Depends | [REQ-002](../REQ/.../REQ-002_...md) | [Prerequisite requirement] | Must complete before this |

**Tags**:
```markdown
@related-req: REQ-001
@depends-req: REQ-002
```
```

### Files to Modify

**Primary File**:
- `ai_dev_flow/TRACEABILITY.md`

**Templates (13 files)**:
- `ai_dev_flow/BRD/BRD-TEMPLATE.md`
- `ai_dev_flow/PRD/PRD-TEMPLATE.md`
- `ai_dev_flow/EARS/EARS-TEMPLATE.md`
- `ai_dev_flow/BDD/BDD-TEMPLATE.feature`
- `ai_dev_flow/ADR/ADR-TEMPLATE.md`
- `ai_dev_flow/SYS/SYS-TEMPLATE.md`
- `ai_dev_flow/REQ/REQ-TEMPLATE.md`
- `ai_dev_flow/IMPL/IMPL-TEMPLATE.md`
- `ai_dev_flow/CTR/CTR-TEMPLATE.md`
- `ai_dev_flow/SPEC/SPEC-TEMPLATE.md`
- `ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml`
- `ai_dev_flow/TASKS/TASKS-TEMPLATE.md`
- `ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md`

**Creation Rules (13 files)**:
- `ai_dev_flow/*/_CREATION_RULES.md`

**Skills (12 files)**:
- `.claude/skills/doc-*/SKILL.md`

### Verification

```bash
# Verify TRACEABILITY.md updated
grep -n "Same-Type Document Relationships" ai_dev_flow/TRACEABILITY.md

# Verify templates updated
grep -r "Same-Type References" ai_dev_flow/*/*TEMPLATE*

# Verify creation rules updated
grep -r "@related-\|@depends-" ai_dev_flow/*/*_CREATION_RULES.md

# Verify skills updated
grep -r "Same-Type" .claude/skills/doc-*/SKILL.md
```

## References

- Primary file: `ai_dev_flow/TRACEABILITY.md`
- Plan file: `/home/ya/.claude/plans/lexical-launching-papert.md`
- Related work: Earlier upstream verification update (completed)
