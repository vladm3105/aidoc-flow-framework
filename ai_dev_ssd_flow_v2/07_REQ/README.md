# Atomic Requirements (REQ) — Layer 7

## Overview

REQ defines atomic, single-testable-concept requirements decomposed from SYS.
Each REQ document addresses ONE specific behavior that can be independently implemented and tested.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code

## C4 Model Position

REQ decomposes Component (SYS) into atomic units for Code (SPEC) implementation.
REQ is NOT a C4 level — it is a decomposition step.

```text
Component (SYS)  — system structure, interfaces, quality attributes
  └─ REQ/CTR     — decompose Component→Code into atomic units        ← this layer
Code (SPEC)      — implementation-ready specifications
  └─ TSPEC       — test specifications
  └─ TASKS       — implementation task breakdown
```

## Files

| File | Purpose |
|------|---------|
| `REQ-TEMPLATE.yaml` | Single source of truth — template with embedded authoring guidance |
| `REQ-00_index.md` | REQ registry — tracks planned and active requirements per project |

## Template Sync Rule

| Location | Role |
|----------|------|
| `ai_dev_ssd_flow/07_REQ/REQ-TEMPLATE.yaml` | **Canonical source** — edit here |
| `mcp_sdd/templates/REQ-TEMPLATE.yaml` | **Runtime copy** — used by MCP tools |

```bash
cp ai_dev_ssd_flow/07_REQ/REQ-TEMPLATE.yaml mcp_sdd/templates/REQ-TEMPLATE.yaml
```

## MCP Tools (mcp_sdd)

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate REQ from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | SPEC-Ready score (>=90/100 to proceed to SPEC) |
| `sdd_consistency` | Cross-document traceability check |

## Atomic Requirement Principle

**ONE requirement per document.** Each REQ must:
- Define exactly one specific, verifiable behavior
- Be independently implementable and testable
- Use statement format: "The system SHALL [precise, atomic behavior]"

## Element IDs

```text
Format: REQ.{doc_id}.{section_id}.{hash}
Example: REQ.01.03.a1c7
```

## Upstream Traceability

Cumulative tags (Layer 7 — all upstream layers):

```text
@sys: SYS.NN.04.xxxx    (system requirement)
@adr: ADR.NN.03.xxxx    (architecture decision)
@bdd: BDD.NN.03.xxxx    (test scenarios)
@ears: EARS.NN.03.xxxx   (formal requirements)
@prd: PRD.NN.09.xxxx    (product features)
@brd: BRD.NN.07.xxxx    (business requirements)
```

## Archive

`REQ_v1_archive/` contains deprecated files. See `REQ_v1_archive/README.md`.
