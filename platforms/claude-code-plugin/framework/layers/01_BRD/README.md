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

### Project initiation: enumerate the roadmap

Before authoring cycle 1, capture the whole-project scope so later cycles are not
under-specified. The recommended (not mandated) home is the **`BRD-00` index
"Planned BRDs" table** — its natural place, which avoids colliding with a
consumer's top-level product-strategy `ROADMAP.md`:

1. Enumerate **every** planned MVP cycle as a **Planned BRDs** row — cycle, target
   PROD, and `@depends:` sequencing.
2. Author only the **current** cycle's BRD set in full; leave the rest as
   `Planned` / `Sketch` rows.

A **Sketch** is a scope-only future-cycle entry — a hypothesis of what a later BRD
will cover, captured as a Planned-BRDs row, not a separate file. A Sketch (and a
Planned row) is **trace-inert**: it carries only its document-level `BRD-NN` id and
`@depends:` for sequencing — **no element IDs, it is not in the `@`-tag graph, and
forward-coverage checks ignore it** (they scan a BRD's `## Functional Requirements`
elements, which a planned row has none of). Because `@depends:` is not a trace tag,
an active BRD may point `@depends: BRD-05` at a not-yet-authored planned row with no
traceability error. On **graduation** to a full BRD, the entry moves to the Document
Registry, gains element IDs, and enters the trace graph.

> A *standalone* scope-only BRD file (its own `BRD-NN_*.md` with only a few
> sections) is **not** supported yet — it would fail the required-section lint as an
> incomplete instance BRD. Until that form ships, keep sketches as Planned-BRDs rows.

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
> **Not verified end-to-end** until `rehash --check` (PROVISIONAL-IDS-002): engines emit stable opaque strings that *should* match this form. The SHA-256 form is the canonicalization target — see `ID_NAMING_STANDARDS.md`.

```text
Format: BRD.{doc_id}.{section_id}.{hash}
Example: BRD.01.07.a7f3
```

Algorithm: SHA256 of `"{doc_id}:{section_id}:{title}:{description}"`, first 4 hex chars (the canonicalization target; not verified until `rehash --check`).
Collision handling: extend to 8 chars. See template `metadata.id_standard` for details.
