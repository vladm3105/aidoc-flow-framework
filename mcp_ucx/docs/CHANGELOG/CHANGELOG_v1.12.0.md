# CHANGELOG — UCX v1.12.0

**Release Date**: 2026-04-02
**Plan**: PLAN-022 (Multi-Persona Mappings)

## Summary

Multi-persona mapping support via `persona_mappings.yaml`. All creation, review, and remediation tools now load multiple persona files per invocation based on a machine-readable per-doctype, per-phase configuration.

## Added

- `persona_mappings.yaml` — machine-readable per-doctype, per-phase persona sequences (10 creation, 10 review, 1 remediation default)
- `content_strategist.md` persona definition for PRD creation workflows
- `load_persona_mapping()` and `load_multi_persona_files()` loader functions in `project_ucx_loader.py`
- `PersonaMappingError` exception class with descriptive validation messages
- `_resolve_personas()` 2-tier resolution: explicit param → mapping config
- `_filter_adaptive_personas()` for remediation domain filtering (design-ready, wiring in future release)
- `map_sections_for_personas()` union category mapping across all loaded personas
- `_format_persona_block()` multi-persona prompt formatting
- `_compute_token_warning()` token budget tracking with 15,000-token threshold
- `PERSONA_CATEGORY_MAP` expanded from 7 → 15 entries (added: product_owner, business_analyst, strategist, requirements_specialist, ux_strategist, qa_lead, fact_checker, content_strategist)
- Optional `personas` array param on `sdd_remediate` and `sdd_remediate_fix`
- `persona_token_estimate`, `persona_token_warning`, `persona_count` fields on `PromptMetadataSidecar`
- YAML schema validation at load time (structure, required keys, persona name cross-references)

## Changed

- Tool schemas: `persona` (string, required) → `personas` (array, optional) on `sdd_create`, `sdd_create_build`, `sdd_review`, `sdd_run_lifecycle`, `sdd_remediate`, `sdd_remediate_fix`
- CLI: `--persona` (required) → `--personas` (optional, `nargs="+"`) on review-build, review, create-build, create
- `PromptMetadataSidecar`: `persona: str` → `personas: list[str]` + `persona_count: int` + token tracking fields
- `PromptAssembly` / `CreationAssembly`: `persona_text: str` → `persona_texts: list[str]` + `persona_names: list[str]`
- `map_sections_for_persona()` → `map_sections_for_personas()` (union categories)
- `discover_relevant_snippets()`: `persona: str` → `personas: list[str]` (union keywords)
- `build_prompt_bundle()`: `persona: str` → `personas: list[str]`
- Scaffold: supports single-file mappings (not just directory trees)
- 31 prompt templates: removed hardcoded persona lists (now runtime-injected from persona_mappings.yaml)

## Removed

- Single `persona` string parameter on all tools and CLI
- `load_project_persona_file()` from public API (kept as internal helper)
- Hardcoded persona sequences from 11 creation, 10 review, 10 remediation prompt templates

## Backward Compatibility

**Breaking** for direct MCP tool callers using `persona` param — must migrate to `personas` array or omit to use mapping defaults. CLI `--persona` no longer accepted; use `--personas`.

## Architecture Review Fixes

Post-implementation architecture review identified and resolved 8 issues:

### Critical
- **C-1**: Added mtime-based LRU cache to `load_persona_mapping()` — eliminates redundant YAML re-parsing and persona file stat calls on repeated tool invocations
- **C-2**: Removed `personas` parameter from `sdd_remediate` and `sdd_remediate_fix` tool schemas — runners do not consume it; avoids silent contract violation

### Important
- **I-1**: Missing persona files in `_validate_persona_mapping()` now raise `ProjectSkillsNotFound` (was `PersonaMappingError`) — correct error type for missing filesystem artifacts
- **I-3**: Resolution hint updated to mention both `sdd_init` (MCP) and `mcp init --project` (CLI)
- **I-5**: Removed `create` from `sdd_run_lifecycle` stage enum — stage handler did not exist, caused silent skip

### Design
- **D-1**: `TOKEN_WARNING_THRESHOLD` raised from 10,000 to 15,000 tokens — default BRD review (11 personas, ~12,250 tokens) no longer triggers false warnings
- **D-4**: Preflight now checks for `persona_mappings.yaml` existence (warning level: `missing_persona_mappings`)
- **D-5**: `validate_project_ucx_root()` now checks `_REQUIRED_FILES` tuple (includes `persona_mappings.yaml`) for early detection of missing config

## Files Changed

~35 source/test files + 31 prompt templates. See PLAN-022 for complete list.
