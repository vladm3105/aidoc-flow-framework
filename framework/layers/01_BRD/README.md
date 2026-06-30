# Business Requirements Documents (BRD) — Layer 1

## Overview

BRDs capture business objectives, stakeholder needs, and success criteria as the
first step in the SDD workflow. Each BRD *set* — a platform BRD plus its child
feature BRDs (linked by `@depends:`) — represents one MVP iteration cycle; a
cycle is not limited to a single BRD.

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
| `BRD-00_index.TEMPLATE.md` | BRD registry template — tracks planned and active BRDs per project |

## Lifecycle: MVP → PROD → NEW MVP

Each BRD *set* represents ONE iteration cycle (5-15 requirements per BRD). A set
is one platform BRD + its feature BRDs (typed via `brd_type`, linked by
`@depends:`); a single-BRD set is the common small case, not the only shape:

```text
Cycle = BRD set:
  BRD-01 (platform)
    ├── BRD-02 (feature, @depends: BRD-01)
    └── BRD-03 (feature, @depends: BRD-01)

BRD set (MVP) → Production v1 → Feedback → next BRD set (NEW MVP) → Production v2
```

- New features = New BRD (don't expand existing BRDs)
- Link cycles via `@depends: BRD-01` in traceability section
- Target: 200-400 lines per BRD instance

## Document Formats

BRDs are authored in YAML (`.yaml`). Documents are validated with cross-section
consistency rules. YAML format enables structured validation (required keys,
element ID format, empty section detection).

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
