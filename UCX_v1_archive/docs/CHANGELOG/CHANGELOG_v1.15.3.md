# CHANGELOG v1.15.3 - BRD-E002, BRD-E009, and GATE-E008 Auto-Fix Improvements

**Release Date**: 2026-03-14

## Overview

This release improves three existing auto-fixers to handle edge cases that were previously missed: status field defaults, document control table updates, and additional reference patterns.

## Bug Fixes

### BRD-E002: Status Field Default Fix

**Problem**: BRD-E002 fixer added `status: draft` which is not a valid value per BRD schema.

**Solution**: Changed default status value from `draft` to `development`.

**Valid Status Values**:
- `development`
- `production`
- `active`

### BRD-E009: Document Control Table Update Fix

**Problem**: BRD-E009 fixer only created a new Document Control section if none existed. Files with existing tables but missing fields were not updated.

**Solution**: Now parses existing Document Control tables and adds missing rows with appropriate defaults.

**Default Values Added**:
| Field | Default Value |
|-------|---------------|
| Project Name | "BeeLocal Cross-Border Remittance Platform" |
| Document Version | "1.0" |
| Date | Current date (YYYY-MM-DD) |
| Document Owner | "BeeLocal Team" |
| Status | "Draft" |

### GATE-E008: Extended Reference Pattern Detection

**Problem**: GATE-E008 duplicate ID detection missed several common reference patterns, causing false positive "duplicate ID" errors on referenced (non-definition) IDs.

**Solution**: Added detection for additional reference context patterns.

**New Patterns Detected**:
| Pattern Type | Example |
|--------------|---------|
| Parenthetical refs with suffix | `(BRD.14.23.01.02 target)` |
| Checkbox items | `- [ ] P1 BRD.40.01.01 — Auth0` |
| Priority-prefixed items | `- P1 BRD.40.01.01: Description` |
| Em-dash separated items | `BRD.40.01.01 — Auth0` |
| 4-part element IDs | `BRD.14.23.01.02` |
| @brd cross-references | `per @brd: BRD.03.01.04` |

**Pattern Sync**: `element_codes.py` and `duplicate_fixer.py` now share identical reference detection patterns.

## Impact

| Error Code | Errors Fixed |
|------------|--------------|
| BRD-E002 | ~45 |
| BRD-E009 | ~18 |
| GATE-E008 | ~32 |

## Files Modified

| File | Changes |
|------|---------|
| `ucx/validators/brd/fixer.py` | Fixed BRD-E002 status default, extended BRD-E009 table parsing |
| `ucx/validators/brd/element_codes.py` | Extended reference context patterns |
| `ucx/validators/brd/duplicate_fixer.py` | Synced patterns with element_codes.py |
| `ucx/version.py` | Updated to v1.15.3 |

## Usage

```bash
# Apply fixes to BRD directory
ucx validate brd docs/01_BRD/BRD-05_multi_agent_ai_system --fix

# Verify fixes applied
ucx validate brd docs/01_BRD/BRD-05_multi_agent_ai_system --no-report
```

## Backward Compatibility

All changes are backward compatible. Existing workflows continue to work unchanged.
