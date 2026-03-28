# DOC-RECONCILIATION-LOG-001

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | mcp/docs reconciliation against implemented runtime behavior |

---

## 1. Objective

Track documentation conflicts, selected source-of-truth decisions, and closure actions.

---

## 2. Source-of-Truth Precedence

1. Runtime code and tests under mcp_sdd/src/mcp_server and mcp_sdd/tests
2. Canonical specs under mcp_sdd/docs/specs
3. Policies under mcp_sdd/docs/policies
4. Architecture and runbooks under mcp_sdd/docs/architecture
5. Plans and reports under mcp_sdd/docs/plans

---

## 3. File Reconciliation Register

| File | Status | Owner | Last Review Date | Notes |
| --- | --- | --- | --- | --- |
| mcp_sdd/docs/architecture/MCP_PERSONA_DESIGN_GUIDE.md | retain | docs-maintainer | 2026-03-24 | Runtime source policy aligns with loader module contracts |
| mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md | retain | runtime-maintainer | 2026-03-24 | Documents implemented runtime flow boundaries |
| mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md | retain | runtime-maintainer | 2026-03-24 | CLI command contracts aligned to argparse definitions |
| mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md | retain | operator-maintainer | 2026-03-24 | Scenario procedures aligned to implemented command behavior |
| mcp_sdd/docs/policies/legacy_report_policy.md | retain | docs-maintainer | 2026-03-24 | Compatible with reporting policy behavior |
| mcp_sdd/docs/policies/DOC_COMPATIBILITY_AND_DEPRECATION_POLICY.md | retain | docs-maintainer | 2026-03-24 | Compatibility and deprecation constraints formalized |
| mcp_sdd/docs/policies/DOC_QUALITY_GATES.md | retain | release-approver | 2026-03-24 | Release-blocking gate criteria formalized |
| mcp_sdd/docs/policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md | retain | docs-maintainer | 2026-03-24 | Lifecycle and version increment triggers formalized |
| mcp_sdd/docs/specs/SPEC-001_mcp_core_architecture_workflow_contracts.md | retain | runtime-maintainer | 2026-03-24 | No unresolved conflicts logged |
| mcp_sdd/docs/specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md | retain | runtime-maintainer | 2026-03-24 | No unresolved conflicts logged |
| mcp_sdd/docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md | retain | runtime-maintainer | 2026-03-24 | No unresolved conflicts logged |
| mcp_sdd/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md | retain | runtime-maintainer | 2026-03-24 | No unresolved conflicts logged |
| mcp_sdd/docs/specs/SPEC-005_mcp_source_input_ingestion_contracts.md | retain | runtime-maintainer | 2026-03-24 | Source payload and ingestion constraints formalized |
| mcp_sdd/docs/specs/SPEC-006_mcp_creation_flow_operational_contracts.md | retain | runtime-maintainer | 2026-03-24 | init and create-build operational contracts formalized |
| mcp_sdd/docs/specs/SPEC-007_mcp_review_remediation_operational_contracts.md | retain | runtime-maintainer | 2026-03-24 | review-build and handoff operational contracts formalized |

---

## 4. Conflict Register

| Conflict ID | Statement Location | Observed Conflict | Selected Source | Resolution Rationale | Action Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | prior verbal interpretation (external) | BRD creation from arbitrary markdown implied as implemented in create-build | mcp_sdd/src/mcp_server/cli/main.py + prompts/context_builder.py | Current implementation accepts structured sections-json and optional synthetic fallback; direct markdown ingestion pipeline is not implemented as a first-class mode | runtime-maintainer | closed |

---

## 5. Deferred Items

| Deferred ID | Item | Reason | Owner | Required Gate for Closure |
| --- | --- | --- | --- | --- |
| None | None | N/A | N/A | N/A |

---

## 6. Closure Criteria

This log is considered closed for release when:
- unresolved conflict count = 0
- deferred item count = 0, or every deferred item has explicit owner and gate
- all canonical files in coverage matrix have PASS status
