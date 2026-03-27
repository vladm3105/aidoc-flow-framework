# MCP CLI Reference

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.1 |
| Date | 2026-03-26 |
| Scope | Implemented command contracts in `mcp/src/mcp_server/cli/main.py` |

---

## 1. Commands

| Command | Required Arguments | Optional Arguments | Output |
| --- | --- | --- | --- |
| init | --project | none | scaffold summary |
| create-build | --project --persona --doc-type --layer --template | --sections-json --out | creation prompt artifacts |
| review-build | --project --persona --doc-type --template --sections-json | --layer --unified --one-turn --no-resume --session-ttl --clean-memory --clean-reports --keep-versions --out | review prompt artifacts and control summary |
| review | same as review-build | same as review-build | alias for review-build |
| validate-build | --project --doc-type --layer --document | --tier1-only --strict --format {text,json} --out | validation report artifacts and status |
| validate-fix | --project --doc-type --layer --document | --validation-report --out | validation-derived artifacts and fix report |
| remediate | --project --doc-type --layer --document | --review-report --out | remediation report |
| remediate-fix | --project --doc-type --layer --document | --remediation-report --out | remediated-derived artifacts and apply report |
| prescreen | --document | --out | prescreen candidate report |
| scan | --report-file | --out | category-count scan report |
| scoring show | --report-file | none | score payload |
| scoring validate | --report-file --threshold | none | threshold validation payload |
| scoring compare | --baseline-report-file --candidate-report-file | none | score delta payload |

---

## 2. Exit Code Semantics

| Condition | Exit Code |
| --- | --- |
| Command success | 0 |
| Validation failure (`validate-build`) | 1 |
| Score threshold failure (`scoring validate`) | 1 |
| CLI usage or parser failure | 2 |

---

## 3. Output Directory Semantics

Default stage output root:

- `.ucx/<stage>`

Stage mapping:

- create-build -> `creation`
- review-build/review -> `review`
- validate-build/validate-fix -> `validate`
- remediate/remediate-fix -> `remediation`

Rule:

- if `--out` points to `.ucx`, CLI appends stage automatically.

---

## 4. Validation Control Contract

`validate-build` controls:

- `--tier1-only`: evaluate blocking tier1 checks only
- `--strict`: treat warnings as failures
- `--format json`: emit deterministic JSON status payload to stdout

JSON status payload fields:

- `report_path`
- `summary_path`
- `tier1_only`
- `strict`
- `errors`
- `warnings`
- `passed`

---

## 5. Examples

```bash
mcp validate-build --project /path/to/project --doc-type brd --layer 01_BRD --document /path/to/doc.md --tier1-only --format json
mcp validate-fix --project /path/to/project --doc-type brd --layer 01_BRD --document /path/to/doc.md --validation-report /path/to/validation_report.json
mcp remediate --project /path/to/project --doc-type brd --layer 01_BRD --document /path/to/doc.md
mcp remediate-fix --project /path/to/project --doc-type brd --layer 01_BRD --document /path/to/doc.md --remediation-report /path/to/remediation_report.json
mcp prescreen --document /path/to/docs/01_BRD
mcp scan --report-file /path/to/validation_report.json
mcp scoring show --report-file /path/to/validation_report.json
mcp scoring validate --report-file /path/to/validation_report.json --threshold 90
mcp scoring compare --baseline-report-file /path/to/a.json --candidate-report-file /path/to/b.json
```
