# SPEC-008: MCP Output Schema Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-008 |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-26 |
| Scope | Canonical output schemas and schema versioning rules for MCP command results |

---

## 1. Purpose

Define stable output schema contracts for MCP command artifacts and console payloads used by operators, tests, and automation.

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:

- schema envelope for MCP JSON outputs
- schema versioning and compatibility rules
- required fields for validate, validate-fix, remediate, remediate-fix, prescreen, scan, and scoring outputs
- deterministic serialization constraints

Out of scope:

- prompt text content quality
- LLM model behavior tuning
- UI rendering concerns outside schema payloads

---

## 3. Global Envelope Contract

All MCP JSON outputs in scope must include:

- `schema_id` string
- `schema_version` string using semantic version format
- `generated_at` ISO-8601 UTC timestamp
- `command` string
- `project_root` string
- `status` string in `{passed, failed, error}`
- `errors` array (empty when none)

Normative rules:

1. `schema_id` must be stable per command family.
2. `schema_version` must increment for structural changes.
3. Unknown fields are allowed but must not alter required field semantics.
4. Arrays must preserve deterministic ordering for identical input.

---

## 4. Command Schema Contracts

### 4.1 validate schema

Schema id:

- `mcp.validate.report`

Required fields:

- `summary`
- `tier1_issues`
- `tier2_issues`
- `is_valid`
- `exit_code`

Constraints:

- `exit_code` mapping must follow CLI contract.
- `is_valid` must be true only when blocking checks pass.

### 4.2 validate-fix schema

Schema id:

- `mcp.validate_fix.report`

Required fields:

- `project_root`
- `document_path`
- `doc_type`
- `layer`
- `validation_report`
- `derived_paths`
- `summary`

Constraints:

- source-protection status must be explicit in summary payload.

### 4.3 remediate schema

Schema id:

- `mcp.remediate.report`

Required fields:

- `project_root`
- `document_path`
- `doc_type`
- `layer`
- `review_report`
- `findings`
- `summary`

Constraints:

- finding category and severity fields must be present for each emitted finding.

### 4.4 remediate-fix schema

Schema id:

- `mcp.remediate_fix.report`

Required fields:

- `project_root`
- `document_path`
- `doc_type`
- `layer`
- `remediation_report`
- `derived_paths`
- `summary`

Constraints:

- no direct mutation of original source document in protected mode.

### 4.5 prescreen schema

Schema id:

- `mcp.prescreen.report`

Required fields:

- `document_path`
- `candidates`
- `summary`

### 4.6 scan schema

Schema id:

- `mcp.scan.report`

Required fields:

- `report_file`
- `categories`
- `summary`

### 4.7 scoring schema

Schema ids:

- `mcp.scoring.show`
- `mcp.scoring.validate`
- `mcp.scoring.compare`

Required fields for compare:

- `baseline_report_file`
- `candidate_report_file`
- `baseline_score`
- `candidate_score`
- `delta`

---

## 5. Text Output Contract

For text outputs paired with JSON:

1. text summary must include command, status, and primary metric line.
2. text output must include artifact paths when files are emitted.
3. text output must not omit blocking errors present in JSON.

---

## 6. Versioning and Change Rules

Allowed without major bump:

- adding optional fields
- adding non-breaking enum values when documented

Requires major bump:

- removing required fields
- renaming required fields
- changing field type for required fields
- changing exit-code semantics tied to schema status

---

## 7. Validation Evidence Requirements

Required checks:

- schema presence test for each command family
- required-fields test per schema id
- deterministic ordering test on repeated identical input
- schema-version regression check in CI

Required test targets:

- `mcp_ucx/tests/unit/test_validation_runner.py`
- `mcp_ucx/tests/unit/test_remediation_runner.py`
- `mcp_ucx/tests/unit/test_prescreening.py`
- `mcp_ucx/tests/unit/test_scoring_cli.py`
- `mcp_ucx/tests/integration/test_migration_flows.py`

---

## 8. Constraints

- Schema contracts are authoritative for automation integration.
- Runtime changes that affect schema shape must update this spec in the same change set.
- Docs and CLI examples must reflect the current schema version.
