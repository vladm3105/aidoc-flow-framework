# `@`-Tag Syntax Reference

Per-layer punctuation, cardinality, and worked examples for the `@<layer>:`
trace tags. This is the **form** reference; the normative rules live elsewhere
and are cross-referenced, not duplicated:

- **Granularity** (element-level vs document-level) — owned by
  [`ID_NAMING_STANDARDS.md`](ID_NAMING_STANDARDS.md) §"Reference granularity"
  (GD-03). Enforced by `sdd_doc_lint REFGRAN01`.
- **Chain order, reverse-lookup, necessary-upstream contract** — owned by
  [`TRACEABILITY.md`](TRACEABILITY.md).

## Tag forms

A trace tag is `@<layer>: <id>` (one space after the colon). **BDD is the
exception** — a BDD doc carries its own upstream `@ears` trace as a structured
YAML `ears:` list per scenario (not an `@`-tag); see `BDD-TEMPLATE.yaml`. The
`@`-tag forms below govern every other element-declaring citation, including
downstream layers citing BDD scenarios via `@bdd:`. The `<id>` is:

| Target layer | Form | Why |
|---|---|---|
| BRD, PRD, EARS, BDD, ADR, TDD | **element** `TYPE.NN.SS.xxxx` | these layers declare canonical elements; functionality is defined in the element, not the document (GD-03) |
| SPEC, IPLAN | **document** `TYPE-NN` | element-ID-exempt — they declare no canonical elements (`ID_NAMING_STANDARDS.md` §element-ID exemption) |

`REFGRAN01` flags a document-level tag (`TYPE-NN`) to an element-declaring target.

## Cardinality — pipe-delimited multi-tags

A unit that traces to **multiple** upstream elements pipe-delimits repeated tags
on one logical line (the value capture terminates at `|`, so each is a distinct
tag):

```text
@ears: EARS.01.03.aaaa | @ears: EARS.01.03.bbbb | @ears: EARS.01.03.cc41
```

This is the form for a **container** whose value is the **union of its
sub-units' element citations** (GD-03). (BDD is the exception — a BDD scenario
carries its `ears` as a structured YAML list, and a Feature's coverage is the
computed union of its scenarios, not a written tag; see `BDD-TEMPLATE.yaml`.) A
genuine whole-document dependency (no specific element) is stated in **prose**,
never a document-level trace tag.

## Carve-outs — NOT trace citations (document-level is correct)

These use the document form and are **exempt** from `REFGRAN01`:

- **Self-tag** — a document citing its own id (`@bdd: BDD-01` on `BDD-01`): an
  identifier, not a lineage citation.
- **Downstream forward-pointer** — a higher layer naming a lower one for
  navigation (`@tdd: TDD-01` as a "Downstream" hint on a SPEC): informational,
  points at a not-yet-or-elsewhere-realized layer.

## Provenance tag — `@chg: CHG-NN` (change back-reference)

`@chg:` is **not a trace tag**: it carries no lineage (CHG is a governance
overlay, not one of the 8 registry layers, and appears in no layer's
`required_tags` or `can_reference`). It is a **provenance back-reference** from
a modified artifact to the change record that authorized the edit:

- **Form:** `@chg: CHG-NN` — always document-level (`CHG-NN` matches the CHG
  record's `chg_id` in `CHG-TEMPLATE.yaml`; CHG declares no elements).
- **Carrier:** every artifact listed in the CHG's
  `implementation.artifacts_modified[]` with `change_type: modified` (created
  artifacts cite the CHG in their own Document Control origin; deleted
  artifacts obviously carry nothing).
- **Placement:** in the modified artifact's **traceability section**. One rule,
  no fallback: all eight layer templates declare that section, so a
  template-conformant artifact always has the slot. (An earlier wording offered
  a Document Control fallback "where the layer template has no traceability
  section" — unreachable, since none lacks one — and then added "anywhere the
  tag is discoverable", which cancelled both placements and left a **P1** check
  citing an undecidable rule. Two auditors would have graded the same artifact
  differently.)
- **Semantics:** without it, a modified artifact is an unsourced edit
  indistinguishable from a hand-edit. The CHG auditor check **C1** (P1)
  enforces it on every modified artifact; this section is the definition C1
  cites. Pipe-delimited cardinality (above) applies unchanged when one
  artifact was touched by several CHGs.

## Per-layer necessary-upstream tags

Each layer's `required_tags` (its direct upstream — see `TRACEABILITY.md`) use
the element form when the target is element-declaring:

| Layer | Necessary-upstream tag(s) | Example |
|---|---|---|
| PRD | `@brd` | `@brd: BRD.01.07.6c3f` |
| EARS | `@prd` | `@prd: PRD.01.09.1dbc` |
| BDD | `ears:` (structured YAML list per scenario — not an `@`-tag) | `ears: [EARS.01.03.5e2a, …]`; Feature coverage = computed union |
| ADR | `@ears @bdd` | `@bdd: BDD.01.03.8f4c` |
| SPEC | `@ears @bdd @adr` | `@adr: ADR.01.03.e5b1` |
| TDD | `@ears @bdd @adr @spec` | `@spec: SPEC-01` (doc-level — SPEC exempt) |
| IPLAN | `@spec @tdd` | `@tdd: TDD.01.04.a3c1`; `@spec: SPEC-01` (doc-level) |
