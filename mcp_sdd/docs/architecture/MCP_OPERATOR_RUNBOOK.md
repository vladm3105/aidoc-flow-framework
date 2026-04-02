# MCP Operator Runbook

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.3 |
| Date | 2026-03-27 |
| Scope | Operational procedures and troubleshooting for implemented MCP command surface |

---

## 1. Purpose

Provide deterministic operational procedures for MCP command execution and failure handling.

Implementation complexity: 3/5.

---

## 2. Preconditions

- Runtime environment can execute mcp CLI command.
- Project path is available and writable for output operations.
- For create-build, review-build, validate, and remediation flows, project contains project-local UCX assets or operator has permission to run init.

---

## 3. Standard Operating Procedures

### 3.1 Initialize project assets

Procedure:

1. Run mcp init with project path.
2. Confirm output reports created and skipped counts.
3. Verify required directories exist under UCX.

Success condition:

- UCX structure exists and command returns successful exit.

### 3.2 Create-build with sections payload

Procedure:

1. Prepare sections-json file with required fields.
2. Run create-build with project, persona, doc-type, layer, template, sections-json, and out.
3. Confirm creation prompt artifacts are present in output directory.
4. Review inspection output for warnings.

Success condition:

- creation_prompt.txt and sidecar artifacts are present.

### 3.3 Create-build without sections payload

Procedure:

1. Run create-build without sections-json argument.
2. Confirm command completes and writes output artifacts.
3. Validate prompt output includes expected template and layer assets.

Constraint:

- This mode does not provide direct markdown ingestion semantics.

### 3.4 Review-build

Procedure:

1. Prepare sections-json payload.
2. Run review-build with required arguments.
3. Confirm review prompt, sidecar, and inspection artifacts are written.

Success condition:

- review artifacts exist and inspection is parseable JSON.

### 3.5 Validate-build

Procedure:

1. Select target document file or document directory.
2. Run validate with project, doc-type, layer, and document arguments.
3. Confirm validation_report.json and validation_report.txt are written in output path.
4. Review report errors and warnings, then remediate source document if required.

Success condition:

- Validation exit code is 0 and report summary indicates passed.

### 3.6 Validate-fix

Procedure:

1. Run validate and capture validation report path.
2. Run validate-fix with source document and validation report path.
3. Confirm derived `_validation` artifact and `validate_fix_report.*` files are produced.

Success condition:

- Derived validation artifact exists and source file remains unchanged.

### 3.7 Remediate and remediate-fix

Procedure:

1. Run remediate against source or validation-derived artifact.
2. Confirm remediation report artifacts are produced.
3. Run remediate-fix with remediation report input.
4. Confirm `_remediated` artifact and apply report artifacts are produced.
5. For remediation reports with findings, confirm each finding includes stable `finding_id` and `action_id` fields.

Success condition:

- Remediation planning and apply phases complete with deterministic artifacts.

### 3.8 Consistency checks

Procedure:

1. Run consistency against a source file or document folder.
2. Review the text or JSON report for missing source, validation, or remediation prerequisites.
3. Correct lineage gaps before running downstream lifecycle stages.

Success condition:

- Report status is pass and command returns exit code 0.

### 3.9 Preflight readiness

Procedure:

1. Run preflight with project path and an appropriate context value.
2. If validating a specific target, include the document path.
3. If a probe payload file exists under tmp, review fallback parsing fields in the report.
4. Do not proceed to review or remediation when preflight returns blocked.

Success condition:

- Report status is ready or degraded, and blocking errors are absent.

### 3.10 Diagnostics commands

Procedure:

1. Run prescreen on target file or folder to identify candidate findings.
2. Run scan on report JSON to collect category metrics.
3. Run scoring show/validate/compare as needed for quality gating.

Success condition:

- Diagnostics payloads are emitted and can be parsed as JSON.

---

## 4. Troubleshooting Scenarios

### Scenario A: sections-json provided

Expected behavior:

- Source sections are loaded from payload and mapped into prompt context.

Troubleshooting checks:

- Validate payload JSON syntax and required keys.
- Validate file path readability.

### Scenario B: sections-json omitted for create-build

Expected behavior:

- Command runs with internal fallback section behavior.

Troubleshooting checks:

- Confirm command invocation did not include malformed sections-json flag.
- Inspect resulting prompt for fallback section presence.

### Scenario C: missing project UCX path

Error indicator:

- ProjectSkillsNotFound

Resolution:

1. Run mcp init --project path.
2. Re-run failed command.

### Scenario D: PersonaMappingError on create/review/remediate

Error indicator:

- `PersonaMappingError` with `doc_type` and `phase` fields in the error payload.

Causes (structural YAML issues):

- `persona_mappings.yaml` has missing `version` field or empty `personas` list.
- The `(doc_type, phase)` pair has no entry in `persona_mappings.yaml` and no `--personas` argument was provided.

Resolution:

1. Verify `{project}/UCX/skills/persona_mappings.yaml` exists. If not, run `mcp init --project {project_root}`.
2. Verify the mapping file contains an entry for the target `(doc_type, phase)` pair.
3. Alternatively, provide explicit `--personas` on the command line to bypass mapping lookup.

### Scenario D-2: ProjectSkillsNotFound for missing persona files

Error indicator:

- `ProjectSkillsNotFound` with `missing_paths` listing persona file paths.

Cause:

- A persona identifier in `persona_mappings.yaml` references a persona file that does not exist under `{project}/UCX/skills/personas/`. The `_validate_persona_mapping` function raises `ProjectSkillsNotFound` (not `PersonaMappingError`) for missing files.

Resolution:

1. Verify all persona identifiers in the mapping resolve to files under `{project}/UCX/skills/personas/`.
2. Run `mcp init --project {project_root}` to restore missing persona files.

### Scenario D-3: Preflight warns on missing persona_mappings.yaml

Detection:

- Preflight report includes warning-level check `missing_persona_mappings`.

Cause:

- `persona_mappings.yaml` does not exist under `{project}/UCX/skills/`. Preflight checks for this file at warning level (not error).

Resolution:

1. Run `mcp init --project {project_root}` to scaffold `persona_mappings.yaml`.
2. Re-run preflight to confirm the warning is resolved.

### Scenario E: validate fails on structure checks

Expected behavior:

- Command returns non-zero exit code and reports missing required fields/tags/sections.

Troubleshooting checks:

- Validate document has YAML frontmatter with required custom_fields and tags.
- Validate layer schema file exists under UCX/templates/layers/{layer}.
- Validate required section headings and structure match schema regex patterns.

### Scenario F: preflight returns blocked

Expected behavior:

- Command returns exit code 1 and report lists blocking errors.

Troubleshooting checks:

- Confirm UCX scaffold exists under the selected project root.
- Confirm required review or creation template folders exist for the selected context.
- Confirm optional probe payload is not signaling blocked provider state.

### Scenario G: source protection telemetry absent

Expected behavior:

- validate-fix or remediate-fix may omit `source_protection_telemetry` when no canonical source files were monitored, such as section-folder copy flows.

### Scenario H: YAML document troubleshooting

Applicable when operating on `.yaml` source documents:

- Frontmatter check is skipped for `.yaml` files. YAML documents are structured data, not Markdown with frontmatter.
- Derived copies (`_validation.yaml`, `_remediated.yaml`) are excluded from source artifact detection during folder resolution.
- Scoring uses categorized weights: structural errors (20pt deduction), cross-section errors (10pt deduction), warnings (5pt deduction).
- If validation reports unexpected frontmatter failures on a YAML file, confirm the runner is using YAML-aware check dispatch rather than the Markdown path.

### Scenario I: remediation finding IDs appear to change between reruns

Expected behavior:

- Identical remediation inputs emit the same `finding_id` and `action_id` values across reruns.

Troubleshooting checks:

- Confirm the source content, category, severity, and recommended action are unchanged.
- Confirm downstream consumers accept legacy sequential finding IDs only through compatibility validation and do not rewrite canonical hash IDs.

Troubleshooting checks:

- Confirm command operated on a folder fallback path rather than a single canonical source file.
- Confirm source protection summary still reports protected mode.
- Treat telemetry omission as valid when source monitoring was not applicable.

---

## 5. Failure Modes and Responses

| Failure Mode | Detection | Response |
| --- | --- | --- |
| ProjectSkillsNotFound | command error payload includes missing_paths | run init, then retry |
| blocked preflight | preflight report status is blocked | repair missing project/runtime prerequisites, then rerun |
| consistency lineage failure | consistency report contains errors | restore missing prerequisite artifact or rerun upstream stage |
| Invalid sections-json payload | parser or deserialization error | correct payload and retry |
| PersonaMappingError | persona resolution fails for structural YAML issues (missing version, empty personas, no mapping entry) | verify persona_mappings.yaml structure and entry exists or provide explicit --personas |
| ProjectSkillsNotFound (persona files) | persona file referenced in mapping does not exist | run init to restore missing persona files or correct mapping identifiers |
| Missing template or persona | loader error via missing path | add required file under UCX and retry |
| missing_persona_mappings (preflight warning) | preflight detects persona_mappings.yaml absent | run init to scaffold persona_mappings.yaml |
| validate structural violations | validation report contains missing requirements | remediate document and re-run validate |
| validate-fix/remediate-fix output missing | fix report generated without derived artifacts | verify document path and output path permissions, then rerun |
| scan/scoring parse failure | report payload invalid JSON | repair upstream report generation, then rerun diagnostics |
| Output write failure | file I/O error | validate output directory permissions |

---

## 6. Escalation Criteria

Escalate to runtime maintainer when:

- ContractValidationError persists after input correction.
- Repeated command failures occur with valid payload and valid project UCX structure.
- Output artifacts are produced but sidecar schema appears malformed.
