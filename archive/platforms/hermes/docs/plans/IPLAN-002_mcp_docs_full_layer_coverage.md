# IPLAN-002: MCP Docs Full Layer Coverage Plan

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

**Phase**: Cross-phase
**Status**: Completed
**Created**: 2026-03-24
**Timezone**: America/New_York
**Issues**: N/A
**Epic**: N/A
**Applies Before**: Next documentation release cycle

---

## 1. Purpose

Define and execute a complete documentation set for all MCP documentation layers in `mcp/docs` so runtime behavior, source contracts, and operational workflows are consistently documented and verifiable.

Implementation complexity: 4/5.

---

## 2. Problem Statement

Observed error class:

- Workflow interpretation drift between:
  - Skill-level BRD generation guidance (`doc-brd`, `doc-brd-autopilot`)
  - MCP CLI/runtime behavior (`create-build`, `context_builder`)
  - Existing canonical contracts (`SPEC-001..004`)

Primary gap:

- `mcp/docs` has strong contract specs, but lacks a complete, layered, operator-facing documentation set that bridges source-input expectations to actual runtime behavior.

Current baseline in `mcp/docs`:

- `specs/`: 4 canonical specs
- `policies/`: 1 policy
- `architecture/`: 1 guide
- `plans/`: implementation and release artifacts

---

## 3. Scope

In scope:

- Full documentation coverage across defined MCP documentation layers (L0-L9 below).
- Canonical cross-linking between architecture, policies, specs, and operational runbooks.
- Explicit documentation for source ingestion behavior and BRD creation flow constraints.
- Drift controls for docs-to-code alignment.
- Reconciliation of existing `mcp/docs` artifacts into explicit states: retain, update, deprecate, split.
- Implemented-state documentation only for this cycle; future-state behavior captured separately.

Out of scope:

- Refactoring runtime implementation behavior.
- Rewriting external project skills under `.claude/skills`.
- Large-scale renaming of existing canonical SPEC IDs.

Boundary rule for this cycle:

- Any behavior not currently implemented in `mcp_ucx/src/mcp_server` must be documented only in a clearly labeled "Future State" subsection.

---

## 4. Documentation Layer Model (Target)

| Layer | Name | Required Artifact | Target Location |
|---|---|---|---|
| L0 | Navigation and Inventory | Docs index and map | `mcp_ucx/docs/README.md` |
| L1 | Architecture Overview | Runtime architecture and boundaries | `mcp_ucx/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md` |
| L2 | CLI and Tool Surface | Command contracts and examples | `mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md` |
| L3 | Source Input Contracts | Source modes, precedence, and constraints | `mcp_ucx/docs/specs/SPEC-005_mcp_source_input_ingestion_contracts.md` |
| L4 | Creation Flow Contracts | `init` + `create-build` end-to-end contracts | `mcp_ucx/docs/specs/SPEC-006_mcp_creation_flow_operational_contracts.md` |
| L5 | Review/Remediation Ops | `review-build` and remediation handoff operations | `mcp_ucx/docs/specs/SPEC-007_mcp_review_remediation_operational_contracts.md` |
| L6 | Policy Layer | Versioning, deprecation, compatibility policy | `mcp_ucx/docs/policies/DOC_COMPATIBILITY_AND_DEPRECATION_POLICY.md` |
| L7 | Validation and Quality Gates | Documentation QA and release gates | `mcp_ucx/docs/policies/DOC_QUALITY_GATES.md` |
| L8 | Runbooks | Operator runbooks and troubleshooting | `mcp_ucx/docs/architecture/MCP_OPERATOR_RUNBOOK.md` |
| L9 | Traceability and Audit | Coverage matrix and evidence checklist | `mcp_ucx/docs/plans/DOC-COVERAGE-MATRIX-001_mcp_layers.md` |

---

## 5. Deliverables

### D1: Navigation Foundation

- Create `mcp_ucx/docs/README.md` with:
  - Layer map (L0-L9)
  - Canonical source-of-truth table
  - Quick links to all specs/policies/runbooks
  - Document reconciliation index with status tags per file

Acceptance criteria:

- Every active canonical artifact is linked from README.
- Every non-canonical artifact is listed in reconciliation index with one status: retain, update, deprecate, split.

### D2: Runtime + CLI Docs

- Create:
  - `mcp_ucx/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
  - `mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md`

Acceptance criteria:

- `create-build`, `review-build`, `init` parameter contracts match `mcp_ucx/src/mcp_server/cli/main.py` exactly.
- Include explicit statement for current behavior: direct markdown source ingestion is not implemented in `create-build`.

### D3: New Canonical Specs for Source and Creation Ops

- Create:
  - `SPEC-005_mcp_source_input_ingestion_contracts.md`
  - `SPEC-006_mcp_creation_flow_operational_contracts.md`
  - `SPEC-007_mcp_review_remediation_operational_contracts.md`

Acceptance criteria:

- Source precedence, conflict semantics, and sections-json contract are defined with failure modes.
- Each spec has: purpose, scope, boundaries, normative rules, failure modes, validation evidence requirements.

### D4: Policy Layer Completion

- Create:
  - `mcp_ucx/docs/policies/DOC_COMPATIBILITY_AND_DEPRECATION_POLICY.md`
  - `mcp_ucx/docs/policies/DOC_QUALITY_GATES.md`

Acceptance criteria:

- Deprecation policy includes explicit write/read compatibility behavior for legacy artifacts.
- Quality gates include blocking criteria for docs/code mismatch.

### D5: Runbook + Coverage Matrix

- Create:
  - `mcp_ucx/docs/architecture/MCP_OPERATOR_RUNBOOK.md`
  - `mcp_ucx/docs/plans/DOC-COVERAGE-MATRIX-001_mcp_layers.md`

Acceptance criteria:

- Runbook includes BRD creation scenarios:
  - sections-json provided
  - sections-json omitted
  - missing project UCX path (`ProjectSkillsNotFound`)
- Coverage matrix maps each layer to file paths, owner, and validation status.

### D6: Lifecycle and Version Governance

- Create:
  - `mcp_ucx/docs/policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md`

Acceptance criteria:

- Defines version increments by change type (patch/minor/major).
- Defines review triggers for CLI contract, prompt assembly contract, loader/scaffold behavior, and prompt artifact schema changes.
- Defines deprecation sunset rules and required compatibility notes.

---

## 5A. Reconciliation Strategy (Mandatory)

Objective:

- Resolve conflicts between existing docs and implemented runtime behavior before declaring coverage complete.

Reconciliation workflow:

1. Inventory all files under `mcp/docs` into a reconciliation table.
2. For each file, assign one status: retain, update, deprecate, split.
3. For each conflicting statement, record:
   - statement identifier
   - observed conflict
   - selected source of truth
   - resolution rationale
   - action owner
4. Apply updates/deprecations and re-validate cross-links.

Source-of-truth precedence for conflict resolution:

1. Runtime code and tests under `mcp_ucx/src/mcp_server` and `mcp/tests`
2. Canonical specs (`mcp_ucx/docs/specs`)
3. Policies (`mcp_ucx/docs/policies`)
4. Runbooks and architecture guides (`mcp_ucx/docs/architecture`)
5. Plans (`mcp_ucx/docs/plans`)

Required output artifact:

- `mcp_ucx/docs/plans/DOC-RECONCILIATION-LOG-001.md`

Acceptance criteria:

- No unresolved conflicts remain in reconciliation log.
- Every `update`, `deprecate`, or `split` action is completed or explicitly deferred with owner and gate.

---

## 6. Execution Workstreams

### Workstream A: Baseline and Taxonomy

Actions:

- Build complete `mcp/docs` file inventory.
- Define canonical layer ownership map (L0-L9).
- Produce reconciliation table with retain/update/deprecate/split statuses.

Outputs:

- Initial matrix scaffold file.
- Initial reconciliation log.

### Workstream B: Contract Expansion

Actions:

- Draft SPEC-005/006/007.
- Cross-link to SPEC-001..004 and runtime modules.

Outputs:

- New canonical specs with normative clauses.

### Workstream C: Operationalization

Actions:

- Draft runtime architecture and CLI reference.
- Draft operator runbook with deterministic command flows.

Outputs:

- Architecture docs and runbook.

### Workstream D: Governance and Drift Controls

Actions:

- Define docs compatibility and deprecation policy.
- Define doc quality gates and release checks.
- Define lifecycle/version policy and change-trigger mapping.

Outputs:

- Policy docs and gate checklist.

### Workstream E: Verification and Release

Actions:

- Validate every claim against current code paths.
- Complete coverage matrix and release readiness checks.
- Resolve all reconciliation conflicts or log approved deferrals.

Outputs:

- Updated matrix with PASS/FAIL status by layer.
- Reconciliation log with closure status.

---

## 7. Anti-Drift Controls (Mandatory)

1. Code-anchored references

- Every behavioral rule must cite concrete module paths under `mcp_ucx/src/mcp_server`.

2. Contract precedence declaration

- Each operational doc must declare precedence:
  - Runtime code/tests > canonical specs > policy docs > runbooks/architecture > plans.

3. Documentation quality gates

- Fail release if:
  - CLI docs differ from current argparse contract.
  - Source-ingestion behavior in docs differs from runtime implementation.
  - Any spec section lacks failure modes.
  - Any reconciliation conflict remains unresolved.
  - Any layer in coverage matrix has status other than PASS.

4. Change impact checklist

- Any PR touching:
  - `mcp_ucx/src/mcp_server/cli/main.py`
  - `mcp_ucx/src/mcp_server/prompts/context_builder.py`
  - `mcp_ucx/src/mcp_server/review/runner.py`

Must also update:

- CLI reference or relevant SPEC-005/006/007 sections.

5. Enforced gate operations model

- Gate owner roles:
  - Documentation maintainer: executes document checks and reconciliation log updates.
  - Runtime maintainer: verifies code-behavior assertions.
  - Release approver: validates gate outcomes before release.
- Enforcement points:
  - Pull request gate: required checks for docs-impacting changes.
  - Release gate: mandatory PASS review using coverage matrix and reconciliation log.
- Required evidence for gate pass:
  - Updated coverage matrix
  - Updated reconciliation log
  - Checklist attestation in release artifact

---

## 8. Validation Procedure

Validation checks:

- Structural:
  - All target files exist.
  - Cross-links resolve.
- Contract:
  - Source contract statements match code behavior.
  - Command examples align with actual CLI arguments.
- Coverage:
  - Each L0-L9 layer marked PASS in coverage matrix.
- Reconciliation:
  - Conflict log contains zero unresolved conflicts.
  - Every deprecated file has replacement or explicit tombstone rationale.

PASS rubric (release blocking):

| Check | Rule | Pass Condition |
|---|---|---|
| Layer coverage | Required layers L0-L9 complete | 10/10 layers PASS |
| Reconciliation closure | Conflict backlog | 0 unresolved conflicts |
| Contract alignment | CLI + source ingestion + review behavior | 0 critical mismatches |
| Cross-link integrity | Internal documentation links | 0 broken links |
| Ownership completeness | Layer owner assignment | 100% assigned |

Evidence artifacts:

- `mcp_ucx/docs/plans/DOC-COVERAGE-MATRIX-001_mcp_layers.md`
- `mcp_ucx/docs/plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md`
- `mcp_ucx/docs/plans/DOC-RECONCILIATION-LOG-001.md`

---

## 9. Risks and Failure Modes

| Risk | Severity | Failure Mode | Mitigation |
|---|---|---|---|
| Spec drift | High | Runtime changes not reflected in docs | Gate on impacted-module checklist |
| Scope creep | Medium | Plan expands beyond `mcp/docs` | Enforce in-scope boundaries section |
| Ambiguous source semantics | High | Conflicting guidance for BRD source ingestion | Canonicalize in SPEC-005 + CLI reference |
| Partial layer completion | Medium | Missing operational docs despite specs | L0-L9 matrix must be fully PASS before closure |

---

## 10. Resource Requirements

- Contributors:
  - 1 primary documentation maintainer
  - 1 runtime maintainer reviewer
- Tooling:
  - existing repository tooling only
- Storage/network:
  - negligible additional requirements

---

## 11. Definition of Done

Done when all are true:

- L0-L9 target artifacts exist in `mcp/docs`.
- Coverage matrix reports PASS for every layer (10/10).
- BRD creation behavior is unambiguous and code-aligned across specs/runbooks/CLI docs.
- Anti-drift gates are documented and applied in release checks.
- Reconciliation log has zero unresolved conflicts.
- Lifecycle/version policy is approved and linked from docs README.

---

## 12. Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-03-24 | AI Collaboration | Initial full-layer documentation plan for `mcp/docs`. |
| 1.1 | 2026-03-24 | AI Collaboration | Added reconciliation workflow, operational gate model, explicit PASS rubric, and lifecycle/version governance. |
| 1.2 | 2026-03-24 | AI Collaboration | Implemented initial L0-L9 artifact set and established reconciliation, coverage, and compliance report files. |
| 1.3 | 2026-03-24 | AI Collaboration | Executed verification checks (artifact existence, internal link integrity, and CLI contract parity signals) and closed plan status to Completed. |
