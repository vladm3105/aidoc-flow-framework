# PLAN-008: Hash-Based Finding and Action ID Generation

## Overview

Replace sequential IDs for Findings (`REM-P1-001`) and Actions (`ACT-001`) with content-based hash IDs (`P1-a7f3`, `ACT-a7f3`) to eliminate state synchronization, prevent duplicates, and enable stable cross-version tracking.

**Problem Statement**: UCX v1.18.0 uses sequential counters for review report IDs:
- 11 personas generate findings in parallel requiring counter synchronization
- Duplicate IDs possible when counter state mismanaged
- Re-running review generates different IDs for identical findings/actions
- Cannot track same finding/action across report versions

**Root Causes**:
1. Sequential ID generation requires stateful counters
2. Counter must be synchronized across parallel persona executions
3. Deduplication breaks sequence continuity (gaps: 001, 003, 007)
4. No content-addressable identity for findings or actions

**Solution**: Content-based hash IDs with:
- Stateless generation from `{file}:{section}:{category}:{description}`
- Deterministic: same finding/action always produces same ID
- Natural deduplication (identical content = identical hash)
- Priority/type preserved in ID format (`P0-xxxx`, `P1-xxxx`, `ACT-xxxx`)

---

## Scope

### In Scope (Hash-Based IDs)

| ID Type | Current Format | Proposed Format | Context |
|---------|---------------|-----------------|---------|
| **Finding IDs** | `REM-P1-001` | `P1-a7f3` | Review reports |
| **Action IDs** | `ACT-001` | `ACT-a7f3` | Handoff actions |

### Out of Scope (Keep Sequential)

| ID Type | Format | Rationale |
|---------|--------|-----------|
| **Document Element IDs** | `BRD.02.01.05` | Traceability chains across SDD layers |
| **Feature IDs** | `PRD.02.01.05` | Human readability, ordering, navigation |
| **Acceptance Criteria** | `TYPE.NN.06.SS` (e.g., `BRD.50.06.01`) | Tied to requirement structure |
| **Risk IDs** | `BRD.02.07.01` | Document-bound, sequential authoring |
| **Report Version IDs** | `v001`, `v002` | Version progression tracking |
| **Document IDs** | `BRD-01`, `BRD-02` | Intentional project numbering |

**Rationale**: Findings and Actions are:
- Generated in parallel by multiple AI personas
- Transient (scoped to single review session)
- Not part of cross-document traceability chains
- Subject to deduplication during report assembly

Document element IDs require sequential numbering for:
- Human-readable traceability (`BRD.02 → PRD.02 → REQ.02`)
- Logical ordering within sections
- Navigation and cross-referencing

**Status**: Implemented (v1.19.0)
**Target Version**: UCX 1.19.0
**Estimated Effort**: Low-Medium complexity
**Implementation Date**: 2026-03-18

### Implementation Progress

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Core hash module (`ucx/utils/finding_hash.py`) |
| Phase 2 | ✅ Complete | Integration with scoring/conflicts.py |
| Phase 3 | ⏳ Pending | Prompt template updates (deferred - requires LLM testing) |
| Phase 4 | ✅ Complete | Backward compatibility layer (context_engine.py) |
| Phase 5 | ✅ Complete | Unit tests (39 passing tests) |
| Phase 6 | ⏳ Pending | Documentation updates |

### Implementation Summary (2026-03-18)

**Files Created:**
- `ucx/utils/finding_hash.py` - Core hash module with FindingIDGenerator, ActionIDGenerator

**Files Modified:**
- `ucx/utils/__init__.py` - Exports for new classes and utilities
- `ucx/scoring/conflicts.py` - Added `resolve_with_id()` method
- `ucx/core/context_engine.py` - Updated patterns for dual-format support

**Test Coverage:**
- `tests/unit/test_finding_hash.py` - 39 unit tests passing

---

## Design

### Current vs Proposed ID Format

#### Finding IDs

| Aspect | Current (Sequential) | Proposed (Hash) |
|--------|---------------------|-----------------|
| Format | `REM-P{0-2}-{NNN}` | `P{0-2}-{xxxx}` |
| Example | `REM-P1-001` | `P1-a7f3` |
| Length | 10 chars | 7 chars |
| State | Counter per priority | Stateless |
| Uniqueness | Per-report sequence | Content-addressable |
| Stability | Changes each run | Deterministic |

#### Action IDs (Handoff Actions)

| Aspect | Current (Sequential) | Proposed (Hash) |
|--------|---------------------|-----------------|
| Format | `ACT-{NNN}` | `ACT-{xxxx}` |
| Example | `ACT-001` | `ACT-a7f3` |
| Length | 7 chars | 8 chars |
| State | Counter | Stateless |
| Uniqueness | Per-report sequence | Content-addressable |
| Stability | Changes each run | Deterministic |

### Hash Generation Algorithm

```python
import hashlib
import re

def generate_finding_id(
    priority: str,
    target_file: str,
    target_section: str,
    category: str,
    description: str,
    hash_length: int = 4
) -> str:
    """
    Generate deterministic finding ID using content hash.

    Args:
        priority: P0, P1, or P2
        target_file: Target file path (normalized)
        target_section: Section identifier
        category: Finding category (functional, compliance, etc.)
        description: Finding description (first 100 chars, normalized)
        hash_length: Hash suffix length (default: 4)

    Returns:
        Finding ID in format: P{0-2}-{hash}
    """
    # Normalize inputs
    file_norm = _normalize_path(target_file)
    section_norm = _normalize_section(target_section)
    desc_norm = _normalize_description(description)

    # Create hash input
    hash_input = f"{file_norm}:{section_norm}:{category}:{desc_norm}"

    # Generate hash
    hash_digest = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    hash_suffix = hash_digest[:hash_length]

    return f"{priority}-{hash_suffix}"


def generate_action_id(
    fixer: str,
    target_file: str,
    target_section: str,
    description: str,
    hash_length: int = 4
) -> str:
    """
    Generate deterministic action ID using content hash.

    Args:
        fixer: Assigned fixer persona (auditor, tech_lead, etc.)
        target_file: Target file path (normalized)
        target_section: Section identifier
        description: Action description (first 100 chars, normalized)
        hash_length: Hash suffix length (default: 4)

    Returns:
        Action ID in format: ACT-{hash}
    """
    # Normalize inputs
    file_norm = _normalize_path(target_file)
    section_norm = _normalize_section(target_section)
    desc_norm = _normalize_description(description)

    # Create hash input
    hash_input = f"{fixer}:{file_norm}:{section_norm}:{desc_norm}"

    # Generate hash
    hash_digest = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    hash_suffix = hash_digest[:hash_length]

    return f"ACT-{hash_suffix}"
```

### Hash Input Components

#### Finding IDs

| Component | Normalization | Purpose |
|-----------|---------------|---------|
| `target_file` | Extract `BRD-XX.N` pattern, lowercase | Scope to document file |
| `target_section` | Remove "Section " prefix, lowercase | Scope to location |
| `category` | Lowercase | Differentiate finding types |
| `description[:100]` | Remove special chars, normalize whitespace | Content uniqueness |

#### Action IDs

| Component | Normalization | Purpose |
|-----------|---------------|---------|
| `fixer` | Lowercase | Assigned persona (auditor, tech_lead, etc.) |
| `target_file` | Extract `BRD-XX.N` pattern, lowercase | Scope to document file |
| `target_section` | Remove "Section " prefix, lowercase | Scope to location |
| `description[:100]` | Remove special chars, normalize whitespace | Action uniqueness |

### Collision Analysis

With 4-character hex hash (16^4 = 65,536 combinations):

| Findings per Report | Collision Probability | Acceptable |
|---------------------|----------------------|------------|
| 50 | ~0.02% | Yes |
| 100 | ~0.07% | Yes |
| 200 | ~0.3% | Yes |
| 500 | ~1.9% | Yes |

**Collision Resolution**: Auto-extend hash length from 4 to 8 if collision detected.

```python
def generate_unique_id(priority: str, ..., existing_ids: set[str]) -> str:
    """Generate unique ID, extending hash if collision detected."""
    for hash_len in range(4, 9):
        candidate = generate_finding_id(..., hash_length=hash_len)
        if candidate not in existing_ids:
            return candidate
    # Fallback: append sequence (extremely rare)
    return f"{candidate}1"
```

---

## Implementation Plan

### Phase 1: Core Hash Module

**New File**: `ucx/utils/finding_hash.py`

```python
"""
Hash-based Finding ID generation.

Provides deterministic, collision-resistant IDs for UCR findings.
Replaces sequential REM-P{0-2}-{NNN} format with P{0-2}-{xxxx}.
"""

import hashlib
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class FindingIdentity:
    """Components that uniquely identify a finding."""
    priority: str           # P0, P1, P2
    target_file: str        # Normalized file path
    target_section: str     # Section reference
    category: str           # Category tag
    description: str        # Finding description

    def to_hash_input(self) -> str:
        """Generate normalized hash input string."""
        return ":".join([
            _normalize_path(self.target_file),
            _normalize_section(self.target_section),
            self.category.lower(),
            _normalize_description(self.description)
        ])


class FindingIDGenerator:
    """
    Stateless finding ID generator using content hashing.

    Benefits:
    - No counter synchronization needed
    - Deterministic: same finding = same ID
    - Natural deduplication
    - Stable across report regeneration
    """

    def __init__(self, hash_length: int = 4):
        self.hash_length = hash_length
        self._generated_ids: set[str] = set()

    def generate(self, identity: FindingIdentity) -> str:
        """Generate unique finding ID."""
        hash_input = identity.to_hash_input()
        hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()

        # Try increasing hash lengths until unique
        for length in range(self.hash_length, 9):
            candidate = f"{identity.priority}-{hash_digest[:length]}"
            if candidate not in self._generated_ids:
                self._generated_ids.add(candidate)
                return candidate

        # Fallback: sequence suffix (extremely rare)
        base = f"{identity.priority}-{hash_digest[:self.hash_length]}"
        seq = 1
        while f"{base}{seq}" in self._generated_ids:
            seq += 1
        final_id = f"{base}{seq}"
        self._generated_ids.add(final_id)
        return final_id

    def reset(self):
        """Reset generated ID cache (call between documents)."""
        self._generated_ids.clear()


def _normalize_path(path: str) -> str:
    """Extract document identifier from path."""
    match = re.search(r'(BRD-\d+(?:\.\d+)?)', path, re.IGNORECASE)
    return match.group(1).lower() if match else path.lower().split('/')[-1]


def _normalize_section(section: str) -> str:
    """Normalize section reference."""
    section = section.lower().strip()
    section = re.sub(r'^section\s+', '', section)
    return section


def _normalize_description(desc: str, max_len: int = 100) -> str:
    """Normalize description for consistent hashing."""
    desc = desc.lower()
    desc = re.sub(r'[^a-z0-9\s]', '', desc)
    desc = ' '.join(desc.split())
    return desc[:max_len]
```

**Tasks**:
| Task | Description |
|------|-------------|
| 1.1 | Create `ucx/utils/finding_hash.py` with FindingIDGenerator class |
| 1.2 | Add normalization functions for path, section, description |
| 1.3 | Export from `ucx/utils/__init__.py` |

### Phase 2: Integration with Scoring

**File**: `ucx/scoring/conflicts.py`

```python
# Add import
from ucx.utils.finding_hash import FindingIDGenerator, FindingIdentity

class CategoryConflictResolver:
    def __init__(self):
        # ... existing code ...
        self._id_generator = FindingIDGenerator(hash_length=4)

    def resolve_with_id(
        self,
        finding_text: str,
        target_file: str,
        target_section: str,
        persona: str,
        explicit_tag: Optional[str] = None,
    ) -> tuple[ConflictResolution, str]:
        """Resolve category and generate stable finding ID."""
        resolution = self.resolve(
            finding_id="",  # No longer needed
            finding_text=finding_text,
            persona=persona,
            explicit_tag=explicit_tag,
        )

        priority = self._extract_priority(finding_text)

        identity = FindingIdentity(
            priority=priority,
            target_file=target_file,
            target_section=target_section,
            category=resolution.resolved_category.name,
            description=finding_text[:100]
        )

        finding_id = self._id_generator.generate(identity)
        return resolution, finding_id
```

**Tasks**:
| Task | Description |
|------|-------------|
| 2.1 | Add `_id_generator` to CategoryConflictResolver |
| 2.2 | Add `resolve_with_id()` method |
| 2.3 | Update callers to use new method |

### Phase 3: Prompt Template Updates

**File**: `ucx/prompts/templates/ucr_chairperson.md`

```markdown
### Finding ID Format

Use hash-based IDs for all findings in the REMEDIATION FINDINGS MANIFEST:

| Priority | Format | Example |
|----------|--------|---------|
| Critical | P0-{hash} | P0-a7f3 |
| High | P1-{hash} | P1-b2c1 |
| Medium | P2-{hash} | P2-8d4e |

NOTE: Hash IDs are auto-generated. Use placeholder `P{N}-AUTO` in tables.
The system will replace with actual hash IDs during report assembly.
```

**Tasks**:
| Task | Description |
|------|-------------|
| 3.1 | Update `ucr_chairperson.md` with new ID format |
| 3.2 | Update all persona prompts to use `P{N}-AUTO` placeholder |
| 3.3 | Add ID replacement logic in report assembly |

### Phase 4: Context Engine Updates

**File**: `ucx/core/context_engine.py`

```python
# Update regex pattern to support both formats (transition period)
self._finding_pattern = re.compile(
    r'((?:REM-)?P[012]-(?:[a-f0-9]{4,8}|\d{3}))',
    re.IGNORECASE
)

# After transition, simplify to:
self._finding_pattern = re.compile(
    r'(P[012]-[a-f0-9]{4,8})',
    re.IGNORECASE
)
```

**Tasks**:
| Task | Description |
|------|-------------|
| 4.1 | Update `_finding_pattern` regex for dual format support |
| 4.2 | Add `is_legacy_id()` and `is_hash_id()` utilities |
| 4.3 | Update `_extract_finding_title()` for new format |

### Phase 5: Testing

**New File**: `tests/unit/test_finding_hash.py`

```python
import pytest
from ucx.utils.finding_hash import (
    FindingIDGenerator,
    FindingIdentity,
    _normalize_path,
    _normalize_section,
    _normalize_description,
)


class TestFindingIDGenerator:

    def test_deterministic_generation(self):
        """Same input produces same ID."""
        gen = FindingIDGenerator()
        identity = FindingIdentity(
            priority="P1",
            target_file="BRD-02.6_functional_requirements.md",
            target_section="Section 6.1",
            category="compliance",
            description="SAR filing workflow missing"
        )

        id1 = gen.generate(identity)
        gen.reset()
        id2 = gen.generate(identity)

        assert id1 == id2

    def test_different_content_different_id(self):
        """Different content produces different ID."""
        gen = FindingIDGenerator()

        id1 = gen.generate(FindingIdentity("P1", "f1", "s1", "c1", "desc1"))
        id2 = gen.generate(FindingIdentity("P1", "f1", "s1", "c1", "desc2"))

        assert id1 != id2

    def test_collision_extension(self):
        """Hash extends on collision."""
        gen = FindingIDGenerator(hash_length=1)  # Force collisions

        ids = set()
        for i in range(50):
            fid = gen.generate(FindingIdentity("P1", "f", "s", "c", f"d{i}"))
            assert fid not in ids, f"Collision: {fid}"
            ids.add(fid)

    def test_priority_preserved(self):
        """Priority level preserved in ID."""
        gen = FindingIDGenerator()

        for priority in ["P0", "P1", "P2"]:
            fid = gen.generate(FindingIdentity(priority, "f", "s", "c", "d"))
            assert fid.startswith(priority)
            gen.reset()

    def test_id_format_regex(self):
        """ID matches expected format."""
        import re
        gen = FindingIDGenerator()
        fid = gen.generate(FindingIdentity("P1", "f", "s", "c", "d"))

        assert re.match(r'P[012]-[a-f0-9]{4,8}', fid)


class TestNormalization:

    def test_normalize_path(self):
        assert _normalize_path("BRD-02.6_functional_requirements.md") == "brd-02.6"
        assert _normalize_path("docs/01_BRD/BRD-50.5.md") == "brd-50.5"

    def test_normalize_section(self):
        assert _normalize_section("Section 6.1") == "6.1"
        assert _normalize_section("SECTION 6.1 BRD.02.01.01") == "6.1 brd.02.01.01"

    def test_normalize_description(self):
        desc = "SAR Filing: Missing CO review!!!"
        assert _normalize_description(desc) == "sar filing missing co review"
```

**Tasks**:
| Task | Description |
|------|-------------|
| 5.1 | Create `tests/unit/test_finding_hash.py` |
| 5.2 | Create `tests/integration/test_finding_hash_e2e.py` |
| 5.3 | Update existing scoring tests for new ID format |

### Phase 6: Documentation

**Tasks**:
| Task | Description |
|------|-------------|
| 6.1 | Update `CHANGELOG_v1.19.0.md` with feature description |
| 6.2 | Update `SCORING_GUIDE.md` with new ID format |
| 6.3 | Add migration notes for existing reports |

---

## File Changes Summary

| File | Change | Description |
|------|--------|-------------|
| `ucx/utils/finding_hash.py` | **NEW** | Hash-based ID generator module |
| `ucx/utils/__init__.py` | MODIFY | Export FindingIDGenerator |
| `ucx/scoring/conflicts.py` | MODIFY | Integrate ID generator |
| `ucx/core/context_engine.py` | MODIFY | Update regex patterns |
| `ucx/prompts/templates/ucr_*.md` | MODIFY | Update ID format in templates |
| `tests/unit/test_finding_hash.py` | **NEW** | Unit tests |
| `tests/integration/test_finding_hash_e2e.py` | **NEW** | Integration tests |
| `docs/CHANGELOG_v1.19.0.md` | MODIFY | Release notes |

---

## Migration Strategy

### Version Roadmap

| Version | Phase | Changes |
|---------|-------|---------|
| **v1.19.0** | Dual-Format | Generate hash IDs, accept both formats |
| **v1.20.0** | Hash-Primary | Default to hash, deprecate sequential |
| **v2.0.0** | Sequential Removal | Remove legacy sequential support |

### Backward Compatibility

```python
def is_legacy_id(finding_id: str) -> bool:
    """Check if ID uses legacy sequential format."""
    return bool(re.match(r'REM-P[012]-\d{3}', finding_id))

def is_hash_id(finding_id: str) -> bool:
    """Check if ID uses new hash format."""
    return bool(re.match(r'P[012]-[a-f0-9]{4,8}', finding_id))

def normalize_finding_id(finding_id: str) -> str:
    """Normalize ID to hash format if legacy."""
    if is_legacy_id(finding_id):
        # Extract priority, return placeholder (actual hash needs content)
        priority = re.search(r'P[012]', finding_id).group(0)
        return f"{priority}-LEGACY"
    return finding_id
```

---

## Configuration

```yaml
# ucx.yaml - New configuration options

finding_id:
  format: "hash"              # "hash" (v1.19+) or "sequential" (legacy)
  hash_length: 4              # Minimum hash length (4-8)
  include_rem_prefix: false   # Include "REM-" prefix (compatibility mode)
```

---

## Benefits Summary

| Metric | Sequential (Current) | Hash (Proposed) |
|--------|---------------------|-----------------|
| State management | Counter per priority | None (stateless) |
| Synchronization | Required (11 personas) | Not needed |
| Duplicate prevention | Manual tracking | Automatic |
| Code complexity | ~50 lines state mgmt | ~20 lines |
| ID stability | Changes each run | Deterministic |
| Cross-version tracking | Not possible | Automatic |
| Deduplication | Requires re-sequencing | Natural (same hash) |

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hash collision | Very Low | Low | Auto-extend hash length |
| Breaking existing tooling | Medium | Medium | Dual-format transition |
| LLM prompt confusion | Low | Low | Clear prompt instructions |
| User adjustment period | Low | Low | Documentation, examples |

---

## Acceptance Criteria

- [ ] Hash-based IDs generated for all new findings
- [ ] Same finding produces same ID across runs (>95% stability)
- [ ] No duplicate IDs in any report
- [ ] Both ID formats accepted during transition
- [ ] All existing tests pass
- [ ] New tests achieve >95% coverage on hash module
- [ ] Performance: ID generation <1ms per finding
- [ ] Documentation updated

---

## References

- PLAN-002: Category-Weighted Scoring System (category integration)
- PLAN-006: Fixer to LLM Handoff (finding extraction)
- `ucx/utils/hash.py`: Existing hash utilities for drift detection
- `ucx/scoring/conflicts.py`: Category conflict resolution

---

*Created: 2026-03-18*
*Author: Claude Opus 4.5*
*UCX Version: 1.18.0*
