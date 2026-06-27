# CFB-PR-2b — Backward leg (`COV02` backward coverage + SPEC-00 coverage section)

> Sub-PR **2b** of CFB-PR-2 (coverage engine). The **backward dual** of 2a's
> forward `COV01` gate: 2a asserts every BRD functional requirement reaches a
> SPEC + IPLAN; 2b asserts every EARS/BDD requirement is **realized downstream**
> (reaches a SPEC or TDD) — the "is anything we required left undesigned/
> untested?" half. Reuses 2a's `build_edge_graph`. **Document-level binding**
> (element granularity → PR-3, by the user's 2026-06-27 scope decision).

| Field          | Value                                                |
| -------------- | ---------------------------------------------------- |
| Task           | CFB-PR-2b (backward leg)                             |
| Type           | feature (tooling + spec)                             |
| Status         | READY — 2026-06-27 · 2 independent passes (P2, P5) + 4 self; gating/severity grounded |
| Parent         | `plans/CFB-PR-2-COVERAGE-ENGINE-PLAN.md` (sub-PR 2b); 2a-core merged `48d501d6` |
| Depends on     | 2a-core (merged, framework `0.24.0`)                 |
| Version impact | framework **MINOR** (new SPEC-00 `coverage` section) + tooling. Bump via `bump_version.py`. |

## Objective

2a built the **forward** half (BRD FR → SPEC/IPLAN). 2b builds the **backward**
half: every EARS/BDD requirement element must be **realized** by a downstream
SPEC or TDD — otherwise we shipped requirements/scenarios that nothing designs
or tests. Implemented as a new `sdd_doc_lint` structural check **`COV02`** (the
backward sibling of 2a's `COV01`), plus a **SPEC-00 `coverage` section**
documenting the contract and a fix to SPEC-00's stale cumulative `Upstream:`
enumeration.

## Implementation reality (grounded — verified against the merged 2a engine + corpus)

- **R2b-a — `COV02` is a STRUCTURAL LINT CODE, not a formal gate error code.**
  2a's `COV01` is a `sdd_doc_lint` finding code (the fast deterministic tier
  beneath the LLM gates), **not** a `GATE-0N-E0NN` entry in the gate catalog.
  `COV02` mirrors that exactly: it is the deterministic structural check that
  *backs* the existing **GATE-06** (Design & Test, L6-L7) coverage intent, but
  adds **no** entry to `GATE-06_DESIGN_TEST.md` / `GATE_ERROR_CATALOG.md` /
  `GATE_APPROVAL_FORM.md`. (This avoids a semantic collision with the existing
  `GATE-06-E002` "TDD must cover all BDD scenarios", which is a *scenario-level,
  score-based* check; `COV02` is *doc-level, deterministic* — complementary, not
  redundant.) The normative doc-of-record for the contract is the **SPEC-00
  `coverage` section** (DD-2b-4).
- **R2b-b — The edge graph already supports backward reach.** `build_edge_graph`
  retains every upstream citation; `EdgeGraph.citers_of(elem)` /
  `citers_of_doc(doc)` give "who cites this", `_doc_forward_reach(g, doc)` gives
  transitive downstream layer-reach, and `EdgeGraph.element_host` enumerates
  every declared element → host doc. No new graph primitive is needed.
- **R2b-c — Document-level binding; element-level is corpus-RED.** At **doc**
  level every EARS/BDD doc in `examples/url-shortener/docs/` transitively reaches
  a SPEC/TDD (corpus-green: EARS-01 → {SPEC,TDD}, BDD-01 → {SPEC,TDD}). At
  **element** level **15 of 31 BDD elements reach nothing** downstream (genuine
  orphaned scenarios; EARS = 0 uncovered). 2b is therefore **doc-level only**
  (symmetric with `COV01`); element-level coverage + the EARS/BDD deferral
  signal + remediating the 15 BDD gaps are **PR-3 / follow-on** (user scope
  decision 2026-06-27).
- **R2b-d — No EARS/BDD deferral signal exists, and v1 needs none.** EARS/BDD
  carry only a document-level priority `P1|P2|P3|P4` — no per-element `Future`/
  deferred marker. At **doc** level the corpus docs are all covered, so v1 needs
  **no deferral escape**: the only thing `COV02` fires on is a requirements doc
  that reaches NO design/test at all. The "deferred vs missed" distinction
  (DESIGN-OF-RECORD V3) is **element-level → PR-3**.
- **R2b-e — SPEC-00 `Upstream:` is stale cumulative.** `SPEC-00_index.TEMPLATE.md:27`
  reads `**Upstream**: BRD, PRD, EARS, BDD, ADR` — the pre-necessary-upstream
  form. SPEC's necessary upstream is `EARS, BDD, ADR` (`TRACEABILITY.md`:
  "Layer 6 (SPEC): @ears @bdd @adr"); BRD/PRD are transitive. This is the
  `INDEX-UPSTREAM-RESIDUE` TODO scoped to SPEC-00.
- **R2b-f — Index-doc gating is a NARROW hazard; the `-00` doc-id guard is
  robust defense.** Pass-5 empirical correction of the Pass-2 framing: the
  per-layer index templates declare `artifact_type` **nested under
  `custom_fields:`** and carry **no top-level `doc_id`** (verified: corpus
  `09_CHG/CHG-00_index.md` is absent from `doc_layer` — `build_edge_graph` skips
  any doc with no top-level `doc_id`, `__init__.py` `if not doc_id: continue`).
  So a *template-shaped* index never enters `doc_layer`, and the naive
  `"SPEC" in doc_layer.values()` test does **not** fire on it. The hazard fires
  **only** for an index authored with a **top-level `doc_id: <TYPE>-00`** (then
  `_artifact_code`'s doc-id-prefix fallback resolves `SPEC`). The **`-00`
  index doc-id convention** (every layer's index is `<TYPE>-00`, content docs
  start at `01`) is the robust guard against that case and against any future
  index relabeling — NOT element-declaration (R2b-g). Fixing the index
  `artifact_type` labels corpus-wide is a tracked follow-up, not 2b.
- **R2b-g — SPEC/IPLAN docs declare NO canonical `LAYER.NN.SS.hex` element
  IDs.** Verified on the corpus: `element_host` hosts elements for BRD(33) /
  PRD(25) / EARS(26) / BDD(31) / ADR(12) / TDD(35) but **SPEC(0) and IPLAN(0)** —
  `SPEC-01.md` contains zero `SPEC.01.*` IDs. SPEC docs carry interface/contract
  sections, not hash element IDs. **Consequence:** "is a real SPEC present?"
  CANNOT be answered by `element_host` (a real SPEC-01 and a bare SPEC-00 index
  both host zero own-layer elements). The gating MUST use the `-00` doc-id
  signal (R2b-f). Enumeration of the EARS/BDD docs being *checked* still uses
  `element_host` correctly (EARS/BDD DO declare elements).

## Design decisions

**DD-2b-1 — Doc-level binding (symmetric with `COV01`).** `COV02` checks, for
each EARS/BDD **doc** that declares ≥1 element, whether the doc transitively
reaches a SPEC or TDD doc (`{SPEC, TDD} ∩ _doc_forward_reach(g, doc)`). It does
NOT check per-element coverage — that is PR-3. Rationale: identical to why
`COV01` is doc-level, and it keeps the corpus green.

**DD-2b-2 — Enumerate EARS/BDD docs via `element_host` (deliberate, not
incidental).** `COV02` enumerates the host docs of declared EARS/BDD elements
(`{host for elem,host in element_host if elem-layer ∈ {EARS,BDD}}`). This is
chosen **specifically because** it excludes the element-less `*-00` index
templates (R2b-f) — a future maintainer must NOT "simplify" it to
`doc_layer ∈ {EARS,BDD}`, which would re-admit index docs. **An EARS/BDD doc
that declares zero parseable elements is OUT of scope** for `COV02` v1 (coverage
is undefined without elements; such a doc is a malformed-ID problem that
`ID03`/`STRUCT01` own, not a coverage gap). Note this trade-off explicitly so it
is a decision, not an accident.

**DD-2b-3 — Gating on a real (non-index) design/test doc + run-mode severity.**
`COV02` no-ops unless the corpus contains a **real** SPEC or TDD doc — defined as
a doc with `doc_layer ∈ {SPEC, TDD}` whose `doc_id` does **not** end in `-00`
(the index convention; R2b-f). This is the activation floor: a doc is realized
by a SPEC **or** a TDD, so the presence of either real design/test doc means the
cascade has reached the realization stage. *The presence test deliberately uses
the `-00` doc-id signal, NOT element-declaration* — because real SPEC/IPLAN docs
declare no canonical elements (R2b-g), so an element-declaring test would treat
every real SPEC as absent. This OR floor **diverges from `COV01`'s AND floor**
(`SPEC AND IPLAN`) — deliberately:
`COV02` activates the moment real design/test exists, which is the correct point
to start asking "is every requirement realized?". Severity uses `COV01`'s
**run-mode mechanism** with a **deliberate divergence**: an EARS/BDD doc
reaching no SPEC/TDD is a **warning in `build`, error in `gate-code`** — this is
intentionally *softer* than the strict analog (`COV01`'s "FR reaches no SPEC"
branch is `error` in **both** modes, `__init__.py:1391`; COV02's "reaches
nothing" is its structural twin). The softening is justified: at **doc** level a
backward gap occurs **transiently during multi-feature incremental design**
(feature-1's SPEC authored — which *activates* the gate — while feature-2's
EARS/BDD is not yet designed), so `build` keeps it advisory and `gate-code`
blocks at promotion. Wired into `lint_path` behind the existing
`--skip-coverage-gate` flag (one escape hatch covers `COV01` + `COV02`).

**DD-2b-4 — SPEC-00 `coverage` section (new, normative — the doc-of-record).**
Add a `## Coverage` section to `SPEC-00_index.TEMPLATE.md` (after "Related
Documents", before "Maintenance Notes") documenting the backward-coverage
contract: every upstream EARS/BDD requirement must be realized by ≥1 downstream
SPEC/TDD, enforced deterministically by `sdd_doc_lint COV02` and reviewed at
GATE-06; element-level enforcement arrives with PR-3. This is the SPEC-side
counterpart to the BRD-template `_authored_form` rule 2a added, and the normative
home for the contract (since `COV02` adds no gate-catalog entry — R2b-a).

**DD-2b-5 — SPEC-00 `Upstream:` fix (R2b-e).** Change `:27`
`**Upstream**: BRD, PRD, EARS, BDD, ADR` → `**Upstream (necessary)**: EARS, BDD,
ADR` + a one-line note that BRD/PRD are reachable transitively (one hop per
layer). Leave the global `**Traceability chain**:` line (correct end-to-end
chain, not a per-layer upstream claim). **Also leave the second `**Upstream**:
[05_ADR]` at `:62`** — it is the "Related Documents" *adjacent-folder nav link*,
a different kind of statement (navigation, not a necessary-upstream claim);
touching it would over-reach. Closes `INDEX-UPSTREAM-RESIDUE` for SPEC-00's
necessary-upstream line only; the cross-template sweep + the `*-00`
`artifact_type` mislabel (R2b-f) stay separate tracked TODOs.

## Scope

**In:** the `COV02` doc-level backward lint check (DD-2b-1/2/3); the SPEC-00
`coverage` section (DD-2b-4); the SPEC-00 `Upstream:` fix (DD-2b-5); unit +
conformance tests (incl. a gating-excludes-bare-index test); re-vendor of the
edited SPEC-00 template + the linter; framework MINOR bump.

**Out of scope (→ PR-3 / follow-on):** element-level backward coverage; the
EARS/BDD per-element deferral signal + the "deferred vs missed" distinction;
remediating the 15 orphaned corpus BDD scenarios (corpus re-cascade, tracked
separately); ADR backward coverage; a formal `GATE-06-E005` catalog entry
(`COV02` is structural-tier, like `COV01` — R2b-a); the `*-00` `artifact_type`
mislabel fix (R2b-f) + the cross-template `Upstream:` sweep; **transitive-orphan
blind spot** — at doc level a BDD doc that reaches a SPEC passes even if that
SPEC is itself never built (no TDD/IPLAN); SPEC→build orphans are COV01/PR-3
territory.

## Verification

| #  | Check | Expected |
| -- | ----- | -------- |
| V1 | `COV02` flags an EARS/BDD doc whose elements reach no SPEC/TDD | finding (severity per mode) |
| V2 | `COV02` is silent when the EARS/BDD doc reaches a SPEC or TDD | no finding |
| V3 | run-mode: no-SPEC/TDD EARS/BDD doc → `warning` in `build`, `error` in `gate-code` | matches `COV01` shape |
| V4 | gating no-ops when the corpus has no **real** (non-`-00`) SPEC/TDD doc. **The fixture must build the index with a top-level `doc_id: SPEC-00`** (e.g. `_doc("SPEC-00","SPEC",…)`) so the `-00` guard is actually exercised — a template-shaped index (nested `artifact_type`, no top-level `doc_id`) is skipped by `build_edge_graph` and would pass even without the guard (R2b-f) | `[]` |
| V5 | `--skip-coverage-gate` suppresses `COV02` (and `COV01`) | `[]` |
| V6 | Example corpus stays green — every EARS/BDD doc reaches SPEC/TDD at doc level | 0 `COV02` |
| V7 | SPEC-00 `coverage` section + `Upstream:` fix present in canonical AND vendored copies | true |
| V8 | Conformance + corpus green; framework + both `FRAMEWORK_SPEC_VERSION` bumped; vendored byte-identity intact | green |

## Build order

1. `_check_backward_coverage` (`COV02`) in `sdd_doc_lint` — reuses
   `build_edge_graph` + `_doc_forward_reach` + `element_host` (to enumerate the
   EARS/BDD docs); non-`-00` SPEC/TDD presence gate (R2b-f/g) + run-mode severity
   (DD-2b-3); wire into `lint_path` behind `--skip-coverage-gate`. Unit tests
   `test_backward_coverage.py` (incl. the `EARS-01` + bare-`SPEC-00` gating case
   V4). Re-vendor the linter (`sync-vendored.sh`).
2. SPEC-00 `coverage` section (DD-2b-4) + `Upstream:` fix (DD-2b-5); **re-vendor
   the SPEC-00 template** into `platforms/claude-code-plugin/framework/`
   (`sync-plugin-framework.sh`). Conformance test (extend
   `test_coverage_engine.py`): `COV02` fires/no-ops + corpus green + the SPEC-00
   section/Upstream present in both copies.
3. Framework MINOR bump (`bump_version.py`) + hard-pin + CHANGELOG; corpus green
   (V6); full suite; pre-push adversarial self-review; PR (spec-tier → human
   sign-off per OPS-0062).

## Review log

### Pass 1 — 2026-06-27 — self (draft)

Drafted from the merged 2a engine + grounded corpus checks (doc-level green,
element-level 15-BDD-gap).

### Pass 2 — 2026-06-27 — independent (fresh-context)

Grounding reproduced exactly (GATE-06 E001-E004; SPEC-00 stale Upstream; doc-level
green / 15 BDD element gaps). 4 load-bearing design gaps + 6 minors folded:

- **Index-doc gating hazard (BLOCKER)** → R2b-f added; DD-2b-3 now gates on
  *element-declaring* SPEC/TDD docs, not bare `doc_layer` values; V4 tests the
  bare-`*-00` case. (`COV01`'s parallel latent hazard noted, fix deferred.)
- **Over-blocking incremental builds** → DD-2b-3 adopts `COV01`'s run-mode
  severity (warning/`build`, error/`gate-code`) instead of error-both-modes.
- **"Mirror COV01" inaccurate for gating** → DD-2b-3 now states the OR floor
  *diverges* from COV01's AND floor, with rationale; only the *severity* mirrors.
- **GATE-06-E005 ↔ E002 collision + multi-surface wiring** → **dropped the
  formal E005 entirely**; R2b-a establishes `COV02` as a structural lint code
  (like `COV01`), with the SPEC-00 `coverage` section as the doc-of-record.
  Removes the gate-catalog/approval-form/§7.1 surface edits.
- Minors: DD-2b-2 documents the `element_host` enumeration choice + the
  element-less-doc out-of-scope; re-vendor of SPEC-00 added to build-order step
  2 + V7; transitive-orphan blind spot added to Out-of-scope; `*-00` mislabel
  noted as a tracked follow-up.

### Pass 3 — 2026-06-27 — self re-validation (empirical, of the Pass-2 patches)

Empirically validated the Pass-2 fixes against the corpus and found one
**broke**:

- **The "element-declaring presence gate" (Pass-2 fix for Finding 1) is
  WRONG.** Verified `element_host` hosts **SPEC(0), IPLAN(0)** elements —
  `SPEC-01.md` declares zero `SPEC.01.*` IDs (SPEC docs carry interface/contract
  sections, not hash element IDs). So a real SPEC-01 and a bare SPEC-00 index
  are indistinguishable by element-declaration → the gate would treat every real
  SPEC as absent. **Re-fixed:** gate on the **`-00` index doc-id convention**
  instead (DD-2b-3, R2b-f, R2b-g): real SPEC/TDD = `doc_layer ∈ {SPEC,TDD}` AND
  `doc_id` not ending `-00`. Re-verified: on the real corpus this activates
  (SPEC-01/TDD-01 present); on a bare-`*-00`-index-only corpus it no-ops
  (`{SPEC,TDD} ∩ non-index = ∅`). Enumeration of the EARS/BDD docs being checked
  still uses `element_host` (EARS/BDD DO declare elements) — unaffected.
- Re-confirmed dropping the formal `GATE-06-E005` leaves no dangling reference:
  the plan no longer cites a catalog/approval-form/§7.1 edit; the SPEC-00
  `coverage` section is the sole doc-of-record (R2b-a / DD-2b-4).

*Pending Pass 4:* confirm the `-00`-signal re-fix introduced no new gap (e.g.
a layer whose only real doc IS numbered `00` — there is none; `NN` starts at 01
for content docs) and that the corpus coverage (EARS/BDD → SPEC/TDD at doc
level) is unchanged by the gating-signal swap.

### Pass 4 — 2026-06-27 — self re-validation (of the Pass-3 re-fix)

- The `-00` gating signal is sound: content docs are numbered from `01`
  (`SPEC-01`, `TDD-01`); `NN=00` is reserved for the per-layer index across all
  8 layers (BRD-00…IPLAN-00). No real content doc is `-00`, so the signal never
  excludes a real SPEC/TDD.
- The gating-signal swap does NOT touch the **coverage** computation (which uses
  `_doc_forward_reach` over `doc_layer`, independent of the presence test), so
  the corpus stays green (every EARS/BDD doc reaches SPEC/TDD at doc level —
  re-confirmed). No new load-bearing gaps.

### Pass 5 — 2026-06-27 — independent (fresh-context, of the final state)

Confirmed the core design holds (the `-00` gating signal + doc-level scope are
correct; R2b-g reproduced — SPEC 0 / IPLAN 0 elements) but found 3 precision
defects in the twice-revised gating/severity decisions:

- **R2b-f's hazard mechanism was empirically wrong** → the index template's
  `artifact_type` is *nested under `custom_fields`* with no top-level `doc_id`,
  so `build_edge_graph` **skips** template-shaped indexes (they never enter
  `doc_layer`); the naive test does not fire on them. The hazard is narrow (only
  a top-level-`doc_id: <TYPE>-00` index). R2b-f corrected; the `-00` guard kept
  as robust defense.
- **V4 was a vacuous regression test** → with a template-shaped `SPEC-00`
  fixture it passes even *without* the guard. V4 now requires the fixture to
  carry a **top-level `doc_id: SPEC-00`** so the guard is actually exercised.
- **"Severity mirrors COV01" was inaccurate** → COV02's reaches-nothing case is
  the twin of COV01's *error-both-modes* "no-SPEC" branch (`:1391`), so
  warning/`build` is a **deliberate divergence** (justified by transient
  multi-feature incremental gaps), not a mirror. DD-2b-3 reframed.
- Minor: the second `**Upstream**: [05_ADR]` at `SPEC-00…:62` is the
  Related-Documents nav link — DD-2b-5 now explicitly leaves it (preempts a
  reviewer flag).

### Pass 6 — 2026-06-27 — self confirm (of the Pass-5 fixes)

- R2b-f/V4 now describe the real trigger (top-level `-00` doc_id) and the test
  exercises it; the `-00` guard is unchanged and still corpus-correct.
- DD-2b-3 severity is now framed as an explicit divergence with rationale — no
  remaining "mirror" overclaim. The `:62` nav link is documented as intentionally
  untouched. No new load-bearing gaps.

**Result:** READY for the plan PR. Converged over **two independent passes
(2, 5)** + **four self passes** (1 draft, 3 + 4 empirical re-validation,
6 confirm). Each independent pass caught a real flaw a self-pass had missed
(Pass 2: the E005 over-formalization + over-blocking; Pass 5: the
empirically-wrong index-hazard mechanism + the vacuous V4 test) — exactly why
the workflow mandates independent cycles. Every gating/coverage/severity claim
is now a verified-present signal; no un-grounded premise remains.
