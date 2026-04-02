# UCX — Unified Context Framework

> **Aliases**: `ucx`, `mcp_sdd`, `sdd-lifecycle`
>
> The package directory is `mcp_sdd/` (historical name). The canonical name is **UCX** (Unified Context Framework). References to `mcp_sdd`, `ucx`, or `sdd-lifecycle` all refer to this system. The legacy `UCX_v1` archive (`ai_dev_ssd_flow/archived/UCX_v1_archive/`) is a historical predecessor — not the current UCX.

| Field | Value |
| --- | --- |
| Canonical Name | UCX (Unified Context Framework) |
| Package Directory | `mcp_sdd/` |
| MCP Server Name | `sdd-lifecycle` |
| Sub-Framework Code | `ucx` (used in report naming: `BRD-03.ucx.validate.json`) |
| Status | Active |
| Version | 1.11.0 |
| Date | 2026-04-02 |
| Timezone | America/New_York |

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

1. Runtime code and tests under mcp_sdd/src/mcp_server and mcp_sdd/tests
2. Canonical specs under mcp_sdd/docs/specs
3. Policies under mcp_sdd/docs/policies
4. Architecture and runbooks under mcp_sdd/docs/architecture
5. Plans and reports under mcp_sdd/docs/plans

---

## 3. Skills and Project Isolation Model

UCX uses a **project isolation model** for AI skills. Framework assets are scaffold sources only — they are never loaded at runtime.

### Initialization

`sdd_init --project <path>` copies all personas, prompts, templates, and layer assets from the framework into `{project}/UCX/`. Existing files are never overwritten.

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

No fallback to framework defaults. Missing assets raise `ProjectSkillsNotFound`. `validate_project_ucx_root()` checks both required directories and required files (including `persona_mappings.yaml`). Preflight checks (`sdd_preflight`) emit a `missing_persona_mappings` warning when the mapping file is absent. Persona mapping loading uses mtime-based caching to avoid redundant YAML parsing.

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

## 8. Changelog

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
