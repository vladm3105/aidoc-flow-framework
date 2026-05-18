# CHANGELOG — UCX v1.19.0

**Release Date**: 2026-04-06
**Plan**: PLAN-028 (Review YAML document support)

## Summary

Extend review pipeline document collection to support YAML source artifacts (`.yaml`, `.yml`) alongside existing `.md` files. Fixes broken `--document` mode for YAML-only BRD folders after the markdown-to-YAML migration.

## Fixed

### Review Pipeline YAML Document Collection (Critical)

The `--document` folder mode for `review-build` and `review` commands now detects `.yaml` and `.yml` source artifacts. Previously, `_list_review_markdown_candidates()` only globbed `*.md`, causing YAML-only folders to return empty sections or silently skip the review executor.

| Finding | Severity | Resolution |
|---------|----------|------------|
| `_list_review_markdown_candidates` only globs `*.md` | Critical | Add `*.yaml` + `*.yml` to glob, merge and sort |
| `_find_canonical_source` regex excludes YAML | Critical | Extend to `\.(md\|yaml\|yml)$` |
| `_LEGACY.md` files match canonical pattern causing multi-match | High | Exclude `_LEGACY` from candidate list |
| BRD-01 dual `.md`/`.yaml` canonical sources cause multi-match | High | YAML-first precedence when both exist |
| Appendix regex `\.18[_.]` misses `.19_appendices.md` | Medium | Rely on `appendix`/`appendices` name match only |
| Suffix checks `.md` only on fallback paths | Medium | Extend to `{".md", ".yaml", ".yml"}` |

### Function Renames

| Old Name | New Name |
|----------|----------|
| `_list_review_markdown_candidates` | `_list_review_document_candidates` |
| `_collect_review_markdown_files` | `_collect_review_document_files` |

`_build_review_sections_from_document` and `_find_canonical_source` retain their names. No external API changes — `tool_registry.py` imports `_build_review_sections_from_document` unchanged.

## Design Decisions

- **YAML-first precedence**: When both `.yaml` and `.md` canonical sources exist in the same folder, YAML wins. Matches the migration direction (MD to YAML) and the template standard.
- **`_LEGACY` exclusion**: Legacy markdown files are backup artifacts excluded at the candidate list level.
- **Appendix detection by name only**: Removed `.18[_.]` regex fallback. Section numbering varies (`.15`, `.18`, `.19`), but the name `appendix`/`appendices` is consistent.

## Files Changed

| File | Change |
|------|--------|
| `mcp_ucx/src/mcp_server/cli/main.py` | 4 functions fixed: `_list_review_document_candidates`, `_find_canonical_source`, `_collect_review_document_files`, `_build_review_sections_from_document` |
| `mcp_ucx/tests/unit/test_review_document_collection.py` | **New** — 16 tests |

## Backward Compatibility

- MD-only folders continue to work identically (unchanged behavior path).
- `_build_review_sections_from_document` signature unchanged — `tool_registry.py` requires no changes.
- `--sections-json` mode unaffected (bypasses document collection entirely).

## Test Coverage

353 tests pass (16 new). Zero regressions.
