# CFB-PR-3 — Ref-granularity enforcement (`REFGRAN01` + tag-syntax page)

> Sub-PR **PR-3** of CFB-PR-2 (the lint-hardening sibling, **co-dependent with
> PR-2**). The coverage gates `COV01`/`COV02` are document-level because the
> *data* isn't guaranteed element-precise: a downstream layer MAY cite an
> upstream requirement at the doc level. PR-3 **enforces the existing
> element-level-ref standard** so element-level coverage becomes computable —
> the prerequisite that makes the engine *bite*.

| Field          | Value                                                |
| -------------- | ---------------------------------------------------- |
| Task           | CFB-PR-3 (ref-granularity) — `BL-REF-GRANULARITY` + `D54-F07` |
| Type           | feature (lint + spec doc)                            |
| Status         | READY — 2026-06-27 · 3 independent (P2/P4/P5) + 3 self passes; GD-03 settled the policy (#192) |
| Parent         | `plans/CONSUMER-FEEDBACK-001-PLAN.md` (PR-3); CFB-PR-2 2a/2b merged (#187/#190, spec `0.25.0`) |
| Depends on     | 2a/2b (merged); **GD-03 ref-granularity policy merged (#192, spec `0.26.0`)** — REFGRAN01 enforces it. **Feeds** the element-level `COV01`/`COV02` upgrade (downstream payoff). |
| Version impact | framework **MINOR** (new tag-syntax page + ID_NAMING clause) + tooling. Bump via `bump_version.py`. |

## Objective

`COV01` (forward) and `COV02` (backward) bind at **document** level because a
verification-context citation MAY be doc-level (`@ears: EARS-01`) instead of
element-level (`@ears: EARS.01.03.xxxx`). The element-level standard **already
exists** (`ID_NAMING_STANDARDS.md:104-111`) but **nothing enforces it**. PR-3
adds the deterministic lint that enforces it (`REFGRAN01`), the human-facing
**tag-syntax reference page** (`D54-F07`), and re-cascades the few corpus
violations — so the data is element-precise and the element-level coverage
upgrade (a named follow-on) becomes possible.

## Implementation reality (grounded — verified against code + corpus)

- **R3-a — The element-level standard EXISTS; enforcement does NOT.**
  `ID_NAMING_STANDARDS.md:104-110` declares `@brd/@prd/@ears/@bdd/@adr/@tdd`
  element-level (`:110` `@tdd: TDD.NN.SS.xxxx … (test case level)`) and
  `@spec/@iplan` document-level (`:109,:111`); `:64-98` is the element-ID
  exemption (SPEC §5 / IPLAN §4 "MAY carry element IDs but are not required to").
  But `sdd_doc_lint` has **no check** requiring element-level refs — `_TAG`'s
  `[^\s|]+` accepts both forms; `ID01/ID02/ID03` validate *form*, not
  *granularity*; `TRACE-RES-001` validates *resolution*, not granularity.
  `REFGRAN01` is **net-new**.
- **R3-b — Element-level refs are IMPOSSIBLE for SPEC/IPLAN targets (R2b-g).**
  SPEC and IPLAN declare **zero** canonical `LAYER.NN.SS.hex` element IDs (the
  element-ID exemption is by design). So the rule requires element-level refs
  ONLY for citations whose **target layer declares elements** — **BL-Q2
  answered:** the "field list" = `@brd @prd @ears @bdd @adr @tdd`
  (element-declaring); `@spec @iplan` stay document-level.
- **R3-c — The corpus is element-precise except 7 doc-level edges across 4
  docs.** Under the precise predicate (an **upstream** trace citation — cited
  layer < citer layer, self-tags + downstream pointers excluded, i.e. the
  `build_edge_graph` edge set — in **doc-level form** to an **element-declaring**
  target) there are **7 violating edges** across 4 docs (Pass-4 corrected the
  earlier per-*pair* count of 4):
  - **5 are redundant** — the doc already carries an element-level trace to the
    same target on/near the line, so the fix is **drop the doc-level tag**:
    `BDD-01:31`, `SPEC-01:31`, `SPEC-01:469`, `TDD-01:204`, `IPLAN-01:43`
    (the `Source TDD | @tdd: TDD-01` header — IPLAN-01 carries `@tdd: TDD.01.04.*`
    anchors at `:188-288`).
  - **2 require CONVERSION** to element-level (GD-03), not a drop: `BDD-01:55` —
    the **feature-level necessary-upstream `@ears` tag** → **fanned out** to the
    pipe-delimited union of its scenarios' `@ears` elements (GD-03's mandated
    form; mechanically derivable — BDD-01 has **26** distinct scenario `@ears`).
    This keeps the BDD convention (the Feature carries the necessary-upstream
    tag) intact, just element-level. `SPEC-01:67` — a prose `@adr: ADR-01` line →
    element-level (or dropped if redundant with `:31`/`:469`).
  Every violating doc retains an element-level same-layer trace after the fix, so
  `TAG01` (required-upstream) stays satisfied and the corpus reaches true-green
  (Pass-3 verified).
- **R3-d — No tag-syntax reference page exists.** `TRACEABILITY.md` owns the
  chain + reverse-lookup + necessary-upstream contract; `ID_NAMING_STANDARDS.md`
  has only a minimal Tag-Format table. The per-layer @-tag punctuation /
  cardinality / granularity page (`D54-F07`) is net-new; its doc-boundary with
  `TRACEABILITY.md` must be drawn.
- **R3-e — `BL-STATUS-SCOPE` is orthogonal + collides with PR-7.** Status enums
  live only as per-layer template comments, validated nowhere. PR-7 adds
  `status: Sketch`. This concerns the `status:` field, NOT @-tags — a different
  concern from ref-granularity.

## Design decisions

**DD-3-1 — `REFGRAN01` reuses the `build_edge_graph` edge set (correct
predicate).** REFGRAN01 iterates `graph.edges` (the same adjacency `COV01`/
`COV02` use), which **already** scopes to upstream citations and excludes
self-tags + downstream forward-pointers (`build_edge_graph`). It flags an edge
whose `cited_token` matches `DOC_FORM` AND whose target layer declares elements
(`BRD/PRD/EARS/BDD/ADR/TDD`). Citations to **SPEC/IPLAN** are exempt (no elements
— R3-b). This avoids the false-positive trap of a raw per-line `DOC_FORM` scan
(which would fire on ~36 self-tags + downstream pointers); reusing the graph's
filtering yields the 7 violating edges (R3-c). It does **not** re-check
resolution (`TRACE-RES-001` owns that) or form (`ID01-03` own that) — those pass
on a doc-level tag, so `REFGRAN01` is the SOLE new finding (no double-fire, Pass-2
F5).

**DD-3-2 — Corpus-level pass + run-mode severity + `rel_by_doc` plumbing.**
REFGRAN01 is a **corpus-level** check `_check_ref_granularity(corpus, mode)`
wired into `lint_path` alongside `_check_trace_resolution` — NOT a per-file
`lint_text` check (`lint_text` has no `mode` parameter; `mode` only reaches the
corpus-level passes via `lint_path`). It needs the graph anyway (DD-3-1).
**Per-edge** finding at the offending `@`-tag line; since `TraceEdge` carries
`citer_doc` (a doc_id) not a file path, the check builds a `rel_by_doc` map to
anchor the finding to a file (the `COV02` precedent, `__init__.py` `_check_backward_coverage`).
Severity mirrors `COV01`/`COV02`'s run-mode: a doc-level ref to an
element-declaring target is a **warning in `build`, error in `gate-code`** — so
the migration window / incremental authoring is not hard-blocked. Runs
unconditionally (not behind `--skip-coverage-gate`, which gates only the corpus
*coverage* passes — REFGRAN is a form rule); it no-ops naturally when there are
no upstream edges (single-file runs).

**DD-3-3 — Necessary-upstream/feature tags are element-level (GD-03); only a
true whole-doc dependency is prose.** The granularity policy is now settled by
**GD-03** (merged spec `0.26.0`): every trace citation to an element-declaring
layer is element-level **in all contexts**, including the necessary-upstream /
feature-level tag, and **a unit realizing multiple upstream elements
pipe-delimits them — the union of its sub-units' element citations.** So a BDD
Feature's `@ears` necessary-upstream tag **fans out** to the union of its
scenarios' `@ears` elements (mechanically derivable from the scenario tags), NOT
a coarse doc-level `@ears: EARS-NN`. The fan-out is **auto-derived trace data**
(the scenarios already carry the elements), so the verbosity of a busy Feature
line is the accepted cost of element precision; if it proves untenable in
practice that is a **GD-03 amendment** (a separate spec change), not a plan-level
deviation — this enforcement PR stays consistent with the merged standard. A
genuine whole-document dependency (rare) is stated in **prose**, never a
doc-level trace tag. REFGRAN01 needs **no context exemption** — the rule is
uniform, backed by GD-03.

**DD-3-4 — `D54-F07` tag-syntax reference page + the doc boundary.** A new
`framework/governance/TAG_SYNTAX.md` documents per-layer @-tag **form**:
pipe-delimited multi-tags (`@brd: X | @brd: Y`, DD-8 from 2a), cardinality, the
self-tag / downstream-pointer carve-outs, and cross-refs the **GD-03** "Reference
granularity" clause (already normative in `ID_NAMING_STANDARDS.md` from the
policy PR — TAG_SYNTAX does not duplicate it). **Boundary:** `TRACEABILITY.md`
keeps the chain order + reverse-lookup + necessary-upstream contract;
`ID_NAMING_STANDARDS.md` owns the granularity rule (GD-03); `TAG_SYNTAX.md` owns
punctuation / cardinality / the per-layer worked examples. Also reconcile the
**doc-form necessary-upstream examples in the layer templates** (e.g.
`BDD-00_index.TEMPLATE.md:92` `@ears: EARS-NN` → element-level) so they stop
teaching the form REFGRAN01 forbids.

**DD-3-5 — Corpus re-cascade: 5 drop + 2 convert (R3-c, GD-03).** Two fix
classes, not one:

- **Drop** the 5 redundant doc-level tags (`BDD-01:31`, `SPEC-01:31`,
  `SPEC-01:469`, `TDD-01:204`, `IPLAN-01:43`) — each doc already carries an
  element-level same-target trace, so dropping leaves lineage + `TAG01` intact.
- **Convert** the 2 non-redundant tags to element-level per GD-03: `BDD-01:55`
  (the feature-level `@ears`) **fans out** to the union of its scenarios' `@ears`
  elements (GD-03's mandated form; mechanically derivable). The BDD convention is
  unchanged — the Feature still carries its necessary-upstream tag, now
  element-level. `SPEC-01:67` prose `@adr: ADR-01` → element-level (or drop if
  redundant with `:31`/`:469`).
Done via the framework **fixer skills** (`doc-<layer>-fixer`), never hand-edited;
if a fixer can't perform the convert/drop on a REFGRAN01 finding, that's a
**framework workflow gap** to fix in the skill (per EARS-RT-001), flagged not
worked around. With run-mode severity (DD-3-2) the corpus stays exit-0
(warnings) until the re-cascade lands; true-green (V7) is reachable because every
violating doc retains an element-level same-layer trace (Pass-3 verified).

**DD-3-6 — SPLIT `BL-STATUS-SCOPE` out (R3-e).** The status-enum hardening is
orthogonal (the `status:` field, not @-tags), P3, and entangles the PR-7
`Sketch` value. Per the parent plan's "split `BL-STATUS-SCOPE` out if a 4th
surface appears" guidance, it ships as a **separate PR-3b**. Not in this PR.

**DD-3-7 — The element-level `COV01`/`COV02` upgrade is the DOWNSTREAM payoff,
not this PR.** Once `REFGRAN01` guarantees element-precise refs, `COV01`/`COV02`
can bind at element level. That upgrade is a **named follow-on** (it forces the
EARS/BDD deferral signal + remediating the 15 orphaned BDD scenarios 2b
surfaced) — out of scope here. PR-3 *enables* it.

## Scope

**In:** `REFGRAN01` corpus-level lint (DD-3-1/2/3); the `TAG_SYNTAX.md` page +
the BDD/SPEC template doc-form-example reconciliation to element-level
(DD-3-4); the 7-edge re-cascade (5 drop + 2 convert, incl. the BDD-01:55
fan-out) via fixers (DD-3-5); unit + conformance tests; re-vendor (linter +
governance/template docs); framework MINOR bump. (GD-03 + the `ID_NAMING` clause
already merged via #192; the BDD necessary-upstream convention is unchanged —
the Feature tag becomes element-level fan-out, it is not removed.)

**Out of scope:** `BL-STATUS-SCOPE` → **PR-3b** (DD-3-6); the element-level
`COV01`/`COV02` upgrade + the EARS/BDD deferral signal + the 15-orphan
remediation → **follow-on** (DD-3-7); the cross-template `Upstream:` sweep
(separate `INDEX-UPSTREAM-RESIDUE` TODO); any change to `TRACE-RES-001` /
`ID01-03` (REFGRAN is additive).

## Verification

| #  | Check | Expected |
| -- | ----- | -------- |
| V1 | `REFGRAN01` flags a doc-level upstream trace tag to an element-declaring layer (`@ears: EARS-01`) | finding (per mode) |
| V2 | silent on the element-level form (`@ears: EARS.01.03.xxxx`) | no finding |
| V3 | silent on `@spec: SPEC-01` / `@iplan: IPLAN-01` (exempt targets — R3-b) | no finding |
| V4 | silent on self-tags + downstream forward-pointers (graph already excludes them) | no finding |
| V5 | run-mode: warning in `build`, error in `gate-code` | matches COV01/COV02 |
| V6 | no double-fire: a doc-level `@ears: EARS-01` yields ONLY `REFGRAN01` (not `ID01`/`TRACE-RES-001`) | true |
| V7 | After the convert/drop re-cascade, the example corpus is true-green (0 `REFGRAN01`) | 0 |
| V8 | `TAG_SYNTAX.md` present (canonical + vendored); `ID_NAMING` cross-ref; boundary with `TRACEABILITY.md` (no duplicate chain/reverse-lookup) | true |
| V9 | Conformance + corpus green; framework + both `FRAMEWORK_SPEC_VERSION` bumped; vendored byte-identity | green |

## Build order

1. `_check_ref_granularity` (`REFGRAN01`) in `sdd_doc_lint` — reuse
   `build_edge_graph` edges + `DOC_FORM` + the element-declaring-layer set;
   per-edge finding; run-mode severity; wire into `lint_path` beside
   `_check_trace_resolution`. Unit tests `test_ref_granularity.py` (incl. the
   self-tag / downstream / SPEC-exempt no-fire cases V3/V4/V6). Re-vendor the
   linter.
2. `governance/TAG_SYNTAX.md` (DD-3-4) + `ID_NAMING_STANDARDS.md` cross-ref;
   re-vendor the bundle. Conformance test (REFGRAN contract + the page present in
   both copies + the TRACEABILITY boundary guard).
3. Corpus re-cascade: the 7 violating edges (5 drop + 2 convert, incl. the
   BDD-01:55 element-level fan-out) via the fixer skills (DD-3-5); re-verify
   true-green (V7).
4. Framework MINOR bump + hard-pin + CHANGELOG; full suite; pre-push adversarial
   self-review; PR (spec-tier → human sign-off per OPS-0062).

## Review log

### Pass 1 — 2026-06-27 — self (draft)

Drafted from grounded standards/corpus facts: the standard already exists (R3-a);
SPEC/IPLAN element-less so the rule scopes to element-declaring targets (R3-b,
BL-Q2). Scoped to `BL-REF-GRANULARITY` + `D54-F07`, splitting `BL-STATUS-SCOPE`.

### Pass 2 — 2026-06-27 — independent (fresh-context)

Grounding confirmed (standard exists; no element-level lint; SPEC/IPLAN
element-less). 3 load-bearing gaps + 2 minors folded:

- **F1 — predicate under-specified; "4" false as a raw per-line scan** (fires
  ~36 on self-tags + downstream pointers). → DD-3-1 now **reuses
  `build_edge_graph` edges** (already upstream-only + self/downstream-excluded),
  yielding exactly 4; V4/V6 added.
- **F2 — IPLAN→TDD whole-doc dependency conflict** (a `Source TDD` manifest has
  no single element; "re-point to the element" was unimplementable). → empirical
  check showed IPLAN-01 ALSO carries element-level `@tdd:` anchors; new **DD-3-3**
  resolves it uniformly: whole-doc dependency goes in **prose + element anchors**,
  never a doc-level trace tag; no context exemption needed.
- **F3 — `lint_text` has no `mode`** (per-file + run-mode were mutually
  exclusive). → DD-3-2 makes REFGRAN a **corpus-level pass in `lint_path`** (has
  `mode` + the graph); dropped "per-file like ID01-03".
- **F4 — the 4 fixes are heterogeneous** → R3-c + DD-3-5: all 4 are redundant
  header/"Source" tags with element-level body traces present, so the fix class
  is uniform **convert/drop**; V7 reachable.
- **F5 (favorable) — no double-fire** (doc-level tag passes ID01 + resolves
  under TRACE-RES-001) → recorded; V6 locks it.
- Minor — R3-c sub-counts mislabeled → replaced with the precise predicate +
  the 4 violations.

### Pass 3 — 2026-06-27 — self re-validation (empirical, of the Pass-2 patches)

Both pending items confirmed against the corpus:

- **`build_edge_graph`-edge reuse yields exactly 4** (re-measured: `BDD→EARS-01`,
  `IPLAN→TDD-01`, `SPEC→ADR-01`, `TDD→ADR-01`) — the graph's upstream/self/
  downstream filtering is the correct predicate (F1 fix holds).
- **The convert/drop re-cascade keeps `TAG01` satisfied for all 4.** Each doc
  retains an element-level same-layer trace after dropping its redundant
  doc-level header tag (BDD-01 has 50 `@ears: EARS.01…`; IPLAN-01/SPEC-01/TDD-01
  retain element-level `@tdd`/`@adr`). Cross-checked against
  `LAYER_REGISTRY.yaml` `required_tags` (BDD→ears, SPEC→ears/bdd/adr, TDD→ears/
  bdd/adr/spec, IPLAN→spec/tdd) — none trips. V7 reachable.

No new gaps. *Pending Pass 4 (independent):* re-validate the revised whole-plan
for any inconsistency the Pass-2 rewrite introduced.

### Pass 4 — 2026-06-27 — independent (fresh-context) — SURFACED A POLICY FORK

Confirmed coverage stays green, run-mode plumbing consistent, MINOR justified.
But found the Pass-2/3 "exactly 4, uniform drop" claim is **wrong**, and the
correction exposes an unresolved framework-policy decision:

- **Per-edge count is 7, not 4** (I'd deduped to citer→target *pairs*):
  `BDD-01 @ears: EARS-01` ×2 (`:31`, `:55`), `SPEC-01 @adr: ADR-01` ×3
  (`:31`, `:67`, `:469`), `IPLAN-01 @tdd: TDD-01` (`:43`), `TDD-01 @adr: ADR-01`
  (`:204`). DD-3-2 emits a per-edge finding → 7. Fix: dedupe by pair OR enumerate
  all 7 lines; "fix the 4" leaves 3 live and V7 fails.
- **`TraceEdge` carries `citer_doc` (doc_id) + `line`, NOT a rel-path** → REFGRAN
  must build a `rel_by_doc` map (the COV02 precedent, `__init__.py:1460-1466`).
- **2 of the 7 are NOT droppable redundant header tags** → `BDD-01:55` is the
  **feature-level necessary-upstream `@ears` tag** (must stay a machine-resolvable
  tag per BDD's necessary-upstream contract — it CANNOT become prose, which
  **contradicts DD-3-3**) and `SPEC-01:67` is a prose `@adr: ADR-01` line. The
  framework is internally **inconsistent**: `04_BDD/README.md:61` shows the
  element form `@ears:EARS.NN.03.xxxx` while `BDD-00_index.TEMPLATE.md:92` ships
  the doc form `@ears: EARS-NN`.

**Open decision (surfaced to the user 2026-06-27):** the simple "all doc-level
refs to element-declaring layers are violations, fixed by drop" rule collides
with two legitimate doc-level patterns — the **necessary-upstream feature tag**
and **whole-doc Source manifests**. Resolving it requires a framework
granularity policy + a template reconciliation. Plan paused for the decision.

### Policy resolution — 2026-06-27 — GD-03 merged (#192, spec `0.26.0`)

The user chose **element-level everywhere** ("functionality is defined in the
elements, not the abstract document"). Settled as **GD-03** + the
`ID_NAMING_STANDARDS.md` "Reference granularity" clause, merged as a standalone
policy PR **before** this enforcement PR. The Pass-4 findings are now folded
against the settled rule:

- Per-edge count corrected to **7** (R3-c); DD-3-2 emits per-edge findings + a
  `rel_by_doc` map.
- The 2 non-redundant edges (`BDD-01:55` feature tag, `SPEC-01:67` prose) are
  **converted to element-level** per GD-03 — the feature tag **fans out** to its
  scenarios' `@ears` union (DD-3-3/DD-3-5); no context exemption, no
  contradiction (DD-3-3 now *aligns* with GD-03, superseding its earlier
  prose-only framing).
- DD-3-4 reconciles the contradictory template doc-form examples
  (`BDD-00_index.TEMPLATE.md:92` etc.).

### Pass 5 — 2026-06-27 — independent (fresh-context, of the GD-03-folded plan)

Confirmed the 7-edge predicate (7 of 272 edges, exact lines), the `rel_by_doc`
plumbing (COV02 precedent), the `mode` wiring, and the scope. Caught **one
decisive contradiction**:

- **The plan's "drop the BDD feature tag" CONTRADICTED merged GD-03**, which
  mandates fan-out ("a unit realizing multiple upstream elements pipe-delimits
  them — the union of its sub-units' element citations") and names the BDD
  Feature `@ears` tag as the worked example. An enforcement PR cannot ship a
  corpus example that violates the standard it enforces; the plan was also
  internally inconsistent (its own resolution log said fan-out). **Fixed:**
  `R3-c`/`DD-3-3`/`DD-3-5`/Scope/build-order all aligned to **fan-out** the
  BDD-01:55 Feature tag (re-cascade = 5 drop + 2 convert, incl. the fan-out); the
  BDD necessary-upstream convention is unchanged (the Feature keeps its tag,
  now element-level). The 26-tag verbosity is the accepted cost of precision
  (auto-derived); if untenable it is a GD-03 amendment, not a plan deviation.
- Minor: build-order step 3 stale "4" → 7 (5 drop + 2 convert).

### Pass 6 — 2026-06-27 — self confirm (of the Pass-5 alignment)

- `R3-c`, `DD-3-3`, `DD-3-5`, Scope, and build-order step 3 now uniformly say
  **fan-out** BDD-01:55 (no residual "drop the container tag"); consistent with
  GD-03 + `ID_NAMING_STANDARDS.md` "Reference granularity" + the BDD README
  convention + the plan's own log. The fan-out is mechanically derivable (26
  scenario `@ears` elements, measured). No new load-bearing gaps.

**Result:** READY for the plan PR. Converged over **3 independent passes
(2, 4, 5)** + **3 self** passes. The recurring load-bearing surfacings (the
predicate scoping, the SPEC-no-elements reality, the per-edge count, and the
GD-03 policy fork) are all resolved against verified-present signals; the policy
itself was settled in a separate PR (#192) so this enforcement PR is consistent
with the standard it enforces.
