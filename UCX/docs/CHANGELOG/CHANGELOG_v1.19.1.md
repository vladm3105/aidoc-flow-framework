# UCX Framework v1.19.1 Changelog

**Release Date**: 2026-03-18

## Summary

This release improves the BRD validator auto-fixer with UCX-ACTION handoffs for downstream references and fixes false positives in duplicate element ID detection.

## New Features

### GATE-E002: UCX-ACTION Handoff Fixer

Premature downstream references in BRD documents are now automatically converted to structured UCX-ACTION handoff blocks instead of simple deferred comments.

**Supported Reference Patterns:**

| Pattern | Target Layer | Priority |
|---------|--------------|----------|
| `@prd: PRD-XX` | PRD (Layer 2) | P1 |
| `@adr: ADR-XX` | ADR (Layer 5) | P1 |
| `@sys: SYS-XX` | SYS (Layer 6) | P1 |
| `@req: REQ.XX` | REQ (Layer 7) | P2 |

**Example Transformation:**

Before:
```markdown
@adr: ADR-56-001 (Identity Provider Migration Strategy)
```

After:
```markdown
@adr
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-8e95d0bf
TYPE: HANDOFF
TARGET: ADR
PRIORITY: P1
SOURCE: BRD-56
CONTEXT: Identity Provider Migration Strategy
REQUIREMENT: Create ADR-56-001 document
<!-- UCX-ACTION-END -->
```

**Benefits:**
- Structured handoff format compatible with UCX review workflow
- Unique ACTION_ID for tracking
- Clear REQUIREMENT field for downstream document creation
- SOURCE traceability back to BRD
- Priority assignment (P1/P2)

### GATE-E008: False Positive Fixes

The duplicate element ID detector now correctly distinguishes between element **definitions** and **references**, eliminating false positives.

**New Reference Context Patterns:**

| Pattern | Description | Example |
|---------|-------------|---------|
| Bold field labels | `**Field**:` followed by IDs | `**Related Requirements**: BRD.19.01.01` |
| Parenthetical with prefix | `(text BRD.XX.XX.XX ...)` | `(see BRD.43.01.08 OFAC Handling)` |
| Validation references | `(validates: BRD.XX)` | `(validates: BRD.49.23.05)` |

**Files Modified:**
- `ucx/validators/brd/element_codes.py`: Added reference context patterns
- `ucx/validators/brd/fixer.py`: Added GATE-E002 UCX-ACTION fixer

## Bug Fixes

### False Positive: Bold Field Labels
- **Issue**: `**Related Requirements**: BRD.19.01.01` was flagged as duplicate definition
- **Fix**: Added pattern `^\*\*(?!BRD\.)[^*]+\*\*:` to detect bold field labels as reference contexts
- **Affected BRDs**: BRD-19 and similar documents with "Related Requirements" fields

### False Positive: Parenthetical References with Prefix
- **Issue**: `(see BRD.43.01.08 OFAC Hit Handling SLA)` was flagged as duplicate
- **Fix**: Added pattern `\([^)]*\bBRD\.\d{2,}\.\d{2}\.\d{2,}[^)]*\)` to detect parenthetical references with text before the ID
- **Affected BRDs**: BRD-43, BRD-49 and similar documents with inline references

## Upgrade Notes

### Automatic Migration
No manual migration required. The new patterns are backward-compatible.

### Verification
Run validation on affected BRDs to verify fixes:

```bash
ucx validate brd docs/01_BRD/ --tier1-only
```

### Expected Results
- GATE-E008 false positives eliminated
- GATE-E002 errors converted to UCX-ACTION handoffs
- No regression in existing validations

## Technical Details

### Reference Context Detection Logic

The `_is_reference_context()` function in `element_codes.py` uses the following priority:

1. Check filename (traceability files, index files)
2. Check section (Section 16 = Traceability)
3. Check for backtick-wrapped IDs
4. Check if line is a definition (return False if definition)
5. Check table rows
6. Check parenthetical patterns
7. Check bold field labels (NEW)
8. Check constraint/driver references
9. Check multiple IDs on same line
10. Check range notation
11. Default: return False (treat as definition)

### UCX-ACTION Generation

The `_fix_gate_e002()` method in `fixer.py`:

1. Extracts BRD ID from file path
2. Matches downstream reference patterns
3. Generates unique 8-char hex ACTION_ID
4. Builds UCX-ACTION block with:
   - TYPE: HANDOFF
   - TARGET: PRD/ADR/SYS/REQ
   - PRIORITY: P1 or P2
   - SOURCE: BRD-XX
   - CONTEXT: Extracted description
   - REQUIREMENT: Document creation instruction

## Compatibility

- **Python**: 3.9+
- **UCX Framework**: 1.18.0+ (for UCX-ACTION support)
- **Pre-commit**: Compatible with existing hooks

## Contributors

- Claude Code (Opus 4.5)
