# Plan: Review YAML Document Support (PLAN-028)

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

| Field | Value |
| --- | --- |
| Status | Implemented |
| Release | UCX v1.19.0 |
| Date | 2026-04-06 |

## Context

The review pipeline (`sdd_review`, CLI `review-build`) uses `--document` mode to auto-load source files from a BRD folder. After migrating 57 BRDs from sectioned markdown to YAML format (PLAN-027 Phase 1/2), the review pipeline is broken for YAML-only folders because `_collect_review_markdown_files` only scans `*.md` files.

The canonical BRD format per `BRD-TEMPLATE.yaml` is:

```text
BRD-NN_{slug}/
  BRD-NN_{slug}.yaml        ← primary source (required)
  BRD-NN.18_appendices.md   ← companion appendices (optional)
```

## Bug Description

`_list_review_markdown_candidates()` calls `document_dir.glob("*.md")` — YAML source documents never enter the pipeline. For YAML-only folders, the review returns an empty sections error or silently skips the executor.

## Affected Functions

All in `mcp_ucx/src/mcp_server/cli/main.py`:

| Function | Line | Role |
| --- | --- | --- |
| `_list_review_markdown_candidates` | 304 | Collects candidate files from folder |
| `_find_canonical_source` | 316 | Identifies the primary source artifact |
| `_collect_review_markdown_files` | 327 | Orchestrates file selection + appendix detection |
| `_build_review_sections_from_document` | 353 | Reads files into SourceSection objects |

Called from:

- `cli/main.py` line 556 — CLI `review-build` / `review` handler
- `tool_registry.py` line 983 — MCP `sdd_review` dispatch

## Deep Review Findings

| # | Finding | Severity | Resolution |
| --- | --- | --- | --- |
| 1 | `_list_review_markdown_candidates` only globs `*.md` — YAML invisible | **Critical** | Add `*.yaml` + `*.yml` to glob, merge and sort |
| 2 | `_find_canonical_source` regex `^[A-Z]+-\d+_.+\.md$` excludes YAML | **Critical** | Extend to `\.(md\|yaml\|yml)$` |
| 3 | 16 `_LEGACY.md` files match canonical pattern — causes multi-match → `None` return | **High** | Exclude `_LEGACY` from candidate list |
| 4 | BRD-01 has both `.md` and `.yaml` canonical sources — multi-match → `None` return | **High** | YAML-first precedence: when both exist, prefer `.yaml` |
| 5 | Appendix regex `\.18[_.]` misses `.19_appendices.md` (BRD-14 through BRD-17) | Medium | Remove `.18[_.]` fallback, rely on `appendix\|appendices` name match only |
| 6 | `_collect_review_markdown_files` suffix checks `.md` only on fallback paths (lines 330, 337) | Medium | Extend to `{".md", ".yaml", ".yml"}` |
| 7 | `BRD-58_development_plan.md` is a non-standard companion — matches canonical pattern | Low | YAML-first precedence handles this (YAML canonical found first, MD companion ignored) |
| 8 | `_build_review_sections_from_document` reads any file — no changes needed | None | Confirmed safe — reads from path list regardless of extension |
| 9 | `tool_registry.py` imports `_build_review_sections_from_document` — no direct scanning | None | No changes needed in tool_registry.py |

## Implementation Steps

### Step 1: Fix `_list_review_markdown_candidates`

```python
def _list_review_document_candidates(document_dir: Path) -> list[Path]:
    candidates = sorted(
        list(document_dir.glob("*.md"))
        + list(document_dir.glob("*.yaml"))
        + list(document_dir.glob("*.yml"))
    )
    return [
        path
        for path in candidates
        if "REVIEW" not in path.name.upper()
        and "REPORT" not in path.name.upper()
        and "_validated" not in path.stem
        and "_remediate_copy" not in path.stem
        and "_LEGACY" not in path.stem
    ]
```

Function renamed from `_list_review_markdown_candidates` to `_list_review_document_candidates`. All 3 internal callers updated.

### Step 2: Fix `_find_canonical_source`

```python
_CANONICAL_SOURCE_RE = re.compile(r"^[A-Z]+-\d+_.+\.(md|yaml|yml)$")

def _find_canonical_source(document_dir: Path) -> Path | None:
    source_artifacts = [
        path
        for path in _list_review_document_candidates(document_dir)
        if _CANONICAL_SOURCE_RE.match(path.name)
        and not re.search(r"(appendix|appendices)", path.name, re.IGNORECASE)
    ]
    if len(source_artifacts) == 1:
        return source_artifacts[0]
    # YAML-first precedence: when multiple canonical sources exist, prefer YAML
    if len(source_artifacts) > 1:
        yaml_sources = [p for p in source_artifacts if p.suffix.lower() in {".yaml", ".yml"}]
        if len(yaml_sources) == 1:
            return yaml_sources[0]
    return None
```

Changes:

- Regex extended to match `.md`, `.yaml`, `.yml`
- Appendix files excluded from canonical detection (prevents `.18_appendices.md` matching)
- YAML-first precedence: when both `.md` and `.yaml` canonical sources exist, prefer YAML
- Multiple YAML sources → returns `None` (ambiguous, same as before)

### Step 3: Fix `_collect_review_markdown_files`

```python
_REVIEW_SOURCE_EXTENSIONS = {".md", ".yaml", ".yml"}

def _collect_review_document_files(document_path: Path) -> list[Path]:
    document_dir = document_path if document_path.is_dir() else document_path.parent
    candidates = _list_review_document_candidates(document_dir)
    if not candidates and document_path.is_file() and document_path.suffix.lower() in _REVIEW_SOURCE_EXTENSIONS:
        return [document_path]

    selected: list[Path] = []
    canonical_source = _find_canonical_source(document_dir)
    if canonical_source is not None:
        selected.append(canonical_source)
    elif document_path.is_file() and document_path.suffix.lower() in _REVIEW_SOURCE_EXTENSIONS:
        selected.append(document_path)

    appendix_files = [
        path
        for path in candidates
        if path not in selected
        and re.search(r"(appendix|appendices)", path.name, re.IGNORECASE)
    ]
    selected.extend(appendix_files)

    if selected:
        return selected
    return candidates
```

Changes:

- Renamed from `_collect_review_markdown_files` to `_collect_review_document_files`
- Suffix checks extended to `_REVIEW_SOURCE_EXTENSIONS`
- Appendix regex simplified: removed `\.18[_.]` fallback, uses name-based detection only

### Step 4: Update `_build_review_sections_from_document`

```python
def _build_review_sections_from_document(document_path: Path) -> tuple[list[SourceSection], list[Path]]:
    files = _collect_review_document_files(document_path)
    sections = [
        SourceSection(
            section_id=path.stem,
            title=f"Source: {path.name}",
            content=path.read_text(encoding="utf-8"),
            included=True,
        )
        for path in files
    ]
    return sections, files
```

Only change: calls `_collect_review_document_files` instead of `_collect_review_markdown_files`.

### Step 5: Update internal callers

Both callers reference `_build_review_sections_from_document` — no signature change, just the internal call chain is fixed.

Verify no external imports of the renamed private functions:

- `_list_review_markdown_candidates` — private, only called internally
- `_collect_review_markdown_files` — private, only called internally
- `_build_review_sections_from_document` — imported by `tool_registry.py` line 983

`_build_review_sections_from_document` keeps its name — no change needed in `tool_registry.py`.

### Step 6: Tests

**`tests/unit/test_review_document_collection.py`** (new, ~8 tests):

- YAML-only folder returns YAML as canonical + appendices MD
- YAML + `_LEGACY.md` folder returns YAML only (ignores LEGACY) + appendices
- YAML + MD coexistence (BRD-01 pattern) returns YAML as canonical (YAML-first precedence)
- MD-only folder returns MD as canonical + appendices (unchanged behavior)
- `.19_appendices.md` detected as appendix (Gap 5 fix verification)
- Folder with no source files returns empty list
- Direct file path to `.yaml` file returns that file
- Direct file path to `.md` file returns that file (backward compat)

**`tests/unit/test_server.py`**: No changes (tool count unchanged).

### Step 7: Verification

```bash
# YAML-only folder (BRD-05)
PYTHONPATH=mcp_ucx/src python -c "
from mcp_server.cli.main import _build_review_sections_from_document
from pathlib import Path
sections, files = _build_review_sections_from_document(
    Path('/opt/data/b-local/b-local-docs/docs/01_BRD/BRD-05_multi_agent_ai_system')
)
for s in sections:
    print(f'{s.section_id}: {len(s.content)} chars')
"

# YAML + LEGACY.md folder (BRD-50)
PYTHONPATH=mcp_ucx/src python -c "
from mcp_server.cli.main import _build_review_sections_from_document
from pathlib import Path
sections, files = _build_review_sections_from_document(
    Path('/opt/data/b-local/b-local-docs/docs/01_BRD/BRD-50_octo_agent_orchestration')
)
for s in sections:
    print(f'{s.section_id}: {len(s.content)} chars')
"

# YAML + MD coexistence (BRD-01)
PYTHONPATH=mcp_ucx/src python -c "
from mcp_server.cli.main import _build_review_sections_from_document
from pathlib import Path
sections, files = _build_review_sections_from_document(
    Path('/opt/data/b-local/b-local-docs/docs/01_BRD/BRD-01_platform_architecture')
)
for s in sections:
    print(f'{s.section_id}: {len(s.content)} chars')
"

# Full test suite
PYTHONPATH=mcp_ucx/src python -m pytest mcp_ucx/tests/ -x -q
```

## Critical Files

| File | Action |
| --- | --- |
| `mcp_ucx/src/mcp_server/cli/main.py` | Edit — 4 functions fixed |
| `mcp_ucx/tests/unit/test_review_document_collection.py` | **Create** — ~8 tests |

## Design Decisions

- **YAML-first precedence**: When both `.yaml` and `.md` canonical sources exist in the same folder, YAML wins. This matches the migration direction (MD → YAML) and the template standard.
- **`_LEGACY` exclusion**: Legacy markdown files are backup artifacts, not review sources. Excluded at the candidate list level so they never participate in canonical detection.
- **Appendix detection by name only**: Removed `.18[_.]` regex fallback. Section numbering varies (`.15`, `.18`, `.19`), but the name `appendix`/`appendices` is consistent. Simpler and handles all variants.
- **Function rename**: `_list_review_markdown_candidates` → `_list_review_document_candidates` and `_collect_review_markdown_files` → `_collect_review_document_files` to reflect YAML support. `_build_review_sections_from_document` keeps its name (public API used by `tool_registry.py`).
- **No changes to tool_registry.py**: The MCP dispatch path imports `_build_review_sections_from_document` which internally calls the fixed functions. No interface change.
