# UCX Hermes — Primary AI Agent Orchestration Platform

> **Status**: Historical migration record (pre-migration `mcp_ucx` → `ucx_hermes`).
> For the current platform overview see [`../README.md`](../README.md) and
> [`HERMES_INTEGRATION.md`](HERMES_INTEGRATION.md).
> **Current runtime**: `hermes/v0.7.3` (framework spec `0.36.2`); package `mcp_server` at `platforms/hermes/`.
> **Date**: 2026-05-02
> **Previous**: mcp_ucx v1.22.0 (DEPRECATED)
> **Timezone**: America/New_York

## What Changed

This directory (`ucx_hermes/`) is now the **sole active runtime** for the UCX MCP server. The historical package directory `mcp_ucx/` is **deprecated and frozen** at v1.22.0.

### Why the Move

| Issue in mcp_ucx | Fix in ucx_hermes |
|-----------------|-------------------|
| Stateless CLI executor delegation silently rewrote documents without human approval | Runtime enforces API-only LiteLLM executors for LLM stages and keeps deterministic stages non-LLM |
| UCX skills and Hermes skills had overlapping names but different semantics | Bridge skill (`ucx-sdd-bridge`) codifies safe integration; no semantic drift |
| No explicit separation between deterministic validation and interactive reasoning | Tool classification: deterministic checks vs prompt-assembly tools (human-gated) |
| No guidance for Hermes-agent-specific safety boundaries | `HERMES_INTEGRATION.md` and bridge skill define safe workflow |

---

## Quick Facts

| Field | Value |
| --- | --- |
| Canonical Name | UCX Hermes |
| Package Directory | `platforms/hermes/` (runtime package `mcp_server`) |
| MCP Server Name | `sdd-lifecycle` |
| Sub-Framework Code | `ucx` (used in report naming: `BRD-03.ucx.validate.json`) |
| Status | **Active** |
| Version | `hermes/v0.7.3` (framework spec `0.36.2`) |
| Date | 2026-05-02 |
| Timezone | America/New_York |

---

## V3 Layer Architecture

Active document flow for SDD v3.2 (8 layers):

```
BRD (L1: Context/C4-L1)
  → PRD (L2: Container/C4-L2)
  → EARS (L3: Decision Bridge)
  → BDD (L4: Decision Bridge)
  → ADR (L5: Decision Bridge)
  → SPEC (L6: Component/C4-L3)
  → TDD (L7: Implementation Bridge)
  → IPLAN (L8: Implementation Bridge)
  → Code
```

### Recommended Agent Split

Use Hermes as control plane for the SDD lifecycle and a code-generation agent (Claude Code, Codex, or equivalent) as the coding executor:

1. Hermes completes a planning-first gate (source analysis -> layer roadmap -> planning index -> changelog plan -> gap review -> per-document IPLAN approval) before creating lifecycle artifacts.
2. Hermes orchestrates BRD -> PRD -> EARS -> BDD -> ADR -> SPEC -> TDD -> IPLAN with UCX MCP tools.
3. Claude Code, Codex, or another code-generation agent implements source code from approved IPLAN artifacts.
4. Hermes runs validation/review/remediation gates before handoff to code and after implementation changes.

### Development and Issue-Fix Loop

Default governance loop managed by Hermes from task intake through merge:

1. A task is defined by a human or AI agent.
2. Hermes completes and records planning-first governance artifacts for the target scope.
3. Hermes creates and prioritizes a GitHub issue with acceptance criteria and traceability (`@spec`, `@tdd`, `@iplan`).
4. Implementation work resolves the issue on a feature branch according to approved plans.
5. A pull request is submitted.
6. Round 1 gate runs in order: `sdd_validate` -> `sdd_review` -> `sdd_remediate` -> post-remediation `sdd_validate` -> Hermes final blocker-gap and inconsistency review.
7. If Round 1 fails, Round 2 repeats the same gate sequence.
8. If Round 2 fails, Hermes escalates to human review and merge remains blocked.
9. If all merge gates pass, PR merges and linked issue is closed on merge.
10. Human alert channels for escalation and merge-time notifications are implementation-defined (TBD).

### Parallel Persona Review (Saga Pattern)

Hermes supports a Saga orchestration pattern for multi-persona review fan-out/fan-in to reduce sequential review latency and limit context-window pressure from long persona chains. This pattern adds branch-level retries, compensation actions, deterministic reducer merge, and escalation rules while preserving source-protected document flow.

Branch LLM fan-out controls:

- `saga_branch_llm_enabled` enables branch-level API calls in `review_mode=saga_parallel`.
- `UCX_REVIEW_SAGA_BRANCH_LLM_PHASE` controls rollout defaults (`A` and `B` off, `C` on when explicit flag is absent).
- `UCX_REVIEW_SAGA_BRANCH_LLM_ENABLED` provides explicit environment override.
- `UCX_REVIEW_DEBUG_RAW_OUTPUTS=true` enables debug-only redacted raw output retention.

Executor defaults:

- Review saga branch default executor: `api/openrouter`.
- Remediation default executor: `api/claude-sonnet`.
- Default generation controls: `temperature=0.2`, `top_p=0.9`, `top_k` unset, `max_output_tokens=4000`.

Reference:

- `architecture/MCP_SAGA_ORCHESTRATION_PATTERN.md`

Execution ownership model (Hermes orchestrator vs execution agents):

1. Hermes monitors observability signals through integrated telemetry systems and triage inputs.
2. Hermes opens and prioritizes GitHub issues with implementation traceability (`@spec`, `@tdd`, `@iplan`) and acceptance criteria.
3. Only issues in `ai:ready` are eligible for autonomous execution.
4. Execution agents (Claude Code, Codex, OpenCode, or equivalent) perform fix implementation, PR submission, validation, and deployment workflows.
5. Hermes reviews post-deployment evidence and closes issues when monitoring and acceptance gates pass.

### C4 Model Alignment

| C4 Level | SDD Layer | Document | Primary Content |
|----------|-----------|----------|-----------------|
| **C4-L1 Context** | L1 | BRD | Actors, boundaries, business environment |
| **C4-L2 Container** | L2 | PRD | Product features, functional blocks |
| **Decision Bridge** | L3-L5 | EARS, BDD, ADR | Formalize requirements → scenarios → decisions |
| **C4-L3 Component** | L6 | SPEC | Interfaces, data models, behavior contracts |
| **Implementation Bridge** | L7-L8 | TDD, IPLAN | Test definitions → execution planning |
| **C4-L4 Code** | — | Source Code | Class/package structure |

### Active Layers (v3.2)

| Layer | Name | Layer ID | C4 Level | Upstream | Downstream |
|-------|------|----------|----------|----------|------------|
| 1 | Business Requirements | `brd` | Context (C4-L1) | — | PRD |
| 2 | Product Requirements | `prd` | Container (C4-L2) | BRD | EARS |
| 3 | Formal Requirements | `ears` | Decision Bridge | PRD | BDD |
| 4 | Behavior-Driven Dev | `bdd` | Decision Bridge | EARS | ADR |
| 5 | Architecture Decisions | `adr` | Decision Bridge | BDD | SPEC |
| 6 | Technical Specification | `spec` | Component (C4-L3) | ADR + BDD | TDD |
| 7 | Test-Driven Dev | `tdd` | Implementation Bridge | SPEC | IPLAN |
| 8 | Implementation Plan | `iplan` | Implementation Bridge | TDD | Code |

### Cut / Deprecated Layers (from 14-layer v2)

These layers were removed in v3.2. Their content is subsumed by the bridge layers above.

| Layer | Old ID | Replacement in v3.2 | Archive Location |
|-------|--------|---------------------|-------------------|
| System Requirements | `sys` | Architecture decisions → ADR | `templates/archive/SYS-TEMPLATE.yaml` |
| Atomic Requirements | `req` | Formal requirements → EARS | `templates/archive/REQ-TEMPLATE.yaml` |
| Data Contracts | `ctr` | Inline SPEC contracts | `templates/archive/CTR-TEMPLATE.yaml` |
| Test Specification | `tspec` | Embedded in TDD Section 4 | `templates/archive/TSPEC-TEMPLATE.yaml` |
| Task Breakdown | `tasks` | IPLAN execution bridge | `templates/archive/TASKS-TEMPLATE.yaml` |

> **Rule**: Do not create new documents referencing SYS, REQ, CTR, TSPEC, or TASKS as active layers. Use the 8-layer v3.2 flow above.

---

## 1. Layer Map

| Layer | Name | Primary Artifact |
| --- | --- | --- |
| L0 | Navigation and Inventory | README.md |
| L1 | Architecture Overview | architecture/MCP_RUNTIME_ARCHITECTURE.md |
| L2 | CLI and Tool Surface | architecture/MCP_CLI_REFERENCE.md |
| L3 | Source Input Contracts | specs/SPEC-005_mcp_source_input_ingestion_contracts.md |
| L4 | Creation Flow Contracts | specs/SPEC-006_mcp_creation_flow_operational_contracts.md |
| L5 | Review and Remediation Operations | specs/SPEC-007_mcp_review_remediation_operational_contracts.md |
| L6 | Policy Layer | policies/DOC_COMPATIBILITY_AND_DEPRECATION_POLICY.md |
| L7 | Validation and Quality Gates | policies/DOC_QUALITY_GATES.md |
| L8 | Runbooks | architecture/MCP_OPERATOR_RUNBOOK.md |
| L9 | Traceability and Audit | plans/DOC-COVERAGE-MATRIX-001_mcp_layers.md |

---

## 2. Canonical Source of Truth Order

Use this precedence for conflict resolution:

1. Runtime code and tests under `ucx_hermes/src/mcp_server` and `ucx_hermes/tests`
2. Canonical specs under `ucx_hermes/docs/specs`
3. Policies under `ucx_hermes/docs/policies`
4. Architecture and runbooks under `ucx_hermes/docs/architecture`
5. Plans and reports under `ucx_hermes/docs/plans`

> **Rule**: `mcp_ucx/` is frozen. Do not edit. All canonical changes go to `ucx_hermes/`.

---

## 3. Skills and Project Isolation Model

Hermes runtime skill index: `../skills/hermes/README.md`

UCX Hermes uses a **project isolation model** for AI skills. Skills are project-specific, not agent-specific — each project receives customized personas, prompts, and templates at initialization. Any AI agent calls UCX to get the right context for that project. Framework assets are scaffold sources only — they are never loaded at runtime.

### Initialization

`sdd_init --project <path>` copies all personas, prompts, templates, and layer assets from the framework into `{project}/UCX/`. Existing files are never overwritten. Use `--update` to sync stale files with framework source (protects `persona_mappings.yaml`). Use `--update --update-mappings` to also reset persona mappings to defaults.

### Runtime Loading

All MCP tools resolve personas, prompts, and templates exclusively from `{project}/UCX/`:

| Asset Type | Runtime Path |
| --- | --- |
| Persona definitions (16 core) | `{project}/UCX/skills/personas/{persona}.md` |
| Persona-to-doc-type mappings | `{project}/UCX/skills/persona_mappings.yaml` |
| Layer alias mappings | `{project}/UCX/skills/layer_aliases/` |
| Creation prompt templates | `{project}/UCX/prompts/templates/creation/` |
| Review prompt templates | `{project}/UCX/prompts/templates/review/` |
| Remediation prompt templates | `{project}/UCX/prompts/templates/remediation/` |
| Document templates and layer schemas | `{project}/UCX/templates/` |

No fallback to framework defaults. Missing assets raise `ProjectSkillsNotFound`. `validate_project_ucx_root()` checks both required directories and required files (including `persona_mappings.yaml`). Preflight checks (`sdd_preflight`) emit a `missing_persona_mappings` warning when the mapping file is absent and run a persona mapping health check when present. Persona mapping loading uses mtime-based caching to avoid redundant YAML parsing.

### Persona Management

Three tools for inspecting and modifying project-specific persona-to-layer mappings:

| Tool | CLI | Purpose |
| --- | --- | --- |
| `sdd_personas_show` | `personas-show` | Display persona assignments per phase/doctype |
| `sdd_personas_set` | `personas-set` | Update persona list for a phase+doctype |
| `sdd_personas_diff` | `personas-diff` | Compare project mappings vs framework defaults |

`persona_mappings.yaml` is project-owned after initialization. The `PROTECTED_PROJECT_FILES` mechanism in `scaffold.py` prevents `--update` from overwriting it.

### Environment Management

Project `.env` files are loaded automatically when executors run. Values are never exposed through MCP tools or CLI output.

| Tool / Command | Purpose |
| --- | --- |
| `sdd_env_show` / `env-show` | Show .env keys without values, blocked vars, key count |

Env merge order: `os.environ` (base) < `config.env` (executor static) < `project_env` (.env file). System variables (`PATH`, `HOME`, `PYTHONPATH`, `LD_LIBRARY_PATH`, `LD_PRELOAD`, `SHELL`, `USER`, `IFS`) are blocked and logged. Loading uses mtime-based caching. Missing `.env` returns empty dict. Preflight reports `env_key_count`, `env_keys`, and `env_blocked_vars`.

### Default Project Resolution

Tools that require `--project` resolve it from a 4-level fallback chain:

1. Explicit `--project` argument (always wins)
2. Session override via `sdd_set_project` (MCP only, cleared on restart)
3. `SDD_DEFAULT_PROJECT` env var (persistent across sessions)
4. `default_project` field in `executors.json` (config file)

| Tool / Command | Purpose |
| --- | --- |
| `sdd_set_project` | Set session default (pass empty string to clear) |
| `sdd_get_project` / `get-project` | Show resolved project and source |

CLI: `--project` becomes optional when `SDD_DEFAULT_PROJECT` is set.

### Prompt Assembly

Prompt assembly tools assemble prompts from: persona files + phase template + actionable rules + layer assets + bundle metadata. Reviews accept `personas: list[str]` (resolved from `persona_mappings.yaml` when omitted). During review, document sections are mapped to persona focus areas so each persona receives domain-relevant content.

### Active vs Compatibility Layers (Normative)

`ucx_hermes` uses the active v3.2 8-layer flow for new artifact creation:
`brd -> prd -> ears -> bdd -> adr -> spec -> tdd -> iplan`.

Compatibility support remains for legacy identifiers (`sys`, `req`, `ctr`,
`tspec`, `tasks`) in alias resolution, persona mappings, and validation
parity checks. This compatibility support does not change active-layer
authoring policy.

---

## 4. Architecture Documents

- [MCP Persona Design Guide](architecture/MCP_PERSONA_DESIGN_GUIDE.md)
- [MCP Unified Context Framework](architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md)
- [MCP Runtime Architecture](architecture/MCP_RUNTIME_ARCHITECTURE.md)
- [MCP CLI Reference](architecture/MCP_CLI_REFERENCE.md)
- [MCP Operator Runbook](architecture/MCP_OPERATOR_RUNBOOK.md)
- [MCP Operational Flows](architecture/MCP_OPERATIONAL_FLOWS.md)
- [MCP Saga Orchestration Pattern](architecture/MCP_SAGA_ORCHESTRATION_PATTERN.md)

## 5. Canonical Specifications

- [SPEC-001 MCP Core Architecture and Workflow Contracts](specs/SPEC-001_mcp_core_architecture_workflow_contracts.md)
- [SPEC-002 MCP Review, Scoring, Handoff, and Identity Contracts](specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md)
- [SPEC-003 MCP Creation, Validation, and Profile Contracts](specs/SPEC-003_mcp_creation_validation_profile_contracts.md)
- [SPEC-004 MCP Reporting, Lineage, and Artifact Contracts](specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md)
- [SPEC-005 MCP Source Input and Ingestion Contracts](specs/SPEC-005_mcp_source_input_ingestion_contracts.md)
- [SPEC-006 MCP Creation Flow Operational Contracts](specs/SPEC-006_mcp_creation_flow_operational_contracts.md)
- [SPEC-007 MCP Review and Remediation Operational Contracts](specs/SPEC-007_mcp_review_remediation_operational_contracts.md)
- [SPEC-008 MCP Output Schema Contracts](specs/SPEC-008_mcp_output_schema_contracts.md)
- [SPEC-009 MCP Remediation and Fix Flow Contracts](specs/SPEC-009_mcp_remediation_and_fix_flow_contracts.md)
- [SPEC-010 MCP Prescreen, Scan, and Scoring Contracts](specs/SPEC-010_mcp_prescreen_scan_scoring_contracts.md)
- [SPEC-011 Team Emulator Contract](specs/SPEC-011_team_emulator_contract.md)

## 6. Policies

- [Compatibility and Deprecation Policy](policies/DOC_COMPATIBILITY_AND_DEPRECATION_POLICY.md)
- [Documentation Quality Gates](policies/DOC_QUALITY_GATES.md)
- [Documentation Lifecycle and Versioning Policy](policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md)
- [MCP Cutover and UCX_v1 Archive Policy](policies/MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md)

## 7. Migration from mcp_ucx

The `mcp_ucx` → `ucx_hermes` migration is complete, and the platform has since
migrated again into this repository's `platforms/hermes/` layout (runtime package
`mcp_server`). The pre-migration project (pristine `ucx_framework` v0.20.4) is
preserved on the protected, read-only branch **`legacy-ucx-v3.2-read-only`**; see
the framework repo's `docs/PROJECT.md` §6 for change-management history. The
former `migration/MIGRATION_FROM_MCP_UCX.md` runbook is retired (the migration it
described has landed).

## 8. Hermes Integration

See [HERMES_INTEGRATION.md](HERMES_INTEGRATION.md) for:

- Safe workflow (UCX validates, Hermes reasons, humans decide)
- Tool safety classification
- Bridge skill installation
- Troubleshooting

## 8.1 First Project Checklist

Use this checklist to make UCX ready for the first project runtime:

1. Analyze provided source information and constraints.
2. Create layer roadmap, planning index, and layer changelog plan artifacts.
3. Review planning artifacts for gaps and resolve or defer with explicit rationale.
4. Create and approve per-document IPLAN artifacts (human reviewer or independent LLM-as-judge session).
5. Create shared runtime virtual environment at `/opt/data/ucx_framework/.venv`.
6. Install runtime dependencies for `ucx_hermes` (`[api]` extra required for LLM stages).
7. Install optional `ucx_kb` runtime dependencies when `project-knowledge` MCP is enabled.
8. Register MCP server `sdd-lifecycle` in Hermes config.
9. Start Hermes session and enable `ucx-sdd-bridge`.
10. Start `ucx_hermes` MCP runtime (`sdd-lifecycle`) and verify tool handshake.
11. Start `ucx_kb` MCP runtime (`project-knowledge`) when KB mode is enabled and verify `kb_status`/`kb_graph_status`.
12. Run `sdd_init` for the project root.
13. Run `sdd_preflight` with `context=any`.
14. Confirm persona mappings with `sdd_personas_show`.
15. Confirm environment keys with `sdd_env_show`.
16. Create BRD only after startup and readiness checks pass.

Command examples:

```text
cd /opt/data/ucx_framework
scripts/bootstrap_ucx_venv.sh

# Optional when KB MCP server is enabled:
scripts/bootstrap_ucx_venv.sh --with-kb

# Runtime startup gate before BRD creation:
/opt/data/ucx_framework/.venv/bin/python -m mcp_server.server
/opt/data/ucx_framework/.venv/bin/python -m ucx_kb.mcp.server

sdd_init project=/absolute/path/to/project
sdd_preflight project=/absolute/path/to/project context=any
sdd_personas_show project=/absolute/path/to/project
sdd_env_show project=/absolute/path/to/project
sdd_create_build project=/absolute/path/to/project doc_type=iplan layer=08_IPLAN template=IPLAN-TEMPLATE
```

Planning package artifacts (layer roadmap, planning index, changelog plan) are created and reviewed as governance documents before lifecycle-stage artifact creation starts.

`sdd_init` update rules:

- Default mode: creates missing project `UCX/` assets and skips existing files.
- `update=true`: syncs stale framework-owned files.
- `update=true update_mappings=true`: also resets `persona_mappings.yaml`.
- `update_mappings=true` without `update=true` is invalid.

Preflight pass criteria (`sdd_preflight context=any`):

- **Go**: status `ready` (exit code 0).
- **Conditional go**: status `degraded` (exit code 0) with documented risk acceptance and no missing required project assets.
- **No-go**: status `blocked` (exit code 1).
- **Operational error**: command runtime error (exit code 2), treat as no-go until corrected.

Minimum checks before first lifecycle run:

- `/opt/data/ucx_framework/.venv/bin/python` exists and reports Python `>=3.12`.
- `mcp_server` import check passes in the shared virtual environment.
- `sdd-lifecycle` MCP runtime is running and reachable from Hermes.
- `project-knowledge` MCP runtime is running and `kb_status` plus `kb_graph_status` return without contract errors (KB mode).
- `UCX/` scaffold exists for the target project.
- `persona_mappings.yaml` exists and persona mapping health check does not report missing persona files.
- Required executor environment keys are present for the configured provider path.

BRD creation gate:

- Do not start `sdd_create_build` for BRD until planning-first artifacts are approved, runtime startup checks pass, and `sdd_preflight` returns `ready` or approved `degraded`.
- Environment bootstrap and all required framework tools must be available before any document creation stage starts.

## 9. Plans and Reports

- [IPLAN-001 MCP Server Implementation from Canonical Specs](plans/IPLAN-001_mcp_server_implementation_from_canonical_specs.md)
- [IPLAN-006 Parallel Persona Review Saga Orchestration](plans/IPLAN-006_parallel_persona_review_saga_orchestration.md)
- [Coverage Matrix](plans/DOC-COVERAGE-MATRIX-001_mcp_layers.md)
- [Reconciliation Log](plans/DOC-RECONCILIATION-LOG-001.md)
- [Compliance Report 001](plans/COMPLIANCE-REPORT-001_mcp_canonical_contracts.md)
- [Compliance Report 002](plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md)

## 10. Changelog

- [CHANGELOG v2.0.0](CHANGELOG/CHANGELOG_v2.0.0.md) — ucx_hermes promotion: AI executor removal, bridge skill, Hermes integration
- [CHANGELOG v1.20.0](CHANGELOG/CHANGELOG_v1.20.0.md) — review/remediation quality (PLAN-029)
- [CHANGELOG v1.19.0](CHANGELOG/CHANGELOG_v1.19.0.md) — review YAML document support (PLAN-028)
- [CHANGELOG v1.18.0](CHANGELOG/CHANGELOG_v1.18.0.md) — default project resolution (PLAN-027 Phase 2)
- [CHANGELOG v1.17.0](CHANGELOG/CHANGELOG_v1.17.0.md) — project environment management (PLAN-027 Phase 1)
- [CHANGELOG v1.16.0](CHANGELOG/CHANGELOG_v1.16.0.md) — persona management tools, sdd_init --update, BRD executive_summary optional
- [CHANGELOG v1.15.0](CHANGELOG/CHANGELOG_v1.15.0.md) — persona optimization (PLAN-024, PLAN-025)
- [CHANGELOG v1.14.0](CHANGELOG/CHANGELOG_v1.14.0.md) — executor simplification + PLAN-021 naming compliance
- [CHANGELOG v1.13.0](CHANGELOG/CHANGELOG_v1.13.0.md) — merge sdd_validate_fix into sdd_validate (PLAN-023)
- [CHANGELOG v1.12.0](CHANGELOG/CHANGELOG_v1.12.0.md) — multi-persona mapping support (PLAN-022)

## 11. Roadmap

- [MCP Roadmap](ROADMAP.md)

---

## 12. Release Blocking Conditions

Release readiness requires:

- Coverage matrix PASS for layers L0 through L9
- Reconciliation log with zero unresolved conflicts
- Quality gates PASS for docs-to-code checks
- No broken links in active canonical artifacts
- Active architecture/spec/policy docs use `ucx_hermes/` runtime paths; legacy `mcp_ucx` references are limited to migration/history context

PR merge readiness for governed issue-fix workflows requires:

- Round-based deterministic checks (`sdd_validate`) PASS in the final round
- UCX persona review and remediation sequence completed for each executed round
- Hermes final blocker-gap/inconsistency review PASS
- Escalation state not set to `REQUIRED`
