# Product Requirements Documents (PRD) — Layer 2

## Overview

PRDs define product features, user personas, and acceptance criteria as the
second step in the SDD v3.2 workflow. Each PRD corresponds to one BRD iteration cycle.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

## C4 Model Mapping

PRD is the **Container** level in the C4 architecture model. Content describes
product features and functional blocks — not business environment (Context),
component details (Component), or implementation details (Code).

```text
Context (BRD)    — business environment, actors, boundaries
  └─ EARS/BDD    — formalize Context→Container transition
Container (PRD)  — product features, functional blocks                 ← this layer
  └─ ADR         — decisions that shape Component architecture
Component (SPEC) — component interfaces, data models, behavior contracts
  └─ TDD         — test case definitions validating SPEC contracts
  └─ IPLAN       — execution plan bridging TDD to Code
```

## Files

| File | Purpose |
|------|---------|
| `PRD-TEMPLATE.yaml` | Single source of truth — template with embedded authoring guidance |
| `PRD-00_index.md` | PRD registry — tracks planned and active PRDs per project |

## Template Sync Rule

**IMPORTANT**: `PRD-TEMPLATE.yaml` exists in two locations that must stay in sync:

| Location | Role |
|----------|------|
| `ai_dev_flow_v3/02_PRD/PRD-TEMPLATE.yaml` | **Canonical source** — edit here |
| `mcp_sdd/templates/PRD-TEMPLATE.yaml` | **Runtime copy** — used by MCP tools |

After any change to the canonical source, copy it to the runtime location:

```bash
cp ai_dev_flow_v3/02_PRD/PRD-TEMPLATE.yaml mcp_sdd/templates/PRD-TEMPLATE.yaml
```

## MCP Tools (mcp_sdd)

All operations run through the `sdd-lifecycle` MCP server:

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate PRD from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | EARS-Ready score (>=90/100 to proceed to EARS) |
| `sdd_consistency` | Cross-document traceability check |
| `sdd_next_action` | Lifecycle advisor — recommends next step |

## Element IDs

Hash-based, content-derived IDs scoped to PRD content (not BRD):

```text
Format: PRD.{doc_id}.{section_id}.{hash}
Example: PRD.01.09.b3f2
```

Algorithm: SHA256 of `"{doc_id}:{section_id}:{title}:{description}"`, first 4 hex chars.
See template `metadata.id_standard` for details.

## Upstream Traceability

Each PRD links to its source BRD via `@brd:` tags using BRD hash-based IDs:

```text
@brd: BRD.NN.07.xxxx    (links to BRD functional requirement)
@brd: BRD.NN.08.xxxx    (links to BRD ADR topic)
```

## Archive

`PRD_v1_archive/` contains deprecated files from the previous dual-file template
approach. See `PRD_v1_archive/README.md` for migration details.
