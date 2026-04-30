# EARS Requirements — Layer 3

## Overview

EARS (Easy Approach to Requirements Syntax) formalizes business and product
requirements into precise, testable statements using WHEN-THE-SHALL-WITHIN syntax.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

## C4 Model Position

EARS is a **refinement step** that formalizes the transition from Context (BRD) to
Container (PRD). It does not have its own C4 level — it translates requirements
into atomic, testable logic for downstream BDD scenarios.

```text
Context (BRD)    — business environment, actors, boundaries
  └─ EARS/BDD    — formalize Context→Container transition              ← this layer
Container (PRD)  — product features, functional blocks
  └─ ADR         — decisions that shape Component architecture
Component (SPEC) — component interfaces, data models, behavior contracts
  └─ TDD         — test case definitions validating SPEC contracts
  └─ IPLAN       — execution plan bridging TDD to Code
```

## Files

| File | Purpose |
|------|---------|
| `EARS-TEMPLATE.yaml` | Single source of truth — template with embedded authoring guidance |
| `EARS-00_index.md` | EARS registry — tracks planned and active EARS documents per project |

## Template Sync Rule

**IMPORTANT**: `EARS-TEMPLATE.yaml` exists in two locations that must stay in sync:

| Location | Role |
|----------|------|
| `ucx_flow_v3/03_EARS/EARS-TEMPLATE.yaml` | **Canonical source** — edit here |
| `mcp_ucx/templates/EARS-TEMPLATE.yaml` | **Runtime copy** — used by MCP tools |

After any change to the canonical source, copy it to the runtime location:

```bash
cp ucx_flow_v3/03_EARS/EARS-TEMPLATE.yaml mcp_ucx/templates/EARS-TEMPLATE.yaml
```

## MCP Tools (mcp_ucx)

All operations run through the `sdd-lifecycle` MCP server:

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate EARS from template |
| `sdd_validate` | Structural + EARS parity validation (trigger + actor clause) |
| `sdd_score_validate` | BDD-Ready score (>=90/100 to proceed to BDD) |
| `sdd_consistency` | Cross-document traceability check |
| `sdd_next_action` | Lifecycle advisor — recommends next step |

## EARS Syntax Patterns

| Pattern | Trigger | Format |
|---------|---------|--------|
| Event-Driven | External event | WHEN [trigger], THE [component] SHALL [action] WITHIN [timing] |
| State-Driven | System state | WHILE [state], THE [component] SHALL [behavior] WITHIN [context] |
| Unwanted | Error condition | IF [error], THE [component] SHALL [recovery] WITHIN [timing] |
| Ubiquitous | Always applies | THE [component] SHALL [behavior] for [scope] |

## Element IDs

Hash-based, content-derived IDs scoped to EARS content:

```text
Format: EARS.{doc_id}.{section_id}.{hash}
Example: EARS.01.03.c4d8
```

Algorithm: SHA256 of `"{doc_id}:{section_id}:{title}:{description}"`, first 4 hex chars.
See template `metadata.id_standard` for details.

## Upstream Traceability

Each EARS links to source PRD and BRD via cumulative tags:

```text
@prd: PRD.NN.09.xxxx    (links to PRD functional requirement)
@brd: BRD.NN.07.xxxx    (links to BRD functional requirement)
```

## Archive

`EARS_v1_archive/` contains deprecated files from the previous dual-file template
approach. See `EARS_v1_archive/README.md` for migration details.
