# SPEC-009: MCP Remediation and Fix Flow Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-009 |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-26 |
| Scope | Deterministic remediation planning and source-protected fix flow contracts |

---

## 1. Commands in Scope

- `remediate`
- `validate-fix`
- `remediate-fix`

---

## 2. Contract Rules

1. `remediate` generates findings and recommended actions only.
2. `validate-fix` generates `_validation` derived artifact(s) from source.
3. `remediate-fix` generates `_remediated` derived artifact(s).
4. Source files are not modified in default protected mode.
5. Each command writes JSON and TXT report artifacts when output path is provided.

---

## 3. Output Artifact Contracts

### 3.1 remediate

Required files:

- `remediation_report.json`
- `remediation_report.txt`

Required JSON fields:

- `project_root`
- `document_path`
- `doc_type`
- `layer`
- `review_report`
- `findings`
- `summary.total_findings`

### 3.2 validate-fix

Required files:

- `validate_fix_report.json`
- `validate_fix_report.txt`
- one or more `*_validation.md` derived artifacts

Required JSON fields:

- `project_root`
- `document_path`
- `derived_paths`
- `summary.source_protected`

### 3.3 remediate-fix

Required files:

- `remediate_fix_report.json`
- `remediate_fix_report.txt`
- one or more `*_remediated.md` derived artifacts

Required JSON fields:

- `project_root`
- `document_path`
- `derived_paths`
- `summary.source_protected`

---

## 4. Failure Modes

| Failure Mode | Detection | Required Behavior |
| --- | --- | --- |
| unreadable source path | input resolution | command failure with non-zero exit |
| invalid report path | report ingest stage | command failure with non-zero exit |
| output write error | artifact write stage | command failure with non-zero exit |

---

## 5. Validation Evidence

- `mcp/tests/unit/test_remediation_runner.py`
- `mcp/tests/integration/test_migration_flows.py`
