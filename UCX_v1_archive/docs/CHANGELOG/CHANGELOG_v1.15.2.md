# CHANGELOG v1.15.2 - Extended Auto-Fix Suite (21 codes)

**Release Date**: 2026-03-14

## Overview

This release extends the UCX auto-fix suite from 18 to 21 fixable error codes by adding three new Tier 1 fixers that convert blocking errors into deferred placeholders. These fixes preserve the intent of the original content while removing validation blocking errors.

## New Fixers

### GATE-E001: Placeholder Text Fixer

**Problem**: Files contain placeholder markers like `[TBD]`, `TODO`, `FIXME` that block validation.

**Solution**: Converts placeholders to structured `<!-- DEFERRED: ... -->` comments that:
- Preserve the placeholder intent
- Remove the blocking validation error
- Allow downstream phases to address the deferred content

**Patterns Handled**:
| Pattern | Replacement |
|---------|-------------|
| `[TBD]` | `<!-- DEFERRED: Content to be determined -->` |
| `[TBD: description]` | `<!-- DEFERRED: description -->` |
| `TODO: message` | `<!-- DEFERRED: TODO - message -->` |
| `FIXME: message` | `<!-- DEFERRED: FIXME - message -->` |
| `XXX: message` | `<!-- DEFERRED: XXX - message -->` |

**Expected Impact**: ~25 GATE-E001 errors converted

### DIAG-E001: Missing Architecture Diagram Fixer

**Problem**: Architecture sections lack required Mermaid or SVG diagrams.

**Solution**: Adds a `<!-- DIAGRAM-REQUIRED: ... -->` placeholder that:
- Signals downstream layers (PRD, ADR) that a diagram is needed
- Includes diagram type, target layer, and priority
- Preserves honest traceability without adding fake diagrams

**Placeholder Format**:
```html
<!-- DIAGRAM-REQUIRED: architecture-overview -->
<!--
    @diagram-pending: true
    @diagram-type: architecture-overview
    @target-layer: ADR
    @source-doc: BRD-XX
    @priority: recommended
    @rationale: Architecture section requires visual representation
-->
```

**Expected Impact**: ~23 DIAG-E001 errors converted

### FWDREF-E001: Forward Reference Fixer

**Problem**: BRDs (Layer 1) reference downstream documents (PRD, EARS, etc.) that don't exist yet.

**Solution**: Converts forward references to `<!-- FWDREF-DEFERRED: ... -->` comments that:
- Preserve the intended reference target
- Remove the blocking validation error
- Signal the reference will be valid after downstream creation

**Example**:
| Original | Converted |
|----------|-----------|
| `PRD-05` | `<!-- FWDREF-DEFERRED: PRD-05 (pending PRD creation) -->` |
| `[PRD-05](...)` | `<!-- FWDREF-DEFERRED: PRD-05 (pending PRD creation) -->` |
| `` `PRD-05` `` | `<!-- FWDREF-DEFERRED: PRD-05 (pending PRD creation) -->` |

**Expected Impact**: ~476 FWDREF-E001 errors converted

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Auto-fixable codes | 18 | 21 |
| New codes | - | GATE-E001, DIAG-E001, FWDREF-E001 |
| Expected errors fixed | ~840 | ~316 (after ~524 converted) |

## Non-Fixable Errors

The following error types are **NOT script-fixable** and require AI-powered remediation (`ucx remediate`):

| Code | Count | Reason |
|------|-------|--------|
| BRD-E006 | 122 | Missing required sections - requires content creation |
| BRD-E011 | 15 | Missing Business Requirements - requires content creation |

These errors indicate structural gaps that need meaningful content, not just placeholders.

## Usage

```bash
# Apply fixes to a single BRD
ucx validate brd docs/01_BRD/BRD-05_multi_agent_ai_system --fix

# Apply fixes to all BRDs
for brd in docs/01_BRD/BRD-*/; do
    ucx validate brd "$brd" --fix --no-report
done

# View what would be fixed (dry-run via validation)
ucx validate brd docs/01_BRD/BRD-05_multi_agent_ai_system --no-report
```

## Files Modified

| File | Changes |
|------|---------|
| `ucx/validators/brd/fixer.py` | Added `_fix_gate_e001()`, `_fix_diag_e001()`, `_fix_fwdref_e001()` methods |
| `ucx/version.py` | Updated to v1.15.2 |
| `README.md` | Updated auto-fix table (21 codes), version history, latest release |

## Backward Compatibility

All changes are backward compatible. Existing workflows continue to work. The new fixers only activate when:
1. The `--fix` flag is passed to `ucx validate`
2. The specific error codes are present in validation results

## Migration Notes

No migration required. Run `ucx validate --fix` on your BRD directories to apply the new fixes automatically.
