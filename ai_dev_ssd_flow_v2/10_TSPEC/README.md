# Test Specifications (TSPEC) — Layer 10

## Overview

TSPEC is the aggregator for 6 test specification subtypes. It validates
SPEC (Layer 9) implementations through structured test categories.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code

## C4 Model Position

TSPEC validates Code (SPEC) — it is NOT a C4 level itself.

```text
Code (SPEC)      — implementation-ready specifications
  └─ TSPEC       — test specifications (validates SPEC)              ← this layer
  └─ TASKS       — implementation task breakdown
```

## 6 Test Specification Subtypes

| Subtype | Directory | Test Category | Scope |
|---------|-----------|--------------|-------|
| [UTEST](./UTEST/) | Unit | Component-level behavior |
| [ITEST](./ITEST/) | Integration | Contract/interaction validation |
| [STEST](./STEST/) | Smoke | Deployment critical-path |
| [FTEST](./FTEST/) | Functional | Quality-attribute validation |
| [PTEST](./PTEST/) | Performance | Load, stress, endurance, spike |
| [SECTEST](./SECTEST/) | Security | Threat/control validation |

## Files

| File | Purpose |
|------|---------|
| `TSPEC-TEMPLATE.yaml` | Single source of truth — parent aggregator template |
| `TSPEC-00_index.md` | TSPEC registry |

## Template Sync Rule

```bash
cp ai_dev_ssd_flow/10_TSPEC/TSPEC-TEMPLATE.yaml mcp_sdd/templates/TSPEC-TEMPLATE.yaml
```

## MCP Tools (mcp_sdd)

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate TSPEC from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | TASKS-Ready score (>=90/100) |

## Element IDs

```text
Format: TSPEC.{doc_id}.{section_id}.{hash}
Example: TSPEC.01.04.c3b1
```

## Archive

`TSPEC_v1_archive/` contains deprecated parent files. 6 subtype directories are active.
