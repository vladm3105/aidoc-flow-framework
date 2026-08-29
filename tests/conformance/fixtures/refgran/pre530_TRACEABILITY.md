# Traceability — SDD

## Traceability Chain

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → SPEC (L6) → TDD (L7) → IPLAN (L8) → Code
```

## Necessary-upstream tagging

Each layer cites only its **necessary upstream** (`required_tags` in
`LAYER_REGISTRY.yaml`) — **not** the cumulative closure of every preceding
layer. Deeper lineage is discoverable transitively (one hop per layer, or a
one-shot trace-walk query). The `tools/*.py` helpers this document names
(`trace_walk.py`, `sdd_coverage.py`) are a **reference implementation outside
the engine-agnostic spec** — the traversal they perform over the `@`-tag graph
is the normative capability; the scripts themselves are a convenience an engine
MAY provide.

```
Layer 1 (BRD):   —
Layer 2 (PRD):   @brd
Layer 3 (EARS):  @prd
Layer 4 (BDD):   ears (YAML carrier)
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

## Coverage gates (`sdd_doc_lint`)

The linter enforces element-level coverage over the `@`-tag graph (ELEMENT-COVERAGE-001):

- **Reference Granularity Principle (GD-03 / #502):** Citing an oracle layer (EARS requirements or BDD scenarios) in verification contexts (e.g. SPEC `upstream.bdd_references`, TDD `scenarios[].bdd_scenario`, inline `source: "@bdd: ..."`) MUST be element-level (`TYPE.NN.SS.xxxx`). Citing a document-level ID (e.g. `BDD-01`) for an oracle defeats element coverage computation. Conversely, citing design/decision units (ADR, SPEC, TDD, IPLAN) at document-level (e.g. `@adr: ADR-01`, `@spec: SPEC-01`) is permitted when referencing the design container as a whole.
- **`COV01` — forward coverage.** Every in-scope (`AUTHORED`) BRD functional requirement
  MUST reach ≥1 SPEC and ≥1 IPLAN downstream. No SPEC → error; SPEC-but-no-IPLAN → warning
  in `build`, error in `gate-code`. Escaped FRs never block: a `Future` band (deferred) or a
  `realized_by: <LAYER>` token (realized off the SPEC path).
- **`COV02` — backward coverage.** The dual: every EARS / BDD element must be realized by a
  downstream doc in its **realizing set** (or explicitly deferred), computed corpus-wide. The
  realizing set is a curated one-hop map (EARS → BDD/SPEC/TDD; BDD → SPEC/TDD — ADR is a
  decision layer and does not realize); an element cited by any doc in its set passes. The
  **normative map is `registry/LAYER_REGISTRY.yaml` `realizing_layers`** (a platform linter
  mirrors it); the element-level treatment is also shown in
  `framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md`.
- **`COV03` — phase-leak advisory (the inverse of `COV01`'s escape).** A **`Future`-banded
  (deferred) FR that IS realized downstream** by its realizing layer draws a **`WARNING`** —
  something scoped for a *next MVP cycle* is being pulled into the current build. **Advisory
  only, in both modes** (never blocks): scope pull-forward is legitimate; the resolution is
  to re-band the FR `P1`/`P2` for the current cycle or confirm the deferral is intentional. A
  `realized_by:` FR is a positive coverage claim, not a leak, and is never flagged. Cross-cycle
  leaks need no gate — later-cycle BRDs are `Planned`/`Sketch` (trace-inert), so their
  elements are not in the graph. *Origin:* D54-F13 / D-0055.

`reuse: referenced` docs are exempt from all three (their elements are reused as-is, not
realized here). Run any gate over a `<docs_root>` with `python -m sdd_doc_lint <docs_root>`.

## Element-ID content-drift check (`IDDRIFT01` — opt-in, advisory)

Under Model 2 (D-0061), an element ID's 4-hex hash **is** the mint-time content
fingerprint. `IDDRIFT01` (PROVISIONAL-IDS-002 Phase 1) verifies that: for a BRD's
§7 gated FR elements it recomputes `SHA256("{doc}:{sec}:{norm(title)}:{norm(description)}")[:N]`
(the normative transform + extraction boundary in `ID_NAMING_STANDARDS.md`) and
warns when the ID's declared hash no longer matches — a **content drift** since the
ID was minted, or a **canonical leak** (the ID was never the real hash).

- **Opt-in + advisory.** Runs ONLY via `python -m sdd_doc_lint.rehash --check
  <docs>` — it is **NOT** part of the default `sdd_doc_lint` pass, so the default
  gate + the example-corpus lint are byte-identical. `IDDRIFT01` is `WARNING`-level
  and never blocks.
- **`canonical`-gated.** A doc declaring `id_state: provisional` is exempt (its IDs
  are declared placeholders, not hashes).
- **Phase-1 scope: BRD §7 FR elements only.** Other BRD sections and the other seven
  layers are not yet verified — later PROVISIONAL-IDS-002 phases extend the
  extractor, add `rehash --fix`, reconcile the corpus, and may promote the advisory
  to a gate. See `plans/PROVISIONAL-IDS-002-PLAN.md`.

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
| ADR-Ready | >=90 | BDD scenario coverage, scenario (YAML) quality, edge cases |
| SPEC-Ready | >=90 | ADR decision completeness, alternatives, consequences |
| TDD-Ready | >=90 | SPEC interface clarity, data model, behavior contracts |
| IPLAN-Ready | >=90 | TDD test case coverage, threshold definitions, execution order |
| EXEC-Ready | >=90 | IPLAN file manifest completeness, execution commands, session handoff |

## Cross-Document Dependencies & Governance Tags

- `@depends: TYPE-NN` — Hard prerequisite. Downstream cannot exist without upstream.
- `@discoverability: TYPE-NN` — Related document for AI search context.
- `@chg: CHG-NN` — Provenance back-reference to authorizing change record.
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
  reuse; the audit-engine enforcement of this rule is a follow-on.)
