# UCX v1.9.8 Changelog - Tier 2 Diagram Advisory Auto-Fix

**Release Date**: 2026-03-11
**Focus**: Diagram advisory fixes with honest traceability pattern

---

## Summary

This release extends the `--fix` flag to handle Tier 2 diagram advisory warnings (BRD-W011 through BRD-W014). Instead of adding false `@diagram:` tags that claim diagrams exist when they don't, the fixer adds `@diagram-request` notices that signal downstream layers (ADR/PRD) to create the actual diagrams.

### Key Design Principle

**Honest Traceability**: BRD layer signals the *need* for diagrams; ADR layer *creates* them.

---

## New Features

### 1. BRD-W011 Auto-Fix (C4-L1 Architecture Diagram)

Adds a `@diagram-request` notice instead of a false `@diagram: c4-l1` tag:

```markdown
<!-- DIAGRAM REQUEST -->
<!-- @diagram-request: c4-l1 -->
<!-- target_layer: ADR -->
<!-- priority: recommended -->
<!-- rationale: BRD architecture requires C4 Level 1 context diagram for visualization -->
<!-- status: pending -->
```

### 2. BRD-W012 Auto-Fix (DFD-L0 Data Flow Diagram)

Adds a `@diagram-request` notice for DFD Level 0:

```markdown
<!-- DIAGRAM REQUEST -->
<!-- @diagram-request: dfd-l0 -->
<!-- target_layer: ADR -->
<!-- priority: recommended -->
<!-- rationale: BRD data flows require DFD Level 0 diagram for visualization -->
<!-- status: pending -->
```

### 3. BRD-W013 Auto-Fix (Sequence Diagram Classification)

Auto-detects sequence diagram type and adds classification tag:

| Content Pattern | Detected Type | Tag Added |
|-----------------|---------------|-----------|
| error, fail, rollback, timeout | `error` | `@diagram: sequence-error` |
| async, event, webhook, callback | `async` | `@diagram: sequence-async` |
| Default | `sync` | `@diagram: sequence-sync` |

### 4. BRD-W014 Auto-Fix (Diagram Intent Header)

Adds diagram metadata fields:

```markdown
<!-- DIAGRAM INTENT -->
<!-- diagram_type: sequence -->
<!-- level: component -->
<!-- scope_boundary: BRD-01-boundary -->
<!-- upstream_refs: BRD-01 -->
<!-- downstream_refs: PRD, EARS, ADR -->
```

---

## Bug Fixes

### 1. Version Numbering Bug Fix

**Problem**: Report version used `len(existing_files) + 1` which could go backwards if files were deleted.

**Example**: v004 existed, file deleted, next report was v002 instead of v005.

**Fix**: Now extracts actual version numbers from filenames and uses `max(versions) + 1`.

```python
# Before (buggy)
version = len(existing) + 1

# After (correct)
versions = [int(match.group(1)) for f in existing if (match := re.search(r"_v(\d+)\.md$", f.name))]
version = max(versions) + 1 if versions else 1
```

### 2. FIXER_SKILLS Configuration Fix

**Problem**: `FIXER_SKILLS` referenced `integration_expert` but projects use `integration_lead`.

**Fix**: Changed to `integration_lead` for consistency across UCX framework.

| Before | After |
|--------|-------|
| `integration_expert` | `integration_lead` |

---

## Usage

```bash
# Fix all Tier 2 diagram warnings
ucx validate brd docs/01_BRD/BRD-01/ --fix

# Fix and generate report
ucx validate brd docs/01_BRD/BRD-01/ --fix --report

# Verify fixes applied
ucx validate brd docs/01_BRD/BRD-01/
# Output: Status: PASSED (0 Tier 2 warnings)
```

---

## Fixable Codes Summary (v1.9.8)

| Code | Tier | Issue | Auto-Fix |
|------|------|-------|----------|
| `BRD-E002` | 1 | Missing custom_fields | Adds document_type, artifact_type, layer |
| `BRD-E003` | 1 | Missing 'brd' tag | Adds to tags array |
| `BRD-E004` | 1 | Missing 'layer-1-artifact' tag | Adds to tags array |
| `BRD-E009` | 1 | Missing Document Control | Adds section |
| `BRD-W005` | 1 | Legacy development_status | Renames to status |
| `VAL-W002` | 1 | Legacy status value | Updates to current values |
| `GATE-W003` | 2 | Count mismatch | Updates prose count |
| `DIAG-W001` | 2 | Diagram node count | Updates prose count |
| **`BRD-W011`** | **2** | **Missing C4-L1 diagram** | **Adds @diagram-request for ADR** |
| **`BRD-W012`** | **2** | **Missing DFD-L0 diagram** | **Adds @diagram-request for ADR** |
| **`BRD-W013`** | **2** | **Sequence diagram unclassified** | **Auto-detects and tags type** |
| **`BRD-W014`** | **2** | **Missing diagram intent** | **Adds metadata fields** |

---

## Updated Error Code Descriptions

| Code | Old Description | New Description |
|------|-----------------|-----------------|
| `BRD-W011` | "Missing BRD advisory diagram tag @diagram: c4-l1" | "C4-L1 architecture diagram not present - recommended for architecture visualization" |
| `BRD-W012` | "Missing BRD advisory diagram tag @diagram: dfd-l0" | "DFD-L0 data flow diagram not present - recommended for data flow visualization" |
| `BRD-W013` | "Sequence diagram present without BRD sequence tag" | "Sequence diagram present without classification tag" |

---

## Architecture: @diagram-request Pattern

### Why Not Just Add @diagram Tags?

Adding `@diagram: c4-l1` when no diagram exists creates **false traceability**:
- Downstream validators expect to find a diagram
- No actual visualization exists
- Creates audit trail inconsistencies

### The @diagram-request Pattern

1. **BRD Layer**: Signals diagram need with `@diagram-request`
2. **Validator**: Recognizes request as resolution (no warning)
3. **ADR Layer**: Processes requests, creates actual diagrams
4. **ADR Validator**: Checks for `@diagram:` tags (actual diagrams)

### Validator Recognition

```python
# quality_gate.py now checks both:
has_c4 = "@diagram: c4-l1" in content
has_c4_request = "@diagram-request: c4-l1" in content

# Warning only if NEITHER exists
if not has_c4 and not has_c4_request:
    result.add_issue("BRD-W011", ...)
```

---

## Files Changed

| File | Changes | Description |
|------|---------|-------------|
| `ucx/validators/brd/fixer.py` | +180 lines | Added _fix_brd_w011/w012/w013/w014 methods |
| `ucx/validators/brd/quality_gate.py` | +6 lines | Added @diagram-request recognition |
| `ucx/validators/common/error_codes.py` | Modified | Updated BRD-W011/W012/W013 descriptions |
| `ucx/cli/main.py` | +8 lines | Fixed version numbering logic |
| `ucx/config/layer_skills.py` | Modified | Changed integration_expert to integration_lead |
| `remediation/run_ucrem.sh` | Modified | Changed integration_expert to integration_lead |
| `ucx/version.py` | Modified | Version bump to 1.9.8 |

---

## Downstream Integration

### ADR Autopilot Processing

ADR agents can process `@diagram-request` notices:

```python
def process_diagram_requests(upstream_doc: str) -> list:
    """Process diagram requests from upstream BRD."""
    requests = extract_diagram_requests(upstream_doc)

    for req in requests:
        if req.diagram_type == "c4-l1":
            # Evaluate if C4 diagram needed
            if architecture_complexity_score() > 3:
                create_c4_diagram()
                update_request_status(req, "created")
            else:
                update_request_status(req, "deferred",
                    reason="Architecture complexity below threshold")
```

---

## Related Documents

- [CHANGELOG_v1.9.7.md](./CHANGELOG_v1.9.7.md) - Count mismatch auto-fix
- [CHANGELOG_v1.9.6.md](./CHANGELOG_v1.9.6.md) - Structural auto-fix
- [QUICK_START.md](./QUICK_START.md) - Usage examples
- [HOW_TO_AUDIT.md](./HOW_TO_AUDIT.md) - Audit workflow

---

*Generated for UCX Framework v1.9.8*
