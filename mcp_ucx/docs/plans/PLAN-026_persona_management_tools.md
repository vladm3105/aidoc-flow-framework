# Plan: UCX Persona Management Tools (PLAN-026)

**Status**: Implemented
**Date**: 2026-04-05
**Changelog**: CHANGELOG_v1.16.0.md

## Context

After `sdd_init` scaffolds a project's UCX directory, there were no MCP tools to inspect or modify the project-specific persona-to-layer mappings. Projects that need different persona configurations must manually edit `persona_mappings.yaml` with no validation guardrails.

## Delivered

### New Tools (3 MCP tools + 3 CLI commands)

| MCP Tool | CLI Command | Purpose |
|----------|-------------|---------|
| `sdd_personas_show` | `personas-show` | Display persona assignments per phase/doctype |
| `sdd_personas_set` | `personas-set` | Update persona list for a phase+doctype with validation |
| `sdd_personas_diff` | `personas-diff` | Compare project mappings against framework defaults |

### Scaffold Update Mode

| Flag | Behavior |
|------|----------|
| `--update` | Sync stale templates/prompts. Protects `persona_mappings.yaml` |
| `--update --update-mappings` | Also reset `persona_mappings.yaml` to framework defaults |

`PROTECTED_PROJECT_FILES` mechanism in `scaffold.py` prevents accidental overwrite of project-owned configs.

### Preflight Persona Health Check

`sdd_preflight` checks persona mapping integrity: verifies all referenced persona `.md` files exist, reports missing doctypes vs framework defaults.

### BRD Template Refinement

- `executive_summary` demoted to optional (derived section, generated on demand)
- BRD-XS-004 entity consistency rule rewritten to use `stakeholders`/`business_objectives` instead of `executive_summary`
- `executive_summary` removed from BRD required keys in remediation runner

### Post-Review Fixes

- `show_persona_mappings`: shallow copy → `copy.deepcopy()` to prevent cache corruption
- `diff_persona_mappings`: added `mode` field comparison (not just `personas` list)

## Files

| File | Action |
|------|--------|
| `mcp_ucx/src/mcp_server/skills/persona_manager.py` | **Created** |
| `mcp_ucx/src/mcp_server/skills/scaffold.py` | `--update` / `--update-mappings` modes |
| `mcp_ucx/src/mcp_server/tool_registry.py` | 3 Tool defs + dispatch (22 tools total) |
| `mcp_ucx/src/mcp_server/preflight/runner.py` | Health check integration |
| `mcp_ucx/src/mcp_server/cli/main.py` | 3 subcommands + init flags |
| `mcp_ucx/src/mcp_server/validation/brd_rules.py` | BRD-XS-004 rewritten |
| `mcp_ucx/src/mcp_server/remediation/runner.py` | Remove executive_summary from required keys |
| `ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml` | executive_summary: required: false |
| `mcp_ucx/tests/unit/test_persona_manager.py` | **Created** — 15 tests |
| `mcp_ucx/tests/unit/test_scaffold_init.py` | +3 tests |
| `mcp_ucx/tests/unit/test_brd_rules.py` | Updated entity tests |
| `mcp_ucx/tests/unit/test_preflight_runner.py` | +1 test |
| `mcp_ucx/tests/unit/test_server.py` | Tool count 19→22 |

## Test Coverage

295 tests pass.
