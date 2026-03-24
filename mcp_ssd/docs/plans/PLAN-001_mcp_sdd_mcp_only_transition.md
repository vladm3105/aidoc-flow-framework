# PLAN-001: MCP_SDD MCP-Only Transition

| Field | Value |
| --- | --- |
| Plan ID | PLAN-001 |
| Title | MCP_SDD MCP-Only Transition |
| Status | In Progress |
| Author | AI Collaboration |
| Date | 2026-03-23 |
| Target | MCP_SDD v1.0.0 |
| Supersedes | UCX v2 naming and architecture draft |

---

## 1. Objective

Create MCP_SDD as an MCP-only SDD validation and remediation server.
Deprecate UCX naming and internal agent-layer indirection.
Keep validator logic reusable and tool outputs stable.

---

## 2. Scope

### In Scope

- Create new MCP_SDD project folder and baseline documentation.
- Define MCP-only architecture where MCP tools are the execution boundary.
- Define naming migration from UCX to MCP_SDD.
- Define compatibility window for legacy UCX import and command aliases.
- Define validation and regression coverage for migration.
- Execute the PLAN-012 PRD six-stage flow as the first implementation slice.

### Out of Scope

- Full production deployment automation.
- Cross-repository integration changes outside this repository.
- New layer-specific rule logic beyond current functional parity.

---

## 3. Architecture Baseline

### 3.1 Runtime Model

Single MCP server process exposes SDD tools directly.
No internal orchestrator-to-layer-agent relay layer.

### 3.2 Execution Boundary

- MCP tools in mcp/tools handle request workflow.
- Validators in validators/layers implement pure validation logic.
- Tool responses remain structured dict payloads.
- Baseline migration from UCX v1 is staged directly under the mcp_ssd root for controlled extraction.

### 3.3 Tool Contract

Required response keys:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| status | string | Yes | Allowed: ok, warning, error |
| path | string | Yes | Absolute or workspace-relative artifact path |
| findings | list[dict] | Yes | Empty list allowed |
| next_step | string | No | Recommended next tool/action |
| data | dict | No | Tool-specific structured payload |

Error envelope rule:
- status=error must include at least one finding with machine-parseable code.

---

## 4. Naming and Compatibility

### 4.1 Primary Names

- Product name: MCP_SDD
- Python package namespace: mcp_sdd
- Server entrypoint: mcp-sdd

### 4.2 Deprecation Policy

- UCX naming marked deprecated.
- Legacy aliases remain temporarily available with runtime warning.
- Removal gates:
	- v1.0.0: aliases enabled by default with warning.
	- v1.1.0: aliases remain, warning severity increased, migration report mandatory.
	- v2.0.0: aliases removed only after all migration acceptance checks pass.

---

## 5. Workstreams

### WS-1 Structure and Metadata

- Create mcp_ssd folder structure.
- Add docs and plan index baseline.
- Align metadata and references.
- Exit criteria: docs/plans path exists and PLAN-001 is tracked.

### WS-2 Package and Entrypoint Rename

- Rename module references from ucx to mcp_sdd.
- Add temporary compatibility imports and command aliases.
- Add deprecation warnings on alias paths.
- Dependency: WS-1 complete.
- Exit criteria: mcp_sdd import path works and alias warning tests pass.

### WS-3 MCP Tool Surface Stabilization

- Preserve the PLAN-012 PRD six-stage tool flow first: create, validate, validate-fix, review, remediate, remediate-apply.
- Keep stable response schema across all tools.
- Add only the PRD support tools required for artifact discovery and workflow state.
- Dependency: WS-2 partial (namespace mapping available).
- Exit criteria: contract regression suite passes for all migrated tools.

### WS-4 Test Migration

- Update unit, smoke, and regression tests to mcp_sdd namespace.
- Add compatibility tests for UCX alias paths.
- Ensure parity of findings and status semantics.
- Dependency: WS-2 and WS-3.
- Exit criteria: CI test matrix passes without namespace errors.

### WS-5 Documentation Migration

- Update architecture docs to MCP_SDD terminology.
- Add migration guide from UCX naming.
- Update quickstart and usage examples.
- Dependency: WS-2 naming finalized.
- Exit criteria: no unresolved UCX references outside deprecation sections.

---

## 6. Risks and Controls

| Risk | Impact | Control |
| --- | --- | --- |
| Name migration breaks imports | High | Keep compatibility aliases with tests |
| Tool output drift during refactor | High | Regression tests on output schema |
| Hidden UCX references remain | Medium | Repo-wide search gate before release |
| User confusion during transition | Medium | Deprecation warnings + migration guide |

---

## 7. Acceptance Criteria

- Folder mcp_ssd exists with docs/plans path.
- PLAN-001 exists under mcp_ssd/docs/plans.
- MCP-only architecture documented without internal agent relay layer.
- MCP_SDD naming defined for package and server entrypoint.
- UCX deprecation path and compatibility strategy documented.
- Baseline migration copied from UCX_v1_archive:
	- scripts/ -> mcp_ssd/scripts
	- ucx/mcp -> mcp_ssd/mcp
	- ucx/validators -> mcp_ssd/validators
	- ucx/utils -> mcp_ssd/utils
	- ucx/config -> mcp_ssd/config
	- ucx/observability -> mcp_ssd/observability
	- ucx/api -> mcp_ssd/api (creation, review, remediation only)
	- ucx/models -> mcp_ssd/models
	- ucx/core -> mcp_ssd/core (context_engine, persona_prompts, review_memory only)
	- ucx/prescreening -> mcp_ssd/prescreening
	- ucx/scoring -> mcp_ssd/scoring
	- ucx/skills -> mcp_ssd/skills (loader only)
	- ucx/prompts -> mcp_ssd/prompts (loader only)
	- ucx/{__init__.py,exceptions.py,version.py} -> mcp_ssd/
- Tool creation scope is limited to the PLAN-012 PRD flow first.

Verification commands:
- ls mcp_ssd/scripts
- ls mcp_ssd
- rg "from ucx\." mcp_ssd

---

## 8. Next Plan Candidates

- PLAN-002: Package rename and compatibility shim implementation.
- PLAN-003: MCP tool migration and contract regression validation.
- PLAN-004: Documentation migration and UCX deprecation completion.

---

## 9. Migration Execution Log (2026-03-23)

Completed in this plan iteration:
- Created migration targets:
	- mcp_ssd/scripts
	- mcp_ssd root package structure
- Migrated baseline scripts and function modules from /opt/data/docs_flow_framework/UCX_v1_archive.
- Expanded migrated runtime to support PLAN-012 PRD create/review/remediate flow:
	- api/{creation.py,review.py,remediation.py}
	- models/*
	- core/{context_engine.py,persona_prompts.py,review_memory.py}
	- prescreening/*
	- scoring/*
	- skills/loader.py
	- prompts/loader.py
- Added migration control documents:
	- mcp_ssd/docs/MIGRATION_INVENTORY.md
	- mcp_ssd/docs/TOOL_CREATION_LIST.md

Current constraint:
- Legacy modules still import ucx.* namespace internally.
- Namespace rewiring to mcp_sdd.* is deferred to PLAN-002.

Migration intent:
- Preserve behavior first, then perform controlled namespace and entrypoint refactor.
