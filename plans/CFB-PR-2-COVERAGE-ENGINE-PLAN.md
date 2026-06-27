# CFB-PR-2 — Coverage engine (`ENG-FWD-COVERAGE` + `D54-F13` + `D54-F05`)

> Wave-2 of `CONSUMER-FEEDBACK-001`. The largest single child: a `@`-tag-graph
> **coverage engine** answering "is every requirement realized, and nothing
> out-of-phase?" — forward + backward + phase + BDD-rollup. Depends on PR-1
> (corrected trace chain, merged `8e001192`). Co-dependent with PR-3
> (ref-granularity makes element-level forward coverage computable).

| Field          | Value                                                |
| -------------- | ---------------------------------------------------- |
| Task           | CFB-PR-2 (coverage engine)                           |
| Type           | feature (tooling + spec)                             |
| Status         | READY — 2026-06-27 · 3 independent passes (P2 design-gaps, P4 soundness, P6 confirming) + 4 self; false-premise class closed |
| Parent         | `plans/CONSUMER-FEEDBACK-001-PLAN.md` (PR-2)         |
| Depends on     | PR-1 (merged); **PR-3 lands with sub-PR 2a** (ref-granularity) |
| Version impact | framework **MINOR** (new `SPEC-00` coverage section, GATE-06, phase tag schema, BRD FR-annotation rule) + tooling. Bump via the fixed `bump_version.py` (#182). |

## Objective

Build the forward/completeness half of traceability the framework lacks:
`trace_walk.py` is **backward/transitive only** and collapses tags to doc-ids.
Nothing asserts forward that **every BRD functional requirement reaches ≥1 SPEC
and ≥1 IPLAN**, that **every EARS/BDD element has a covering SPEC/TDD or an
explicit deferral**, or that **no out-of-phase item leaked into an in-phase
plan**. This engine adds those checks + the BDD doc-set roll-up + a generated
trace matrix.

## Implementation reality (grounded — Pass-4 verified; every DD obeys these)

- **R-a — The linter parses frontmatter YAML only; the body is flat regex.**
  `sdd_doc_lint` reads frontmatter via `_extract_frontmatter` (`__init__.py:738`)
  and harvests element IDs + tags by **line-by-line regex** (`_ELEM_ID`/`_TAG`).
  There is **no parsed body tree / YAML path** for an authored artifact.
- **R-b — Authored artifacts are Markdown prose, not the template YAML.**
  `examples/url-shortener/docs/01_BRD/BRD-01.md` has `## 7. Functional
  Requirements` (`:158`) with FRs as bullets `**BRD.01.07.6c3f — Title**
  (P1, …)` (`:172`). Priority is **inline prose `(P1|P2|Future, …)`**, not a
  YAML `priority:` field. §7 ALSO contains an "Acceptance criteria:" sub-block
  with its own element IDs under the same `.07.` ordinal (`:195-208`).
- **R-c — No edge set is retained.** `element_index` (`:944,956-964`) is a
  presence map `elem → host_doc` that **excludes downstream citations**
  (`:954-955`); citation edges are computed per-line and discarded. The
  bidirectional adjacency forward coverage needs is **net-new**.
- **R-d — The CLI has no mode/skip surface.** `__main__.py` exposes only
  `paths`, `--registry`, `--format`; `_check_trace_resolution` runs
  unconditionally. `--mode`/`--skip-*` are **net-new args** (the only existing
  skip/mode precedent lives in a *different* subsystem — the hermes
  orchestrator `sdd_config.yaml` + plugin `gate-check` skill).
- **R-e — PR-1 names no matrix.** Merged `governance/TRACEABILITY.md:29-30`
  says reverse lookup "walks the chain transitively, **not a local tag**"
  (i.e. `trace_walk.py`). There is no pre-existing matrix contract to honor.

## Resolved design decisions (folded from Pass-2 + corrected by Pass-4)

**DD-1 — Engine host + the graph is NET-NEW.** Host = **`sdd_doc_lint`** (the
only whole-corpus tool). Reuse its frontmatter parse + `_ELEM_ID`/`_TAG`
regexes + the doc/element **presence** indexes. **Build** a new bidirectional
element-level **edge graph** (R-c: today's `element_index` excludes downstream
citations — the adjacency does not exist yet; "inverse traversal of the existing
edge set" was wrong). Refactor `trace_walk`'s `_TAG` + `_locate_doc` into a
shared module; the matrix emitter is a new thin reporter `tools/sdd_coverage.py`
consuming the shared core. **Gate the coverage check to whole-corpus runs** —
skip on the single-file `on_author` invocation (else "FR reaches no SPEC"
false-fires because no SPECs are in a one-file corpus).

**DD-2 — Extensible `covered_state` enum (PR-5 extension point; R2-HIGH).**
`covered_state ∈ { authored | deferred | realized_by:<layer> |
satisfied_by_reference }`. **`authored`** = the success state: the element
reaches ≥1 downstream realizing doc. `deferred` / `realized_by` /
`satisfied_by_reference` are the non-blocking **escapes**. The "covered?"
predicate dispatches on this enum; the gate blocks only when state is `authored`
AND the required downstream is absent. PR-2 ships `authored`/`deferred`/
`realized_by`; **`satisfied_by_reference` is an enum member, stubbed** (PR-5
adds the member's logic — not a rewrite).

**DD-3 — FR identification by markdown heading-context (not YAML path).** R-a/R-b
make "scope by YAML path" impossible and the bare `.07.` ordinal ambiguous (§7
mixes FRs and acceptance-criteria elements). Mechanism: **extend the line scanner
to track the current `## N. <Heading>` context + in-section sub-block boundary.**
An element ID is a gated **FR** iff its line is under `## … Functional
Requirements` AND before that section's `Acceptance criteria:` **label line**
(a plain prose boundary line, not a `##` heading — confirmed in `BRD-01.md:195`).
The line scanner already tracks `## N.` heading context (`_SECTION_HEADING`,
`:106`); this adds an in-section sub-block toggle on the literal
`Acceptance criteria:` line. The BRD template formalizes both markers (the FR
bullet form + the `Acceptance criteria:` label) so the boundary is reliable.
Objectives / stakeholders / risks / acceptance-criteria elements are NOT gated.

**DD-4 — Priority/phase band parsed from the FR-bullet annotation (R-b).** The
band is the **inline `(P1 | P2 | Future[, <note>])`** on the FR bullet
(`BRD-01.md:172`). PR-2 **formalizes this annotation in the BRD template** as the
machine-readable band (the allowed values already live single-sourced in
`priority_definitions`, `BRD-TEMPLATE.yaml:529-532`; the template gains a rule
"every FR bullet MUST carry `(P1|P2|Future, …)`"). The gate parses it via a
regex on the FR line. **`Future` = the deferral signal** (no new YAML field; no
value duplication — the registry phase-schema entry *references*
`priority_definitions`, it does not re-enumerate). Reject the element-ID-segment
option. *Note (Pass-6):* the structured template schema also carries
`requirements[].priority:` as a YAML field (`BRD-TEMPLATE.yaml:538`); that and
the authored markdown `(P1, …)` annotation are two surfaces for the same value —
the **annotation is the authored-artifact form the flat-token gate reads**;
the template rule keeps them in sync (no third source). Integrates with the
existing `BRD-XS-002` rule ("phase names + count match between scope and
implementation", `BRD-TEMPLATE.yaml:159`).

**DD-5 — Escape taxonomy (reconciled with DD-6).** An FR/EARS/BDD element does
NOT block if its `covered_state` is `deferred` (band `Future`),
`realized_by:<layer>` (ADR-only decision / NFR / infra with no dedicated SPEC),
or (PR-5) `satisfied_by_reference`. `realized_by` ships; `satisfied_by_reference`
stubbed.

**DD-6 — Run-mode-dependent severity (the escapes carve out the NO-SPEC block).**
The check takes a **run-mode** (`--mode {build | gate-code}`, default `build` —
a net-new CLI arg per R-d). Same finding, two severities; **escaped FRs never
block** (fixes the Pass-4 DD-5⊥DD-6 contradiction):

| finding | `build` | `gate-code` |
|---|---|---|
| escaped FR (Future / realized_by / satisfied_by_reference), no SPEC/IPLAN | warning | warning |
| in-scope (P1/P2, no escape) FR, no IPLAN | **warning** | **block** |
| in-scope (P1/P2, no escape) FR reaching **NO SPEC** | **block** | **block** |
| a deferred (`Future`-band) FR that **reaches an IPLAN** in the corpus — built despite deferral (the D54-F13 leak) | **block** | **block** |

**Phase-leak grounding (Pass-6 fix — R-f).** The leak signal is **derived
entirely from signals that exist**: the FR band (DD-4, from the `(Future, …)`
annotation) + the forward trace (does that `Future` FR reach an IPLAN). **No
separate IPLAN "cycle" field is invented** — none exists (registry, IPLAN
template, and corpus carry no phase/cycle key; the only IPLAN "phase" is the
TDD Red/Green/Refactor build phase, which is orthogonal). The rule is symmetric
with row 1: a `Future` FR *without* an IPLAN is legitimate deferral (warning);
*with* an IPLAN it is a leak (block). The richer **scope-ledger reconciliation**
(BRD accepted-scope set vs the realized set) is a future enhancement, not v1.

**DD-7 — Matrix = a NEW generated artifact; create the cross-ref, don't fake it
(R-e).** PR-1 names no matrix, so there is no contract to honor. `sdd_coverage.py`
emits a generated **`docs/TRACEABILITY_MATRIX.md`** (underscore form, aligning to
the hermes `*_TRACEABILITY_MATRIX.md` convention; distinct from the governance
`TRACEABILITY.md`). **2a adds the cross-reference into `governance/TRACEABILITY.md`**
— amend its reverse-lookup note to "…walks the chain transitively (or consult the
generated `docs/TRACEABILITY_MATRIX.md` / `trace_walk.py`)" — turning a
non-existent contract into a real one. Generated/regenerable; never hand-edited.
BDD-rollup output is a section of the same file.

**DD-8 — Multi-`@brd` already parses; new work is OR-group + lint.** `_TAG`'s
`([^\s|]+)` terminates on `|`, so `@brd: X | @brd: Z` already `finditer`s as two
tags. New: (a) **OR-group-by-layer** in the coverage predicate (the
`required_tags` check at `:531` is set-membership only), and (b) the
**zero-downstream lint**. PR-2 *consumes* multi-`@brd`; **PR-3 `taglint` owns
enforcing** the punctuation.

**DD-9 — Corpus path to green (R-d; flags are net-new).** New blocking gates fire
on `examples/url-shortener/`. (a) Add **`--skip-coverage-gate`** as a net-new
`__main__.py` arg (the skip *pattern* exists only in the hermes/plugin gate
subsystem — model the behavior, not a sdd_doc_lint precedent) for the transient
migration window. (b) Coverage gaps are **not regen-able**; they close by adding
legitimate band annotations — the url-shortener FRs are all `P1`, so the corpus
step either confirms genuine SPEC/IPLAN coverage or annotates the few legitimate
gaps `(Future)` / `realized_by:` in the FR bullets (content authored via the BRD
skill, then re-cascade downstream).

## Scope

**In:** forward gate with the DD-6 severity split; the backward leg (the SPEC-00
`coverage` section and the GATE-06 check, BeeLocal #54); phase band + scope
reconciliation (D54-F13, DD-4);
BDD roll-up (D54-F05), multi-`@brd` consume + zero-downstream lint (DD-8),
generated matrix + the `TRACEABILITY.md` cross-ref (DD-7), `covered_state` enum
(DD-2), the **BRD FR-annotation formalization** (DD-3/DD-4), and the net-new
`--mode`/`--skip-coverage-gate` CLI args (DD-6/DD-9). Document-level binding for
SPEC/TDD/IPLAN.

**Also in (Pass-2 #F):** fix the two stale `Upstream:` lines in
`SPEC-00_index.TEMPLATE.md` (:27,:29) while that file is open for the coverage
section.

**Out of scope:** `satisfied_by_reference` *mechanism* → PR-5 (enum member
defined here). Cross-template `Upstream:` sweep → follow-up TODO. GATE-CODE's
cross-subsystem invocation wiring (hermes orchestrator / plugin gate-check
calling `--mode gate-code`) is *named* here as the contract but its
implementation in those subsystems is a separate platform task.

## Sub-PR split (Pass-4 G — boundaries named)

- **2a — graph core + forward gate** (largest; **split if > ~3 effective
  surfaces**): the net-new bidirectional element-level edge graph + heading-
  context scanner (DD-3) in `sdd_doc_lint`; `tools/sdd_coverage.py` matrix
  emitter; `covered_state` enum + escapes; multi-`@brd` OR-group; `--mode`/
  `--skip-coverage-gate` args; the BRD FR-annotation rule; the `TRACEABILITY.md`
  cross-ref. **Co-lands PR-3 ref-granularity** — PR-3 touches
  `ID_NAMING_STANDARDS.md` + the tag-syntax page + `sdd_doc_lint` taglint; name
  those files so the 2a/PR-3 boundary is explicit. If 2a exceeds the cap, split
  **2a-core** (engine) from **2a-ref** (PR-3).
- **2b — backward leg:** SPEC-00 `coverage` section + GATE-06 + SPEC-00
  `Upstream:` fix. Reuses 2a's graph.
- **2c — phase reconciliation:** *2c-schema* (`LAYER_REGISTRY.yaml` +
  `ID_NAMING_STANDARDS.md`, 2 surfaces) and *2c-gate* (`BRD-TEMPLATE.yaml`
  FR-annotation rule + `sdd_doc_lint` phase-leak gate, 2 surfaces).
- **2d — BDD doc-set EARS roll-up** + split-by-functional-block convention.

Each sub-PR inherits C-1…C-5 (corpus via DD-9; vendored-lint sync; conformance
tests per gate; framework MINOR via the fixed bumper; branch from `origin/main`).

## Verification (per sub-PR; high-level)

| #  | Check | Expected |
| -- | ----- | -------- |
| V1 | Forward gate `--mode gate-code` on corpus: every in-scope (non-escaped) FR → ≥1 SPEC + ≥1 IPLAN; escaped FRs never block | DD-6 severities exact |
| V2 | Heading-context scanner classifies §7 FRs as gated but the §7 `Acceptance criteria:` sub-block as NOT gated | no AC false-blocks |
| V3 | GATE-06 flags an EARS/BDD element with no downstream SPEC/TDD; distinguishes deferred vs missed | true |
| V4 | Out-of-phase (`Future`) item inside a P1 plan → block; multi-`@brd` OR-groups; zero-downstream FR flagged | true |
| V5 | `docs/TRACEABILITY_MATRIX.md` regenerates deterministically; `TRACEABILITY.md` cross-ref added | true |
| V6 | Conformance + corpus green (DD-9 annotations + `--skip-coverage-gate` for the migration window) | green |

## Review log

### Pass 1 — 2026-06-27 — self (design). Pass 2 — independent — 9 blocking gaps folded as DD-1…DD-9. Pass 3 — self re-validation.

### Pass 4 — 2026-06-27 — independent (fresh-context, soundness)

NOT-READY: the DD resolutions were plausible but ungrounded. Corrected:

- **DD-3** "YAML-path scoping" impossible (R-a/R-b) → **markdown heading-context
  scanner**, with the §7 FR-vs-acceptance-criteria boundary named.
- **DD-4** "reuse YAML `priority:` field" unreadable (R-b) → **parse + formalize
  the inline `(P1|P2|Future)` FR-bullet annotation**.
- **DD-7** invented a PR-1 matrix contract (R-e) → matrix is a **new** artifact;
  **this PR adds the cross-ref** to `TRACEABILITY.md`; name aligned to hermes
  `*_TRACEABILITY_MATRIX.md`.
- **DD-5⊥DD-6** deferred-no-SPEC contradiction → severity table now **carves out
  escaped FRs** from the NO-SPEC block.
- **DD-6/DD-9** fictional `--skip-lint-smoke` precedent (R-d) → `--mode`/
  `--skip-coverage-gate` declared **net-new** `__main__.py` args; real precedent
  located in the hermes/plugin subsystem.
- **DD-1** "inverse traversal of existing edge set" overstated (R-c) → graph is
  **net-new**; coverage gated to **whole-corpus** runs.
- DD-2 `authored` role defined; DD-4 value single-sourced in `priority_definitions`;
  2a/PR-3 file boundary named.
- Added the **Implementation reality (R-a…R-e)** section so no future DD drifts
  from the code again.

### Pass 5 — 2026-06-27 — self re-validation (of the Pass-4 corrections)

- Every DD cites a verified R-fact/file:line; no DD assumes a parsed body tree,
  a YAML `priority:` field, or a PR-1 matrix contract. (Pass 6 then caught one
  residual — see below — confirming self-passes don't catch the deep class.)

### Pass 6 — 2026-06-27 — independent (fresh-context, confirming soundness)

Verified 5 of 6 corrections genuinely grounded (DD-3 heading scanner — the
`_SECTION_HEADING` mechanism already exists `:106`; DD-4 annotation present on
all 4 corpus FRs; DD-7 `TRACEABILITY.md:29-30` names no matrix + no path
collision; DD-5/DD-6 escape carve-out consistent; `--mode`/`--skip` confirmed
net-new). Found **one residual ungrounded premise → fixed:**

- **DD-6 row 4** compared the item band against "the plan's cycle" — a signal
  with NO source (no phase/cycle field on IPLANs; the only IPLAN phase is TDD
  R/G/R, orthogonal). → Re-grounded (**R-f**): the leak = a `Future`-band FR
  that *reaches an IPLAN*, derived purely from the FR band (DD-4) + the forward
  trace; **no invented IPLAN-cycle field**. Symmetric with the deferred-no-IPLAN
  warning. Scope-ledger reconciliation noted as a future enhancement.
- Minors folded: `Acceptance criteria:` is a prose label line (not a `##`
  heading); dual priority surfaces (YAML field + markdown annotation) noted.

### Pass 7 — 2026-06-27 — self re-validation (of the Pass-6 fix)

- DD-6 row 4 now uses only grounded signals (band + trace); no new field
  invented. Symmetric with row 1. The remaining phase work (2c-schema registers
  the band *values* by reference; 2c-gate compares band→IPLAN-presence) needs no
  un-sourced signal. No new load-bearing gaps.

**Result:** READY. Converged over **three independent passes** (Pass 2
design-gaps, Pass 4 soundness, Pass 6 confirming) + four self passes. The
false-premise class (assuming structure/fields/contracts the code & artifacts
don't provide) is closed — every gate input is now a verified-present signal.
Plan PR may open; implementation proceeds 2a→2d.

## Implementation log — sub-PR 2a-core

Branch `feat/cfb-pr-2a-coverage-core` (rebased onto main `169b43c5`). The
engine half of 2a (split from 2a-ref / PR-3 per HANDOFF). Build order tracked
in `plans/HANDOFF.md`.

### Step 1 — shared trace primitives (DD-1 foundation) — DONE (`0da6f4de`)

`sdd_trace_graph` extracted from `trace_walk.py` (layer order, `@`-tag regex,
ID forms, `doc_id_from_token` / `locate_doc` / `emit_tags`). `trace_walk`
repointed; `test_sdd_trace_graph.py` (8) + `test_trace_walk` green.

### Step 2 — edge-graph + heading-context FR scanner (DD-1/R-c, DD-3) — DONE

- **Module-location decision (the DD-1 placement question).** The shared core
  **moved into the `sdd_doc_lint` package** as `tools/sdd_doc_lint/trace_graph.py`
  (commit `113af0c0`), not a loose `tools/` sibling. Rationale: the **vendored**
  linter copies (`platforms/*/sdd_doc_lint/`) must import it; a package submodule
  resolves via package-relative `from .trace_graph import …` regardless of how
  the package landed on `sys.path`, whereas a loose sibling relies on a fragile
  parent-dir assumption. `sync-vendored.sh` carries the submodule; the
  byte-identity drift-guard (`test_doc_lint_vendoring`) now guards it too.
  `trace_graph` stays pure stdlib (`re` + `pathlib`); the unvendored `tools/`
  scripts reach it via `from sdd_doc_lint.trace_graph import …`.
- **Heading-context FR scanner (DD-3)** — `scan_fr_elements()` / `FRElement`
  (commit `209bc62c`). A gated FR = an FR definition bullet
  (`- **<ID> — <Title>** …`) under a `## … Functional Requirements` heading and
  before that section's `Acceptance criteria:` label line. Reuses the level-2
  `_SECTION_HEADING` + `_normalise_heading` mechanism. The heading + boundary
  are the discriminators (not the band), so prose citations and the §7 AC
  sub-block are excluded, and a bullet missing its band still classifies (DD-4
  can then flag it). Band token captured from the bullet's first line only →
  tolerant of a wrapping parenthetical (corpus `882c`).
- **Bidirectional element edge-graph (DD-1/R-c)** — `build_edge_graph()` /
  `EdgeGraph` / `TraceEdge` (commit `f3d9b8f2`). Net-new upstream-citation
  adjacency (today's `element_index` discards downstream citations). Strictly-
  downstream skip matches `_check_trace_resolution`; same-layer siblings kept,
  self-refs / index docs dropped; multi-`@brd` per DD-8 via the shared regex.
  Lookups: `citers_of` / `citers_of_doc` / `citers_in_layer`.
- **Corpus grounding (V2 partial).** On `examples/url-shortener/docs/`: the 4
  BRD-01 §7 FRs classify (band P1), the 4 acceptance-criteria elements are
  excluded, and all 4 FRs are cited element-level by PRD-01 — the one-hop
  necessary-upstream chain (BRD←PRD←EARS…) confirms transitive forward reach is
  computable. `test_fr_scanner.py` (9) + `test_edge_graph.py` (9); 208
  unit+conformance green.

### Step 3 — `covered_state` enum + band parser + escapes (DD-2/DD-4/DD-5) — DONE (`216f9c94`)

The classification layer the forward gate (step 4) dispatches on.

- **`CoveredState` (StrEnum, DD-2)** — `AUTHORED` (success: must reach
  downstream) + the non-blocking escapes `DEFERRED` / `REALIZED_BY` +
  `SATISFIED_BY_REFERENCE` (enum member only; PR-5 adds its logic, never
  produced here).
- **`parse_band()` (DD-4)** — validates the FR-bullet band token against the
  priority bands `{P1, P2, Future}`. These mirror `priority_definitions`
  (`BRD-TEMPLATE.yaml:529-532`) in code with a source comment; the gate reads
  the band by regex (per DD-4), and the *registry* phase-schema references that
  single source in **2c-schema** (no re-enumeration). `Future` = deferral.
- **`covered_state_of()` (DD-5)** — `realized_by` → `REALIZED_BY` (precedence);
  `Future` band → `DEFERRED`; else (`P1`/`P2`, or a missing/invalid band) →
  `AUTHORED`. A missing/invalid band never silently becomes an escape.
- **`realized_by` authoring surface (net-new; D-0037).** None existed. Minimal
  grounded surface: a `realized_by: <LAYER>` token on the FR bullet's first
  line (canonically inside the band parenthetical, `(P1, realized_by: ADR)`),
  captured by the scanner into the additive `FRElement.realized_by` field. No
  new YAML field, single-line (no wrap-parsing). The BRD-template normative
  rule formalizing the annotation rides with the **forward gate (step 4)**,
  where the rule + gate are coupled.
- Corpus: all 4 BRD-01 FRs (P1, no escape) → `AUTHORED`.
  `test_covered_state.py` (11); 221 unit+conformance green.

### Step 4 — forward coverage gate + run-mode severity + CLI args (DD-6/DD-9) — DONE (`0bdd12fc`)

`_check_forward_coverage` (`COV01`) wires the graph + scanner + classifier into
a corpus-level gate.

- **Reach is document-level** from the FR's host BRD (`_doc_forward_reach`,
  transitive over `citers_of_doc`). The plan's "document-level binding for
  SPEC/TDD/IPLAN" — PR-3 refines reach to element granularity. *Granularity is
  chosen to avoid false BLOCKS:* element-level reach would false-block an
  AUTHORED FR that its downstream cites at the doc level (necessary-upstream
  permits doc-level citation), so coverage uses doc-level reach. Under-detection
  (a coarse miss) is acceptable; a false block is not.
- **Severity (DD-6 rows 2-3):** AUTHORED FR, no SPEC → error (both modes);
  AUTHORED FR, SPEC but no IPLAN → warning (`build`) / error (`gate-code`).
  Escaped FRs (`deferred` / `realized_by`) are skipped entirely — the DD-5
  suppression (they never block even with no SPEC).
- **DD-1 gating:** runs only when the corpus has reached BOTH the SPEC and
  IPLAN layers (`{SPEC, IPLAN} ⊆ present`). No-ops on the single-file
  `on_author` case and partial-cascade fixtures (`valid/` has no SPEC,
  `broken/` has no IPLAN — both unaffected; no test regressions).
- **CLI (DD-6/DD-9):** net-new `--mode {build | gate-code}` (default `build`) +
  `--skip-coverage-gate`, threaded through `lint_path(mode=, skip_coverage=)`.
- **Deferred (need element granularity / 2c):** DD-6 row 1 (escaped-FR
  informational warning — meaningless at doc-level) and row 4 (phase leak — its
  per-FR correctness needs element reach to avoid false-blocking a `Future` FR
  in a mixed-band BRD). Both land with 2c-gate / PR-3.
- **DD-9 verified:** corpus findings are **byte-identical to main** (`--format
  json` diff empty) — all 4 BRD-01 FRs reach SPEC+IPLAN, 0 `COV01`. No
  `--skip-coverage-gate` / annotation needed for the corpus.
- **Pre-existing corpus issue surfaced (out of scope):** `TH-RES-001` errors on
  `02_PRD/PRD-01.md` (missing `component_decomposition`; 11 unresolvable
  `@threshold:` citations) — confirmed identical under main's linter, unrelated
  to coverage (CLEANUP-PR-D threshold-resolution). Flagged in `FRAMEWORK-TODO.md`
  for framework-fixer remediation (never hand-edit the example artifact).
- `test_forward_coverage.py` (9); 231 unit+conformance green.

### Step 5 — `sdd_coverage.py` matrix emitter (DD-7) — DONE (`19d95a1a`)

`tools/sdd_coverage.py` — a thin reporter over the shared engine (`tools/`
script, not vendored, like `trace_walk.py`).

- `render_matrix(corpus)` (pure, testable) consumes `build_edge_graph` +
  `scan_fr_elements` + `covered_state_of` + `_doc_forward_reach` from
  `sdd_doc_lint` — the SAME graph the forward gate reads, so the matrix and the
  gate never disagree (DD-1). Emits a GENERATED, deterministic
  `TRACEABILITY_MATRIX.md`: one row per gated FR (id, band, `covered_state`, a
  ✓ per downstream layer reached) + a summary.
- CLI `python tools/sdd_coverage.py <docs_root> [--output PATH|-]`; default
  writes `<docs_root>/TRACEABILITY_MATRIX.md`.
- Generated `examples/url-shortener/docs/TRACEABILITY_MATRIX.md` (all 4 BRD-01
  FRs reach SPEC+IPLAN). Idempotent regeneration verified; 0 added linter
  findings (the matrix file has no `doc_id`, inert to the graph/scanner);
  markdownlint clean. Output sorted by FR id → deterministic (V5 regenerate-
  and-diff is step 6's conformance test).
- `test_sdd_coverage.py` (6); 240 unit+conformance green.

**Resequencing note:** the `framework/governance/TRACEABILITY.md` reverse-lookup
cross-ref (also DD-7) **moved to step 6**. Reason: it is a `framework/` spec
change, which couples to GATE-SPEC (needs the VERSION bump + CHANGELOG). Grouping
it with the framework MINOR bump keeps the framework change one coordinated,
GATE-SPEC-compliant unit rather than a spec edit stranded ahead of its bump.

### Step 6 — framework bump + deferred spec changes + conformance (DD-3/DD-4/DD-7/DD-9) — NEXT

One coordinated GATE-SPEC-compliant framework change: (a) `TRACEABILITY.md`
cross-ref to the generated matrix; (b) the BRD-template FR-annotation rule
(every FR bullet MUST carry `(P1|P2|Future, …)` + the `Acceptance criteria:`
label); (c) conformance tests per gate (COV01 fires/doesn't; matrix
regenerate-and-diff); (d) bump `framework/VERSION` MINOR + CHANGELOG + re-vendor

- both `FRAMEWORK_SPEC_VERSION`. Then 2a-core is PR-ready.
