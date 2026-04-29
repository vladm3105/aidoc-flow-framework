# Architecture Decision Records (ADR) — Layer 5

## Overview

ADRs document architecture decisions using the Context-Decision-Consequences
pattern. Each ADR addresses ONE decision, synthesizing inputs from PRD, EARS, and BDD.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code

## C4 Model Position

ADR is the **decision bridge** between Container (PRD) and Component (SYS).
It records architectural decisions that shape the Component-level design.

```text
Context (BRD)    — business environment, actors, boundaries
  └─ EARS/BDD    — formalize Context→Container transition
Container (PRD)  — product features, functional blocks
  └─ ADR         — decisions that shape Component architecture        ← this layer
Component (SYS)  — system structure, interfaces, quality attributes
  └─ REQ/CTR     — decompose Component→Code into atomic units
Code (SPEC)      — implementation-ready specifications
  └─ TSPEC       — test specifications
  └─ TASKS       — implementation task breakdown
```

## Files

| File | Purpose |
|------|---------|
| `ADR-TEMPLATE.yaml` | Single source of truth — template with embedded authoring guidance |
| `ADR-00_index.md` | ADR registry — tracks planned and active ADRs per project |
| `ADR-00_ai_powered_*.md` | Active ADR instance — framework architecture decision |
| `ADR-CTR_SEPARATE_FILES_POLICY.md` | Active ADR instance — contract file policy |

## Template Sync Rule

**IMPORTANT**: `ADR-TEMPLATE.yaml` exists in two locations that must stay in sync:

| Location | Role |
|----------|------|
| `ai_dev_ssd_flow/05_ADR/ADR-TEMPLATE.yaml` | **Canonical source** — edit here |
| `mcp_sdd/templates/ADR-TEMPLATE.yaml` | **Runtime copy** — used by MCP tools |

```bash
cp ai_dev_ssd_flow/05_ADR/ADR-TEMPLATE.yaml mcp_sdd/templates/ADR-TEMPLATE.yaml
```

## MCP Tools (mcp_sdd)

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate ADR from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | SYS-Ready score (>=90/100 to proceed to SYS) |
| `sdd_consistency` | Cross-document traceability check |
| `sdd_next_action` | Lifecycle advisor |

## ADR Status Lifecycle

ADR uses a **different status lifecycle** from other layers:

```text
Proposed → Accepted → Deprecated → Superseded
```

(NOT Draft/In Review/Approved)

| Status | SYS-Ready Score | Meaning |
|--------|-----------------|---------|
| Proposed | 70-89% | Decision under evaluation |
| Accepted | >=90% | Decision approved, ready for SYS |
| Deprecated | — | Decision no longer relevant |
| Superseded | — | Replaced by newer ADR |

## Element IDs

Hash-based, content-derived IDs scoped to ADR content:

```text
Format: ADR.{doc_id}.{section_id}.{hash}
Example: ADR.01.03.e5b1
```

## Upstream Traceability

ADR synthesizes inputs from all upstream layers (cumulative tags):

```text
@prd: PRD.NN.14.xxxx    (originating topic — PRD ADR elaboration)
@brd: BRD.NN.08.xxxx    (business-level topic origin)
@ears: EARS.NN.03.xxxx   (timing constraints informing decision)
@bdd: BDD.NN.03.xxxx     (integration/failure scenarios)
```

## Archive

`ADR_v1_archive/` contains deprecated template/rules files. Active ADR instances
remain in this directory. See `ADR_v1_archive/README.md` for migration details.
