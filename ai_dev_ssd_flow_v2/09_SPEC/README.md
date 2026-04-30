# Technical Specifications (SPEC) — Layer 9

## Overview

SPEC defines implementation-ready specifications at the C4 Code level.
SPEC is an **orchestrator** that routes to subtypes based on `deliverable_type`.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code

## C4 Model Position — CODE LEVEL

SPEC is the **C4 Code level** — the deepest zoom in the C4 architecture model.
"Code level" means the most detailed zoom for ANY deliverable type — not just source code.

```text
Context (BRD)    — business environment, actors, boundaries
Container (PRD)  — product features, functional blocks
Component (SYS)  — system structure, interfaces, quality attributes
Code (SPEC)      — implementation-ready specifications                 ← this layer
  └─ TSPEC       — test specifications
  └─ TASKS       — implementation task breakdown
```

## Subtype Routing

SPEC routes to specialized subtypes based on `deliverable_type` (set at BRD Layer 1):

| deliverable_type | Subtype | Output | CTR Required | Readiness Score |
|-----------------|---------|--------|-------------|-----------------|
| `code` (default) | [CSPEC](./CSPEC/) | Source code specs | Yes | TASKS-Ready |
| `document` | [DSPEC](./DSPEC/) | Documentation specs | No | DOC-Ready |
| `ux` | [UXSPEC](./UXSPEC/) | UX/wireframe specs | Optional | DESIGN-Ready |
| `risk` | [RISKSPEC](./RISKSPEC/) | Risk matrix specs | No | RISK-Ready |
| `process` | [PROCSPEC](./PROCSPEC/) | SOP/runbook specs | Optional | PROC-Ready |

## Files

| File | Purpose |
|------|---------|
| `SPEC-TEMPLATE.yaml` | Single source of truth — parent orchestrator template |
| `SPEC-00_index.md` | SPEC registry |
| `CSPEC/` | Code specification subtype (10 sections) |
| `DSPEC/` | Documentation specification subtype (8 sections) |
| `UXSPEC/` | UX specification subtype |
| `RISKSPEC/` | Risk specification subtype |
| `PROCSPEC/` | Process specification subtype |

## Template Sync Rule

| Location | Role |
|----------|------|
| `ucx_flow_v3/09_SPEC/SPEC-TEMPLATE.yaml` | **Canonical source** — edit here |
| `mcp_sdd/templates/SPEC-TEMPLATE.yaml` | **Runtime copy** — used by MCP tools |

```bash
cp ucx_flow_v3/09_SPEC/SPEC-TEMPLATE.yaml mcp_sdd/templates/SPEC-TEMPLATE.yaml
```

## MCP Tools (mcp_sdd)

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate SPEC from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | TASKS-Ready/DOC-Ready score |
| `sdd_consistency` | Cross-document traceability check |

## Element IDs

```text
Format: SPEC.{doc_id}.{section_id}.{hash}
Example: SPEC.01.05.d8e2
```

## Diagram Tags

C4 Code level: `c4-l4`, `dfd-l4`, class diagrams, sequence diagrams.

## Archive

`SPEC_v1_archive/` contains deprecated parent SPEC files.
Subtype directories (CSPEC, DSPEC, UXSPEC, RISKSPEC, PROCSPEC) are active.
