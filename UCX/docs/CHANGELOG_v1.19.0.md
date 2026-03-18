# Changelog v1.19.0 - Hash-Based Finding IDs

**Release Date**: 2026-03-18
**Status**: Released

## Overview

UCX v1.19.0 introduces **hash-based finding and action ID generation** (PLAN-008), replacing sequential IDs (`REM-P1-001`) with content-addressable hash IDs (`P1-a7f3`). This eliminates state synchronization issues, enables natural deduplication, and provides stable cross-version tracking.

## Key Features

### Hash-Based Finding IDs

| Aspect | Before (v1.18) | After (v1.19) |
|--------|----------------|---------------|
| Format | `REM-P{0-2}-{NNN}` | `P{0-2}-{xxxx}` |
| Example | `REM-P1-001` | `P1-a7f3` |
| State | Sequential counter | Stateless hash |
| Deduplication | Manual tracking | Automatic |
| Cross-version | Different IDs | Same ID |

### Hash-Based Action IDs

| Aspect | Before (v1.18) | After (v1.19) |
|--------|----------------|---------------|
| Format | `ACT-{NNN}` | `ACT-{xxxx}` |
| Example | `ACT-001` | `ACT-a7f3` |
| State | Sequential counter | Stateless hash |

### Benefits

1. **Stateless Generation**: No counter synchronization needed across 11+ personas
2. **Deterministic**: Same finding content always produces same ID
3. **Natural Deduplication**: Identical findings = identical hashes
4. **Stable Tracking**: Same finding tracks across report versions
5. **Simpler Code**: ~50 lines state management reduced to ~20 lines

## New Components

### FindingIDGenerator

```python
from ucx.utils.finding_hash import FindingIDGenerator, FindingIdentity

gen = FindingIDGenerator()
identity = FindingIdentity(
    priority="P1",
    target_file="BRD-02.6_functional.md",
    target_section="Section 6.1",
    category="compliance",
    description="SAR filing workflow missing"
)
finding_id = gen.generate(identity)  # Returns "P1-a7f3"
```

### ActionIDGenerator

```python
from ucx.utils.finding_hash import ActionIDGenerator, ActionIdentity

gen = ActionIDGenerator()
identity = ActionIdentity(
    fixer="auditor",
    target_file="PRD-01",
    target_section="Section 3.2",
    description="Add SAR filing user story"
)
action_id = gen.generate(identity)  # Returns "ACT-b2c1"
```

### CategoryConflictResolver.resolve_with_id()

```python
from ucx.scoring.conflicts import CategoryConflictResolver

resolver = CategoryConflictResolver()
resolution, finding_id = resolver.resolve_with_id(
    finding_text="SAR filing workflow missing",
    target_file="BRD-02.6_functional.md",
    target_section="Section 6.1",
    persona="auditor",
    priority="P1",
)
# finding_id: "P1-a7f3"
# resolution: ConflictResolution with category info
```

## Hash Algorithm

Finding IDs are generated from content hash:

```
hash_input = "{file}:{section}:{category}:{description[:100]}"
hash = sha256(hash_input)[:4]  # 4-8 chars, extends on collision
id = f"P{priority}-{hash}"     # e.g., "P1-a7f3"
```

### Collision Handling

- Default hash length: 4 characters (65,536 combinations)
- Collision probability: <0.02% for 50 findings
- Auto-extends to 8 characters if collision detected
- Fallback: sequence suffix (e.g., `P1-a7f31`) for extremely rare edge cases

## Backward Compatibility

### Dual-Format Support

During the transition period (v1.19.0-v1.20.0), UCX accepts both formats:

| Format | Pattern | Status |
|--------|---------|--------|
| Legacy | `REM-P{0-2}-{NNN}` | Supported (deprecated) |
| Legacy | `ARCH-P{0-2}-{NNN}` | Supported (deprecated) |
| Hash | `P{0-2}-{xxxx}` | **Recommended** |

### Migration Path

| Version | Behavior |
|---------|----------|
| v1.19.0 | Generate hash IDs, accept both formats |
| v1.20.0 | Hash-only generation, accept both formats |
| v2.0.0 | Remove legacy format support |

### ID Detection Utilities

```python
from ucx.utils.finding_hash import (
    is_legacy_finding_id,
    is_hash_finding_id,
    normalize_finding_id,
)

is_legacy_finding_id("REM-P0-001")  # True
is_hash_finding_id("P1-a7f3")       # True
normalize_finding_id("REM-P1-001") # "P1-LEGACY"
```

## Files Changed

| File | Change |
|------|--------|
| `ucx/utils/finding_hash.py` | **NEW** - Core hash module |
| `ucx/utils/__init__.py` | Added exports |
| `ucx/scoring/conflicts.py` | Added `resolve_with_id()` |
| `ucx/core/context_engine.py` | Dual-format pattern support |
| `ucx/core/review_memory.py` | **UPDATED** - Integrated hash-based ID generation in `_extract_findings()` |
| `tests/unit/test_finding_hash.py` | **NEW** - 43 unit tests |
| `docs/plans/PLAN-008_hash_based_finding_ids.md` | **NEW** - Design document |

## Bug Fixes

### Review Pipeline Integration (v1.19.0-patch1)

**Issue**: Hash-based IDs were implemented but not integrated into the review assembly pipeline. Review reports still displayed legacy persona-prefix format (`ARCH-P0-001`) instead of hash-based format (`P0-a7f3`).

**Fix**: Updated `ucx/core/review_memory.py`:
- Added import for `FindingIDGenerator` and `FindingIdentity`
- Added `SECTION_PATTERN` for extracting section references from finding context
- Modified `_extract_findings()` to generate hash-based IDs using content hash
- Findings now include both `id` (hash-based) and `legacy_id` (persona-prefix) for traceability

**Finding Dict Structure** (after fix):
```python
{
    "id": "P0-a7f3",        # New hash-based ID
    "legacy_id": "ARCH-P0-001",  # Original persona-prefix (traceability)
    "persona": "architect",
    "priority": "P0",
    "category": "compliance",
    ...
}
```

## Test Coverage

- **43 unit tests** covering:
  - FindingIDGenerator (13 tests)
  - ActionIDGenerator (4 tests)
  - Normalization functions (9 tests)
  - ID format utilities (6 tests)
  - Dual-format patterns (5 tests)
  - Identity dataclasses (2 tests)
  - Review memory integration (4 tests)

## Configuration

```yaml
# ucx.yaml (optional)
finding_id:
  format: "hash"        # "hash" (v1.19+) or "sequential" (legacy)
  hash_length: 4        # Minimum hash length (4-8)
```

## References

- [PLAN-008: Hash-Based Finding IDs](plans/PLAN-008_hash_based_finding_ids.md)
- [SCORING_GUIDE.md](scoring/SCORING_GUIDE.md) - Updated manifest format
- [CHANGELOG_v1.18.0.md](CHANGELOG_v1.18.0.md) - Previous version

---

*Released: 2026-03-18*
*Author: Claude Opus 4.5*
