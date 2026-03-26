# MCP Roadmap

## Overview

This roadmap defines planned documentation and governance milestones for MCP documentation under mcp/docs.

| Field | Value |
| --- | --- |
| Current Version | 1.0.1 |
| Latest Release | 1.0.1 (validate-build script validation and .ucx stage output normalization) |
| Next Minor | 1.1.0 (full UCX_v1-to-MCP migration without autopilot) |
| Next Major | 2.0.0 (post-migration governance hardening and policy enforcement) |
| Timezone | America/New_York |

Versioning policy reference:
- policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md

---

## Version Timeline

v1.0.1 (Current) -> v1.1.0 (Migration Core) -> v1.2.0 (Migration Completion) -> v2.0.0

---

## Planned Releases

### v1.1.0 - Migration Core (UCX_v1 to MCP without autopilot)

| Field | Value |
| --- | --- |
| Status | Planned |
| Type | Minor |
| Scope | Implement missing MCP runtime capabilities and migrate to MCP-first documentation |

Planned scope:
- Implement currently missing commands except autopilot: `remediate`, `validate-fix`, `remediate-fix`.
- Add operational command controls for validation and review modes.
- Implement prescreen and diagnostics entry points (`prescreen`, `scan`, `scoring`).
- Publish MCP-first documentation for framework overview and operational flows.
- Remove active MCP runtime-doc dependency on UCX_v1 references.

Acceptance targets:
- In-scope commands execute with deterministic output contracts and tests.
- MCP docs are sufficient to operate MCP without consulting UCX_v1 archive docs.
- Migration plan execution starts from `plans/IPLAN-003_mcp_full_migration_from_ucx_v1.md`.

---

### v1.2.0 - Migration Completion and Cutover

| Field | Value |
| --- | --- |
| Status | Planned |
| Type | Minor |
| Scope | Complete migration closure and UCX_v1 sunset readiness for MCP |

Planned scope:
- Finalize all in-scope capabilities and flow-level runbook procedures.
- Publish migration completion report and deprecation/sunset policy execution evidence.
- Enforce MCP as canonical source for runtime behavior and operator guidance.
- Restrict UCX_v1 mentions to migration/deprecation policy artifacts only.

Acceptance targets:
- UCX_v1 is no longer required for MCP runtime operation or documentation interpretation.
- Migration completion report is published with test and documentation parity evidence.

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
- Added `validate-build` CLI command for script-based structural validation against layer schema/template assets.
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