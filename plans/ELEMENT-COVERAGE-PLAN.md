# ELEMENT-COVERAGE-001 Plan — element-level COV01 / COV02 coverage

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | ELEMENT-COVERAGE-001                                         |
| Type           | feature                                                      |
| Status         | PLANNED — 2026-06-29T00:00:00Z                               |
| Depends on     | CFB-PR-2 coverage engine (`COV01`/`COV02`, #187/#190), REFGRAN01 (#194), YAML-BDD-SCHEMA arc (#198–#206) — the corpus is now element-precise |
| Feeds          | CORPUS-REFGRAN-RECASCADE (orthogonal); future phase-leak (DD-6 row 4) |
| Version impact | framework MINOR (gate semantics change); plugin none         |

## Objective

Upgrade the coverage gates `COV01` (forward) and `COV02` (backward) from
**document-level** reach to **element-level** reach, so they detect requirement
**elements** that the host document covers at doc-level but that are
individually traced to nothing downstream. The headline payoff: `COV02` will
catch the **16 orphaned BDD scenarios** (31 declared − 15 reached by a realizing
layer) that doc-level `COV02` cannot see (BDD-01 as a *document* reaches SPEC, so
the doc-level gate passes while 16 of its scenarios are realized by nothing).
This was the deferred payoff the CFB-PR-2 design-of-record named as "PR-3
refines reach to element granularity" — now unblocked because REFGRAN01 + the
YAML-BDD arc made every requirement-layer citation element-precise.

## Scope

**In:**

- A shared **element-level realization** primitive over the existing
  `EdgeGraph`, using each requirement layer's **immediate-downstream realizing
  layer(s)** (registry-derived), not a doc-level layer-reach.
- `COV02` element-level: each declared EARS/BDD **element** must be cited by
  ≥1 doc in its realizing layer(s); else it is an unrealized (orphan) element.
- `COV01` element-level: each AUTHORED BRD FR **element** must be cited by ≥1
  doc in its immediate-downstream realizing layer (PRD), preserving the existing
  doc-level transitive SPEC + IPLAN requirement.
- Preserve the DD-5 escape carve-out (`deferred` / `realized_by` never block)
  and the DD-6 run-mode severity split (`build` warning / `gate-code` error) —
  unchanged in shape, applied per element.
- Corpus impact recorded + the 16 BDD orphans surfaced (warning in `build`,
  error in `gate-code`); the gate stays warnings-only in `build` so the corpus
  exit code is unchanged on `main`.

**Out of scope (deferred):**

- DD-6 **row 1** (escaped-FR informational warning) and **row 4** (phase-leak
  gate) — separate follow-ups; this plan does not design them.
- `CORPUS-REFGRAN-RECASCADE` (the 5 SPEC/TDD/IPLAN `@adr`/`@tdd` doc-form edges)
  — orthogonal corpus cleanup, tracked separately.
- Remediation of the 16 orphan scenarios themselves (a corpus/skill concern —
  never hand-edit the fixture; dispatch the framework skills). This plan only
  makes the gate *see* them.
- Any change to the `EdgeGraph` shape, the BDD YAML schema, or REFGRAN01.

## Approach / Design

### Why doc-level misses orphans (the gap)

`_check_backward_coverage` (COV02) enumerates **host docs** of EARS/BDD elements
and asks `_doc_forward_reach(graph, doc_id)` whether the *document* reaches a
SPEC/TDD layer. `_doc_forward_reach` traverses `citers_of_doc` (who cites **any**
element of the doc). So one cited scenario makes the whole BDD doc "reach" SPEC,
masking every uncited sibling scenario. Element granularity is the fix.

### The realization model — immediate-downstream, not transitive doc-reach

A requirement element is **realized** when its **immediate-downstream realizing
layer** picks it up by element-level citation. This is the necessary-upstream
contract applied per element, and it is deliberately **not** a transitive
doc-level reach (which would be unsound — see the ADR-conflation pitfall below).

Realizing-layer map. **This is a curated set of the downstream "realization"
layers — acceptance (BDD) / design (SPEC) / test (TDD) — NOT the raw registry
`downstream` list** (which for BDD also includes the decision layer ADR; ADR
citing a requirement does not *realize* it). A requirement element is realized
iff it is **directly cited by a doc in any layer of its realizing set**:

| Requirement element | Realizing set | Rationale |
| ------------------- | ------------- | --------- |
| BDD scenario        | {SPEC, TDD}        | a scenario is realized by a design/test that cites it; ADR excluded |
| EARS requirement    | {BDD, SPEC, TDD}   | realized by a scenario that exercises it **or** a design/test that cites it directly — see false-block guard below |
| BRD FR (COV01)      | {PRD}              | the FR element must be picked up by its consuming PRD; the host BRD's existing doc-level SPEC + IPLAN reach is retained on top |

**Why EARS's set is {BDD, SPEC, TDD} and not just {BDD}:** an EARS element cited
directly by SPEC but not by any BDD scenario is still realized; restricting EARS
to {BDD} alone would false-flag it. Conversely an EARS cited only by BDD (16 of
26 in the corpus are not cited directly by SPEC/TDD) must NOT be flagged — BDD is
in the set, so it passes. Including every realization layer in the set, checked
**one-hop / directly**, satisfies both without a transitive traversal.

**Accepted limitation (one-hop, by design):** an EARS realized *only* by an
**orphan** BDD scenario (a scenario that itself reaches no SPEC/TDD) passes
COV02, even though its acceptance path dead-ends. Empirically the 16
"EARS-realized-only-via-BDD" elements coincide with the 16 orphan scenarios. This
is **not a hidden false-pass**: each orphan scenario is independently flagged by
COV02 at the BDD layer, so the defect surfaces at its root; also flagging the
upstream EARS would be redundant noise pointing at the same fix. A transitive
"is the realizing scenario itself realized" check is deliberately out of scope
(it reintroduces the multi-hop traversal the one-hop model avoids). A V-test
pins this as intended behavior so it is not later "fixed" into a false-block.

**Empirical justification for immediate-downstream (not "must reach SPEC/TDD"
directly):** in the corpus, **all 26 EARS elements are cited by a BDD scenario**,
but **16 of them are not cited directly by any SPEC/TDD**. A one-hop "EARS must
be cited by SPEC/TDD" rule would **false-flag those 16 legitimately-realized
EARS elements** — precisely the false-block the CFB-PR-2 design-of-record warned
element-level reach could cause. Checking each element against its *immediate*
downstream realizing layer avoids this: EARS is realized by BDD (all 26 pass);
BDD is realized by SPEC/TDD (16 orphans correctly surface).

**The ADR-conflation pitfall (why not seed a doc-level forward reach from an
element's citers):** an orphan BDD scenario cited *only* by ADR-01 would be
deemed "realized" by a reach that seeds from its citers then walks doc-level
forward, because ADR-01 (as a doc) reaches SPEC. But no SPEC realizes that
scenario. Restricting the check to the element's **immediate realizing layer**
(SPEC/TDD for BDD; ADR is a decision layer, not a realizing layer) avoids the
false pass. (In the corpus, BDD elements are cited by ADR/SPEC/TDD; the
ADR-only-cited scenario is exactly the +1 that separates the 15 "cited at all"
from the 16 "cited by a realizing layer".)

### New primitive

`_element_realizing_citers(graph, token, realizing_layers) -> set[str]` — the
set of citer docs of `token` whose layer ∈ `realizing_layers`. Built directly on
`EdgeGraph.citers_in_layer(token, layer)` (already exists). An element is
realized iff this set is non-empty. No new transitive traversal, no `EdgeGraph`
change.

### COV02 element-level (the payoff)

Replace the per-host-doc `_doc_forward_reach` check with: for each declared
EARS/BDD element (`graph.element_host`), if it has no citer in its realizing
set, emit a `COV02` finding **at element granularity** — file = host doc rel,
element id in the message, **line = the element's declaration line** in its host
doc (BDD: reuse `_bdd_line_of`; EARS: the line where the element id is declared).
Gating unchanged (DD-2b-3: only when a real non-`-00` SPEC/TDD exists). Severity
unchanged (DD-2b-3: warning/`build`, error/`gate-code`). The enumeration via
`element_host` already excludes `*-00` index docs. **Finding count changes from
per-doc to per-element** — any count-based test assertion is updated (V-tests).

### COV01 element-level

For each AUTHORED BRD FR element (`scan_fr_elements`), additionally require the
FR element to be cited by its realizing layer (PRD); keep the existing host-BRD
doc-level SPEC + IPLAN reach and the DD-5 escape skip and DD-6 severity.

**One finding per FR (dedup precedence):** an AUTHORED FR emits **at most one**
COV01 finding, in precedence order: (1) **not cited by any PRD** → error both
modes (untraced at the immediate downstream — the most upstream failure), with a
distinct "no PRD citer" message; else (2) host reaches no SPEC → error both
modes (the existing "no SPEC" message preserved); else (3) reaches a SPEC but no
IPLAN → warning/`build`, error/`gate-code` (existing "no IPLAN" message). This
keeps the single-finding shape that `test_in_scope_fr_with_no_spec_blocks`
(`tests/conformance/test_coverage_engine.py:74`, code+severity only) asserts.

**Existing negative tests assert message text (Pass-4 F10):** because precedence
(1) reorders which branch fires, any negative test whose corpus omits a PRD now
gets the "no PRD" message instead of "no SPEC"/"no IPLAN". Such tests must either
gain a PRD that element-cites the FR (so they exercise the intended downstream
branch) or update their message assertion. Affected: forward unit
`test_no_spec_reach_blocks_in_both_modes` (`:80 assertIn("no SPEC")`); and on the
COV02 side the per-element message names the element id, so backward unit
`test_uncovered_requirement_doc_flags_cov02` (`:82 assertIn("EARS-01")`) must be
updated to the element-id wording. (COV02 messages name both the host doc and the
element id to keep doc-anchored assertions working where practical.)

**Corpus vs fixtures — the framing caveat (Pass-3 F9):** on the *real* example
corpus all 4 BRD-01 FRs are cited element-level by PRD-01, so COV01 surfaces
**0 new findings there**. But the **synthetic conformance/unit fixtures cite BRD
doc-level** (`@brd: BRD-01`), so element-level COV01 *does* change their result —
`test_fully_covered_cascade_has_no_cov01` (`:71`) and the unit `_chain` helper
will flag unless rewritten to element-level PRD citations. This leg is therefore
correctness-hardening **for the real corpus** but **a fixture-rewriting change**
for the test suite (Task 3 test-first + Task 4 re-baseline cover it).

### Corpus / exit-code impact

The lint **exit code** on the corpus is unchanged (the 16 orphans are `build`
warnings; warnings don't raise it; `gate-code` is unit-fixture-only, never run on
the full corpus). **But the exit code is NOT the binding CI gate for the corpus —
the conformance assertion is.** `tests/conformance/test_coverage_engine.py:96`
(`BackwardCoverageContract.test_example_corpus_has_no_cov02`) asserts
`[f for f in _check_backward_coverage(corpus) if f.code=="COV02"] == []` —
it counts **findings, not exit codes**, in default `build` mode, and runs in CI
via `conformance.yml`. Element-level COV02 makes that list length 16 → the
assertion **fails → conformance.yml goes red** unless it is re-baselined.

Therefore this is **not** a no-op: a green CI **requires actively rewriting**
`test_example_corpus_has_no_cov02` to expect the 16 element-level orphans
(build=warning / gate-code=error). That is Task 4's explicit job. Codifying 16
known orphans in a conformance test while deferring their remediation (a
corpus/skill follow-up; never hand-edit the fixture) is an accepted, stated
trade-off — the orphans are surfaced, not hidden.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `tools/sdd_doc_lint/__init__.py` | add `_element_realizing_citers` (+ realizing-layer map); rewrite `_check_backward_coverage` to element granularity; extend `_check_forward_coverage` with the FR-element realizing-citer check |
| `platforms/claude-code-plugin/sdd_doc_lint/__init__.py` + `platforms/hermes/sdd_doc_lint/__init__.py` | re-vendored byte-identical via `sync-vendored.sh` |
| `framework/governance/TRACEABILITY.md` (or the SPEC-00 `## Coverage` section) | document COV01/COV02 are element-level; the realizing-layer map |
| `tests/unit/test_backward_coverage.py`, `tests/unit/test_forward_coverage.py` | **rewrite the doc-level `_chain` / `_covered`-style helpers to element-level citations** (else existing "covered" cases break under element granularity), + add element-level cases (orphan-sibling, EARS-realized-via-BDD, EARS-via-orphan-BDD-passes, ADR-only-cited-not-realized, FR-uncited-by-PRD, one-finding-per-FR, escape still skips) |
| `tests/conformance/test_coverage_engine.py` | **rewrite `test_example_corpus_has_no_cov02` (:96)** to expect the 16 element-level COV02 orphans (build=warning/gate-code=error) instead of `== []`; add the element-level contract + `REALIZING_LAYERS`-excludes-ADR assertions |
| `framework/VERSION` + both `FRAMEWORK_SPEC_VERSION` pins + frontmatter fanout | MINOR bump via `bump_version.py` |
| `CHANGELOG.md`, `plans/HANDOFF.md`, `plans/FRAMEWORK-TODO.md`, `plans/DECISIONS.md` | docs of record |

## Implementation sequence

### Task 1: realizing-layer map + `_element_realizing_citers`

- Define a **curated constant** `REALIZING_LAYERS = {"BDD": ("SPEC", "TDD"),
  "EARS": ("BDD", "SPEC", "TDD"), "BRD": ("PRD",)}` — **NOT** derived from
  `LAYER_REGISTRY.yaml` `downstream`, which is the single-hop linear cascade
  (`BDD→[ADR]`, `EARS→[BDD]`, …); pinning to it would route `BDD→{ADR}` —
  exactly the decision layer the ADR-conflation pitfall says to exclude, and it
  would mask all 16 orphans. The existing `_BACKWARD_REALIZED_LAYERS =
  ("SPEC","TDD")` (`tools/sdd_doc_lint/__init__.py:1599`) backs the BDD entry.
- Add `_element_realizing_citers(graph, token, layers)` over `citers_in_layer`.
- **Test-first — [CODE]:** unit test the primitive on a hand-built `EdgeGraph`
  (orphan element → empty; realized → non-empty; ADR-only citer not counted);
  add a conformance assertion (R2) that `REALIZING_LAYERS` excludes ADR and that
  `EARS` includes `SPEC`/`TDD` (the F1 false-block guard).

### Task 2: COV02 element-level

- Rewrite `_check_backward_coverage` to iterate `element_host` EARS/BDD elements
  and check `_element_realizing_citers`. Preserve gating + severity.
- **Test-first — [CODE]:** orphan-sibling scenario flagged; EARS realized via
  BDD not flagged; deferred/escape still skipped; `build` vs `gate-code` severity.
  **Update the existing negative test's message assertion**
  (`test_uncovered_requirement_doc_flags_cov02`, `test_backward_coverage.py:82`)
  to the per-element message wording (F10 secondary).

### Task 3: COV01 element-level

- Extend `_check_forward_coverage` to require the FR element to be cited by PRD,
  retaining the host-BRD SPEC+IPLAN doc-reach + DD-5 escape + DD-6 severity, with
  the one-finding-per-FR precedence above.
- **Test-first — [CODE]:** an FR cited only at doc-level (host covered, FR
  element uncited) flags; element-cited FR passes; escaped FR skips; one COV01
  finding per FR (dedup). **Convert the doc-level unit helpers** (`_chain` in
  `test_forward_coverage.py`; the `_covered`-style helpers in
  `test_backward_coverage.py`) to **element-level citations** so existing
  "covered" cases stay green for the right reason. **Also update
  `test_no_spec_reach_blocks_in_both_modes` (`test_forward_coverage.py:68`)** —
  its corpus omits a PRD, so add a PRD that element-cites the FR (so precedence
  (1) passes and it genuinely exercises the no-SPEC branch its `:80` message
  assertion checks) (F10).

### Task 4: re-baseline conformance + spec doc + MINOR bump + re-vendor + docs

- **Rewrite `tests/conformance/test_coverage_engine.py:96`
  `test_example_corpus_has_no_cov02`** to expect the 16 element-level COV02
  orphans (build=warning, gate-code=error) — without this, conformance.yml goes
  red. Add the `REALIZING_LAYERS`-excludes-ADR + EARS-includes-SPEC/TDD assertions.
- **Rewrite the COV01 conformance fixtures (Pass-3 F9):**
  `test_fully_covered_cascade_has_no_cov01` (`:71`) — its `_covered` fixture
  cites BRD doc-level, which now flags; convert it to an element-level PRD
  citation so it asserts `== []` for the right reason. Re-baseline
  `test_in_scope_fr_with_no_spec_blocks` (`:74`) per the one-finding precedence.
- Update the coverage doc-of-record (element-level statement + realizing map).
- `bump_version.py <MINOR>`; re-vendor byte-identical; update the
  release-metadata hard-pin; CHANGELOG / HANDOFF / FRAMEWORK-TODO / DECISIONS.

## Verification

| #  | Check (command) | Expected | Maps to |
| -- | --------------- | -------- | ------- |
| V1 | `pytest tests/unit/test_backward_coverage.py -q` | element-level COV02 cases green | COV02 |
| V2 | `pytest tests/unit/test_forward_coverage.py -q` | element-level COV01 cases green | COV01 |
| V3 | `pytest tests/conformance -q` (AFTER the COV01+COV02 fixture rewrites in Task 4) | all green incl. coverage-engine contract; `test_fully_covered_cascade_has_no_cov01` (:71) + `test_example_corpus_has_no_cov02` (:96) updated | regression |
| V4 | `PYTHONPATH=tools python3 -m sdd_doc_lint examples/url-shortener/docs/` (build) | 16 new `COV02` **warnings** for the orphan scenarios; exit code unchanged vs `main` (still 1× TH-RES-001 error) | corpus impact |
| V5 | same with `--mode gate-code` | the 16 orphans are **errors**; EARS elements NOT flagged (realized via BDD) | false-block guard |
| V6 | byte-identity: `diff` canonical ↔ both vendored `sdd_doc_lint` | identical | D-0022 |
| V7 | both `FRAMEWORK_SPEC_VERSION` == `framework/VERSION` | match | bump |
| V8 | `pytest tests/conformance/test_coverage_engine.py -q` after rewriting `test_example_corpus_has_no_cov02` | green; asserts exactly 16 element-level COV02 orphans (was `== []`) | Finding 1 / R3 |
| V9 | unit test: an EARS cited only by an orphan BDD scenario is NOT flagged by COV02 (one-hop accepted limitation) | passes (intended behavior pinned) | Finding 3 |

## Docs to update

- [ ] `CHANGELOG.md` — element-level COV01/COV02 entry + MINOR bump
- [ ] `ROADMAP.md` — coverage-engine milestone bullet (if tracked there)
- [ ] `plans/HANDOFF.md` — narrative + next steps (orphan remediation follow-up)
- [ ] `plans/FRAMEWORK-TODO.md` — close the element-level upgrade item
- [ ] `plans/DECISIONS.md` — the immediate-downstream realization model (D-number)
- [ ] coverage doc-of-record (`TRACEABILITY.md` / SPEC-00 `## Coverage`)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | element-level reach **false-blocks** legitimately-realized elements (the design-of-record's named risk) | med | immediate-downstream model (not transitive doc-reach); V5 asserts the 16 EARS-via-BDD elements are NOT flagged |
| R2 | realizing-layer map is curated (NOT raw registry downstream — that includes ADR); a hand-maintained map can drift | low | define it as a single named constant with the rationale inline; a conformance test asserts BDD→{SPEC,TDD}, EARS→{BDD,SPEC,TDD}, excludes ADR |
| R3 | CI red on the corpus from 16 new COV02 findings — **via the conformance assertion `test_example_corpus_has_no_cov02`, not the lint exit code** | high | Task 4 rewrites that assertion to expect the 16 orphans (build=warning/gate-code=error); V8 confirms conformance green; exit code separately unchanged (V4) |
| R4 | ADR-only-cited scenario falsely counted as realized | low | realizing layers exclude ADR; V5 covers the ADR-only case |
| R5 | element-level COV01 breaks **doc-level conformance/unit fixtures** (`:71`, `_chain`), not just the corpus (Pass-3 F9) | high | Task 4 rewrites `:71`; Task 3 converts the unit helpers to element-level; one-finding precedence keeps `:74` shape; V3 gated on the rewrites |
| R6 | an FR failing two COV01 sub-checks emits duplicate findings | low | one-finding-per-FR precedence (no-PRD → no-SPEC → no-IPLAN) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | COV02 currently enumerates EARS/BDD **host docs** and checks doc-level layer reach | `_check_backward_coverage` | `tools/sdd_doc_lint/__init__.py:1602` |
| 2  | doc-level reach traverses `citers_of_doc` (who cites ANY element of a doc) — masks uncited sibling elements | `_doc_forward_reach` | `tools/sdd_doc_lint/__init__.py:1515` |
| 3  | the element-level primitive already exists: citer docs of a token restricted to a layer | `citers_in_layer` | `tools/sdd_doc_lint/__init__.py:1151` |
| 4  | `element_host` maps each declared element → host doc (citations excluded) — the COV02 enumeration source | `element_host` | `tools/sdd_doc_lint/__init__.py:1139` |
| 5  | edges carry `citer_doc` + `citer_layer` + `cited_token` (the element-level citation data) | `TraceEdge` | `tools/sdd_doc_lint/__init__.py:1117` |
| 6  | COV01 currently binds at the host-BRD doc level (`_doc_forward_reach` from the FR's host BRD) | `_check_forward_coverage` | `tools/sdd_doc_lint/__init__.py:1533` |
| 7  | DD-5 escape: non-AUTHORED FRs never block | `covered_state_of` | `tools/sdd_doc_lint/__init__.py:1569` |
| 8  | DD-6 severity: warning in `build`, error in `gate-code` (COV02) | `severity =` | `tools/sdd_doc_lint/__init__.py:1648` |
| 9  | COV02 gating: only when a real non-`-00` SPEC/TDD exists | `_BACKWARD_REALIZED_LAYERS` | `tools/sdd_doc_lint/__init__.py:1628` |
| 10 | corpus: 31 declared BDD scenario elements, 15 cited by a realizing layer (SPEC/TDD) → 16 orphans (measured via this fn over examples/) | `build_edge_graph` | `tools/sdd_doc_lint/__init__.py:1287` |
| 11 | corpus: all 26 EARS elements are cited by a BDD scenario; 16 are NOT cited directly by SPEC/TDD (⇒ one-hop-to-SPEC/TDD would false-block them) — measured via this fn | `build_edge_graph` | `tools/sdd_doc_lint/__init__.py:1287` |
| 12 | BDD elements are cited by layers {ADR, SPEC, TDD} — ADR must be excluded from realizing layers (measured via this fn) | `build_edge_graph` | `tools/sdd_doc_lint/__init__.py:1287` |
| 13 | design-of-record defers element-level reach and flags the false-block risk | `false-block` | plans/CFB-PR-2-COVERAGE-ENGINE-PLAN.md:357 |
| 14 | the deferred DD-6 row 1 / row 4 (out of scope here) | `DD-6 row 1` | plans/CFB-PR-2-COVERAGE-ENGINE-PLAN.md:371 |
| 15 | vendored byte-identity is contractually required (D-0022) | `byte-identical` | tools/sdd_doc_lint/sync-vendored.sh:4 |
| 16 | `gate-code` mode is exercised only by unit-test fixtures, not the full corpus (so the lint *exit code* is unaffected) | `gate-code` | tests/unit/test_backward_coverage.py:80 |
| 17 | the binding CI gate for the corpus is a conformance assertion that COV02 findings == [] (counts findings, default build mode) — element-level COV02 breaks it unless rewritten | `test_example_corpus_has_no_cov02` | tests/conformance/test_coverage_engine.py:96 |
| 18 | registry `downstream` is single-hop (`BDD: [ADR]`) — so the realizing map must be a curated constant, not registry-derived | `BDD` | framework/registry/LAYER_REGISTRY.yaml:78 |
| 19 | a COV01 conformance fixture asserts the covered cascade yields `_check_forward_coverage == []`; its `_covered` fixture cites BRD doc-level → element-level COV01 breaks it unless rewritten | `test_fully_covered_cascade_has_no_cov01` | tests/conformance/test_coverage_engine.py:71 |
| 20 | forward unit negative test asserts the finding message contains "no SPEC"; its corpus omits a PRD, so precedence-(1) "no PRD" reorders the message → assertion breaks (F10) | `assertIn("no SPEC"` | tests/unit/test_forward_coverage.py:80 |
| 21 | backward unit negative test asserts the message contains the host doc id "EARS-01"; per-element COV02 message must retain it or the test updates (F10 secondary) | `EARS-01` | tests/unit/test_backward_coverage.py:82 |

## Review log

### Pass 1 — 2026-06-29T00:00:00Z — self-review

- **F1 (load-bearing) — realizing map too narrow for EARS.** Original map set
  `EARS → {BDD}` only. An EARS element cited directly by SPEC but not by any BDD
  scenario would be **false-flagged**. Fixed: EARS realizing set = {BDD, SPEC,
  TDD}, checked one-hop/directly (still passes the 16 EARS-only-via-BDD; still
  catches a truly orphaned EARS). Added an explicit false-block guard paragraph.
- **F2 — map is curated, not registry-derived.** Raw `LAYER_REGISTRY` downstream
  for BDD includes ADR (a decision layer that does not *realize*). Reframed the
  map as a curated "realization layers" constant (acceptance/design/test), ADR
  excluded; updated R2; conformance asserts the curated map.
- **F3 — COV01 new-subcheck severity unspecified.** Specified: an AUTHORED FR not
  cited by any PRD = error both modes (mirrors "reaches no SPEC").
- **F4 — COV02 finding line/granularity.** Specified element-declaration line
  reporting (BDD via `_bdd_line_of`; EARS via declaration line) + noted the
  per-doc→per-element count change for test assertions.
- **F5 — gate-code-on-corpus exit-code risk.** Verified `gate-code` is only used
  by unit fixtures, not the full-corpus CI lint (default `build`); added claim 16
  - folded into the corpus-impact section and R3. Confirms no CI breakage.

### Pass 2 — 2026-06-29T00:00:00Z — independent (fresh-context)

Independent reviewer re-ran `build_edge_graph` over the corpus (all empirical
rows 10–12 confirmed exactly: 31/15/16 BDD, 26 EARS all via BDD, BDD cited by
{ADR:21,SPEC:37,TDD:34}, the +1 ADR-only scenario) and verified citations 1–9 /
13–16. Three findings, all folded:

- **F6 (load-bearing) — wrong CI gate named.** The binding CI exposure is the
  conformance assertion `test_example_corpus_has_no_cov02`
  (`test_coverage_engine.py:96`), which counts COV02 findings `== []` in build
  mode — NOT the lint exit code. Element-level COV02 → 16 findings → conformance
  goes red unless that assertion is rewritten. Fixed: corrected the
  corpus-impact §, R3 (→ high), added claim 17 + V8, and made the rewrite an
  explicit Task-4 step + File-structure entry. The plan no longer claims "no-op".
- **F7 (load-bearing) — Task 1 self-contradiction.** Task 1 still carried the
  pre-F1 `EARS→{BDD}` and "pin to `LAYER_REGISTRY.yaml` downstream" — but registry
  `downstream` is single-hop (`BDD→[ADR]`), so pinning to it yields `BDD→{ADR}`
  (masks all orphans) and contradicts F1/F2. Fixed: Task 1 now defines a curated
  `REALIZING_LAYERS` constant, explicitly NOT registry-derived; added claim 18.
- **F8 (soundness, non-blocking) — EARS realized via an orphan BDD scenario
  passes COV02.** Accepted by design (the orphan is flagged at the BDD layer; an
  EARS finding would be redundant). Documented as an explicit accepted limitation
  - pinned by V9 so it isn't later "fixed" into a false-block.

### Pass 3 — 2026-06-29T00:00:00Z — independent (fresh-context, confirming)

Confirmed F6/F7/F8 correctly folded (re-verified the corpus numbers; the COV02
conformance sweep is complete; the curated map is consistent across Approach
table / Task 1 / R2 / claims with no stale `EARS→{BDD}`). One NEW load-bearing
finding, folded:

- **F9 (load-bearing) — element-level COV01 breaks doc-level fixtures the plan
  didn't list.** F6 swept COV02's conformance assertions but the symmetric COV01
  sweep was missed. `test_fully_covered_cascade_has_no_cov01`
  (`test_coverage_engine.py:71`) asserts `_check_forward_coverage(_covered)==[]`,
  but the `_covered` fixture cites BRD **doc-level** → element-level COV01 flags
  it → conformance red. Same root cause threatens `:74` (dedup) and the unit
  `_chain` helpers. Fixed: added the COV01 fixture rewrite to Task 4 +
  File-structure, the one-finding-per-FR **dedup precedence** to Task 3/Design
  (R6), the helper-conversion to Task 3 test-first, R5, claim 19, V3 gating, and
  **qualified the misleading "0 new findings / not corpus-changing" framing** to
  "true for the real corpus; the synthetic fixtures DO change."
- *(minor, fixed)* claim 18 line 31→78 (`BDD: [ADR]` is at :78; :31 is BRD).

### Pass 4 — 2026-06-29T00:00:00Z — independent (fresh-context, confirming)

Confirmed F9 folded; re-verified all empirical claims (4 AUTHORED FRs all
element-cited by PRD-01 → real corpus COV01-clean; 16 BDD orphans / 0 EARS
orphans; dedup keeps `:74`; citations 18/19 resolve). Did the **exhaustive
three-file per-test sweep** — every breaking test is covered by the plan EXCEPT
one, folded:

- **F10 (load-bearing) — forward unit negative test message assertion.**
  `test_no_spec_reach_blocks_in_both_modes` (`test_forward_coverage.py:68`) has a
  corpus with no PRD; under precedence (1) the "no PRD" branch now fires, so its
  `:80 assertIn("no SPEC")` breaks. It uses `_brd()` directly (not `_chain`), so
  the helper-conversion didn't cover it. Fixed: Task 3 now adds a PRD that
  element-cites the FR so it exercises the no-SPEC branch; the message-wording
  decision (distinct "no PRD" message; "no SPEC"/"no IPLAN" preserved) is in the
  Design dedup block; claim 20.
- **F10 secondary — backward unit message assertion.**
  `test_uncovered_requirement_doc_flags_cov02` (`test_backward_coverage.py:82`)
  asserts `"EARS-01"` in the message; per-element COV02 names the element id.
  Fixed: COV02 message names both host doc + element id; Task 2 updates the
  assertion; claim 21.

Pass 4's complete table confirms every other breaking test in all three files is
already covered by the `_chain`/helper-conversion + conformance-rewrite
instructions.

### Pass 5 — 2026-06-29T00:00:00Z — independent (fresh-context, confirming)

Confirmed F10 + secondary correctly folded and the plan internally consistent:

- forward `:68` fix is feasible/sound — adding a PRD that element-cites
  `BRD.01.07.aaaa` makes precedence (1) pass while the disconnected SPEC-99 keeps
  the host BRD reaching no SPEC, so the "no SPEC" branch (2) fires and `:80`
  holds; gate stays active (real SPEC present).
- backward `:82` stays satisfiable (COV02 message names host doc + element id);
  Task 2 instructs the assertion update.
- dedup precedence + message wording identical across Design / Task 2 / Task 3 /
  R6 / claims 20-21; realizing map consistent everywhere (no `EARS→{BDD}`
  residue); claims 20/21 resolve to the exact cited lines; no Task/Design/
  File-structure/Verification contradiction.

**No new load-bearing findings.**

**Result:** ready
