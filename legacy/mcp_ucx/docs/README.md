# UCX — Unified Context eXcelerator

> ⚠️ **DEPRECATED — FROZEN AT v1.22.0**
>
> This directory (`mcp_ucx/`) is **deprecated** as of 2026-05-02. All active development, runtime code, tests, documentation, templates, and skills have moved to **`ucx_hermes/`** (v2.0.0+).
>
> - **New work**: Use `ucx_hermes/`
> - **Bug reports**: File against `ucx_hermes/`
> - **MCP config**: Point to `ucx_hermes/src`
> - **Migration guide**: See `ucx_hermes/docs/migration/MIGRATION_FROM_MCP_UCX.md`
> - **Historical reference**: This file and the `mcp_ucx/` tree are frozen for audit purposes only.
>
> ---

> **Aliases**: `ucx`, `mcp_ucx`, `sdd-lifecycle`
>
> The package directory is `mcp_ucx/` (historical name). **The canonical active directory is now `ucx_hermes/`**. References to `mcp_ucx` in historical docs and templates should be treated as legacy. The legacy `UCX_v1` archive (`ucx_flow_v3/archived/UCX_v1_archive/`) is a historical predecessor — not the current UCX.
>
> UCX is an AI agent orchestration platform that creates and manages context for AI agents (Claude Code, Gemini CLI, GitHub Copilot, Codex, OpenRouter) per project. Skills are project-specific, not agent-specific — any agent calls UCX to get the right context for a specific project.

| Field | Value |
| --- | --- |
| Canonical Name | UCX (Unified Context eXcelerator) |
| Package Directory | `mcp_ucx/` |
| MCP Server Name | `sdd-lifecycle` |
| Sub-Framework Code | `ucx` (used in report naming: `BRD-03.ucx.validate.json`) |
| Status | Active |
| Version | 1.22.0 |
| Date | 2026-04-30 |
| Timezone | America/New_York |

## V3 Layer Architecture

Active document flow for SDD v3.2:

`BRD (L1) -> PRD (L2) -> EARS (L3) -> BDD (L4) -> ADR (L5) -> SPEC (L6) -> TDD (L7) -> IPLAN (L8) -> Code`

Document type notes:
- New layers: `tdd`, `iplan`
- Deprecated/cut layers for v3 flow: `sys`, `req`, `ctr`, `tspec`, `tasks`

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

1. Runtime code and tests under mcp_ucx/src/mcp_server and mcp_ucx/tests
2. Canonical specs under mcp_ucx/docs/specs
3. Policies under mcp_ucx/docs/policies
4. Architecture and runbooks under mcp_ucx/docs/architecture
5. Plans and reports under mcp_ucx/docs/plans

---

## 3. Skills and Project Isolation Model

UCX uses a **project isolation model** for AI skills. Skills are project-specific, not agent-specific — each project receives customized personas, prompts, and templates at initialization. Any AI agent calls UCX to get the right context for that project. Framework assets are scaffold sources only — they are never loaded at runtime.

### Initialization

`sdd_init --project <path>` copies all personas, prompts, templates, and layer assets from the framework into `{project}/UCX/`. Existing files are never overwritten. Use `--update` to sync stale files with framework source (protects `persona_mappings.yaml`). Use `--update --update-mappings` to also reset persona mappings to defaults.

### Runtime Loading

All MCP tools resolve personas, prompts, and templates exclusively from `{project}/UCX/`:

| Asset Type | Runtime Path |
| --- | --- |
| Persona definitions (15 core) | `{project}/UCX/skills/personas/{persona}.md` |
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

LLM-dependent tools assemble prompts from: persona files + phase template + actionable rules + layer assets + bundle metadata. Reviews accept `personas: list[str]` (resolved from `persona_mappings.yaml` when omitted). During review, document sections are mapped to persona focus areas so each persona receives domain-relevant content.

---

## 4. Architecture Documents

- [MCP Persona Design Guide](architecture/MCP_PERSONA_DESIGN_GUIDE.md)
- [MCP Unified Context Framework](architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md)
- [MCP Runtime Architecture](architecture/MCP_RUNTIME_ARCHITECTURE.md)
- [MCP CLI Reference](architecture/MCP_CLI_REFERENCE.md)
- [MCP Operator Runbook](architecture/MCP_OPERATOR_RUNBOOK.md)
- [MCP Operational Flows](architecture/MCP_OPERATIONAL_FLOWS.md)

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

## 6. Policies

- [Legacy Report Policy](policies/legacy_report_policy.md)
- [Compatibility and Deprecation Policy](policies/DOC_COMPATIBILITY_AND_DEPRECATION_POLICY.md)
- [Documentation Quality Gates](policies/DOC_QUALITY_GATES.md)
- [Documentation Lifecycle and Versioning Policy](policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md)
- [MCP Cutover and UCX_v1 Archive Policy](policies/MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md)

## 7. Plans and Reports

- [IPLAN-001 MCP Server Implementation from Canonical Specs](plans/IPLAN-001_mcp_server_implementation_from_canonical_specs.md)
- [IPLAN-002 MCP Docs Full Layer Coverage Plan](plans/IPLAN-002_mcp_docs_full_layer_coverage.md)
- [IPLAN-003 MCP Full Migration from UCX_v1 (without autopilot)](plans/IPLAN-003_mcp_full_migration_from_ucx_v1.md)
- [Coverage Matrix](plans/DOC-COVERAGE-MATRIX-001_mcp_layers.md)
- [Reconciliation Log](plans/DOC-RECONCILIATION-LOG-001.md)
- [Compliance Report 001](plans/COMPLIANCE-REPORT-001_mcp_canonical_contracts.md)
- [Compliance Report 002](plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md)
- [Release Readiness 001](plans/RELEASE-READINESS-001_mcp_cutover_status.md)
- [Rollback Notes 001](plans/ROLLBACK-NOTES-001_mcp_partial_deployment.md)
- [Test Checklist 001](plans/TEST-CHECKLIST-001_mcp_new_contract_rows.md)
- [PLAN-016 Cross-Section Validation](plans/PLAN-016_cross_section_validation.md)
- [PLAN-016 Checklist](plans/PLAN-016_checklist.md)
- [PLAN-017 Executor Output and Logging](plans/PLAN-017_executor_output_and_logging.md)
- [PLAN-018 YAML Parity and API Consistency](plans/PLAN-018_yaml_parity_and_api_consistency.md)
- [PLAN-019 Remediation Build Enhancement](plans/PLAN-019_remediation_build_enhancement.md)
- [PLAN-020 UCX Root Relocation](plans/PLAN-020_ucx_root_relocation.md)
- [PLAN-021 SDD Reporting Naming Standard](plans/PLAN-021_sdd_reporting_naming_standard.md)
- [PLAN-028 Review YAML Document Support](plans/PLAN-028_review_yaml_document_support.md)

## 8. Changelog

- [CHANGELOG v1.20.0](CHANGELOG/CHANGELOG_v1.20.0.md) — review/remediation quality (PLAN-029)
- [CHANGELOG v1.19.0](CHANGELOG/CHANGELOG_v1.19.0.md) — review YAML document support (PLAN-028)
- [CHANGELOG v1.18.0](CHANGELOG/CHANGELOG_v1.18.0.md) — default project resolution (PLAN-027 Phase 2)
- [CHANGELOG v1.17.0](CHANGELOG/CHANGELOG_v1.17.0.md) — project environment management (PLAN-027 Phase 1)
- [CHANGELOG v1.16.0](CHANGELOG/CHANGELOG_v1.16.0.md) — persona management tools, sdd_init --update, BRD executive_summary optional
- [CHANGELOG v1.15.0](CHANGELOG/CHANGELOG_v1.15.0.md) — persona optimization (PLAN-024, PLAN-025)
- [CHANGELOG v1.14.0](CHANGELOG/CHANGELOG_v1.14.0.md) — executor simplification + PLAN-021 naming compliance
- [CHANGELOG v1.13.0](CHANGELOG/CHANGELOG_v1.13.0.md) — merge sdd_validate_fix into sdd_validate (PLAN-023)
- [CHANGELOG v1.12.0](CHANGELOG/CHANGELOG_v1.12.0.md) — multi-persona mapping support (PLAN-022)
- [CHANGELOG v1.11.0](CHANGELOG/CHANGELOG_v1.11.0.md) — unified report naming standard
- [CHANGELOG v1.10.0](CHANGELOG/CHANGELOG_v1.10.0.md) — UCX root relocation (docs/UCX → UCX)
- [CHANGELOG v1.9.0](CHANGELOG/CHANGELOG_v1.9.0.md) — review report parsing in sdd_remediate
- [CHANGELOG v1.8.0](CHANGELOG/CHANGELOG_v1.8.0.md) — YAML parity, categorized scoring, API aliases
- [CHANGELOG v1.7.0](CHANGELOG/CHANGELOG_v1.7.0.md) — cross-section validation, YAML fork, BRD diagram registry
- [CHANGELOG v1.6.0](CHANGELOG/CHANGELOG_v1.6.0.md) — 3-segment element IDs, template migration
- [CHANGELOG v1.5.0](CHANGELOG/CHANGELOG_v1.5.0.md) — sdd_validate_links tool, executor write fixes
- [CHANGELOG v1.0.0](CHANGELOG/CHANGELOG_v1.0.0.md) — initial MCP documentation layer

## 9. Roadmap

- [MCP Roadmap](ROADMAP.md)

---

## 10. Reconciliation Index

| Path | Type | Canonical Status | Action |
| --- | --- | --- | --- |
| architecture/MCP_PERSONA_DESIGN_GUIDE.md | architecture guide | active | retain |
| architecture/MCP_RUNTIME_ARCHITECTURE.md | architecture guide | active | retain |
| architecture/MCP_CLI_REFERENCE.md | architecture guide | active | retain |
| architecture/MCP_OPERATOR_RUNBOOK.md | runbook | active | retain |
| policies/legacy_report_policy.md | policy | active | retain |
| policies/DOC_COMPATIBILITY_AND_DEPRECATION_POLICY.md | policy | active | retain |
| policies/DOC_QUALITY_GATES.md | policy | active | retain |
| policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md | policy | active | retain |
| specs/SPEC-001_mcp_core_architecture_workflow_contracts.md | spec | active | retain |
| specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md | spec | active | retain |
| specs/SPEC-003_mcp_creation_validation_profile_contracts.md | spec | active | retain |
| specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md | spec | active | retain |
| specs/SPEC-005_mcp_source_input_ingestion_contracts.md | spec | active | retain |
| specs/SPEC-006_mcp_creation_flow_operational_contracts.md | spec | active | retain |
| specs/SPEC-007_mcp_review_remediation_operational_contracts.md | spec | active | retain |

---

## 11. Release Blocking Conditions

Release readiness requires:

- Coverage matrix PASS for layers L0 through L9
- Reconciliation log with zero unresolved conflicts
- Quality gates PASS for docs-to-code checks
- No broken links in active canonical artifacts
