# MCP Operational Flows

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-26 |
| Scope | End-to-end command execution flows for implemented MCP CLI operations |

---

## 1. Flow Set

- create flow: `create-build`
- review flow: `review-build` and `review`
- validate flow: `validate-build`
- validation-derived artifact flow: `validate-fix`
- remediation planning flow: `remediate`
- remediation-apply derived artifact flow: `remediate-fix`
- prescreen flow: `prescreen`
- report scan flow: `scan`
- score flows: `scoring show`, `scoring validate`, `scoring compare`

---

## 2. Validate and Fix Flow

1. Execute `validate-build` against source file or folder.
2. Emit `validation_report.json` and `validation_report.txt`.
3. Execute `validate-fix` with source-protected mode.
4. Emit `_validation` derived artifact(s) and `validate_fix_report.*`.

Constraints:

- source document is not modified in default mode.
- derived artifacts are generated deterministically.

---

## 3. Remediation Flow

1. Execute `remediate` against source or validation-derived artifact.
2. Emit `remediation_report.json` and `remediation_report.txt`.
3. Execute `remediate-fix`.
4. Emit `_remediated` derived artifact(s) and `remediate_fix_report.*`.

Constraints:

- source document remains unchanged.
- remediation planning and apply phases are explicit separate commands.

---

## 4. Diagnostics Flow

1. Execute `prescreen` to identify high-priority candidate files.
2. Execute `scan` on JSON report files to extract finding-category counts.
3. Execute `scoring` commands for numeric quality scoring and comparisons.

Outputs:

- prescreen report: `prescreen_report.json`
- scan report: `scan_report.json`
- scoring payloads: JSON printed to stdout

---

## 5. Operational Controls

Validation controls:

- `validate-build --tier1-only`
- `validate-build --strict`
- `validate-build --format {text,json}`

Review controls:

- `--persona`, `--unified`, `--one-turn`, `--no-resume`, `--session-ttl`
- `--clean-memory`, `--clean-reports`, `--keep-versions`

---

## 6. Exit Behavior

| Command Group | Pass | Fail |
| --- | --- | --- |
| validate-build | 0 | 1 |
| scoring validate | 0 | 1 |
| other implemented commands | 0 | 2 only for CLI usage/argument failures |

---

## 7. Evidence Commands

- `pytest mcp/tests/unit/test_cli_main.py`
- `pytest mcp/tests/unit/test_validation_runner.py`
- `pytest mcp/tests/unit/test_remediation_runner.py`
- `pytest mcp/tests/unit/test_prescreening.py`
- `pytest mcp/tests/unit/test_scoring_cli.py`
- `pytest mcp/tests/integration/test_migration_flows.py`
