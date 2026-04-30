---
title: "IPLAN-003: MCP Full Migration from UCX_v1 (without autopilot)"
id: IPLAN-003
date_created: 2026-03-26
last_updated: 2026-03-26
status: planning
owner: ai-agent
tags:
  - implementation-plan
  - mcp
  - migration
  - documentation
  - unified-context
custom_fields:
  document_type: iplan
  plan_id: IPLAN-003
  status: planning
  created_date: 2026-03-26
  timezone: America/New_York
---

## IPLAN-003: MCP Full Migration from UCX_v1 (without autopilot)

## 1. Objective

Complete migration of runtime and documentation capabilities from legacy archive behavior into MCP, excluding autopilot orchestration, and establish MCP as an independent SSD Unified Context framework implementation with no legacy-archive prerequisite.

## 2. Scope

### In Scope

1. Implement all currently missing MCP capabilities except autopilot.
2. Replace placeholder CLI contracts with executable runtime behavior.
3. Add missing MCP-first documentation: framework overview, flow contracts, CLI contracts, runbooks, and archive/cutover policy.
4. Remove or neutralize legacy archive references in MCP runtime-facing and runbook docs.
5. Add deterministic validation and acceptance gates for migration completion.

### Out of Scope

1. Autopilot orchestration (`autopilot` command and multi-iteration orchestration loop).
2. Backporting MCP changes into UCX_v1 archive.
3. Maintaining long-term feature parity guarantees with UCX_v1 after MCP cutover.
4. Rollback design and rollback execution procedures for this migration phase.

## 3. Migration Principles

1. MCP naming is canonical for runtime, docs, and artifacts.
2. MCP cutover is immediate for active workflows; no deprecation window is planned.
3. UCX_v1 is archived and historical only, and must not remain in active MCP user-facing documentation except archive mapping notes.
4. Script-based validation remains deterministic and independent from LLM review.
5. Source-protected derived-artifact flow is mandatory for fix application commands.
6. CLI behavior must be test-backed before documentation is marked active.

## 4. Missing Capability Inventory (Target State)

### 4.1 Priority P0 (Foundational for migration)

1. `remediate` runtime implementation (currently placeholder).
2. `validate-fix` runtime implementation (currently placeholder).
3. `remediate-fix` runtime implementation (currently placeholder).
4. Derived artifact flow:
   - source -> `_validation` copy + validation report
   - `_validation` -> `_remediated` copy + remediation report

### 4.2 Priority P1 (Operational parity and CI readiness)

1. `validate-build` options:
   - `--tier1-only`
   - `--strict`
   - `--format {text,json}`
   - stable exit-code contract by severity tier
2. `review-build` and `review` mode controls:
   - `--persona`
   - `--unified`
   - `--one-turn`
   - `--no-resume`
   - `--session-ttl`
3. Session and report maintenance operations:
   - `--clean-memory`
   - `--clean-reports`
   - `--keep-versions`

### 4.3 Priority P2 (Decision support and diagnostics)

1. `prescreen` command for remediation scope reduction.
2. `scan` command for report category extraction and finding metrics.
3. `scoring` command group:
   - `scoring show`
   - `scoring validate`
   - `scoring compare`

## 5. Implementation Workstreams

### 5.1 Workstream A: CLI and Runtime Implementation

Target modules:

1. `mcp_ucx/src/mcp_server/cli/main.py`
2. `mcp_ucx/src/mcp_server/review/*`
3. `mcp_ucx/src/mcp_server/validation/*`
4. `mcp_ucx/src/mcp_server/remediation/*` (new)
5. `mcp_ucx/src/mcp_server/prescreening/*` (new)
6. `mcp_ucx/src/mcp_server/scoring/*` (new)
7. `mcp_ucx/src/mcp_server/scan/*` (new)

Required outcomes:

1. Placeholder commands replaced by functional handlers.
2. New command families registered with deterministic argument contracts.
3. Output directories normalized under `.ucx/<stage>` with naming frozen in M1 for this migration release.

### 5.2 Workstream B: Test and Validation Coverage

Target test areas:

1. `mcp_ucx/tests/unit/test_cli_main.py`
2. `mcp_ucx/tests/unit/test_validation_runner.py`
3. `mcp_ucx/tests/unit/test_remediation_runner.py` (new)
4. `mcp_ucx/tests/unit/test_prescreening.py` (new)
5. `mcp_ucx/tests/unit/test_scoring_cli.py` (new)
6. `mcp_ucx/tests/integration/test_migration_flows.py` (new)

Required outcomes:

1. Command-level tests for each new and implemented command.
2. Derived-artifact invariants verified (source unchanged, copy mutated).
3. Exit-code and JSON and text formatting behavior verified.

### 5.3 Workstream C: MCP Documentation Migration and Independence

Create new docs:

1. `mcp_ucx/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md`
   - General description of MCP as SSD Unified Context framework.
2. `mcp_ucx/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
   - End-to-end flow descriptions: create, review, validate, validate-fix, remediate, remediate-fix, scan, scoring.
3. `mcp_ucx/docs/specs/SPEC-009_mcp_remediation_and_fix_flow_contracts.md`
4. `mcp_ucx/docs/specs/SPEC-010_mcp_prescreen_scan_scoring_contracts.md`
5. `mcp_ucx/docs/policies/MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md`

Update existing spec:

1. `mcp_ucx/docs/specs/SPEC-008_mcp_output_schema_contracts.md`
   - Extend with any new schema ids introduced by M2 and M3 command implementation.

Update existing docs:

1. `mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md`
2. `mcp_ucx/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
3. `mcp_ucx/docs/architecture/MCP_OPERATOR_RUNBOOK.md`
4. `mcp_ucx/docs/README.md`
5. `mcp_ucx/docs/ROADMAP.md`
6. `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.0.0.md` (or next release changelog file)

Documentation migration rules:

1. Remove phrasing that positions MCP as compatibility wrapper for UCX_v1.
2. Use MCP-native command names and flow semantics.
3. Keep a single MCP cutover/archive policy page for historical mapping.
4. Treat naming policy as frozen after M1 and allow only additive documentation updates afterward.

## 6. Phase Plan

### Phase M1: Stabilize command contracts

1. Finalize CLI argument contracts for all missing commands except autopilot.
2. Freeze command names and artifact naming patterns.
3. Add and refresh CLI contract tests.
4. Publish baseline `MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md` and lock naming semantics for downstream phases.

Exit criteria:

1. No placeholder command paths remain for in-scope commands.
2. CLI reference can be generated from runtime contracts without manual overrides.
3. Unit tests for command parsing and dispatch pass for all implemented in-scope commands.
4. Baseline `MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md` is published and referenced from `mcp_ucx/docs/README.md`.

### Phase M2: Implement fix and remediation runtime

1. Implement `validate-fix` as source-protected validation-derived artifact creator.
2. Implement `remediate` report generation and report discovery.
3. Implement `remediate-fix` apply pipeline to produce `_remediated` outputs.

Exit criteria:

1. End-to-end source -> validation copy -> remediated copy flow passes integration tests.
2. Source documents remain unchanged unless explicit non-protected mode is introduced.
3. Protected-mode verification includes checksum equality for source files before and after fix commands.

### Phase M3: Implement operational controls and diagnostics

1. Add validation modes (`--tier1-only`, `--strict`, format and exit semantics).
2. Add review mode and session controls and cleanup operations.
3. Implement `prescreen`, `scan`, and `scoring` command group.

Exit criteria:

1. All commands produce deterministic output contracts with tests.
2. Operator runbook includes normal, degraded, and error scenarios.
3. Exit code behavior is documented and validated for success, validation-fail, and runtime-error paths.

### Phase M4: Documentation cutover to MCP-first

1. Publish new general description and flow docs.
2. Update CLI, runtime, runbook, and spec docs for implemented command set.
3. Update cutover and archive policy and roadmap milestones using locked M1 naming semantics.

Exit criteria:

1. MCP docs are complete for in-scope commands and flows.
2. No active runtime docs require UCX_v1 references to be understandable.
3. Documentation index links resolve and pass link consistency checks.

### Phase M5: UCX_v1 detachment gate

1. Run reference scans to ensure no active MCP runtime docs rely on UCX_v1 language.
2. Confirm archive-only notes are isolated to cutover/archive policy docs.
3. Publish release readiness summary for migration closure.

Exit criteria:

1. MCP is independently documented and operable.
2. UCX_v1 is documented as archived and non-authoritative for MCP runtime behavior.

## 7. Acceptance Thresholds

Pass and fail determination is driven only by this section and Section 7.1 command evidence.

1. Command implementation threshold: 100% of in-scope commands in Section 4 return implemented behavior (no placeholder response text).
2. Test threshold: all new and modified MCP tests pass with 0 failures for targeted unit and integration suites listed in Section 5.2.
3. Schema threshold: all in-scope command JSON outputs conform to SPEC-008, SPEC-009, or SPEC-010 contracts.
4. Documentation threshold: 0 unresolved internal links in updated MCP docs scope.
5. Independence threshold: 0 operational legacy-archive dependency references outside `MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md`.

## 7.1 Validation Evidence Command Set

Use the following command set as the authoritative execution proof for migration acceptance:

1. Unit and integration tests:
   - `pytest mcp_ucx/tests/unit/test_cli_main.py`
   - `pytest mcp_ucx/tests/unit/test_validation_runner.py`
   - `pytest mcp_ucx/tests/unit/test_remediation_runner.py`
   - `pytest mcp_ucx/tests/unit/test_prescreening.py`
   - `pytest mcp_ucx/tests/unit/test_scoring_cli.py`
   - `pytest mcp_ucx/tests/integration/test_migration_flows.py`
2. Command surface verification:
   - `mcp --help`
   - `mcp <command> --help` for each in-scope command in Section 4
3. Documentation and policy verification:
   - `python scripts/validate_doc_links.py --root mcp/docs --include "*.md" --fail-on-broken`
   - `rg -n "UCX_v1|UCX v1|ucx_v1|UCX" mcp/docs --glob "*.md" --glob "!mcp_ucx/docs/policies/MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md"`

Required evidence artifacts:

1. Test output logs with command lines and exit codes.
2. Command help snapshots for each in-scope command.
3. Link-check result report for updated docs scope.
4. UCX_v1 reference scan report with file-level findings.
5. Schema conformance evidence for command outputs mapped to SPEC-008, SPEC-009, and SPEC-010.

## 8. Acceptance Matrix

This matrix is a qualitative coverage checklist and does not replace Section 7 thresholds.

### 8.1 Functional acceptance

1. All in-scope commands execute and return documented outputs.
2. Fix flow commands produce expected derived artifacts and reports.
3. Prescreen, scan, and scoring commands execute with deterministic output schema.

### 8.2 Documentation acceptance

1. New framework overview and operational flow docs are published.
2. CLI reference and runbook cover all implemented commands.
3. Specs include remediation and fix and diagnostics contracts.

### 8.3 Independence acceptance

1. MCP docs do not require legacy archive docs for runtime execution.
2. UCX_v1 references are isolated to an archive and cutover document.
3. MCP docs identify MCP as canonical source of truth.

## 9. Execution Checklist

1. Create implementation branches for each phase.
2. Implement P0 commands and tests.
3. Implement P1 controls and tests.
4. Implement P2 diagnostics commands and tests.
5. Author and update MCP docs listed in Workstream C.
6. Run Section 7.1 validation evidence command set and collect artifacts.
7. Run documentation consistency and link checks.
8. Publish migration completion report with mandatory evidence bundle.

## 10. Risks and Controls

1. Risk: command-surface expansion causes inconsistent behavior.
   - Control: strict CLI contract tests and schema-based output validation.
2. Risk: remediation applies unsafe edits.
   - Control: source-protected default and explicit apply semantics on copies only.
3. Risk: docs drift from runtime after migration.
   - Control: release gate requiring CLI-doc parity checks before merge.

## 11. Ownership and Accountability

1. Workstream A owner: MCP runtime maintainer.
2. Workstream B owner: MCP test and quality maintainer.
3. Workstream C owner: MCP documentation maintainer.
4. Phase exit approval owner: MCP release approver.
5. Active release tracking record: `mcp_ucx/docs/plans/IPLAN-003_RELEASE_TRACKING.yaml`.
6. Release tracking record minimum fields: `release_id`, `iplan_id`, `phase`, `status`, `workstream_a_owner`, `workstream_b_owner`, `workstream_c_owner`, `release_approver`, `evidence_bundle_path`, `last_updated`.
7. Named assignees for items 1-4 must be recorded in the active release tracking record before M2 starts.
8. The release tracking record must be updated at each phase transition and before final closure sign-off.
9. Each phase exit requires explicit sign-off from workstream owner and release approver with linked evidence artifacts from Section 7.1.

## 12. Deliverables

1. Runtime: all in-scope missing capabilities implemented.
2. Tests: unit and integration coverage for all new commands.
3. Documentation: MCP-first overview, flows, specs, runbook, roadmap, changelog.
4. Governance: cutover and archive policy for UCX_v1 references.
5. Closure artifact: `mcp_ucx/docs/plans/IPLAN-003_MIGRATION_CLOSURE_REPORT.md`.

## 12.1 Closure Report Minimum Contents

1. Scope summary with in-scope command completion matrix.
2. Test execution table with command, result, and evidence path.
3. Schema conformance summary for SPEC-008, SPEC-009, and SPEC-010.
4. Documentation link-check summary and unresolved-link count.
5. Legacy-archive scan summary confirming archive-only references.
6. Final sign-off section with workstream owner approvals and release approver approval.
