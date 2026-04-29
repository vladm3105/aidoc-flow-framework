# Business Requirements Documents (BRD) — Layer 1

## Overview

BRDs capture business objectives, stakeholder needs, and success criteria as the
first step in the SDD v3.2 workflow. Each BRD represents one MVP iteration cycle.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

## C4 Model Mapping

BRD is the **Context** level in the C4 architecture model. Content describes the business
environment, actors, and system boundaries — not product features, architecture, or code.

```text
Context (BRD)    — business environment, actors, boundaries        ← this layer
Container (PRD)  — product features, functional blocks
  └─ EARS/BDD    — formalize Context→Container transition
  └─ ADR         — decisions that shape Component architecture
Component (SPEC) — component interfaces, data models, behavior contracts
  └─ TDD         — test case definitions validating SPEC contracts
  └─ IPLAN       — execution plan bridging TDD to Code
```

## Files

| File | Purpose |
|------|---------|
| `BRD-TEMPLATE.yaml` | Single source of truth — template with embedded authoring guidance |
| `BRD-00_index.md` | BRD registry — tracks planned and active BRDs per project |

## Template Sync Rule

**IMPORTANT**: `BRD-TEMPLATE.yaml` exists in two locations that must stay in sync:

| Location | Role |
|----------|------|
| `ai_dev_flow_v3/01_BRD/BRD-TEMPLATE.yaml` | **Canonical source** — edit here |
| `mcp_sdd/templates/BRD-TEMPLATE.yaml` | **Runtime copy** — used by MCP tools |

After any change to the canonical source, copy it to the runtime location:

```bash
cp ai_dev_flow_v3/01_BRD/BRD-TEMPLATE.yaml mcp_sdd/templates/BRD-TEMPLATE.yaml
```

## MCP Tools (mcp_sdd)

All operations run through the `sdd-lifecycle` MCP server:

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate BRD from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | PRD-Ready score (>=90/100 to proceed to PRD) |
| `sdd_consistency` | Cross-document traceability check |
| `sdd_preflight` | Environment readiness |
| `sdd_next_action` | Lifecycle advisor — recommends next step |

## Lifecycle: MVP → PROD → NEW MVP

Each BRD represents ONE iteration cycle (5-15 requirements):

```text
BRD-01 (MVP) → Production v1 → Feedback → BRD-02 (NEW MVP) → Production v2
```

- New features = New BRD (don't expand existing BRDs)
- Link cycles via `@depends: BRD-01` in traceability section
- Target: 200-400 lines per BRD instance

## Document Formats

BRDs are authored in YAML (`.yaml`). Both formats are validated by `sdd_validate` with cross-section consistency rules. YAML format enables structured validation (required keys, element ID format, empty section detection).

## BRD Types

| Type | Filename Pattern | Purpose |
|------|-----------------|---------|
| Platform | `BRD-NN_platform_{slug}.yaml` | Infrastructure, technology foundations |
| Feature | `BRD-NN_{feature_slug}.yaml` | Business features, user workflows |

## Element IDs

Hash-based, content-derived IDs (not sequential):

```text
Format: BRD.{doc_id}.{section_id}.{hash}
Example: BRD.01.07.a7f3
```

Algorithm: SHA256 of `"{doc_id}:{section_id}:{title}:{description}"`, first 4 hex chars.
Collision handling: extend to 8 chars. See template `metadata.id_standard` for details.

## Archive

`BRD_v1_archive/` contains deprecated files from the previous dual-file template
approach (MD + YAML templates, standalone creation/validation rules, legacy scripts).
See `BRD_v1_archive/README.md` for migration details.
