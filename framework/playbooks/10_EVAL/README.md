# 10_EVAL — EVAL Playbooks

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-27 |
| Author | Framework Maintainer |
| Framework Version | 0.53.1 |

## Purpose

Playbooks for authoring and managing EVAL (Layer 10) documents. EVAL documents
define what to test for each IPLAN, enforce the ID naming standard, and ensure
one-source-per-test-case traceability.

## Core Concept: EVAL Authoring

Each IPLAN owns exactly one EVAL document (1:1 mapping). The EVAL authoring
playbook creates the EVAL document from the IPLAN's scope and upstream sources.

```
IPLAN Completed
  └── Author EVAL document
      ├── Extract test cases from TDD/BDD sources
      ├── Assign independent element IDs (EVAL.NN.SS.xxxx)
      ├── Build coverage matrix
      └── Register in EVAL-00 index
```

## Playbooks

| Playbook | Role | Purpose |
|----------|------|---------|
| `author.md` | EVAL Author | Creates EVAL documents from IPLANs |

## Key Rules

- **1:1 Mapping**: Each IPLAN owns exactly one EVAL document
- **ID Standard**: Test case IDs follow `EVAL.NN.SS.xxxx` (independent from source)
- **One Source Per Test Case**: Each test case maps to exactly one upstream element
- **Coverage**: Every test case must appear in the coverage matrix
- **Traceability**: Source info lives in `source_type` + `source_id` fields, not in the ID

## Directory Structure

```
docs/sdd/10_EVAL/
  EVAL-00_index.md              # master index
  EVAL-NN/
    EVAL-NN.yaml                # active strategy
    reports/
      EVAL-NN-RPT-NNN.yaml      # eval cycle reports
```

## Related

- **Template**: `framework/layers/10_EVAL/EVAL-TEMPLATE.yaml`
- **Report Template**: `framework/layers/10_EVAL/EVAL-RPT-TEMPLATE.yaml`
- **ID Standard**: `framework/governance/ID_NAMING_STANDARDS.md`
- **Lint Rules**: `framework/governance/LINT_RULES.md` §Evaluation (L10)
- **Verification Playbooks**: `playbooks/10_IPLAN_VERIFY/` (evaluator, verifier, etc.)
