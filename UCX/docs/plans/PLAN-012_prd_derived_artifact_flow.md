# PLAN-012: PRD Derived Artifact Flow

**Document ID**: PLAN-012_prd_derived_artifact_flow
**Created**: 2026-03-21
**Updated**: 2026-03-21
**Status**: Revised (v2)
**Target Version**: UCX v1.22.0
**Related Plans**: PLAN-009_prd_creation.md, PLAN-010_prd_validation.md, PLAN-011_ucx_reporting_standards.md

---

## Objective

Implement a PRD-specific derived-artifact workflow that preserves the canonical source PRD as immutable while generating report artifacts and copy-based document variants for validation fixes and remediation fixes.

This plan introduces a deterministic six-stage PRD flow:

1. Create canonical source PRD
2. Generate validation report only
3. Generate `_validation` PRD copy with validation fixes applied
4. Generate review report against `_validation` copy
5. Generate remediation report against `_validation` copy
6. Generate `_remediated` PRD copy with remediation fixes applied

The purpose is auditability, repeatability, and isolation of each transformation stage.

Runtime boundary:

- Current released behavior in v1.21.6 is limited to source-protected, report-only validation.
- Fixed PRD validation report naming, derived copy commands, and stage-aware pre-commit checks are planned work for v1.22.0.
- Documentation must distinguish current runtime behavior from this target-state plan.

---

## Problem Statement

Current UCX PRD processing conflates analysis, fix generation, and source modification responsibilities in ways that make audit reconstruction difficult.

Observed gaps:

- Validation and fix logic historically assumed in-place mutation paths
- Review and remediation outputs are not explicitly anchored to immutable intermediate document variants
- There is no formal lifecycle contract for derived PRD artifacts
- Pre-commit validation can become overloaded if it attempts to duplicate full validation behavior instead of checking artifact presence and consistency

Required outcome:

- Source PRD remains untouched after `ucx create`
- Every subsequent stage emits either a report artifact or a derived PRD artifact
- The relationship between source, validation-fixed, and remediated PRDs is explicit and machine-checkable

---

## Target PRD Workflow

### Stage 1: Create Canonical Source PRD

**Command**:
- `ucx create prd ...`

**Output**:
- Canonical source PRD only

**Example**:
- `PRD-01_platform_architecture.md`

**Rules**:
- Source PRD is the canonical authored artifact
- No derived postfix in filename
- `custom_fields.development_status: active`
- `custom_fields.processing_stage: source`

---

### Stage 2: Validation Report

**Command**:
- `ucx validate prd <source-prd>`

**Output**:
- Validation report only

**Required filename**:
- `PRD-01_validation_report.md`

**Rules**:
- Validation reads the canonical source PRD
- Validation must not modify the source PRD
- Validation report is deterministic, script-based, and non-LLM
- This stage documents findings and candidate deterministic fixes only

**Required report metadata**:

```yaml
custom_fields:
  report_type: validation
  source_artifact_id: PRD-01
  source_artifact_file: PRD-01_platform_architecture.md
  source_processing_stage: source
```

---

### Stage 3: Validation Fix Copy

**Command (new)**:
- `ucx validate-fix prd <source-prd> --report PRD-01_validation_report.md`

**Output**:
- Derived validation-fixed PRD copy

**Required filename**:
- `PRD-01_platform_architecture_validation.md`

**Rules**:
- Input is canonical source PRD + validation report
- Output is a new document copy with validation fixes applied
- Source PRD remains untouched
- Derived document keeps the same `doc_id` and `version` as the source PRD
- Derived document uses same `status` as source unless explicitly overridden
- Metadata must record both lifecycle and processing stage separately

**Required metadata**:

```yaml
custom_fields:
  development_status: active
  processing_stage: validation-fixed
  source_doc_id: PRD-01
  source_version: 0.1.0
  derived_from: PRD-01_platform_architecture.md
```

**Rationale**:
- `development_status` remains a lifecycle field
- `processing_stage` represents pipeline state
- Do not overload `development_status` with both `active` and `validation-fixed`

---

### Stage 4: Review Report on Validation-Fixed Copy

**Command**:
- `ucx review prd PRD-01_platform_architecture_validation.md`

**Output**:
- Review report only

**Recommended filename**:
- `PRD-01_validation_review_report_v001.md`

**Rules**:
- Review must run on `_validation` PRD, not on canonical source PRD
- Review remains LLM-based and report-only
- Review report metadata must identify the specific source artifact filename

**Required report metadata**:

```yaml
custom_fields:
  source_artifact_id: PRD-01
  source_artifact_file: PRD-01_platform_architecture_validation.md
  source_processing_stage: validation-fixed
```

---

### Stage 5: Remediation Report on Validation-Fixed Copy

**Command**:
- `ucx remediate prd PRD-01_platform_architecture_validation.md --report <review-report>`

**Output**:
- Remediation report only

**Recommended filename**:
- `PRD-01_validation_remediation_report_v001.md`

**Rules**:
- Remediation must run on `_validation` PRD, not on canonical source PRD
- Remediation remains report-only
- Remediation report must reference both the `_validation` PRD and the review report it consumed

**Required report metadata**:

```yaml
custom_fields:
  report_type: remediation
  source_artifact_id: PRD-01
  source_artifact_file: PRD-01_platform_architecture_validation.md
  source_processing_stage: validation-fixed
  source_review_report: PRD-01_validation_review_report_v001.md
```

---

### Stage 6: Remediation Apply Copy

**Command (new)**:
- `ucx remediate-apply prd PRD-01_platform_architecture_validation.md --report <remediation-report>`

**Output**:
- Derived remediated PRD copy

**Required filename**:
- `PRD-01_platform_architecture_remediated.md`

**Rules**:
- Input is `_validation` PRD + remediation report
- Output is a new `_remediated` copy with remediation fixes applied
- `_validation` PRD remains untouched
- Source PRD remains untouched
- Derived document keeps the same `doc_id` and `version` as the source PRD

**Required metadata**:

```yaml
custom_fields:
  development_status: active
  processing_stage: remediated
  source_doc_id: PRD-01
  source_version: 0.1.0
  derived_from: PRD-01_platform_architecture_validation.md
```

---

## Canonical Artifact Set

For one PRD, the expected artifact set becomes:

| Stage | Artifact Type | Example Filename | Mutates Prior Artifact |
|------|---------------|------------------|------------------------|
| 1 | Source PRD | `PRD-01_platform_architecture.md` | No |
| 2 | Validation report | `PRD-01_validation_report.md` | No |
| 3 | Validation-fixed PRD | `PRD-01_platform_architecture_validation.md` | No |
| 4 | Review report | `PRD-01_validation_review_report_v001.md` | No |
| 5 | Remediation report | `PRD-01_validation_remediation_report_v001.md` | No |
| 6 | Remediated PRD | `PRD-01_platform_architecture_remediated.md` | No |

All prior artifacts remain available for audit and comparison.

### Artifact Discovery Rules

- Each PRD folder must contain exactly one canonical source PRD without a stage suffix.
- `_validation` and `_remediated` suffixes are reserved for UCX-derived copies only.
- `PRD-01_validation_report.md` is reserved for deterministic PRD validation output and must not be reused for review or remediation content.
- Review and remediation reports remain versioned artifacts so repeated analysis does not overwrite prior runs.
- Source-only PRD folders remain valid; downstream artifacts become required only after the corresponding later-stage artifact exists.

---

## Metadata Contract

### Canonical Source PRD

```yaml
custom_fields:
  development_status: active
  processing_stage: source
  source_doc_id: PRD-01
  source_version: 0.1.0
  derived_from: null
```

### Validation-Fixed PRD

```yaml
custom_fields:
  development_status: active
  processing_stage: validation-fixed
  source_doc_id: PRD-01
  source_version: 0.1.0
  derived_from: PRD-01_platform_architecture.md
```

### Remediated PRD

```yaml
custom_fields:
  development_status: active
  processing_stage: remediated
  source_doc_id: PRD-01
  source_version: 0.1.0
  derived_from: PRD-01_platform_architecture_validation.md
```

### Required Rule

Do not encode processing stage into `version` or `doc_id`.

Do not overload `development_status` with multiple meanings.

---

## Revision History Contract

Derived copies must append explicit provenance rows while preserving the source semantic version value.

Example rows:

| Version | Date | Author | Changes Made |
|---------|------|--------|--------------|
| 0.1.0 | 2026-03-21T00:00:00Z | UCX Validation Fixer | Derived validation-fixed copy from `PRD-01_platform_architecture.md` using `PRD-01_validation_report.md` |
| 0.1.0 | 2026-03-21T00:00:00Z | UCX Remediation Apply | Derived remediated copy from `PRD-01_platform_architecture_validation.md` using remediation report |

This keeps semantic version stable while documenting pipeline provenance.

---

## Pre-commit Role

Git pre-commit must **not** duplicate full validation functionality.

### Pre-commit Scope

Pre-commit should perform **availability and consistency checks only**.

### Required Checks

For PRD artifact folders under this flow, pre-commit must verify:

1. Canonical source PRD exists
2. Validation report exists if `_validation` artifact exists
3. `_validation` PRD exists if review/remediation artifacts exist
4. Remediation report exists if `_remediated` artifact exists
5. `doc_id` matches across source, `_validation`, and `_remediated`
6. `version` matches across source, `_validation`, and `_remediated`
7. `processing_stage` values are correct for each artifact
8. `derived_from` points to the correct prior artifact

### Explicit Non-Goals for Pre-commit

Pre-commit must not:

- rerun full PRD validation logic
- rerun LLM review logic
- regenerate reports
- apply fixes
- compare semantic content quality beyond artifact consistency

### Pre-commit Failure Examples

- `_validation` file exists but `PRD-01_validation_report.md` is missing
- `_remediated` file exists but remediation report is missing
- `_validation` file version differs from source version
- `_remediated` file has `processing_stage: validation-fixed`
- `_validation` file `derived_from` points to wrong artifact

---

## CLI and API Changes

### Existing Commands to Preserve

- `ucx create prd`
- `ucx validate prd`
- `ucx review prd`
- `ucx remediate prd`

### New Commands to Add

1. `ucx validate-fix prd <source-prd> --report <validation-report>`
   - Creates `_validation` copy only
   - Applies deterministic validation fixes to the copy only

2. `ucx remediate-apply prd <validation-prd> --report <remediation-report>`
   - Creates `_remediated` copy only
   - Applies remediation fixes to the copy only

### Optional Future Command

3. `ucx promote prd <remediated-prd>`
   - Out of scope for PLAN-012
   - Future path to promote approved remediated artifact back into canonical source with version bump

---

## Relationship to Existing Plans

### PLAN-010 Impact

PLAN-010 remains the PRD validation baseline, but its operational flow is refined:

- `ucx validate prd` becomes report-only
- deterministic fixer application moves to `ucx validate-fix prd`
- review and remediation target `_validation` copy rather than canonical source

### PLAN-011 Impact

PLAN-011 defines generalized UCX reporting standards. PLAN-012 introduces a PRD-specific exception for validation report naming:

- PRD validation report filename is fixed as `PRD-01_validation_report.md`
- review and remediation reports remain versioned
- pre-commit remains separate from reporting semantics and performs availability checks only

If generalized later, PLAN-011 may need revision to support stage-aware derived artifact workflows across other SSD layers.

### Gap Closures in This Revision

- Clarifies current-vs-planned runtime scope so docs do not present PLAN-012 behavior as already released.
- Defines mandatory lineage metadata for validation and remediation reports, not only derived PRD copies.
- Adds artifact discovery rules so pre-commit can distinguish source, derived copies, and reserved report names deterministically.

---

## Implementation Phases

### Phase 1: Artifact Naming and Metadata Contract

**Goal**: Define deterministic PRD artifact naming and metadata rules.

Tasks:
- Add helper utilities for derived PRD filenames
- Add helper utilities for processing-stage metadata injection
- Add validation helpers for lineage fields (`source_doc_id`, `source_version`, `derived_from`, `processing_stage`)

Deliverables:
- Shared PRD artifact naming utility
- Metadata normalization helper for derived PRD copies

---

### Phase 2: Validation Report-Only Normalization

**Goal**: Make `ucx validate prd` report-only with fixed report name.

Tasks:
- Ensure validation never mutates source PRD
- Emit `PRD-01_validation_report.md`
- Align CLI help and docs with report-only semantics

Deliverables:
- PRD validation report-only path
- Deterministic validation report naming

---

### Phase 3: Validation Copy Fix Command

**Goal**: Add copy-based validation fix application.

Tasks:
- Implement `ucx validate-fix prd`
- Copy source PRD to `_validation` filename
- Apply deterministic validation fixes to the copy only
- Update metadata and revision history on copied artifact

Deliverables:
- `_validation` artifact creator
- Regression tests for source immutability and metadata correctness

---

### Phase 4: Review and Remediation Rebinding

**Goal**: Re-anchor review and remediation to `_validation` PRD artifacts.

Tasks:
- Update review path to accept and prefer `_validation` artifacts
- Update remediation path to accept `_validation` artifacts as canonical input for later stages
- Add report metadata fields identifying exact artifact filename and stage

Deliverables:
- Review/remediation report lineage support
- Tests ensuring reports reference `_validation` input artifact

---

### Phase 5: Remediation Apply Copy Command

**Goal**: Add copy-based remediation fix application.

Tasks:
- Implement `ucx remediate-apply prd`
- Copy `_validation` PRD to `_remediated` filename
- Apply remediation fixes to `_remediated` copy only
- Update metadata and revision history on copied artifact

Deliverables:
- `_remediated` artifact creator
- Tests ensuring `_validation` remains unchanged

---

### Phase 6: Pre-commit Availability Guardrail

**Goal**: Add lightweight artifact presence and consistency checks.

Tasks:
- Implement stage-aware pre-commit checker for PRD artifact folders
- Check required reports and derived variants based on what exists
- Do not rerun validation logic
- Emit concise failure messages describing missing or inconsistent artifacts

Deliverables:
- Pre-commit PRD artifact checker
- Tests covering missing artifact and metadata mismatch cases

---

## Acceptance Criteria

### Functional

- `ucx create prd` creates canonical source PRD only
- `ucx validate prd` creates `PRD-01_validation_report.md` only
- `ucx validate-fix prd` creates `_validation` PRD copy only
- `ucx review prd` can review `_validation` PRD and emit separate review report
- `ucx remediate prd` can consume `_validation` PRD and review report to emit remediation report
- `ucx remediate-apply prd` creates `_remediated` PRD copy only

### Integrity

- Source PRD is never modified after creation by validation, review, or remediation flows
- `_validation` PRD is never modified by remediation apply flow
- `doc_id` matches across source, `_validation`, and `_remediated`
- `version` matches across source, `_validation`, and `_remediated`
- `processing_stage` is correct on all variants

### Pre-commit

- Pre-commit checks artifact availability and metadata consistency only
- Pre-commit does not duplicate validation logic
- Pre-commit clearly reports missing report/document variants

---

## Test Strategy

### Unit Tests

- Derived filename generation
- Metadata normalization for `_validation` and `_remediated`
- Revision history row insertion for derived artifacts
- Report filename generation for `PRD-01_validation_report.md`

### Integration Tests

- Full PRD flow from source to validation report to `_validation` copy
- Review/remediation binding to `_validation` copy
- Remediation apply creating `_remediated` copy without mutating `_validation`
- Pre-commit artifact availability checks

### Regression Tests

- Source PRD immutability after validate/review/remediate/apply flows
- Report filenames remain deterministic
- Existing PRD validation semantics still operate without duplicate validation in pre-commit

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Artifact proliferation confuses users | Medium | Deterministic naming + docs + CLI help |
| Metadata drift between variants | High | Shared metadata normalization helper |
| PLAN-011 naming conflict | Medium | Scope PLAN-012 as PRD-specific exception initially |
| Users edit derived copy directly and lose provenance | Medium | Add lineage metadata + pre-commit consistency checks |
| Pre-commit becomes too heavy | High | Restrict pre-commit to availability/consistency checks only |

---

## Open Design Decisions

1. Should review/remediation report names remain stage-specific (`validation_review`, `validation_remediation`) or align to generalized UCX naming with stage metadata only?
2. Should `_validation` and `_remediated` artifacts be hidden from default create/review path discovery unless explicitly targeted?
3. Should future layers (EARS, ADR, SYS) adopt the same derived-artifact workflow after PRD proves stable?

These questions are intentionally deferred; PLAN-012 defines the PRD implementation baseline first.

---

## Success Definition

PLAN-012 is complete when UCX can process a PRD through the entire derived-artifact chain and produce this auditable set without mutating the canonical source:

- source PRD
- `PRD-01_validation_report.md`
- `_validation` PRD
- review report
- remediation report
- `_remediated` PRD

and when pre-commit can verify artifact availability and lineage consistency without rerunning validation logic.