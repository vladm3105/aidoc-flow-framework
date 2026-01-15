# Cumulative Tagging Reference - Tag Count by Layer

**Purpose**: Single source of truth for expected tag counts at each layer  
**Last Updated**: 2026-01-11  
**Version**: 1.0  
**Referenced by**: Validators, TRACEABILITY.md, README.md  

---

## Tag Count Formula

Each layer N requires tags from layers 1 through N-1, with adjustments for optional layers (IMPL at Layer 8, CTR at Layer 9).

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
| 8 | IMPL | 7 | 7 | @brd→@req | Optional layer |
| 9 | CTR | 7 | 8 | @brd→@req, +opt @impl | Optional layer |
| 10 | SPEC | 7 | 9 | @brd→@req, +opt @impl/@ctr | |
| 11 | TASKS | 8 | 10 | @brd→@spec, +opt @impl/@ctr | +opt @icon (excluded from count) |
| 12 | Code | 9 | 11 | @brd→@tasks, +opt @impl/@ctr | |
| 13 | Tests | 10 | 12 | @brd→@code, +opt @impl/@ctr | |
| 14 | Validation | 9+ | 14+ | All upstream (advisory) | Count not strictly enforced |

**Note**: IPLAN (formerly Layer 12) has been **deprecated** as of 2026-01-15. Execution commands are now part of TASKS (Section 4).

**CHG Note**: CHG is NOT a layer - it's a change management procedure. CHG artifacts don't require tags.

---

## Tag Counting Rules

1. **Base Count**: Layer number minus 1 (e.g., Layer 7 REQ = 6 base tags)
2. **Optional Layers**: Add 0-2 tags depending on whether IMPL and/or CTR exist in project
3. **ICON Exception**: `@icon` tags are allowed but NOT counted toward cumulative total
4. **Validation Layer**: Consumes all upstream tags; count is advisory (10-15 expected range)

---

## Validation Formula by Layer

### Layers 1-9 (Fixed Count)
```
Expected Tags = Layer Number - 1
```

### Layers 10-14 (Range)
```
Min Tags = Base + Present Optional Layers
Max Tags = Base + Total Optional Layers (2)

Where:
  Base = 7 for L10, 8 for L11, 9 for L12, 10 for L13
  Present Optional Layers = count(IMPL in project, CTR in project)
  Total Optional Layers = 2 (IMPL + CTR)
```

---

## Example Scenarios

### Scenario A: Project WITHOUT IMPL or CTR
```
SPEC (L10):  7 tags  (@brd, @prd, @ears, @bdd, @adr, @sys, @req)
TASKS (L11): 8 tags  (@brd→@spec)
Code (L12):  9 tags  (@brd→@tasks)
Tests (L13): 10 tags (@brd→@code)
```

### Scenario B: Project WITH IMPL, WITHOUT CTR
```
SPEC (L10):  8 tags  (@brd→@req + @impl)
TASKS (L11): 9 tags  (@brd→@spec)
Code (L12):  10 tags (@brd→@tasks)
Tests (L13): 11 tags (@brd→@code)
```

### Scenario C: Project WITH IMPL AND CTR
```
SPEC (L10):  9 tags  (@brd→@req + @impl + @ctr)
TASKS (L11): 10 tags (@brd→@spec)
Code (L12):  11 tags (@brd→@tasks)
Tests (L13): 12 tags (@brd→@code)
```

---

## Validator Implementation

### Python Validation Logic

```python
def get_expected_tag_count(layer: int, has_impl: bool, has_ctr: bool) -> tuple[int, int]:
    """
    Returns (min_count, max_count) for a given layer.
    
    Args:
        layer: Layer number (1-15)
        has_impl: Whether project uses IMPL (Layer 8)
        has_ctr: Whether project uses CTR (Layer 9)
    
    Returns:
        (min_count, max_count) tuple
    """
    # Layers 1-9: Fixed count
    if layer <= 9:
        count = layer - 1
        return (count, count)
    
    # Calculate optional layer count
    optional_layers = 0
    if has_impl:
        optional_layers += 1
    if has_ctr:
        optional_layers += 1
    
    # Layer-specific base counts (IPLAN deprecated - layers shifted)
    layer_bases = {
        10: 7,   # SPEC
        11: 8,   # TASKS
        12: 9,   # Code (was 13, shifted after IPLAN deprecation)
        13: 10,  # Tests (was 14, shifted after IPLAN deprecation)
        14: 9,   # Validation (advisory) (was 15, shifted after IPLAN deprecation)
    }
    
    if layer not in layer_bases:
        return (0, 0)
    
    base = layer_bases[layer]
    
    # Layer 14 (Validation) has advisory range
    if layer == 14:
        return (base, 14)
    
    # Layers 10-13: Range based on optional layers
    min_count = base + optional_layers
    max_count = base + 2  # Maximum 2 optional layers (IMPL + CTR)
    
    return (min_count, max_count)


def validate_tag_count(artifact_tags: list[str], layer: int, has_impl: bool, has_ctr: bool) -> tuple[bool, str]:
    """
    Validates that an artifact has the correct number of cumulative tags.
    
    Returns:
        (is_valid, error_message) tuple
    """
    min_count, max_count = get_expected_tag_count(layer, has_impl, has_ctr)
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

- **2026-01-11**: Initial creation - unified tag counts from README.md, TRACEABILITY_SETUP.md, TRACEABILITY_VALIDATION.md
