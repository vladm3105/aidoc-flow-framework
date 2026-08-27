# Business Requirements Documents (BRD) — Layer 1

## Overview

BRDs capture business objectives, stakeholder needs, and success criteria as the
first step in the SDD workflow. Each BRD *set* — a platform BRD plus its child
feature BRDs (linked by `@depends:`) — represents one MVP iteration cycle; a
cycle is not limited to a single BRD.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

## Seed input

The BRD is the point where the chain first accounts for the `seed/` tier — the
raw, human-authored source material a cycle starts from
(`../../README.md` inputs row; `../../docs/AIDOC.md` tier table). The seed is
governed by [`../../governance/SEED_CONTRACT.md`](../../governance/SEED_CONTRACT.md)
(GD-08):

- **The seed is frozen historical input.** Once this cycle's first BRD is
  authored, seed files are not edited to resolve findings — a "the seed says X,
  the chain does not" finding is resolved **in the BRD**, never by amending the
  seed. New human input arrives through the gated `chg/` tier.
- **Every seed claim gets a total disposition** in the BRD's `seed_disposition:`
  section: `absorbed` (names ≥1 BRD element ID), `rejected` (rationale), or
  `deferred` (rationale + target cycle). A claim first appearing at PRD or later
  with no BRD row is a gap.

The `seed_disposition:` carrier ships `_required: false` (additive), so BRDs
authored before the contract are unaffected. `SEED01` checks the ledger is
well-formed and each `absorbed` target resolves; the auditor lens (C8) owns
completeness against the seed prose.

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
| `BRD-TEMPLATE.yaml` | **Default** — full template with embedded authoring guidance (`_guidance`, `_note`, `_example`, `_antipatterns` fields). Self-documenting for AI agents. |
| `BRD-MVP-TEMPLATE.yaml` | Skeleton — stripped-down structural form with fill-in-the-blank fields. No embedded guidance. **Do not use standalone:** the authoring agent MUST also read the full template for section-level expectations and authoring conventions. |
| `BRD-00_index.TEMPLATE.md` | BRD registry template — tracks planned and active BRDs per project |

### Template selection

The full `*-TEMPLATE.yaml` is the **default** for all cycles — it carries the embedded
guidance an AI agent needs to author a valid document without external reference.

The MVP `*-MVP-TEMPLATE.yaml` skeleton is an optional fast-pass for experienced
agents already familiar with the full template's conventions. Using it without also
reading the full template produces incomplete documents with missing context, empty
required sections, and incorrect element IDs. The agent MUST load both files when
using the MVP skeleton: the skeleton as the structural form, and the full template
as the reference for section-level expectations and authoring conventions.

| Cycle | Template | Rationale |
|-------|----------|-----------|
| **All cycles** (default) | `*-TEMPLATE.yaml` | Embedded guidance makes it self-documenting. Lower error rate, fewer validation failures. |
| **MVP** (experienced agents only) | `*-MVP-TEMPLATE.yaml` | Faster authoring if the agent has previously read the full template. Must also load the full template as a reference. |

## Lifecycle: MVP → PROD → NEW MVP

Each BRD *set* represents ONE iteration cycle of 5-15 requirements. A BRD document
**SHOULD** carry at most 5 functional requirements (GD-14), so a cycle needs at least
ceil(N/5) documents — a floor, not a ceiling; a set may hold more for reasons unrelated
to size. Note this fixes the cycle total at 5-15 *per cycle*: earlier wording here read
"5-15 per BRD", which for a multi-BRD set implied a far larger ceiling. A set
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
> **Verifiable on demand** via `rehash --check` (PROVISIONAL-IDS-002 Phase 1 — advisory `IDDRIFT01`, opt-in, not in the default lint): engines emit stable opaque strings; `rehash --check` recomputes a canonical BRD's §7 FR IDs against the SHA-256 form below and flags drift. Scoped *verifiable on demand*, not *verified*. See `ID_NAMING_STANDARDS.md`.

```text
Format: BRD.{doc_id}.{section_id}.{hash}
Example: BRD.01.07.a7f3
```

Algorithm: SHA256 of `"{doc_id}:{section_id}:{norm(title)}:{norm(description)}"`, first 4 hex chars (the canonicalization target; verifiable on demand via `rehash --check`). `norm()` is the normalization transform, and `governance/ID_NAMING_STANDARDS.md` is its **single source** — along with the byte-exact input assembly and the §7 FR field-extraction boundary. Do not re-specify it here.
Collision handling: extend to 8 chars. See template `metadata.id_standard` for details.
