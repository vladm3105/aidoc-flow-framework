# Implementation Plan - Extend EARS_STYLE_GUIDE Additions to Other Document Types

**Created**: 2025-11-30 11:15:28 EST
**Completed**: 2025-11-30
**Status**: Completed

## Objective

Extend the additions from EARS_STYLE_GUIDE.md (now merged into EARS_CREATION_RULES.md) to other document types in the doc_flow SDD framework. Specifically:
1. Add Status/Score Mapping tables to 6 documents with scoring systems
2. Add Common Mistakes tables with document-specific error patterns

## Context

- EARS_STYLE_GUIDE.md was merged into EARS_CREATION_RULES.md (completed)
- Added: Status/BDD-Score mapping table, code block formatting, traceability format details, common mistakes table
- User selected "Full Extension" approach
- Only documents with readiness scoring systems are candidates

## Task List

### Completed
- [x] Merge EARS_STYLE_GUIDE.md into EARS_CREATION_RULES.md
- [x] Analyze all document types for scoring systems
- [x] Identify 6 files requiring updates
- [x] PRD_CREATION_RULES.md - Add Status/Score mapping + extend §20 common mistakes (v2.0 → v2.1)
- [x] BDD_CREATION_RULES.md - Add Status/Score mapping + new §12 common mistakes (v1.0 → v1.1)
- [x] ADR_CREATION_RULES.md - Add Status/Score mapping + new §12 common mistakes (v1.0 → v1.1)
- [x] SYS_CREATION_RULES.md - Add Status/Score mapping + new §12 common mistakes (v1.0 → v1.1)
- [x] SPEC_CREATION_RULES.md - Add Status/Score mapping + new §12 common mistakes (v1.0 → v1.1)
- [x] REQ_CREATION_RULES.md - Add Status/Score mapping + new §12 common mistakes (v3.0 → v3.1)

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/ai_dev_flow/` directory
- Understanding of each document type's scoring system

### Files to Modify

| # | File Path | Score Type | Version Bump |
|---|-----------|-----------|--------------|
| 1 | `ai_dev_flow/PRD/PRD_CREATION_RULES.md` | SYS-Ready + EARS-Ready | 2.0 → 2.1 |
| 2 | `ai_dev_flow/BDD/BDD_CREATION_RULES.md` | ADR-Ready | 1.0 → 1.1 |
| 3 | `ai_dev_flow/ADR/ADR_CREATION_RULES.md` | SYS-Ready | 1.0 → 1.1 |
| 4 | `ai_dev_flow/SYS/SYS_CREATION_RULES.md` | REQ-Ready | 1.0 → 1.1 |
| 5 | `ai_dev_flow/SPEC/SPEC_CREATION_RULES.md` | TASKS-Ready | 1.0 → 1.1 |
| 6 | `ai_dev_flow/REQ/REQ_CREATION_RULES.md` | SPEC-Ready + IMPL-Ready | 3.0 → 3.1 |

### Per-File Changes

#### Addition 1: Status/Score Mapping Table
Add after Document Control Requirements section in each file:

```markdown
### Status and [X]-Ready Score Mapping

| [X]-Ready Score | Required Status |
|-----------------|-----------------|
| >= 90% | Approved |
| 70-89% | In Review |
| < 70% | Draft |
```

Replace `[X]` with appropriate score type (SYS, EARS, ADR, REQ, TASKS, SPEC, IMPL).

#### Addition 2: Common Mistakes Tables

**PRD** (extend existing §20):
| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with 70% score) | `Status: In Review` |
| `@adr: ADR-012` (referencing ADR before it exists) | Omit ADR references in PRD |
| Missing section numbering | Use explicit `## N. Section Title` |

**BDD** (NEW section §12):
| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with <90% ADR-Ready score) | `Status: In Review` or `Status: Draft` |
| Missing @ears traceability tag | `@ears: EARS-NNN:STATEMENT-ID` |
| Scenario without tags | Add `@positive`, `@negative`, `@boundary` tags |
| `Given-When-Then` without concrete values | Use specific data in steps |

**ADR** (NEW section §12):
| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with <90% SYS-Ready score) | Match status to score threshold |
| Missing Consequences section | Document positive AND negative consequences |
| Alternatives without evaluation | Include trade-off analysis for each option |
| `@sys: SYS-NNN` (referencing downstream) | ADR should not reference downstream SYS |

**SYS** (NEW section §12):
| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with <90% REQ-Ready score) | Match status to score threshold |
| NFRs without percentiles | Use p50/p95/p99 for performance targets |
| Missing criticality level | Specify Mission-Critical/Business-Critical/Operational |
| Interface specs without CTR reference | Create CTR for external APIs |

**SPEC** (NEW section §12):
| Mistake | Correct |
|---------|---------|
| `status: approved` (with <90% TASKS-Ready score) | Match status to score threshold |
| Invalid YAML syntax | Validate with YAML linter before commit |
| Missing traceability.cumulative_tags | Include all upstream artifact tags |
| Hardcoded values in behavior | Use configuration references |

**REQ** (NEW section §12):
| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with <90% SPEC-Ready score) | Match status to score threshold |
| Missing upstream tags (need all 6) | Include @brd, @prd, @ears, @bdd, @adr, @sys |
| <15 acceptance criteria | Minimum 15 covering functional/error/quality |
| Template Version != 3.0 | Update to current template version |

### Update Checklist per File

1. Add Status/Score Mapping table after Document Control Requirements section
2. Add Common Mistakes section (new or extend existing)
3. Update TOC if needed (add new section reference)
4. Bump version number in header
5. Update Last Updated date to 2025-11-30
6. Update Changes field to describe additions

### Verification

After each file update:
1. Check markdown syntax renders correctly
2. Verify TOC links work
3. Confirm version bump is correct
4. Validate Changes field describes the additions

## References

- Completed merge: `ai_dev_flow/EARS/EARS_CREATION_RULES.md` (v1.1)
- Deleted source: `ai_dev_flow/EARS/EARS_STYLE_GUIDE.md`
- Plan file: `/home/ya/.claude/plans/purring-jingling-minsky.md`

## Skipped Document Types

- **BRD**: Uses 0-100 scale (not percentage)
- **IPLAN**: Score is optional/recommended
- **CTR, ICON, IMPL, TASKS**: No readiness scoring systems
