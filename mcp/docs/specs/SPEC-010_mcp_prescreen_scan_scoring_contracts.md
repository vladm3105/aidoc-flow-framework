# SPEC-010: MCP Prescreen, Scan, and Scoring Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-010 |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-26 |
| Scope | Deterministic diagnostics contracts for prescreen, scan, and scoring command groups |

---

## 1. Commands in Scope

- `prescreen`
- `scan`
- `scoring show`
- `scoring validate`
- `scoring compare`

---

## 2. prescreen Contract

Input:

- `--document` file or directory path

Output:

- JSON payload with `candidates` and `summary`
- optional `prescreen_report.json` and `prescreen_report.txt`

Required fields:

- `document_path`
- `candidates`
- `summary.files_scanned`
- `summary.candidates_found`

---

## 3. scan Contract

Input:

- `--report-file` JSON path

Output:

- JSON payload with category counts
- optional `scan_report.json` and `scan_report.txt`

Required fields:

- `report_file`
- `categories`
- `summary.error_count`
- `summary.warning_count`
- `summary.category_count`

---

## 4. scoring Contract

### show

Input:

- `--report-file`

Required output fields:

- `report_file`
- `score`
- `summary`

### validate

Input:

- `--report-file`
- `--threshold`

Required output fields:

- `report_file`
- `score`
- `threshold`
- `passed`

Exit code rule:

- pass: `0`
- fail threshold: `1`

### compare

Input:

- `--baseline-report-file`
- `--candidate-report-file`

Required output fields:

- `baseline_report_file`
- `candidate_report_file`
- `baseline_score`
- `candidate_score`
- `delta`

---

## 5. Validation Evidence

- `mcp/tests/unit/test_prescreening.py`
- `mcp/tests/unit/test_scoring_cli.py`
