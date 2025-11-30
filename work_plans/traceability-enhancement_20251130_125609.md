# Implementation Plan - Traceability Enhancement

**Created**: 2025-11-30 12:56:09 EST
**Status**: Completed
**Completed**: 2025-11-30 13:05 EST

## Objective

Enhance `ai_dev_flow/TRACEABILITY.md` with 4 valuable additions from the Unified Traceability Framework document:
1. Quick Reference Card (tag counts by layer + separator rules)
2. Schema Authority Principle (schema > style guide conflict resolution)
3. Optional Extension Tags (@threshold, @entity)
4. Tag Format Specification (consolidated format rules)

## Context

### Background
- User provided a "Unified Traceability Framework for SDD Artifacts" document from BeeLocal project
- Analysis showed 80% overlap with existing docs_flow_framework documentation
- Decision: Surgical enhancement of existing TRACEABILITY.md rather than creating new file

### Key Decisions
- Full adoption of @threshold and @entity tags as optional extensions
- Ignore EARS_STYLE_GUIDE conflict (already implemented per schema)
- Enhance existing file rather than duplicate content

### Existing Documentation Structure
| File | Purpose | Lines |
|------|---------|-------|
| `TRACEABILITY.md` | Comprehensive guide | 1,537 |
| `TRACEABILITY_SETUP.md` | Scripts, CI/CD | 353 |
| `TRACEABILITY_VALIDATION.md` | Quality gates | ~200 |

## Task List

### Completed
- [x] Read full TRACEABILITY.md to identify optimal insertion points
- [x] Add Schema Authority Principle section (after "Core Principle" ~line 30)
- [x] Add Quick Reference Card section (after "Layer Numbering Reference" ~line 276)
- [x] Add Optional Extension Tags section (after "Same-Type Relationship Tags")
- [x] Tag Format Specification already comprehensive - no changes needed
- [x] Verify no duplication with existing content
- [x] Validate markdown formatting (pre-existing style issues only)

## Implementation Guide

### Prerequisites
- Read current state of `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md`
- Identify exact line numbers for insertion points

### Content to Add

#### 1. Schema Authority Principle (after Core Principle section)

```markdown
### Schema Authority Principle

**Critical Rule**: `*_SCHEMA.yaml` files are the single source of truth for their respective artifact types. When conflicts exist between style guides and schemas, **the schema is authoritative**.

| Artifact | Schema File | Layer |
|----------|-------------|-------|
| PRD | `ai_dev_flow/PRD/PRD_SCHEMA.yaml` | 2 |
| EARS | `ai_dev_flow/EARS/EARS_SCHEMA.yaml` | 3 |
| BDD | `ai_dev_flow/BDD/BDD_SCHEMA.yaml` | 4 |
| ADR | `ai_dev_flow/ADR/ADR_SCHEMA.yaml` | 5 |
| SYS | `ai_dev_flow/SYS/SYS_SCHEMA.yaml` | 6 |
| REQ | `ai_dev_flow/REQ/REQ_SCHEMA.yaml` | 7 |
| CTR | `ai_dev_flow/CTR/CTR_SCHEMA.yaml` | 9 |
| SPEC | `ai_dev_flow/SPEC/SPEC_SCHEMA.yaml` | 10 |
| TASKS | `ai_dev_flow/TASKS/TASKS_SCHEMA.yaml` | 11 |
| IPLAN | `ai_dev_flow/IPLAN/IPLAN_SCHEMA.yaml` | 12 |
```

#### 2. Quick Reference Card

```markdown
## Quick Reference Card

### Tag Counts by Layer

| Layer | Artifact | Min Tags | Max Tags |
|-------|----------|----------|----------|
| 1 | BRD | 0 | 0 |
| 2 | PRD | 1 | 1 |
| 3 | EARS | 1 | 2 |
| 4 | BDD | 3 | 3 |
| 5 | ADR | 4 | 4 |
| 6 | SYS | 5 | 5 |
| 7 | REQ | 6 | 6 |
| 8 | IMPL | 7 | 7 |
| 9 | CTR | 7 | 8 |
| 10 | SPEC | 7 | 9 |
| 11 | TASKS | 8 | 10 |
| 12 | IPLAN | 9 | 11 |

### Tag Separator Rules

| Format | Status |
|--------|--------|
| Space + Pipe + Space (` \| `) | **CORRECT** |
| Comma (`,`) | **INCORRECT** |
| Trailing comma (`, \|`) | **INCORRECT** |
```

#### 3. Optional Extension Tags

```markdown
## Optional Extension Tags

Projects may define optional tags for cross-referencing specialized documents:

| Tag | Format | Use Case |
|-----|--------|----------|
| @threshold | `PRD-NNN:category.key` | Reference timing/limits from Platform Threshold Registry |
| @entity | `PRD-NNN:EntityName` | Reference data entities from Data Model document |

### @threshold Tag Usage

References centralized timing, limits, and configuration values.

**Format**: `@threshold: PRD-035:category.key`

**Example Categories**:
- `kyc.*` - KYC timing and limits
- `transaction.*` - Transaction processing
- `compliance.*` - Compliance thresholds
- `security.*` - Security parameters
- `system.*` - System performance

**Example**:
```markdown
**Traceability**: @prd: PRD-006:FR-006-001 | @threshold: PRD-035:kyc.tier1_timeout
```
```

#### 4. Tag Format Specification

```markdown
### Tag Format Specification

**Standard Syntax**:
```
@artifact-type: DOCUMENT-ID:REQUIREMENT-ID
```

**Examples**:
- `@brd: BRD-001:FR-001`
- `@prd: PRD-006:FR-006-001`
- `@ears: EARS-006:EARS-006-001`

**SPEC YAML Format** (Layer 10 - no @ prefix):
```yaml
traceability:
  cumulative_tags:
    brd: "BRD-001:FR-001"
    prd: "PRD-006:FR-006-001"
```
```

### Verification
- [ ] All 4 sections added to TRACEABILITY.md
- [ ] No duplicate content with existing sections
- [ ] Markdown renders correctly
- [ ] Table formatting is correct

## References

- **Target file**: `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md`
- **Source document**: User-provided Unified Traceability Framework (BeeLocal)
- **Related docs**: TRACEABILITY_SETUP.md, TRACEABILITY_VALIDATION.md
- **Plan file**: `/home/ya/.claude/plans/fizzy-stirring-sutton.md`
