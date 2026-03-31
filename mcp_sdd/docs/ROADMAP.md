# MCP Roadmap

## Overview

This roadmap defines planned documentation and governance milestones for MCP documentation under mcp_sdd/docs.

| Field | Value |
| --- | --- |
| Current Version | 1.6.0 |
| Latest Release | 1.6.0 (3-segment element IDs, template + prompt migration) |
| Previous Release | 1.3.0 (diagnostics and governance refinement) |
| Next Major | 2.0.0 (post-migration governance hardening and policy enforcement) |
| Timezone | America/New_York |

Versioning policy reference:

- policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md

---

## Version Timeline

v1.2.0 -> v1.3.0 (Diagnostics) -> v1.4.0 (Current: MCP Transport) -> v2.0.0

---

## Planned Releases

### v1.1.0 - Migration Core (UCX_v1 to MCP without autopilot)

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Scope | Implement missing MCP runtime capabilities and migrate to MCP-first documentation |

Delivered scope:

- Implement currently missing commands except autopilot: `remediate`, `validate-fix`, `remediate-fix`.
- Add operational command controls for validation and review modes.
- Implement prescreen and diagnostics entry points (`prescreen`, `scan`, `scoring`).
- Publish MCP-first documentation for framework overview and operational flows.
- Remove active MCP runtime-doc dependency on UCX_v1 references.

Outcome summary:

- In-scope commands execute with deterministic output contracts and tests.
- MCP docs are sufficient to operate MCP without consulting UCX_v1 archive docs.
- Migration tracking is recorded in `plans/IPLAN-003_mcp_full_migration_from_ucx_v1.md` and `plans/IPLAN-003_RELEASE_TRACKING.yaml`.

---

### v1.2.0 - Lifecycle Normalization and Command Alignment

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Scope | Normalize active MCP lifecycle command naming, generalize derived-artifact flow semantics, and publish explicit project-initialization guidance |

Delivered scope:

- Normalize active validation command naming to `validate` across runtime, tests, and active documentation.
- Generalize source-protected derived-artifact flow semantics across all SSD document layers.
- Normalize folder-based artifact resolution so downstream stages consume the correct prior artifact.
- Publish explicit project initialization flow documentation for `init`, `create-build`, and `create`.
- Record historical closure in `plans/IPLAN-004_mcp_lifecycle_normalization_and_command_alignment.md`.

Outcome summary:

- Active runtime and architecture docs use MCP-native lifecycle naming.
- Derived artifact naming and source resolution rules are explicit and test-backed.
- Project-specific prompt/template initialization is documented as part of the operational flow.

References:

- plans/IPLAN-004_mcp_lifecycle_normalization_and_command_alignment.md
- architecture/MCP_OPERATIONAL_FLOWS.md
- architecture/MCP_CLI_REFERENCE.md

---

### v1.3.0 - Diagnostics and Governance Refinement

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Scope | Refine diagnostics coverage, operational controls, and release governance evidence |

Planned scope:

- Expand diagnostics and command-control coverage where needed.
- Continue aligning operator and runtime documentation to implemented contracts.
- Strengthen release-history and governance evidence artifacts for future MCP releases.

Implemented scope to date:

- Implement IPLAN-005 baseline command contracts for:
  - `consistency` (lightweight artifact-lineage checks)
  - `preflight` (runtime and environment readiness checks)
- Add preflight fallback parsing and runtime-error exit-contract coverage.
- Complete remediation source-restoration telemetry hardening with present and omitted branch coverage.
- Expand EARS and SPEC TASKS CTR validation parity-depth checks, including negative-path fixtures and EARS folder validation coverage.
- Add deterministic hash-based `finding_id` and `action_id` emission for remediation findings with legacy finding-ID compatibility validation.
- Update runbook, lifecycle flow documentation, and remediation/reporting specs for G3 diagnostics contracts.
- Publish final IPLAN-005 closure tracking and evidence artifacts.
- Normalize monolith-first validation behavior across all layers:
  - file-input validation redirects to canonical source artifact when folder contains a unique canonical source
  - index, appendix, glossary, and section-split markdown inputs resolve to canonical main document under this condition
- Expand review document-mode source assembly across all layers:
  - `review-build` and `review` support `--document` mode to auto-load canonical main plus appendix artifacts
  - `--sections-json` compatibility mode remains available for explicit section payload workflows
- Add cross-layer unit coverage for both validation redirection and review document-mode source assembly.

---

### v1.4.0 - MCP Protocol Transport Layer

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-03-28 |
| Scope | MCP server exposing SDD lifecycle as 19 native tools with per-call executor selection |

Delivered scope:

- MCP server entry point (`mcp_sdd/src/mcp_server/server.py`) over stdio transport, server name `sdd-lifecycle`
- Executor package (`mcp_sdd/src/mcp_server/executor/`): open registry with CLI and API type system, async subprocess runner, LiteLLM API stub, type-based dispatcher
- Tool registry (`mcp_sdd/src/mcp_server/tool_registry.py`): 20 tools (12 deterministic, 2 orchestration, 6 LLM-dependent)
- Packaging: `mcp_sdd/pyproject.toml` with `mcp-sdd` console script
- Registration: `.mcp.json` for Claude Code auto-discovery
- Tests: 33 new tests in `mcp_sdd/tests/unit/test_server.py`, all passing
- Validated against b-local project (BRD create, validate, pipeline)

References:

- plans/PLAN-001_mcp_protocol_transport_layer.md (repo-level plan)
- changelog/CHANGELOG_v0.1.0.md (repo-level changelog)

---

### v1.5.0 - Link Validation Tool and Executor Write Fixes

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-03-30 |
| Scope | New sdd_validate_links tool and CLI executor write-mode fixes |

Delivered scope:

- New tool: `sdd_validate_links` (20th tool, 12th deterministic) — validates markdown links and anchor references
- Executor fixes: Claude Code `--dangerously-skip-permissions`, Codex `--full-auto` for non-interactive file writes
- Tool count: 19 → 20 (12 deterministic, 2 orchestration, 6 LLM-dependent)
- 18 new unit tests (186 total, 0 regressions)
- Standalone `scripts/validate_doc_links.py` replaced by MCP tool

References:

- changelog/CHANGELOG_v0.12.1.md (repo-level changelog)

---

### v1.6.0 - 3-Segment Element ID Migration

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-03-31 |
| Scope | Element IDs from TYPE.NN.TT.hash to TYPE.NN.hash |

Delivered scope:

- All 11 templates: format, guidance, examples updated to 3-segment
- Prompt templates: UCC_PROMPT_PRD "4-segment" instruction removed
- Validation regex: `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$`
- Element type code table deprecated
- AUTOPILOT directory archived

---

### v2.0.0 - Governance Expansion and Hard Enforcement

| Field | Value |
| --- | --- |
| Status | Future |
| Type | Major |
| Scope | Contract-governance expansion and strict release enforcement |

Planned scope:

- Introduce stronger contract-governance rules for documentation updates tied to runtime module changes.
- Define stricter evidence requirements for release readiness with explicit blocker categories.
- Consolidate policy and compliance artifacts into a normalized release reporting model.

Potential breaking considerations:

- Stronger mandatory gate enforcement may require process updates for documentation maintainers.
- Release checklist format changes may require downstream automation updates.

---

## Completed Releases

### v1.0.1 (2026-03-25)

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Patch |
| Summary | Script-based validation command and stage output path normalization |

Delivered:

- Added `validate` CLI command for script-based structural validation against layer schema/template assets.
- Added validation runner package under `mcp_sdd/src/mcp_server/validation/` with JSON/TXT report outputs.
- Standardized stage output root from `.ucx_create` to `.ucx` and validation stage from `validation` to `validate`.
- Updated CLI reference and test coverage for new command and stage-path behavior.
- Defined UCX_v1 compatibility command contracts in MCP CLI and docs:
  - `review` alias for `review-build`
  - Reserved `remediate`, `remediate-fix`, and `validate-fix` commands with explicit not-implemented status

References:

- architecture/MCP_CLI_REFERENCE.md
- CHANGELOG/CHANGELOG_v1.0.0.md

---

### v1.0.0 (2026-03-24)

| Field | Value |
| --- | --- |
| Status | Released |
| Type | Major |
| Summary | Initial MCP documentation program baseline |

Delivered:

- L0-L9 artifacts for architecture, specs, policies, runbook, and traceability.
- Reconciliation log and coverage matrix with PASS status.
- Compliance report updates and plan closure evidence for IPLAN-002.
- Initial changelog release record in CHANGELOG/CHANGELOG_v1.0.0.md.

References:

- plans/IPLAN-002_mcp_docs_full_layer_coverage.md
- plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md
- CHANGELOG/CHANGELOG_v1.0.0.md

---

## Constraints

- This roadmap covers documentation scope under mcp_sdd/docs.
- Runtime feature changes are out of scope unless separately approved and tracked.
- Release sequencing can change based on reconciliation outcomes and policy updates.
