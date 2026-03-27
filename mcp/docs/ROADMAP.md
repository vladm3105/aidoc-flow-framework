# MCP Roadmap

## Overview

This roadmap defines planned documentation and governance milestones for MCP documentation under mcp/docs.

| Field | Value |
| --- | --- |
| Current Version | 1.2.0 |
| Latest Release | 1.2.0 (lifecycle normalization, command alignment, and project initialization flow documentation) |
| Next Minor | 1.3.0 (diagnostics and governance refinement) |
| Next Major | 2.0.0 (post-migration governance hardening and policy enforcement) |
| Timezone | America/New_York |

Versioning policy reference:

- policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md

---

## Version Timeline

v1.2.0 (Current) -> v1.3.0 (Diagnostics and Governance Refinement) -> v2.0.0

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
- Added validation runner package under `mcp/src/mcp_server/validation/` with JSON/TXT report outputs.
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

- This roadmap covers documentation scope under mcp/docs.
- Runtime feature changes are out of scope unless separately approved and tracked.
- Release sequencing can change based on reconciliation outcomes and policy updates.
