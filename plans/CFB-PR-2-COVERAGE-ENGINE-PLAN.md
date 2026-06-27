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
| Status         | READY — 2026-06-27 · converged Pass 1 (self) + Pass 2 (independent) + Pass 3 (self) |
| Parent         | `plans/CONSUMER-FEEDBACK-001-PLAN.md` (PR-2)         |
| Depends on     | PR-1 (merged); **PR-3 lands with sub-PR 2a** (ref-granularity) |
| Version impact | framework **MINOR** (new `SPEC-00` coverage section, GATE-06, phase tag schema) + tooling. Bump via the now-fixed `bump_version.py` (PR #182). |

## Objective

Build the forward/completeness half of traceability the framework lacks:
`trace_walk.py` is **backward/transitive only** and collapses tags to doc-ids.
Nothing asserts forward that **every BRD functional requirement reaches ≥1 SPEC
and ≥1 IPLAN**, that **every EARS/BDD element has a covering SPEC/TDD or an
explicit deferral**, or that **no out-of-phase item leaked into an in-phase
plan**. This engine adds those checks + the BDD doc-set roll-up + the generated
trace matrix, surfacing gaps only caught by manual re-reading today.

## Resolved design decisions (folded from Pass-2 independent review)

**DD-1 — Engine host (Pass-2 #7).** Gate logic lives in **`sdd_doc_lint`**,
reusing its existing full-corpus `doc_index` + **`element_index`** built in
`_check_trace_resolution` (`__init__.py:943-964`) — forward coverage is the
inverse traversal over that same edge set. **Do NOT extend `trace_walk.walk()`**
(it is a single-start backward BFS that collapses tags to doc-ids at the door —
wrong data model). Refactor `trace_walk`'s `_TAG` regex + `_locate_doc` into a
shared helper module; the **matrix emitter is a new thin reporter
`tools/sdd_coverage.py`** consuming that shared core.

**DD-2 — "covered" is an extensible covered-state enum (Pass-2 #1, closes
orchestration R2-HIGH).** Define `covered_state ∈ { authored | deferred |
realized_by:<layer> | satisfied_by_reference }`. PR-2 implements `authored`,
`deferred`, `realized_by`; **`satisfied_by_reference` is declared as an enum
member but stubbed** (PR-5 implements it — adds a member, not a rewrite). The
gate's "covered?" predicate dispatches on this enum so PR-5 extends, never
re-defines.

**DD-3 — FR identification (Pass-2 #2).** The forward gate gates **only BRD
elements under `functional_requirements.requirements[]`** (form `BRD.NN.07.*`
but identified by **YAML path, not the `.07.` ordinal**, which is per-doc and
not guaranteed). Objectives / stakeholders / risks carry element IDs but are
NOT gated. Mechanism: the lint resolves the element's owning section via the
artifact's parsed structure; only `functional_requirements` elements enter the
forward-coverage set.

**DD-4 — Phase model (Pass-2 #3; reconciled with the EXISTING model).** Separate
schema from value:

- *Schema:* register the phase concept in `LAYER_REGISTRY.yaml` +
  `ID_NAMING_STANDARDS.md` (allowed values, "required on gated FR elements").
- *Value:* **reuse the existing `priority: P1 | P2 | Future`** on FR elements
  (`BRD-TEMPLATE.yaml:529-532`) as the cycle band; `priority: Future` IS the
  **deferral signal** (resolves the missing-`deferred:`-field gap — no new
  field). The authoritative current-phase / scope ledger is the existing BRD
  `project_scope` / `acceptance_criteria` section + the `BRD-TEMPLATE.yaml:160`
  rule ("phase names + count match between scope and implementation").
- **Reject** the element-ID-segment option (IDs are content-hashed; encoding
  phase would churn every `@`-ref and collide with PR-4/PR-9).

**DD-5 — Non-SPEC realization escape taxonomy (Pass-2 #4).** An FR / EARS / BDD
element is NOT a false-block if its `covered_state` is `deferred`
(`priority: Future`), `realized_by:<layer>` (e.g. an ADR-only decision, NFR, or
infra with no dedicated SPEC component), or (PR-5) `satisfied_by_reference`. The
gate blocks only on a `priority:P1/P2` FR with **none** of these and no SPEC/
IPLAN. Enumerated now; `realized_by` ships, `satisfied_by_reference` stubbed.

**DD-6 — Severity is run-mode-dependent (Pass-2 #6; reconciles ENG-FWD vs
D54-F13).** The gate takes a **run-mode** input (`--mode {build | gate-code}`,
default `build`). Same finding, two severities:

| finding | `build` (mid-build) | `gate-code` |
|---|---|---|
| `deferred` FR (priority:Future) no IPLAN | warning | warning |
| in-scope (P1/P2) FR no IPLAN | **warning** | **block** |
| FR reaches NO SPEC at all | **block** | **block** |
| out-of-phase item in an in-phase plan | **block** | **block** |

**DD-7 — Matrix deliverable (Pass-2 #5; the PR-1 reverse-lookup contract).**
`sdd_coverage.py` emits a generated **`docs/TRACEABILITY-MATRIX.md`** (BRD→…→
IPLAN, one row per gated FR with its realizing docs + `covered_state`) — this is
the named artifact PR-1's `TRACEABILITY.md` reverse-lookup points at. Generated/
regenerable; never hand-edited. BDD-rollup output is a section of the same.

**DD-8 — Multi-`@brd` (Pass-2 #B-minor).** Parsing is ALREADY supported
(`_TAG = ...([^\s|]+)` terminates on `|`, so `@brd: X | @brd: Z` already
`finditer`s as two tags). New work is only: (a) **OR-group-by-layer** in the
coverage predicate (the existing `required_tags` check is set-membership only,
`:531`), and (b) the **zero-downstream lint**. PR-2 *consumes* multi-`@brd`;
**PR-3 `taglint` owns enforcing** the per-layer punctuation — line drawn.

**DD-9 — C-1 corpus path to green (Pass-2 #9).** New blocking gates WILL fire on
`examples/url-shortener/`. Two distinct remedies: (a) a **`--skip-coverage-gate`
flag** (mirroring `--skip-lint-smoke` / `SDD_LINT_SKIP_TRACE_RES`) for the
transient migration window so the cascade bootstraps; (b) coverage gaps are
**not regen-able** — they close by adding legitimate **`priority:Future` /
`realized_by` annotations** (content, authored via the layer skills, not a
re-cascade). The child plan's corpus step documents which annotations the
url-shortener legitimately needs.

## Scope

**In:** the forward gate + severity split (DD-6), backward leg (SPEC-00
`coverage` section + GATE-06, BeeLocal #54), phase tag + scope reconciliation
(D54-F13, DD-4), BDD doc-set roll-up (D54-F05), multi-`@brd` consume + zero-
downstream lint (DD-8), the generated matrix (DD-7), the `covered_state` enum
(DD-2). Document-level binding for SPEC/TDD/IPLAN (never depends on their exempt
element IDs).

**Also in (Pass-2 #F):** fix the two stale `Upstream:` lines in
`SPEC-00_index.TEMPLATE.md` (:27, :29) **while that file is open** for the
coverage section — shipping a new coverage section into a template still
advertising the cumulative upstream model is self-contradictory. (The broader
multi-template `Upstream:` sweep stays the deferred follow-up.)

**Out of scope (deferred):** `satisfied_by_reference` *mechanism* → PR-5 (the
enum member is defined here; PR-5 implements it). The cross-template `Upstream:`
sweep → new follow-up TODO.

## Sub-PR split (Pass-2 #8 — corrected)

- **2a — graph core + forward gate** (with **PR-3 ref-granularity**, co-landed):
  the shared **bidirectional element-level edge-graph** in `sdd_doc_lint` +
  `tools/sdd_coverage.py` matrix emitter + the forward block/warning gate +
  `covered_state` enum + multi-`@brd` OR-group. PR-3 lands here because element-
  level forward coverage is undefined until doc-level verification refs are
  forbidden.
- **2b — backward leg:** `SPEC-00` `coverage` section + GATE-06 + the SPEC-00
  `Upstream:` fix. Reuses 2a's core (inverse traversal).
- **2c — phase tag + scope reconciliation:** **split for the cap** — *2c-schema*
  (`LAYER_REGISTRY.yaml` + `ID_NAMING_STANDARDS.md`) and *2c-gate*
  (`BRD-TEMPLATE.yaml` phase/priority wiring + `sdd_doc_lint` phase-leak gate),
  each ≤3 surfaces.
- **2d — BDD doc-set EARS roll-up** + split-by-functional-block convention.

Each sub-PR inherits C-1…C-5 (corpus via DD-9, vendored-lint sync, conformance
tests per gate, framework MINOR via the fixed bumper, branch from `origin/main`).

## Verification (per sub-PR; high-level)

| #  | Check | Expected |
| -- | ----- | -------- |
| V1 | Forward gate on corpus, `--mode gate-code`: every P1/P2 FR → ≥1 SPEC + ≥1 IPLAN unless `deferred`/`realized_by` | matrix emitted; DD-6 severities correct |
| V2 | GATE-06 flags an EARS/BDD element with no downstream SPEC/TDD; distinguishes deferred vs missed | true |
| V3 | Out-of-phase (priority:Future) item inside a P1 plan → block | true |
| V4 | Multi-`@brd` per EARS line OR-groups; zero-downstream BRD FR flagged | true |
| V5 | `docs/TRACEABILITY-MATRIX.md` regenerates deterministically; matches PR-1 reverse-lookup contract | true |
| V6 | Conformance + corpus green (via DD-9 annotations + bypass for the migration window) | green |

## Review log

### Pass 1 — 2026-06-27 — self-review (design)

- Grounded against `trace_walk.py` (backward/transitive-only), `SPEC-00_index`
  (no coverage section), the orchestration plan's fork-decisions. Parked the
  stale `Upstream:` finding.

### Pass 2 — 2026-06-27 — independent (fresh-context, `Plan` agent)

NOT-READY; 9 blocking design gaps — all folded as DD-1…DD-9:

- #1 "covered" extension point → **DD-2** (enum; closes R2-HIGH).
- #2 FR identification → **DD-3** (YAML-path-scoped, not `.07.` ordinal).
- #3 phase + deferral signal → **DD-4** (reuse `priority:Future`; schema vs value; reject ID-segment).
- #4 non-SPEC escape taxonomy → **DD-5** (`realized_by`).
- #5 matrix format/location → **DD-7** (`docs/TRACEABILITY-MATRIX.md`).
- #6 severity ↔ D54-F13 → **DD-6** (run-mode `build|gate-code`).
- #7 engine host → **DD-1** (sdd_doc_lint gate + sdd_coverage reporter; not trace_walk).
- #8 sub-split → corrected (PR-3 with **2a**; 2c split for cap; 2a = shared graph core).
- #9 C-1 corpus path → **DD-9** (bypass flag + annotations, not regen).
- Plus #F minor: fix SPEC-00 local `Upstream:` lines in-PR (file already open).

### Pass 3 — 2026-06-27 — self re-validation (of the DD edits)

- Each of the 9 blocking items maps to a concrete DD with a named mechanism +
  citation; no DD contradicts another (the `covered_state` enum DD-2 is the
  hub the severity DD-6, escape DD-5, and FR-scope DD-3 all reference
  consistently). Sub-split now: PR-3↔2a, 2c split, 2a graph-core — consistent
  with the DAG. Matrix↔PR-1 contract pinned (DD-7). No new load-bearing gaps.

**Result:** READY. Converged over an independent Pass-2 that found 9 blocking
gaps, all folded with concrete mechanisms. The plan PR may open; implementation
proceeds as sub-PRs 2a→2d (2a is itself a substantial engine build).
