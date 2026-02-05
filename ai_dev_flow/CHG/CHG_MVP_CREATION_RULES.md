---
title: "CHG MVP Creation Rules"
tags:
  - creation-rules
  - change-management
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: CHG
  priority: shared
  development_status: active
  version: "2.0"
  last_updated: "2026-02-05"
---

# CHG Creation Rules

## 1. Change Classification System

All changes in the SDD framework are classified into three levels:

### 1.1 Classification Levels

| Level | Name | Description | Template | Process |
|-------|------|-------------|----------|---------|
| **L1** | Patch | Bug fixes, typos, clarifications | None (in-place edit) | Version increment only |
| **L2** | Minor | Feature additions, non-breaking changes | `CHG-MVP-TEMPLATE.md` | Lightweight CHG |
| **L3** | Major | Breaking changes, architectural pivots | `CHG-TEMPLATE.md` | Full CHG process |

### 1.2 Level Decision Matrix

| Change Characteristic | L1 Patch | L2 Minor | L3 Major |
|-----------------------|----------|----------|----------|
| Breaks existing functionality | No | No | Yes |
| Requires downstream regeneration | No | Partial | Full cascade |
| Affects architecture (ADR) | No | No | Yes |
| Deprecates existing artifacts | No | Optional | Required |
| Requires stakeholder approval | No | Optional | Required |
| Creates archive folder | No | No | Yes |

## 2. Change Sources

### 2.1 Five Change Sources

| # | Source | Origin Layers | Direction | Typical Level |
|---|--------|---------------|-----------|---------------|
| 1 | **Upstream** | L1-L4 (BRD→BDD) | Top-down cascade | L2-L3 |
| 2 | **Midstream** | L5-L11 (ADR→TASKS) | Bi-directional | L1-L3 |
| 3 | **Downstream** | L12-L14 (Code→Validation) | Bottom-up bubble | L1-L2 |
| 4 | **External** | Outside layers | Inject at appropriate layer | L1-L3 |
| 5 | **Feedback** | Post-L14 (Production) | Loop back to source | L1-L3 |

### 2.2 Source-Specific Guides

Detailed workflows for each source are documented in:
- `sources/UPSTREAM_CHANGE_GUIDE.md` - BRD/PRD/EARS/BDD changes
- `sources/MIDSTREAM_CHANGE_GUIDE.md` - ADR/SYS/REQ/CTR/SPEC/TSPEC/TASKS changes
- `sources/DOWNSTREAM_CHANGE_GUIDE.md` - Defect management from tests
- `sources/EXTERNAL_CHANGE_GUIDE.md` - Dependencies, security, third-party APIs
- `sources/FEEDBACK_CHANGE_GUIDE.md` - Production incidents, user feedback

## 3. When to Create a CHG

### 3.1 L3 Major (Full CHG Required)

Create a **full CHG artifact** when:

1. **Architectural Pivot**: Switching core technologies (e.g., database, framework, language)
2. **Strategy Shift**: Changing fundamental patterns (e.g., monolith to microservices)
3. **Mass Deprecation**: Retiring a significant set of requirements or capabilities
4. **Breaking Changes**: Changes that invalidate existing contracts or interfaces
5. **Security Incident**: Critical vulnerability requiring immediate architectural response

### 3.2 L2 Minor (Lightweight CHG)

Create a **lightweight CHG** when:

1. **Feature Addition**: New capability that extends existing architecture
2. **Non-Breaking Enhancement**: Improvement that maintains backward compatibility
3. **Partial Regeneration**: Change affecting 2-5 layers without architectural impact
4. **Dependency Update**: Library update with minor API changes
5. **Performance Optimization**: Design improvement without contract changes

### 3.3 L1 Patch (No CHG)

**Do NOT create a CHG** for:

1. Bug fixes with clear root cause at code level
2. Typos, formatting, documentation clarifications
3. Test additions that don't change requirements
4. Refactoring within a single component
5. Configuration changes

## 4. Lifecycle & Status

The `status` field tracks the change's progress:

| Status | Description | Next Action |
|--------|-------------|-------------|
| **Proposed** | Impact analysis in progress | Complete analysis, get approval |
| **Approved** | Approved for implementation | Begin archival and creation |
| **In Progress** | Migration steps being executed | Complete all steps |
| **Implemented** | Archival and creation complete | Execute TASKS, run tests |
| **Completed** | Verified and closed | None (terminal state) |
| **Rejected** | Change not approved | Document reason, close |
| **Rolled Back** | Change failed, reverted | Post-mortem analysis |

## 5. Rule of Immutability (CRITICAL)

> [!IMPORTANT]
> **You must NEVER modify an existing, approved artifact to reflect a fundamental change.**
> **You must ALWAYS Deprecate/Archive the old file and Create a NEW file.**

This ensures:
- History of the project is preserved
- Change is explicit and auditable
- LLM probabilistic errors are prevented
- Traceability chain remains intact

### 5.1 Immutability by Level

| Level | Immutability Rule |
|-------|-------------------|
| **L1 Patch** | Edit in place, increment patch version (1.0.0 → 1.0.1) |
| **L2 Minor** | Create new version OR new artifact, document change |
| **L3 Major** | MUST archive old, MUST create new with new ID |

## 6. File Organization

### 6.1 L3 Major CHG Structure (Full)

```
docs/CHG/CHG-XX_{slug}/
├── CHG-XX_{slug}.md        # The Definition (from CHG-TEMPLATE.md)
├── implementation_plan.md  # The Audit Log (frozen plan)
└── archive/                # The Graveyard (moved artifacts)
    ├── ADR-XX_old.md
    ├── SPEC-XX_old.yaml
    └── ...
```

### 6.2 L2 Minor CHG Structure (Lightweight)

```
docs/CHG/CHG-XX_{slug}/
├── CHG-XX_{slug}.md        # The Definition (from CHG-MVP-TEMPLATE.md)
└── implementation_plan.md  # Brief change log
```

Note: L2 Minor changes typically don't require an archive folder.

## 7. The Workflow

### 7.1 L3 Major Workflow (6 Steps)

| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | **Initialize** | CHG directory, CHG document, implementation plan |
| 2 | **Archive & Deprecate** | Artifacts moved to `archive/`, deprecation notices added |
| 3 | **Supersede** | New artifacts created in standard locations |
| 4 | **Repair & Audit** | All traceability links updated |
| 5 | **Execute** | TASKS implemented, TSPEC tests run |
| 6 | **Close** | Status updated to Completed, lessons documented |

### 7.2 L2 Minor Workflow (4 Steps)

| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | **Document** | CHG document with change summary |
| 2 | **Update** | Affected artifacts updated or versioned |
| 3 | **Validate** | Tests pass, traceability verified |
| 4 | **Close** | Status updated to Completed |

### 7.3 L1 Patch Workflow (2 Steps)

| Step | Action | Deliverable |
|------|--------|-------------|
| 1 | **Fix** | Edit artifact in place, increment version |
| 2 | **Validate** | Tests pass |

## 8. Cross-Linking Tags

**Purpose**: Establish machine-readable hints for AI discoverability.

| Tag | Purpose | Example |
|-----|---------|---------|
| `@depends: CHG-NN` | Hard prerequisite | `@depends: CHG-01` |
| `@discoverability: CHG-NN (rationale)` | Related document | `@discoverability: CHG-02 (related API)` |
| `@source: [type]` | Change source | `@source: Upstream (BRD-05)` |

**Validator Behavior**: Cross-linking tags are **info-level** (non-blocking).

## 9. Common Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| **Over-Scoping** | Assuming all related items must change | Check "Retaining" lists carefully |
| **Skipping Layers** | Ignoring middle layers (EARS, BDD, SYS) | V-Model requires ALL layers |
| **Missing TSPEC** | Forgetting test specifications | Layer 10 MUST be included |
| **Implicit Replacement** | Editing instead of archive+create | Violates immutability |
| **No Root Cause** | Fixing symptoms without analysis | Trace to source layer first |
| **Scope Creep** | Adding unrelated changes | One CHG = one focused change |

## 10. Validation

### 10.1 Pre-Commit Checks

```bash
# Validate CHG document structure
python CHG/scripts/validate_chg.py docs/CHG/CHG-XX_{slug}/

# Verify no orphaned references
python scripts/validate_traceability_matrix.py

# Check archived files have deprecation notices
grep -r "DEPRECATED" docs/CHG/CHG-XX_{slug}/archive/
```

### 10.2 Completion Checklist

- [ ] Change level correctly identified (L1/L2/L3)
- [ ] Change source documented
- [ ] Impact matrix complete (all 15 layers assessed)
- [ ] Archived files have deprecation notices (L3 only)
- [ ] New artifacts pass validation
- [ ] Traceability repaired (no broken links)
- [ ] TSPEC tests pass
- [ ] Status updated to Completed
