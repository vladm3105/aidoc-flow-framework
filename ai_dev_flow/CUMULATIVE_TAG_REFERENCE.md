---
title: "Cumulative Tag Reference"
tags:
  - framework-guide
  - traceability
  - shared-architecture
custom_fields:
  document_type: reference
  priority: shared
  development_status: active
---

# Cumulative Tagging Reference - Tag Count by Layer

**Purpose**: Single source of truth for expected tag counts at each layer  
**Last Updated**: 2026-01-11T00:00:00  
**Version**: 1.0  
**Referenced by**: Validators, TRACEABILITY.md, README.md  

---

## Tag Count Formula

Each layer N requires tags from layers 1 through N-1, with adjustments for optional layer CTR at Layer 8.

---

## Complete Tag Count Table

| Layer | Artifact | Min Tags | Max Tags | Required Tags | Notes |
|-------|----------|----------|----------|---------------|-------|
| 0 | STRAT | 0 | 0 | (none) | External strategy documents |
| 1 | BRD | 0 | 0 | (none) | Top-level entry point |
| 2 | PRD | 1 | 1 | @brd | |
| 3 | EARS | 2 | 2 | @brd, @prd | |
| 4 | BDD | 3 | 3 | @brd, @prd, @ears | |
| 5 | ADR | 4 | 4 | @brd→@bdd | |
| 6 | SYS | 5 | 5 | @brd→@adr | |
| 7 | REQ | 6 | 6 | @brd→@sys | |
| 8 | CTR | 7 | 7 | @brd→@req | Optional layer |
| 9 | SPEC | 7 | 8 | @brd→@req, +opt @ctr | |
| 10 | TSPEC | 8 | 9 | @brd→@spec, +opt @ctr | |
| 11 | TASKS | 9 | 10 | @brd→@tspec, +opt @ctr | |
| 12 | Code | 10 | 11 | @brd→@tasks, +opt @ctr | |
| 13 | Tests | 11 | 12 | @brd→@code, +opt @ctr | |
| 14 | Validation | 12 | 13 | All upstream (advisory) | Count not strictly enforced |

**CHG Note**: CHG is NOT a layer - it's a change management procedure. CHG artifacts don't require tags.

---

## Tag Counting Rules

1. **Base Count**: Layer number minus 1 (e.g., Layer 7 REQ = 6 base tags)
2. **Optional Layers**: Add 0-1 tags depending on whether CTR exists in project
3. **Validation Layer**: Consumes all upstream tags; count is advisory (11-12 expected range)

---

## Validation Formula by Layer

### Layers 1-9 (Fixed Count)
```
Expected Tags = Layer Number - 1
```

### Layers 9-13 (Range)
```
Min Tags = Base + Present Optional Layers
Max Tags = Base + Total Optional Layers (1)

Where:
  Base = 7 for L9, 8 for L10, 9 for L11, 10 for L12, 11 for L13
  Present Optional Layers = count(CTR in project)
  Total Optional Layers = 1 (CTR)
```

---

## Example Scenarios

### Scenario A: Project WITHOUT CTR
```
SPEC (L9):  7 tags  (@brd, @prd, @ears, @bdd, @adr, @sys, @req)
TASKS (L10): 8 tags  (@brd→@spec)
Code (L11):  9 tags  (@brd→@tasks)
Tests (L12): 10 tags (@brd→@code)
Validation (L13): 11 tags (all upstream)
```

### Scenario B: Project WITH CTR
```
SPEC (L9):  8 tags  (@brd→@req + @ctr)
TASKS (L10): 9 tags (@brd→@spec + @ctr)
Code (L11):  10 tags (@brd→@tasks + @ctr)
Tests (L12): 11 tags (@brd→@code + @ctr)
Validation (L13): 12 tags (all upstream)
```

---

## Validator Implementation

### Python Validation Logic

```python
def get_expected_tag_count(layer: int, has_ctr: bool) -> tuple[int, int]:
    """
    Returns (min_count, max_count) for a given layer.
    
    Args:
        layer: Layer number (1-13)
        has_ctr: Whether project uses CTR (Layer 8)
    
    Returns:
        (min_count, max_count) tuple
    """
    # Layers 1-8: Fixed count
    if layer <= 8:
        count = layer - 1
        return (count, count)
    
    # Calculate optional layer count
    optional_layers = 1 if has_ctr else 0
    
    # Layer-specific base counts
    layer_bases = {
        9: 7,   # SPEC
        10: 8,  # TASKS
        11: 9,  # Code
        12: 10, # Tests
        13: 11, # Validation (advisory)
    }
    
    if layer not in layer_bases:
        return (0, 0)
    
    base = layer_bases[layer]
    
    # Layer 14: Validation) has advisory range
    if layer == 13:
        return (base, 12)
    
    # Layers 9-12: Range based on optional layers
    min_count = base + optional_layers
    max_count = base + 1
    
    return (min_count, max_count)


def validate_tag_count(artifact_tags: list[str], layer: int, has_ctr: bool) -> tuple[bool, str]:
    """
    Validates that an artifact has the correct number of cumulative tags.
    
    Returns:
        (is_valid, error_message) tuple
    """
    min_count, max_count = get_expected_tag_count(layer, has_ctr)
    actual_count = len(artifact_tags)
    
    if actual_count < min_count or actual_count > max_count:
        if min_count == max_count:
            return (False, f"Expected {min_count} tags, found {actual_count}")
        else:
            return (False, f"Expected {min_count}-{max_count} tags, found {actual_count}")
    
    return (True, "")
```

---

## Cross-Reference

**Update the following files to reference this document**:
- README.md (line ~755): Replace tag count section with link to this file
- TRACEABILITY_SETUP.md (line ~120): Replace inline counts with reference
- TRACEABILITY_VALIDATION.md: Update all tag count references

**Example Reference**:
```markdown
See [CUMULATIVE_TAG_REFERENCE.md](./CUMULATIVE_TAG_REFERENCE.md) for complete tag count formulas by layer.
```

---

## Update History

- **2026-01-11T00:00:00**: Initial creation - unified tag counts from README.md, TRACEABILITY_SETUP.md, TRACEABILITY_VALIDATION.md
