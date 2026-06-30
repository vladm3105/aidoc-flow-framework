# Traceability — SDD

## Traceability Chain

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → SPEC (L6) → TDD (L7) → IPLAN (L8) → Code
```

## Necessary-upstream tagging

Each layer cites only its **necessary upstream** (`required_tags` in
`LAYER_REGISTRY.yaml`) — **not** the cumulative closure of every preceding
layer. Deeper lineage is discoverable transitively (one hop per layer, or
`tools/trace_walk.py` for a one-shot query).

```
Layer 1 (BRD):   —
Layer 2 (PRD):   @brd
Layer 3 (EARS):  @prd
Layer 4 (BDD):   @ears
Layer 5 (ADR):   @ears @bdd
Layer 6 (SPEC):  @ears @bdd @adr
Layer 7 (TDD):   @ears @bdd @adr @spec
Layer 8 (IPLAN): @spec @tdd
```

`required_tags` is the **minimum trace-resolution set**: a layer MAY
additionally carry provenance tags (e.g. a platform ADR recording `@brd`/`@prd`
in its `context`) but is not required to. Reverse lookup ("which BRD does
SPEC-07 trace to?") walks the chain transitively, not a local tag — run
`tools/trace_walk.py <ID>` for that one-shot backward query, or consult the
generated **forward-coverage matrix** `docs/TRACEABILITY_MATRIX.md` (produced by
`tools/sdd_coverage.py <docs_root>`; CFB-PR-2) for the forward direction — "which
SPEC/IPLAN realizes this BRD requirement?". Both read the same `@`-tag graph, so
the forward matrix and the backward walker never disagree. The matrix is
**generated/regenerable — never hand-edited.**

> *Origin:* NECESSARY-UPSTREAM-001 (spec `0.15.2` → `0.16.0`) replaced the
> former cumulative-trace contract — every downstream layer redeclaring every
> upstream layer — after it caused trace fabrication when an upstream layer was
> genuinely absent from a project. See `governance/REVIEW_TEAM.md`
> §"Necessary upstream + transitive trace".

> **Cross-layer cardinality (CLEANUP-PR-F item 18):** doc numbers are
> per-layer sequential and INDEPENDENT across layers. One BRD MAY drive
> multiple PRDs; one PRD MAY cite multiple BRDs. The url-shortener
> example's 1:1 numbering is coincidence, not contract. See
> `framework/governance/ID_NAMING_STANDARDS.md` §Cross-layer cardinality.

## Upstream/Downstream Validation

| Layer | Required Upstream Tags | Validated Downstream |
|-------|----------------------|---------------------|
| BRD | — | PRD |
| PRD | @brd | EARS |
| EARS | @prd | BDD |
| BDD | @ears | ADR |
| ADR | @ears, @bdd | SPEC |
| SPEC | @ears, @bdd, @adr | TDD |
| TDD | @ears, @bdd, @adr, @spec | IPLAN |
| IPLAN | @spec, @tdd | Code |

## Layer Readiness Gates

Each layer must achieve a readiness score >=90/100 before generating its immediate downstream artifact:

| Gate | Score | Criteria |
|------|-------|----------|
| PRD-Ready | >=90 | BRD completeness in business objectives, requirements, scope |
| EARS-Ready | >=90 | PRD completeness in features, user stories, domain clarity |
| BDD-Ready | >=90 | EARS syntax compliance, atomicity, testability, spec_trace links |
| ADR-Ready | >=90 | BDD scenario coverage, Gherkin quality, edge cases |
| TDD-Ready | >=90 | SPEC interface clarity, data model, behavior contracts |
| IPLAN-Ready | >=90 | TDD test case coverage, threshold definitions, execution order |
| EXEC-Ready | >=90 | IPLAN file manifest completeness, execution commands, session handoff |

## Cross-Document Dependencies

- `@depends: TYPE-NN` — Hard prerequisite. Downstream cannot exist without upstream.
- `@discoverability: TYPE-NN` — Related document for AI search context.
- `@threshold: TYPE.NN.key` — Performance or quality threshold reference.

## Reuse (satisfied-by-reference) — REUSE-MANIFEST-001

A brownfield project may **reuse an existing upstream artifact** instead of
re-authoring it. A reused doc declares, in frontmatter:

```yaml
reuse:
  state: referenced            # default: authored
  target: PRD-01@<commit>      # in-repo doc_id or path, pinned to a commit
  rationale: "reuse the platform PRD"
```

Semantics:

- **Satisfied by reference, not re-audited.** A `referenced` doc's elements are
  exempt from the coverage gates (`COV01`/`COV02` skip them) — they are reused
  as-is, not realized downstream. The linter emits one **`REUSE01`** advisory per
  referenced doc to keep every reuse visible.
- **Target must be in-repo + pinned** (`<doc_id|path>@<commit>`, commit = 7–40
  hex). A live URL, an unpinned target, or a target that does not resolve in-repo
  is a **`REUSE02`** error. Live external URLs belong in `@discoverability` only,
  never as the trace target.
- **Full-prefix rule.** A reused doc carries its own outbound upstream `@`-tags,
  so its **entire upstream lineage must also be present in-repo and `referenced`**
  — reuse the chain up to the boundary, not a single dangling doc. An upstream
  tag to an absent doc is a (correct) `TRACE-RES-001` finding (incomplete reuse).
- **No free readiness score.** A referenced layer is *present + linked* but was
  not authored/audited here, so the authoring/audit flow MUST NOT grant it an
  authored-quality (≥90) readiness score. (The deterministic lint records the
  reuse; the audit-skill enforcement of this rule is a follow-on.)
