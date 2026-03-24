# Changelog

All notable changes to UCX are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [2.0.0] — 2026-03-23

### Added

**Architecture**
- MCP-first design: FastMCP server is the only user-facing interface (no CLI)
- `ucx-mcp` console script entry point (`ucx/mcp/server.py`)
- `create_server(settings)` factory for test-friendly server construction
- `register_all_tools(mcp, settings)` registry pattern for layer namespaces

**MCP Tool Namespaces** (31 tools registered, stubs with `NotImplementedError`)
- `brd_*` — BRD layer (Layer 1): `brd_validate`, `brd_review`, `brd_remediate`, `brd_status`
- `prd_*` — PRD layer (Layer 2): `prd_validate`, `prd_validate_fix`, `prd_review`, `prd_remediate`, `prd_remediate_apply`, `prd_artifacts`, `prd_status`
- `ears_*` — EARS layer (Layer 3): `ears_validate`, `ears_review`, `ears_remediate`, `ears_status`
- `adr_*` — ADR layer (Layer 5): `adr_validate`, `adr_review`, `adr_remediate`, `adr_status`
- `sys_*` — SYS layer (Layer 6): `sys_validate`, `sys_review`, `sys_remediate`, `sys_status`
- `req_*` — REQ layer (Layer 7): `req_validate`, `req_review`, `req_remediate`, `req_status`
- `ctr_*` — CTR layer (Layer 8): `ctr_validate`, `ctr_review`, `ctr_remediate`, `ctr_status`

**Validators**
- `ucx/validators/result.py`: `ValidationResult`, `Finding`, `Severity` data classes
- `ucx/validators/base.py`: `Validator` structural Protocol
- `ucx/validators/layers/brd.py`: `BRDValidator` stub (PLAN-001)
- `ucx/validators/layers/prd.py`: `PRDValidator` stub (PLAN-002)

**Agents**
- `ucx/agents/stages.py`: `Stage` enum, `TRANSITIONS` map, `can_transition()`
- `ucx/agents/workflow.py`: `WorkflowEngine` — `next_step()`, `assert_can_proceed()`

**Models**
- `ucx/models/document.py`: `DocumentLayer`, `ArtifactClass`, `LayerInfo`, `LAYER_REGISTRY`

**Configuration**
- `ucx/config/settings.py`: `UCXSettings` (pydantic-settings, `UCX_` env prefix)

**Exceptions**
- `ucx/exceptions.py`: `UCXError`, `UCXConfigError`, `UCXValidationError`, `UCXDocumentNotFound`, `UCXStageError`, `UCXAIError`, `UCXToolError`

**Tests**
- `tests/mcp/test_server.py`: server creation + tool registration (4 tests)
- `tests/unit/`: unit tests for all core modules
- `tests/smoke/`: smoke tests — server starts, all tools listed
- `tests/regression/`: regression tests — tool contracts, layer counts, return shapes

**Documentation**
- `README.md`: v2 architecture overview, quickstart, migration table
- `docs/ROADMAP.md`: v2 release timeline and plan index
- `docs/plans/PLAN-001` through `PLAN-005` scope defined

### Changed

- Package version: `1.1.0` → `2.0.0`
- Python minimum: `3.10` → `3.11`
- Dependencies: removed `click`, `rich`, `jinja2`, `opentelemetry-*`; added `fastmcp` as primary

### Removed

- CLI entrypoint (`ucx` command) — replaced by `ucx-mcp` MCP server
- All v1 CLI code (`ucx/cli/`), validator CLI wrappers, script automation
- v1 source archived in `UCX_v1_archive/` (full history preserved via `git mv`)

### Migration

See [README.md — Migration from v1](README.md#migration-from-v1).

v1 CLI → v2 MCP tool mapping:

| v1 CLI | v2 MCP Tool |
| --- | --- |
| `ucx validate brd <path>` | `brd_validate(brd_path=<path>)` |
| `ucx review brd <path>` | `brd_review(brd_path=<path>)` |
| `ucx remediate <path>` | `brd_remediate(brd_path=<path>, review_report_path=<report>)` |
| `ucx validate prd <path>` | `prd_validate(prd_path=<path>)` |
| `ucx validate-fix prd <path>` | `prd_validate_fix(prd_path=<path>)` |
| `ucx review prd <path>` | `prd_review(validation_prd_path=<path>)` |
| `ucx remediate prd <path>` | `prd_remediate(validation_prd_path=<path>, review_report_path=<report>)` |

---

## v1.x History

v1.x changes are preserved in [UCX_v1_archive/](../UCX_v1_archive/).
The v1 changelog spans versions 1.1.0 through 1.21.7 and covers:
- PLAN-001: Unified BRD validation
- PLAN-002: Category-weighted scoring
- PLAN-003: Persona prompt restructuring
- PLAN-004: Advanced context engineering
- PLAN-005: Prompt engineering toolset
- PLAN-006: Fixer to LLM handoff
- PLAN-007: Layer notice handoff
- PLAN-008: Hash-based finding IDs
- PLAN-009: PRD creation
- PLAN-010: PRD validation
- PLAN-011: UCX reporting standards
- PLAN-012: PRD derived-artifact flow (immutable-source model)
- PLAN-013: PRD fix plan generalization
- PLAN-014: PRD-layer MCP tool namespace prototype
- PLAN-015: UCX version strategy
- PLAN-016: UCX v2 MCP-first architecture decision

[Unreleased]: https://github.com/ucx/ucx/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/ucx/ucx/releases/tag/v2.0.0
