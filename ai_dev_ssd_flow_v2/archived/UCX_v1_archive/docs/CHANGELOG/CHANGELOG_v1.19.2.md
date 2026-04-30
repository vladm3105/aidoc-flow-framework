# UCX Framework v1.19.2 Changelog

**Release Date**: 2026-03-18

## Summary

This release implements a unified UCX-ACTION approach for all internal tasks and handoffs. Placeholders (TODO, [TBD], FIXME) and legacy DEFERRED comments are now converted to UCX-ACTION blocks with `TYPE: INTERNAL` for consistent task tracking across the BRD layer.

## New Features

### Unified UCX-ACTION Format

All auto-fixers now use a unified UCX-ACTION format for task tracking:

```markdown
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-xxxxxxxx
TYPE: {INTERNAL|HANDOFF}
TARGET: {BRD|PRD|ADR|SYS|REQ|...}
PRIORITY: {P0|P1|P2|P3}
SOURCE: BRD-XX Section Y
CONTEXT: {PREFIX}: Description
REQUIREMENT: What needs to be done
<!-- UCX-ACTION-END -->
```

| Field | Description |
|-------|-------------|
| **TYPE** | `INTERNAL` for same-layer tasks, `HANDOFF` for downstream layers |
| **TARGET** | `BRD` for internal tasks, layer acronym for handoffs |
| **PRIORITY** | P0=Critical, P1=High, P2=Medium, P3=Low |
| **CONTEXT** | Prefixed description (TODO:, TBD:, MOVE:, FIXME:, etc.) |

### GATE-E001: UCX-ACTION INTERNAL Blocks

Placeholder text is now converted to UCX-ACTION INTERNAL blocks instead of DEFERRED comments.

**Before:**
```markdown
TODO: Add monitoring thresholds
[TBD]
FIXME: Update SLA values
```

**After:**
```markdown
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-a1b2c3d4
TYPE: INTERNAL
TARGET: BRD
PRIORITY: P2
SOURCE: BRD-49 Section 6
CONTEXT: TODO: Add monitoring thresholds
REQUIREMENT: Complete: Add monitoring thresholds
<!-- UCX-ACTION-END -->
```

### GATE-W008: UCX-ACTION for Move Tasks

Elements in wrong sections now get UCX-ACTION INTERNAL blocks instead of simple move markers.

**Before:**
```markdown
<!-- MOVE-TO-SECTION: Element type 23 → Section 2 -->
```

**After:**
```markdown
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-b2c3d4e5
TYPE: INTERNAL
TARGET: BRD
PRIORITY: P2
SOURCE: BRD-49 Section 5
CONTEXT: MOVE: Element type 23 in wrong section
REQUIREMENT: Relocate to Section 2
<!-- UCX-ACTION-END -->
```

### Legacy DEFERRED Migration

Existing DEFERRED comments are automatically migrated to UCX-ACTION format:

**Before:**
```markdown
<!-- DEFERRED: Move to Section 2 (element type 23) -->
```

**After:**
```markdown
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-c3d4e5f6
TYPE: INTERNAL
TARGET: BRD
PRIORITY: P2
SOURCE: BRD-49
CONTEXT: CONTENT: Move to Section 2 (element type 23)
REQUIREMENT: Add missing content
<!-- UCX-ACTION-END -->
```

## Design Decisions

### Why UCX-ACTION INTERNAL?

1. **Unified Format**: Same block structure for both internal tasks and downstream handoffs
2. **Validation Score Impact**: INTERNAL actions DO affect validation score (unlike DEFERRED comments)
3. **No PERSONA Field**: Removed for internal actions (only relevant for cross-layer handoffs)
4. **Full Format**: No compact option - consistent format aids parsing and tooling
5. **Actionable Requirements**: Each block has clear CONTEXT and REQUIREMENT fields

### Context Prefixes

The CONTEXT field uses prefixes to categorize the type of task:

| Prefix | Use Case |
|--------|----------|
| `TODO:` | TODO comments from code |
| `FIXME:` | FIXME markers |
| `XXX:` | XXX flags |
| `TBD:` | Content to be determined |
| `PENDING:` | Pending content |
| `CONTENT:` | Generic content placeholder |
| `MOVE:` | Element relocation task |
| `PLACEHOLDER:` | Explicit placeholder markers |

## Bug Fixes

None in this release.

## Breaking Changes

- **DEFERRED comments deprecated**: All new placeholder fixes generate UCX-ACTION blocks
- **Move markers deprecated**: GATE-W008 now uses UCX-ACTION instead of `<!-- MOVE-TO-SECTION: ... -->`
- **Migration automatic**: Running `ucx validate` will migrate existing DEFERRED comments

## Migration Guide

1. Run `ucx validate brd <path>` on your BRD documents
2. The validator will automatically migrate DEFERRED comments to UCX-ACTION
3. Review the migrated UCX-ACTION blocks for accuracy
4. Commit the changes

## Files Changed

- `ucx/validators/brd/fixer.py` - Updated `_fix_gate_e001()`, `_fix_gate_w008()`, added `_migrate_deferred_comments()`
- `ucx/validators/README.md` - Added unified UCX-ACTION documentation
- `ucx/cli/main.py` - Always run fixer for migration even with no issues
- `ucx/version.py` - Bumped to 1.19.2

## Testing

Validated on BeeLocal documentation project:
- BRD-49: 21 DEFERRED comments migrated successfully
- Multiple BRDs: 34 total migrations across documents
- No regressions in existing GATE-E002, GATE-E008 fixes
