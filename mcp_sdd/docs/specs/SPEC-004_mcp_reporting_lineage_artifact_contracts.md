# SPEC-004: MCP Reporting, Lineage, and Derived Artifact Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-004 |
| Status | Active |
| Version | 1.3 |
| Date | 2026-03-27 |
| Source Basis | Canonical normative specification |
| Scope | Report naming, report schema, derived artifact naming, lineage metadata, artifact discovery, pre-commit separation |

---

## 1. Purpose

Define normative contracts for versioned reporting, stage-aware artifact naming, lineage metadata, derived artifact discovery, and separation of standard workflow reporting from pre-commit diagnostics.

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:
- Validation, review, remediation, and pre-commit report contracts.
- Stage-aware naming for derived artifacts.
- Lineage metadata for reports and document copies.
- Artifact-set discovery rules.
- Version allocation and concurrent write protection for versioned reports.

Out of scope:
- Review scoring semantics (defined by SPEC-002).
- Validation profile structure (defined by SPEC-003).
- Namespace and lifecycle stage ownership (defined by SPEC-001).

---

## 3. Report Mode Contract

Report modes:
- STANDARD
- PRECOMMIT

Rules:
- STANDARD emits canonical workflow reports only.
- PRECOMMIT emits `.precommit_validation_report.md` only.
- Pre-commit reporting must not be reused as the standard validation artifact.
- Create flows must never emit pre-commit reports.

Failure modes:
- Standard validate emits pre-commit report.
- Pre-commit path emits versioned or stage workflow artifacts.

---

## 4. Report Naming Contract (Mandatory)

Canonical file patterns:
- Validation report: `{DOC_ID}_validation_report.md`
- Review report: `{DOC_ID}_{source_stage}_review_report_vNNN.md`
- Remediation report: `{DOC_ID}_{source_stage}_remediation_report_vNNN.md`
- Pre-commit report: `.precommit_validation_report.md`

Scope clarification:
- Section 4 defines lifecycle-level canonical report families.
- Section 4.1 defines audit-wrapper/fixer-compatible naming specializations and deterministic selection rules.
- Where both naming families are available for the same workflow handoff, Section 4.1 selection rules take precedence for fixer intake.

Rules:
- Validation report naming is reserved for validation of the canonical source stage only.
- Validation report is deterministic and single-name per source stage.
- Review and remediation reports are versioned and append-only.
- Report naming derives from canonical `doc_id` and source processing stage.
- Version allocation must retry on collision and fail explicitly after bounded retries.

Legacy compatibility policy:
- Legacy `UCX_validation_report`, `UCX_review_report`, and `UCX_remediation_report` files are read-only compatible migration inputs.
- MCP implementations must not write new legacy `UCX_*` report filenames.
- Legacy report files are ignored for canonical version allocation unless explicitly imported into canonical naming.
- Repositories may choose import, ignore, or fail-fast policy, but that policy must be configured explicitly at repository level.

Required naming inputs:
- source_artifact_id
- source_processing_stage
- report_type

### 4.1 Audit/Review/Fix Report Family Contract

Canonical report families:
- Combined audit report: `{DOC_ID}.A_audit_report_vNNN.md`
- Reviewer-native report (legacy-compatible): `{DOC_ID}.R_review_report_vNNN.md`
- Fix report: `{DOC_ID}.F_fix_report_vNNN.md`

Rules:
- `.A_audit_report` is the preferred normalized handoff report for fixer workflows when available.
- `.R_review_report` remains valid reviewer-native review input and compatibility input for fixer workflows.
- `.F_fix_report` records fixer-side applied changes and unresolved findings.
- If two candidate inputs are equivalent by timestamp/version, selection must prefer `.A_audit_report` over `.R_review_report`.

Naming-mapping rules:
- Lifecycle review outcomes may be represented by either:
	- `{DOC_ID}_{source_stage}_review_report_vNNN.md` (lifecycle family), or
	- `{DOC_ID}.A_audit_report_vNNN.md` / `{DOC_ID}.R_review_report_vNNN.md` (audit-wrapper family).
- Lifecycle remediation/apply outcomes may be represented by either:
	- `{DOC_ID}_{source_stage}_remediation_report_vNNN.md` (lifecycle family), or
	- `{DOC_ID}.F_fix_report_vNNN.md` (audit-wrapper family).
- Implementations must preserve lineage linkage across mapped families (source artifact, source stage, and upstream report references).

Terminology clarification:
- "legacy-compatible" in this section refers to compatibility within MCP reviewer/audit report families (`.R_` accepted when `.A_` is unavailable).
- It does not refer to `UCX_*` legacy filenames governed by Section 4 legacy compatibility policy.

Failure modes:
- Fixer intake ignores `.A_audit_report` when both `.A_` and `.R_` are equally current.
- Runtime emits non-versioned `.A_`, `.R_`, or `.F_` report names for canonical workflows.

---

## 5. Standard Report Schema Contract

Required frontmatter fields:
- title
- tags
- custom_fields

Required `custom_fields` minimum:
- report_type
- source_artifact_type
- source_artifact_id
- source_artifact_file
- source_processing_stage
- status
- generated_at

Additional required metrics by report type:
- Validation: `checks_run`, `blocking_findings`, `warning_findings`
- Review: `weighted_score`, `finding_counts`, `personas_applied`
- Remediation: `findings_addressed`, `changes_applied`, `remaining_findings`

Conditional lifecycle fields:
- Source-protected fix flows may emit `source_protection_telemetry`.
- `source_protection_telemetry` is required only when one or more source files were actively monitored for mutation during `validate-fix` or `remediate-fix`.
- When source monitoring is not applicable, `source_protection_telemetry` must be omitted rather than emitted as an empty object.

Rules:
- Report schema must be machine-parseable.
- Review and remediation reports must identify the exact source artifact filename consumed.
- Remediation reports must reference the upstream review report when one was consumed.
- Conditional telemetry omission is schema-valid when source monitoring did not occur.
- Remediation findings must include `finding_id`, `action_id`, and `priority` fields when findings are present.

Timestamp normalization rules:
- `generated_at` must be RFC 3339 / ISO 8601 with explicit timezone offset.
- Repository policy may require `America/New_York` (EST/EDT) normalization; when enabled, report timestamps must be emitted in that timezone.
- Missing timezone offset in `generated_at` is schema-invalid.

### 5.1 Combined Audit Fix Queue Contract

When a combined audit report is produced, required fix-queue buckets are:
- auto_fixable
- manual_required
- blocked

Each normalized fix-queue finding must include:
- source
- code
- severity
- file
- section
- action_hint
- confidence

Allowed confidence domain:
- high
- medium
- manual-required

Fix-queue naming normalization:
- Bucket key `manual_required` is canonical for queue grouping.
- Confidence value `manual-required` is canonical for finding-level confidence.
- Implementations must not treat `manual_required` and `manual-required` as interchangeable in the same field.

Rules:
- Fix-queue findings must remain machine-parseable and stable across re-runs with identical inputs.
- Missing required fix-queue fields are schema-invalid for combined audit handoff.

### 5.2 Remediation Finding Identity Contract

Required per-finding fields for remediation reports:
- finding_id
- action_id
- priority

Rules:
- `finding_id` must use `P{0|1|2|3}-{hex}` format.
- `action_id` must use `ACT-{hex}` format.
- Legacy sequential finding IDs remain accepted only through compatibility validation layers; canonical remediation outputs must emit hash-based IDs.

---

## 6. Derived Artifact Naming Contract

Canonical file patterns:
- Source artifact: `{DOC_ID}_{slug}.md`
- Validation-fixed artifact: `{DOC_ID}_{slug}_validation.md`
- Remediated artifact: `{DOC_ID}_{slug}_remediated.md`

Rules:
- Source artifact has no stage suffix.
- `_validation` and `_remediated` suffixes are reserved for MCP-derived copies only.
- Derived artifacts retain the same `doc_id` and `version` as the canonical source unless an explicit versioning policy overrides them.
- Prior artifacts remain immutable after successor generation.

Failure modes:
- Source artifact overwritten during fix flow.
- Non-derived document uses reserved stage suffix.
- Derived artifact changes canonical `doc_id`.

---

## 7. Lineage Metadata Contract

Source artifact metadata minimum:
- processing_stage: source

Derived artifact metadata minimum:
- processing_stage
- source_doc_id
- source_version
- derived_from

Rules:
- `processing_stage` represents pipeline state and must not be overloaded with lifecycle status.
- Validation-fixed artifacts must declare `processing_stage: validation-fixed`.
- Remediated artifacts must declare `processing_stage: remediated`.
- Reports must identify both source artifact ID and source processing stage.
- Creation provenance artifacts must identify the canonical source artifact file they produced.

### 7.1 Drift Hash Contract

When drift-cache validation is enabled by profile or repository policy, drift metadata must include upstream hash entries.

Required drift-hash fields:
- upstream_artifact
- hash_algorithm
- hash_value

Required format:
- `hash_value` must use `sha256:<64 lowercase hex chars>`.

Rules:
- Missing required upstream hash entries are blocking validation failures when drift-cache validation is enabled.
- Invalid hash format is a blocking validation failure.

Failure modes:
- Missing `derived_from` on a derived document.
- Report lineage omits source stage.
- Lifecycle status field used in place of processing stage.

---

## 8. Artifact Discovery Contract

For any artifact family, discovery rules are:
- exactly one canonical source artifact without a stage suffix
- zero or one validation report per source stage
- zero or more versioned review reports per source stage
- zero or more versioned remediation reports per source stage
- zero or one validation-fixed artifact derived from the source stage at a time unless versioning strategy explicitly allows more
- zero or one remediated artifact derived from a validation-fixed stage at a time unless versioning strategy explicitly allows more

Rules:
- Source-only folders remain valid before later stages run.
- Once a later-stage artifact exists, its prerequisite artifacts must also exist.
- Discovery failures must report missing prerequisite type and expected filename pattern.

Default selection precedence by operation:
- `create`: target folder must resolve to canonical source output path only.
- `validate`: folder target resolves to canonical source artifact.
- `validate_fix`: folder target resolves to canonical source artifact plus canonical validation report.
- `review`: folder target resolves to validation-fixed artifact and fails explicitly if absent.
- `remediate_content`: folder target resolves to validation-fixed artifact and latest applicable review report unless a report is specified explicitly.
- `remediate_apply`: folder target resolves to validation-fixed artifact and latest applicable remediation report unless a report is specified explicitly.

Fixer review-input precedence:
1. latest `.A_audit_report_vNNN.md`
2. latest `.R_review_report_vNNN.md`

Tie-break rule:
- If `.A_` and `.R_` candidates are equivalent by selection timestamp/version, `.A_` must win.

---

## 9. Concurrent Write and Version Allocation Contract

Rules:
- Versioned report writes must use temp-file plus atomic rename.
- If target version exists at write time, allocator recomputes and retries.
- Retry loop must be bounded to 3 attempts.
- Failure after retry limit must be explicit and non-silent.

Verification targets:
- no partial report files on collision
- deterministic next-version selection under serial execution
- explicit collision error after bounded retries

---

## 10. Compliance Matrix

| Contract Area | Verification Method | Pass Condition |
| --- | --- | --- |
| Report mode separation | CLI/integration tests | Standard and pre-commit outputs never cross modes |
| Report naming | Naming contract tests | All reports match canonical patterns |
| Audit/review/fix report families | Family-naming fixtures | `.A_`, `.R_`, `.F_` report names are versioned and precedence rules are deterministic |
| Naming-family mapping | Mapping fixtures | Lifecycle and audit-wrapper families map with preserved lineage and deterministic precedence |
| Report schema | Schema tests | Required frontmatter and metrics fields present |
| Timestamp normalization | Timestamp schema fixtures | `generated_at` includes explicit timezone and follows repository timezone policy when enabled |
| Combined audit fix queue | Schema and parser tests | Required buckets and per-finding fields are present and parseable |
| Derived artifact naming | File contract tests | Stage-suffixed files follow reserved patterns only |
| Lineage metadata | Fixture tests | Source and derived artifacts include required lineage fields |
| Drift hash validation | Drift-cache fixtures | Required upstream hash entries and sha256 format are enforced when enabled |
| Artifact discovery | Multi-stage integration tests | Missing prerequisites and duplicate sources are detected |
| Concurrent writes | Collision tests | Atomic retry behavior works and bounded failure is explicit |

---

## 11. Resource Requirements and Constraints

- CPU: low-to-moderate for naming and discovery logic; moderate for integration verification.
- Memory: low.
- Storage: moderate due to append-only versioned reports and preserved derived artifacts.
- Constraint: report naming and lineage rules must remain deterministic across repeated runs.

---

## 12. Canonical Change Control

Change policy:
- Contract changes must be applied to this document first.
- Implementations may add report content fields but must not weaken required lineage or naming fields.
- Version must increment for normative contract updates.

---

## 13. References

- mcp_sdd/docs/specs/SPEC-001_mcp_core_architecture_workflow_contracts.md
- mcp_sdd/docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md