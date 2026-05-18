---
title: "IPLAN-027: Unified Core Metadata Contract (status migration)"
id: IPLAN-027
date_created: 2026-03-01
last_updated: 2026-03-01
status: planning
owner: ai-agent
tags:
  - implementation-plan
  - metadata
  - framework
  - schema
  - validation
custom_fields:
  document_type: iplan
  plan_id: IPLAN-027
  status: draft
  created_date: 2026-03-01
  timezone: America/New_York
---

# IPLAN-027: Unified Core Metadata Contract (status migration)

## 1. Objective

Define and implement one **mandatory core metadata contract** across layers, using `status` as the canonical lifecycle field (replacing `development_status`), while allowing layer-specific custom fields and tag extensions.

## 2. Scope

### In Scope
- Canonical metadata matrix document for all layers.
- Framework metadata guide updates.
- Schema and validator migration design (`development_status` -> `status`).
- Pre-commit metadata enforcement policy update (targeted scope filtering).
- Layer applicability mapping and exception policy.
- Rollout and acceptance gates.

### Out of Scope
- Full immediate hard-cut migration in all repositories in one change.
- Rewriting non-metadata content sections.
- Removing layer-specific custom fields/tags beyond contract alignment.

## 3. Gap Review of Prior Plan

## 3.1 Identified Gaps

1. **No canonical artifact path for the matrix**
   - Gap: Plan intent existed but no explicit source-of-truth document location.
   - Impact: Multiple conflicting summaries can emerge.

2. **No explicit framework-vs-doc-type documentation worklist**
   - Gap: Missing concrete update/create targets by file path.
   - Impact: Partial migration and inconsistent adoption.

3. **No compatibility policy detail**
   - Gap: `status` migration lacked fallback behavior and precedence.
   - Impact: Validator breakage during transition.

4. **No validator/schema sequencing**
   - Gap: Missing order of operations across templates, schemas, validators, guides.
   - Impact: Temporary contract conflicts.

5. **No acceptance command matrix for metadata checks**
   - Gap: No explicit evidence commands for completion gates.
   - Impact: Subjective completion status.

6. **No owner/sign-off mapping by gate**
   - Gap: Execution authority and approval points undefined.
   - Impact: unclear closeout.

## 3.2 Gap Closure in This Plan

- Canonical matrix path defined (Section 5.1).
- File-level update/create worklist defined (Section 5.2, Section 6).
- Compatibility and precedence policy defined (Section 7).
- Ordered migration phases defined (Section 8).
- Acceptance command matrix defined (Section 9).
- Sign-off matrix defined (Section 10).

## 4. Canonical Core Metadata Contract

Mandatory core metadata (all layers, directly or mapped in schema profile):

1. `title`
2. `tags` (required minimal layer tags + optional extensions)
3. `custom_fields.document_type`
4. `custom_fields.artifact_type`
5. `custom_fields.layer`
6. `custom_fields.status` (canonical lifecycle field)
7. `custom_fields.schema_version`
8. `custom_fields.last_updated`

### Notes
- `deliverable_type` remains mandatory only in layers/contracts where routing is required.
- `instance_document_type` is not core mandatory; treat as layer/template extension during migration.
- Pre-commit metadata enforcement scope:
   - Ignore `document_type: template` artifacts.
   - Ignore `status: draft` artifacts.
   - Enforce metadata checks only for instance artifacts with `status` in `{development, production}`.

## 5. Documentation Deliverables

## 5.1 New Canonical Document (Framework Layer)

Create:
- `ai_dev_ssd_flow/METADATA_CORE_MATRIX.md`

Minimum sections:
1. Purpose and authority
2. Core mandatory metadata table (field, meaning, allowed values)
3. Per-layer applicability matrix
4. Layer extension policy (custom fields/tags)
5. Migration policy (`development_status` -> `status`)
6. Validation gates and command evidence

## 5.2 Framework Documentation Updates

Update:
- `ai_dev_ssd_flow/METADATA_TAGGING_GUIDE.md`
- `ai_dev_ssd_flow/METADATA_QUICK_REFERENCE.md`
- `ai_dev_ssd_flow/README.md` (metadata contract pointer only)

Required changes:
- Add canonical pointer to `METADATA_CORE_MATRIX.md`.
- Replace lifecycle references from `development_status` to `status`.
- Keep legacy note for transition window.
- Add explicit pre-commit scope rule text (template/draft ignore policy).

## 5.3 Pre-Commit Policy Documentation (Framework Layer)

Update or create policy text in:
- `ai_dev_ssd_flow/VALIDATION_DECISION_FRAMEWORK.md`
- `ai_dev_ssd_flow/VALIDATION_STANDARDS.md`
- `ai_dev_ssd_flow/VALIDATION_COMMANDS.md`

Required content:
1. Metadata pre-commit checks are **targeted**, not universal.
2. `document_type: template` and `status: draft` are excluded from blocking pre-commit metadata checks.
3. Blocking pre-commit metadata checks apply to instance artifacts with `status: development|production`.
4. Non-blocking report mode may still include excluded docs for visibility.

## 6. Doc-Type Layer Update Plan

For doc-type layers with `required_custom_fields`:
- `01_BRD/*_MVP_SCHEMA.yaml`
- `02_PRD/*_MVP_SCHEMA.yaml`
- `03_EARS/*_MVP_SCHEMA.yaml`
- `04_BDD/*_MVP_SCHEMA.yaml`
- `05_ADR/*_MVP_SCHEMA.yaml`
- `06_SYS/*_MVP_SCHEMA.yaml`
- `07_REQ/*_MVP_SCHEMA.yaml`
- `08_CTR/*_MVP_SCHEMA.yaml`
- `11_TASKS/*_MVP_SCHEMA.yaml`

Actions:
1. Add `status` as canonical required field.
2. Keep `development_status` as legacy-accepted during compatibility window.
3. Add schema note: legacy key deprecation timeline.
4. Add/align status allowed values to include `development` and `production` for instance enforcement profile.

For layer families with distinct schema models (L9, L10):
- map canonical fields to equivalent paths; do not force identical `custom_fields` layout.
- document mapping in matrix rather than imposing structural rewrite.

## 7. Migration Compatibility Policy

Compatibility window behavior:
1. Accept both `status` and `development_status`.
2. If both present, `status` is authoritative.
3. Emit warning for `development_status` usage.
4. Hard-fail on legacy key after cutover gate approval.

Pre-commit enforcement behavior:
5. Skip blocking metadata validation for `document_type: template`.
6. Skip blocking metadata validation for `status: draft`.
7. Apply blocking metadata validation to instance docs with `status: development|production`.
8. If `status` missing on instance docs, treat as validation error.

## 8. Ordered Implementation Phases

### Phase M1 — Contract & docs baseline
- Create `METADATA_CORE_MATRIX.md`.
- Update framework guide/quick-reference/readme pointers.

### Phase M2 — Schema alignment
- Update layer schemas to include `status` and legacy compatibility notes.

### Phase M3 — Validator alignment
- Update validators to support compatibility policy and warning semantics.
- Update pre-commit hooks to apply scope filtering by `document_type` and `status`.

### Phase M4 — Template alignment
- Update template frontmatter examples to `status` canonical field.
- Ensure templates keep `document_type: template` and remain non-blocking in pre-commit metadata checks.

### Phase M5 — Strict cutover
- Remove legacy acceptance paths after repository-wide conformance.

## 9. Acceptance Command Matrix

Evidence commands:
1. Core-field presence scan:
   - `grep -R --line-number -E 'status:|development_status:' ai_dev_ssd_flow`
2. Schema required field scan:
   - `grep -R --line-number -E 'required_custom_fields:|status:|development_status:' ai_dev_ssd_flow/**/*_MVP_SCHEMA.yaml`
3. Guide pointer integrity:
   - `grep -R --line-number 'METADATA_CORE_MATRIX.md' ai_dev_ssd_flow/METADATA_TAGGING_GUIDE.md ai_dev_ssd_flow/METADATA_QUICK_REFERENCE.md ai_dev_ssd_flow/README.md`
4. Validator support check:
   - layer validator grep for status-field handling rules.
5. Pre-commit scope filter check:
   - `grep -R --line-number -E 'document_type|status|template|draft|development|production' ai_dev_ssd_flow/scripts/pre_commit_hooks ai_dev_ssd_flow/.pre-commit-config.yaml`

Pass criteria:
- Canonical matrix exists and is referenced by framework metadata docs.
- `status` present in canonical contract and migration policy documented.
- Compatibility behavior documented and validator logic planned/implemented.
- Pre-commit policy explicitly enforces only instance `development|production` docs and excludes templates/drafts.

## 10. Sign-off Matrix

| Gate | Responsible | Approver |
|---|---|---|
| G1 Contract Definition | Operator | Framework Maintainer |
| G2 Doc Update Completeness | Operator | Documentation Lead |
| G3 Schema/Validator Compatibility | Operator | Validation Owner |
| G4 Cutover Readiness | Operator | Governance Owner |

## 11. Risks and Mitigations

1. **Mixed-state metadata during migration**
   - Mitigation: compatibility mode + warnings + explicit cutover date.
2. **Layer-specific schema divergence**
   - Mitigation: mapping policy for L9/L10, not forced structural homogenization.
3. **Validation regressions**
   - Mitigation: phase gates and command evidence before strict enforcement.

## 12. Immediate Next Actions

1. Create `METADATA_CORE_MATRIX.md` (draft v1).
2. Patch framework metadata guides with canonical references.
3. Add pre-commit policy text to validation framework docs.
4. Prepare schema, validator, and pre-commit hook delta list per layer.
5. Execute M1 acceptance commands and record evidence.
