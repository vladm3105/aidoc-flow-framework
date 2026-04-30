# CHANGELOG v0.12.1

**Release Date**: 2026-03-30
**Type**: Patch (Framework Cleanup + sdd_validate_links Tool)

## Summary

Comprehensive framework cleanup: archived deprecated infrastructure, fixed ~130 stale references across 30+ active docs, added `sdd_validate_links` MCP tool (20th tool), and updated CLI executor configs for non-interactive file writes.

## Changes

### New: sdd_validate_links Tool (20th MCP Tool)

- Validates markdown links in documentation files
- Checks relative file links exist and anchor references (#heading) resolve
- Reports broken links with file, line number, target, and reason
- CLI subcommand: `validate-links --target <path>`
- 18 unit tests, all passing
- Replaces standalone `scripts/validate_doc_links.py`
- Tool count: 19 → 20 (12 deterministic, 2 orchestration, 6 LLM-dependent)

### Fixed: CLI Executor Configs for Non-Interactive File Writes

- **Claude Code**: added `--dangerously-skip-permissions` for pipeline mode
- **Codex CLI**: added `--full-auto` (workspace-write sandbox + auto-approve)
- Both executors verified: file creation and BRD template editing work end-to-end

### Framework Cleanup: Archived Deprecated Infrastructure

| Archive | Content | Replacement |
|---------|---------|-------------|
| `VALIDATION_v1_archive/` | 11 stale validation/schema/splitting docs | Unified YAML templates + mcp_ucx |
| `scripts_v1_archive/` | 37 per-layer validation scripts | mcp_ucx `sdd_validate` |
| `automation_v1_archive/` | AI_EXPERTS + pipelines | mcp_ucx tools |
| Root `scripts/` | 2 standalone scripts | mcp_ucx `sdd_validate_links` |
| Root migration scripts | `update_schema_references.py`, `update_schemas_dual_format.py` | One-time migration completed |

### Framework Cleanup: Stale Reference Fixes (~130 references across 30+ files)

Updated all active framework docs for post-unification compliance:

- Template names: `*-MVP-TEMPLATE.md/.feature` → `*-TEMPLATE.yaml`
- BDD format: `.feature` → `.yaml` (Gherkin in `_example` fields)
- C4/DFD alignment: DFD-L0→L1, ADR=bridge (no C4), SYS=C4-L3
- Document size: sectioned files deprecated → 50,000 tokens monolithic
- Validation: per-layer scripts → mcp_ucx `sdd_validate` / `sdd_validate_links`
- Directory names: `ai_dev_flow/` → `ai_dev_ssd_flow/`

### Rewritten Documents (Project-Agnostic)

| Document | Before | After |
|----------|--------|-------|
| Root `README.md` | 1,819 lines | 175 lines |
| `ai_dev_ssd_flow/README.md` | 1,693 lines | 260 lines |
| `MVP_WORKFLOW_GUIDE.md` | 691 lines | 193 lines |
| `ID_NAMING_STANDARDS.md` | 1,641 lines | 1,175 lines (sectioned content removed) |

### Archived Stale Docs

- `DOCUMENT_SPLITTING_RULES.md`, `DUAL_MVP_TEMPLATES_ARCHITECTURE.md`
- `SCHEMA_TEMPLATE_GUIDE.md`, `FILE_SIZE_LIMITS_FIX_PLAN.md`
- `VALIDATION_COMMANDS.md`, `VALIDATION_STRATEGY_GUIDE.md`, `VALIDATION_GUIDES_INDEX.md`
- `VALIDATION_FRAMEWORK_README.md`, `VALIDATION_TEMPLATE_GUIDE.md`
- `TRACEABILITY_VALIDATION.md`, `MATRIX_TEMPLATE_COMPLETION_GUIDE.md`
- `MVP_AUTOMATION_DESIGN.md`, `SDD_AUTOMATION_WORKFLOW.md`

## Validation

- mcp_ucx: 186 passed (18 new link validation tests), 0 regressions
- All 20 tools dry-run verified: 16 passed, 4 skipped (need LLM executor)
- Claude Code and Codex CLI verified: file creation and BRD editing work end-to-end
