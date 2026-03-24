# PLAN-011: UCX Reporting Standards

**Document ID**: PLAN-011_ucx_reporting_standards
**Created**: 2026-03-20
**Updated**: 2026-03-21
**Status**: Revised (v7)
**Target Version**: UCX v1.22.0
**Related Plans**: PLAN-009_prd_creation.md, PLAN-010_prd_validation.md, PLAN-012_prd_derived_artifact_flow.md

---

## Objective

Establish UCX-wide reporting standards across all supported SSD layers with deterministic behavior across four report channels:

1. Versioned validation report (`{DOC_TYPE}-XX.UCX_validation_report_vNNN.md`)
2. Versioned review report (`{DOC_TYPE}-XX.UCX_review_report_vNNN.md`)
3. Versioned remediation report (`{DOC_TYPE}-XX.UCX_remediation_report_vNNN.md`)
4. Pre-commit report (`.precommit_validation_report.md`) generated only by commit-time validation

This standard must apply consistently to BRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TSPEC, and future layer validators integrated into UCX. PRD is now a documented transition case: PLAN-012 introduces a stage-aware derived-artifact workflow whose validation-report naming and lineage fields refine the generic rules in this plan.

Naming rule:
- `{DOC_TYPE}-XX` is exactly the document ID from the parent artifact folder (for example: `BRD-01`, `PRD-01`, `EARS-03`).

---

## UCX Architecture Context

UCX provides three document lifecycle phases and one commit-time guardrail path relevant to this plan:

| Path | Command | Purpose | PLAN-011 Role |
|------|---------|---------|---------------|
| UCC | `ucx create` | Create artifacts | Must never emit pre-commit report |
| UCR | `ucx validate` / `ucx review` | Structural + contextual checks | Must emit versioned UCX reports across all layers |
| UCRem | `ucx remediate` | Guided corrections | Must emit versioned remediation report |
| Pre-commit guardrail | `ucx validate --precommit` (hook path) | Commit-time fast gate | Must be sole emitter of `.precommit_validation_report.md` |

PLAN-011 scope is reporting-system normalization only. It does not alter artifact content-generation prompts/templates defined in layer-specific plans.

PRD exception boundary:
- Current PRD runtime behavior in v1.21.6 remains source-protected and report-only.
- Planned v1.22.0 PRD work in PLAN-012 replaces the generic validation filename with `PRD-01_validation_report.md` and adds derived-copy lineage requirements.
- Review and remediation report versioning remain under PLAN-011 unless a future cross-layer revision generalizes the PRD pattern.

---

## Current State and Gap

### BRD Behavior (reference implementation)

| Capability | BRD Status |
|-----------|------------|
| Versioned validation report | Implemented |
| Versioned review report | Implemented |
| Versioned remediation report | Implemented |
| Pre-commit report generated on git commit | Implemented |

### UCX-Wide Behavior (current)

| Capability | Cross-Layer Status | Gap |
|-----------|------------|-----|
| Versioned validation report | Partial/inconsistent | Missing deterministic generation path in all layers |
| Versioned review report | Partial/inconsistent | Missing deterministic naming/versioning in all layers |
| Versioned remediation report | Partial/inconsistent | Missing deterministic naming/versioning in all layers |
| Pre-commit report generated on git commit only | Not globally enforced | Generated during non-commit flows in some paths |

Gap summary:
- Report emission policy is not centralized across all UCX call paths.
- Versioning logic is not explicitly collision-safe for concurrent runs.
- Pre-commit and standard reporting semantics are not strictly separated.
- Report schema fields vary by module and are not uniformly enforced.
- Cross-layer review policy is not documented as a single UCX standard.

---

## Scope

### In Scope

- UCX reporting behavior in create/validate/review/remediate paths across all supported layers
- Report path policy, naming policy, and version increment policy for all layer artifacts
- Separation of commit-time `.precommit_validation_report.md` from versioned reports
- Regression tests for BRD baseline and representative downstream layers (PRD/EARS/SYS/REQ minimum)
- CLI behavior updates required to keep report generation deterministic
- Standard report schema and validation rules for all UCX reports

### Out of Scope

- Rewriting report content templates across all layers
- Introducing report types beyond UCX_validation/UCX_review/UCX_remediation/pre-commit
- Changes to external CI pipelines outside UCX repository
- Generalizing PRD derived-copy naming to all layers before PLAN-012 is implemented and validated

---

## PRD Exception Handling

PLAN-012 creates a PRD-specific exception to the generic validation naming rule in this plan.

Interim alignment rules:
- PRD validation stays report-only.
- PRD validation target filename becomes `PRD-01_validation_report.md` when PLAN-012 is implemented.
- PRD review and remediation reports remain versioned report families with lineage metadata identifying the `_validation` source artifact.
- `.precommit_validation_report.md` remains reserved for commit-time diagnostics only and must not be reused as the standard PRD validation artifact.

---

## Target Reporting Contract

### 1) Validation Report (versioned)

**File Pattern**: `{DOC_TYPE}-XX.UCX_validation_report_vNNN.md`

PRD note:
- PLAN-012 defines `PRD-01_validation_report.md` as a PRD-specific validation artifact for the derived-copy workflow.
- Other layers continue using the generic naming contract until a broader stage-aware standard is approved.

**Generation Trigger**:
- `ucx validate <doc_type> <path>`
- optional post-create validation when explicitly requested by create flow flags

**Rules**:
- Must include YAML frontmatter
- Must include tier counts and score fields
- Must increment `vNNN` based on existing files in directory
- Must be script-based only (no LLM dependency): structure checks, element-ID checks, metadata checks, quality gates, and deterministic rule validation

### 2) Review Report (versioned)

**File Pattern**: `{DOC_TYPE}-XX.UCX_review_report_vNNN.md`

**Generation Trigger**:
- `ucx review <doc_type> <path>`

**Rules**:
- Must include weighted score summary and findings counts
- Must increment `vNNN`
- Must be LLM-based content review for semantic and cross-layer compliance
- Must enforce universal SSD layer discipline: each artifact must align to its immediate upper-layer sources, stay focused on its own layer requirements, and avoid drifting into other layer scopes
- May include implementation guidance for the immediate next layer when that guidance supports downstream artifact creation without violating current-layer scope
- Example for PRD: align with BRD, focus on product requirements, and avoid EARS/ADR scope drift
- Example for EARS: align with PRD stories/requirements, focus on formal EARS requirement syntax, and avoid BDD scenario authoring scope
- Example for BDD: align with EARS statements, focus on executable behavior scenarios, and avoid architecture-decision scope

### 3) Remediation Report (versioned)

**File Pattern**: `{DOC_TYPE}-XX.UCX_remediation_report_vNNN.md`

**Generation Trigger**:
- `ucx remediate <path>`

**Rules**:
- Must include remediation execution summary
- Must increment `vNNN`

### 4) Pre-commit Report (single file)

**File Pattern**: `.precommit_validation_report.md`

**Generation Trigger**:
- Git pre-commit hook path only (`ucx validate --precommit ...` or hook entrypoint)

**Rules**:
- Must not be emitted by standard validate/review/remediate flows
- Must be overwritten each commit run (single latest state)
- Must contain bounded summary fields (`Status`, `Errors`, `Warnings` at minimum)

### 5) Standard Report Schema (all versioned reports)

Required frontmatter fields:
- `title`
- `tags`
- `custom_fields`

Required `custom_fields` keys:
- `report_type` (`validation|review|remediation`)
- `source_artifact_type`
- `source_artifact_id`
- `status`
- `report_version`
- `validator_or_reviewer`
- `generated_at`

Additional required metrics by report type:
- Validation: `tier1_errors`, `tier1_warnings`, `tier2_warnings`, `checks_run`
- Review: `weighted_score`, `p0_findings`, `p1_findings`, `p2_findings`, `personas_applied`
- Remediation: `findings_addressed`, `changes_applied`, `remaining_findings`

---

## Architecture Changes

### A. Reporting Policy Layer

Add an explicit report emission policy resolver used by all reporting paths.

Proposed policy enum:
- `ReportMode.STANDARD`: emits versioned report files only
- `ReportMode.PRECOMMIT`: emits `.precommit_validation_report.md` only

Report type semantics:
- `UCX_validation_report`: script-based deterministic validation output
- `UCX_review_report`: LLM-based content and cross-layer compliance review output (general rule for all layers: align to upper layer, focus on current layer, optionally guide next layer)
- `UCX_remediation_report`: remediation actions and outcomes after validation/review findings

Severity standard (review/remediation):
- `P0`: blocking; must be fixed before downstream progression
- `P1`: high priority; fix required before release
- `P2`: advisory; schedule via backlog

### B. Shared Report Naming Utility

Consolidate naming/version logic in common utility.

Expected responsibilities:
- Resolve source artifact ID from document path/content
- Detect next report version (`vNNN`)
- Return deterministic output file name by report type and mode
- Allocate version atomically to avoid concurrent writer collisions

Concurrency controls:
- Use write-to-temp + atomic rename for report writes
- If target version already exists at write time, recompute next version and retry
- Keep retry loop bounded (max 3 retries) and fail with explicit error after limit

### C. Call-Site Normalization

Ensure each command path passes correct mode for every supported `doc_type`:
- `create`: `STANDARD` (no precommit file)
- `validate` default: `STANDARD`
- `validate --precommit`: `PRECOMMIT`
- `review`: `STANDARD`
- `remediate`: `STANDARD`

### D. Naming Enforcement

- Keep existing BRD report filenames unchanged
- Do not support legacy report-name aliases for UCX reporting

Canonical naming policy:
- Read path: canonical `UCX_*` report patterns only
- Write path: canonical `UCX_*` report patterns only
- Version path: compute next version from canonical `UCX_*` files only

Doc-type resolution policy:
- Resolve `{DOC_TYPE}-XX` from parent artifact folder ID only
- Reject write if folder ID and parsed document ID are mismatched

---

## Implementation Phases

### Phase 1: Discovery and Baseline Lock

**Goal**: Identify all report write call sites and freeze expected behavior with tests.

Tasks:
1. Enumerate report writer functions and CLI/API call sites
2. Document BRD baseline expectations and UCX-wide expected parity
3. Add failing tests for parity and pre-commit-only rule across representative layers

Deliverables:
- Report call-site inventory document in code comments/tests
- Initial failing tests committed
- Baseline matrix for BRD/PRD/EARS/SYS/REQ report outputs by command path

### Phase 2: Core Refactor

**Goal**: Implement mode-aware reporting in shared utilities.

Tasks:
1. Implement `ReportMode` policy and centralized naming/version resolver
2. Update validators/review/remediation writers across supported doc types to use resolver
3. Prevent pre-commit report writes in non-precommit mode
4. Enforce required report schema fields through shared report-schema validator

Deliverables:
- Unified reporting helper in `ucx/validators/common/` or `ucx/reporting/`
- Updated writer call paths
- Deterministic file-write behavior with collision retry handling

### Phase 3: Cross-Layer Parity and Regression Protection

**Goal**: Make cross-layer behavior match BRD reference model and keep BRD unchanged.

Tasks:
1. Validate versioned report generation for validate/review/remediate across representative layers
2. Validate pre-commit single-file generation only in precommit mode for representative layers
3. Add BRD regression tests for unchanged behavior

Deliverables:
- Passing cross-layer parity tests
- Passing BRD regression tests

### Phase 4: Documentation and CLI Help Sync

**Goal**: Align user-facing docs and command help.

Tasks:
1. Update CLI help text for reporting mode semantics
2. Update reporting docs with file patterns and triggers
3. Add migration note for old non-canonical report naming behavior

Deliverables:
- Updated docs under UCX docs
- Release note fragment for v1.22.0
- Operator note describing when to use `--precommit` outside hooks for diagnostics

---

## Proposed File Touchpoints

Likely modules (confirm in Phase 1):

- `UCX/ucx/cli/main.py`
- `UCX/ucx/api/creation.py`
- `UCX/ucx/api/review.py`
- `UCX/ucx/api/remediation.py`
- `UCX/ucx/validators/common/*` (shared naming/policy utilities)
- `UCX/ucx/validators/*` (layer-specific reporting call sites)
- `UCX/tests/*` (new and updated tests)

---

## Acceptance Criteria

1. Running `ucx validate <doc_type> <path>` creates/updates only the standard validation artifact for that layer. For PRD, PLAN-012 defines the planned exception `PRD-01_validation_report.md`; other supported layers use `{DOC_TYPE}-XX.UCX_validation_report_vNNN.md`.
2. Running `ucx review <doc_type> <path>` creates/updates only `{DOC_TYPE}-XX.UCX_review_report_vNNN.md` for supported layers.
3. Running `ucx remediate <path>` creates/updates only `{DOC_TYPE}-XX.UCX_remediation_report_vNNN.md` for supported layers.
4. Running pre-commit mode creates/updates only `.precommit_validation_report.md`.
5. Standard validate/review/remediate commands do not emit `.precommit_validation_report.md`.
6. Existing BRD report naming and behavior remains unchanged.
7. Tests cover BRD baseline and representative downstream layers for all four channels.
8. Validation reports include required frontmatter and required score/count fields (`status`, tier counts, and score fields).
9. Review/remediation reports include required frontmatter and required summary fields (weighted score/findings for review, execution summary for remediation).
10. Version increments are collision-safe under concurrent executions.
11. Validation path remains script-based and deterministic (no LLM call required).
12. Review path remains LLM-based and enforces semantic/cross-layer compliance for all layers.
13. Review confirms each layer artifact aligns with its upper layer and remains scoped to current-layer requirements, while permitting bounded guidance for next-layer creation.
14. Non-canonical report names are rejected for new writes in all supported layers.

---

## Complexity and Resource Profile

### Complexity (1-5)

- **Implementation Complexity**: 3/5
  - Rationale: Multiple call sites and behavior gating, no major architectural rewrite.

### Resource Requirements

- CPU: low to moderate (unit/integration test execution)
- Memory: low
- Storage: low (additional report files and tests)
- Network: none required for local reporting tests

---

## Failure Modes and Controls

| Failure Mode | Detection | Control |
|-------------|-----------|---------|
| Pre-commit report emitted during standard validation | Unit/integration tests on validate path | Mode gate in writer utility |
| Incorrect version increment (`vNNN`) | Version resolver tests | Parse existing files and compute max+1 |
| BRD naming regression | BRD regression tests | Snapshot/expectation tests |
| Report missing required schema fields | Schema/content tests | Shared report-schema validator |
| Remediation report naming drift | Remediation tests | Canonical naming utility with strict pattern checks |
| Folder document ID mismatch with report name | Unit/integration tests | Doc-type resolution guard with hard-fail |

---

## Verification Plan

### Test Categories

1. Unit tests for naming/version resolver
2. Unit tests for report mode policy
3. Integration tests for CLI flows:
  - `validate <doc_type>`
  - `review <doc_type>`
  - `remediate <doc_type>`
   - `validate --precommit`
4. Regression tests for BRD report outputs
5. Git hook integration tests (real pre-commit path) to verify `.precommit_validation_report.md` is emitted only through commit-time flow
6. Concurrent execution tests for version allocation and collision retry behavior
7. Cross-layer policy tests for upper-layer alignment and in-layer scope enforcement

### Pass Conditions

- All new tests pass
- Existing UCX test suite passes
- Manual smoke run confirms expected file outputs in BRD/PRD/EARS/SYS/REQ sample directories

---

## Rollout Strategy

1. Merge behind deterministic tests (no feature flag required)
2. Release in UCX v1.22.0
3. Run one-time migration cleanup for stale `.precommit_validation_report.md` files generated by non-commit flows
4. Monitor first cross-layer runs for report file outputs
5. If mismatch occurs, revert to previous writer path and preserve generated reports

Rollout exit criteria:
- Command-path report outputs match acceptance criteria in one clean-room run across representative layers
- BRD regression tests remain green with unchanged filenames
- No standard-mode command emits `.precommit_validation_report.md`

Migration cleanup policy:
- Do not delete BRD historical report artifacts
- Remove or regenerate stale pre-commit artifacts only when provenance indicates non-commit generation
- Record cleanup actions in release notes for audit traceability

---

## Execution Checklist

- [x] Phase 1 complete: call-site inventory + failing tests
- [x] Phase 2 complete: mode-aware shared reporter utilities
- [x] Phase 3 complete: cross-layer parity + BRD regression green
- [x] Phase 4 complete: docs and CLI help synchronized
- [x] Final validation in sample BRD and PRD directories

---

## Notes

- This plan formalizes UCX reporting standards across supported SSD layers.
- The authoritative pre-commit behavior is commit-time generation only.
- Any report generation outside this contract is treated as a defect.
- Manual `--precommit` invocation is permitted for diagnostics/tests but remains explicitly precommit mode (never standard mode).

---

## Change History

| Date | Version | Change |
|------|---------|--------|
| 2026-03-20 | v6 | Moved preflight to shared AI clients so every LLM request runs a UTC-date availability probe before main prompt execution. |
| 2026-03-20 | v5 | Added PRD creation preflight sequence in UCC: first probe LLM with a current UTC date request and validate response, then proceed to large PRD prompt only when probe passes. |
| 2026-03-20 | v4 | Completed UCX reporting standardization and cross-layer parity baseline. |
