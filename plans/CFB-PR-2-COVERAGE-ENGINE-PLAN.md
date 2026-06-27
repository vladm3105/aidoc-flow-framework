# CFB-PR-2 — Coverage engine (`ENG-FWD-COVERAGE` + `D54-F13` + `D54-F05`)

> Wave-2 of `CONSUMER-FEEDBACK-001`. The largest single child: a `@`-tag-graph
> **coverage engine** answering "is every requirement realized, and nothing
> out-of-phase?" — forward + backward + phase + BDD-rollup. Depends on PR-1
> (the corrected trace chain, merged `8e001192`). Co-dependent with PR-3
> (ref-granularity makes element-level coverage computable).

| Field          | Value                                                |
| -------------- | ---------------------------------------------------- |
| Task           | CFB-PR-2 (coverage engine)                           |
| Type           | feature (tooling + spec)                             |
| Status         | DRAFT — 2026-06-27 · Pass 1 only (Pass 2 + impl pending) |
| Parent         | `plans/CONSUMER-FEEDBACK-001-PLAN.md` (PR-2)         |
| Depends on     | PR-1 (merged); co-dependent with PR-3                |
| Version impact | framework **MINOR** (new `SPEC-00` coverage section, GATE-06 check, phase tag) + tooling. Bump via the now-fixed `bump_version.py` (PR #182). |

## Objective

Build the forward/completeness half of traceability the framework lacks today:
`trace_walk.py` is **backward/transitive only** ("find every artifact tracing
*back* to BRD-NN"). Nothing asserts, forward, that **every BRD FR reaches ≥1
SPEC and ≥1 IPLAN**, that **every EARS/BDD element has a covering SPEC/TDD (or
an explicit `deferred:`)**, or that **no out-of-phase item leaked into an
in-phase plan**. This engine adds those checks + the BDD doc-set coverage
roll-up, surfacing the gaps that today are only caught by manual re-reading.

## Scope (resolved fork-decisions from the triage — see FRAMEWORK-TODO)

**In:**

- **(a) Forward coverage gate** (`ENG-FWD-COVERAGE`, `sdd_coverage` /
  GATE-CODE pre-check): resolve the `@`-tag graph; assert every BRD FR reaches
  ≥1 SPEC + ≥1 IPLAN; emit the full BRD→…→IPLAN **matrix**; list broken/empty
  downstream paths. **Severity split (Eng-Q2):** a `deferred:`/future-cycle FR
  with no IPLAN = **warning**; an in-scope FR with no IPLAN at GATE-CODE =
  **block**; an FR reaching **no SPEC** = **block** (the false-pass design gap).
- **(b) Backward leg** (`D54-F05` rollup + BeeLocal #54): a `coverage` section
  in the `SPEC-00` index template (each L3/L4 element → its covering SPEC or
  `deferred: <reason>`) + a **GATE-06** check flagging any EARS req / BDD
  scenario with no downstream SPEC/TDD, distinguishing *deferred* from *missed*.
- **(c) Phase tag + scope reconciliation** (`D54-F13`): a first-class phase tag
  on capability elements; "out-of-phase item in an in-phase plan" = **block**;
  the **scope ledger is a designated section of the existing BRD acceptance/
  index, NOT a new artifact**.
- **(d) BDD doc-set EARS roll-up** (`D54-F05`): aggregate `ears_coverage` across
  a split `BDD-01/02` set + a documented split-by-functional-block convention.
- **(e) Multi-`@brd:` per EARS line** (`ENG-FWD-COVERAGE` (b)): permit + lint;
  pipe-delimited repeated same-layer tags `@brd: X | @brd: Z | @prd: Y` (per
  BL-Q3 / `D54-F07`); lint any BRD FR with zero downstream EARS coverage.
- **Binding:** SPEC/TDD/IPLAN bound at **document level** (`@spec: SPEC-NN`),
  so the gate never depends on their (exempt) element IDs — keeps it
  non-conflicting with `ENG-SPEC-IPLAN-ID-EXEMPTION-NOTE`.

**Out of scope (deferred):**

- The reuse-manifest interaction (`satisfied_by_reference` counts as covered) —
  PR-5 builds on this engine; this PR defines "covered", PR-5 extends it.
- The stale `Upstream:` enumerations in the layer index templates / READMEs
  (e.g. `SPEC-00_index` "Upstream: BRD, PRD, EARS, BDD, ADR" — the residual
  cumulative model PR-1's V6 grep missed) → **new follow-up TODO** (same class
  as CFB-PR-1; do NOT expand this PR).

## Approach / Design (grounded)

- **`tools/trace_walk.py`** already builds the transitive `@`-tag closure
  (backward). Extend it (or add `tools/sdd_coverage.py` reusing its graph) to
  walk **forward** (upstream element → realizing downstream docs) and emit the
  matrix. The graph machinery (TAG regex, DOC/ELEM forms, hop walk) is reusable.
- **`sdd_doc_lint`** gains the GATE-06 backward-coverage check + the
  multi-`@brd` permission/zero-coverage lint (extends the existing
  `required_tags` / TRACE-RES-001 machinery at `__init__.py:~530,~917`).
- **`SPEC-00_index.TEMPLATE`** gains the `coverage` section (registry-shaped).
- **Phase tag:** define in `LAYER_REGISTRY.yaml` + `ID_NAMING_STANDARDS.md`;
  scope ledger = a section of the BRD acceptance/index (no new artifact).

## Cross-cutting child-PR contract (inherited — see orchestration plan C-1…C-5)

- **C-1 Corpus:** new **blocking** gates (forward, GATE-06, phase-leak) WILL
  fire on `examples/url-shortener/` — regenerate via skills, never hand-edit;
  needs a migration/bypass note for transient findings.
- **C-2** vendored-lint sync (`sync-plugin-framework.sh`).
- **C-3** conformance tests for every new gate.
- **C-4** framework MINOR bump (now clean via `bump_version.py` #182).
- **C-5** branch from `origin/main`; multi-hour cascade regen — budget it.

## Surface-cap / split guidance

This is **>3 surfaces** and a large engine. The orchestration plan flags it to
**split into sub-PRs sharing the engine** if it exceeds the cap, e.g.:
**2a** forward gate + matrix + multi-`@brd`; **2b** backward leg (SPEC-00
coverage + GATE-06); **2c** phase tag + scope reconciliation; **2d** BDD
roll-up. PR-2a lands the engine; 2b–2d build on it. Co-dependent PR-3
(ref-granularity) lands with 2b (granularity makes element-level coverage
computable).

## Verification (high-level; each sub-PR finalizes)

| #  | Check | Expected |
| -- | ----- | -------- |
| V1 | Forward gate on the corpus: every BRD FR → ≥1 SPEC + ≥1 IPLAN (or `deferred:`) | matrix emitted; severity split correct |
| V2 | GATE-06 flags an EARS/BDD element with no downstream SPEC/TDD; distinguishes deferred vs missed | true |
| V3 | Out-of-phase item in an in-phase plan → block | true |
| V4 | Multi-`@brd` per EARS line parses; zero-downstream BRD FR flagged | true |
| V5 | Conformance + corpus green after skill-regen (C-1) | green |

## Review log

### Pass 1 — 2026-06-27 — self-review (design)

- Grounded against `trace_walk.py` (confirmed backward/transitive-only today;
  forward is genuinely new) + `SPEC-00_index.TEMPLATE` (no coverage section
  today) + the orchestration plan's resolved fork-decisions.
- Surfaced an out-of-scope finding (stale `Upstream:` enumerations in index
  templates) → parked as a follow-up TODO, not folded (avoids the PR-1 scope-
  creep pattern).
- Confirmed the binding decision (document-level for SPEC/TDD/IPLAN) keeps the
  gate independent of the ID-exemption (PR-9).

### Pass 2 — pending — independent (fresh-context)

- Required before the PR opens. **Not yet run.** Should pressure-test: is
  forward coverage best in `trace_walk.py` vs a new `sdd_coverage.py`? Does the
  phase tag belong in the registry or a BRD section? Is the 2a/2b/2c/2d split
  the right cut?

**Result:** DRAFT — design grounded (Pass 1); Pass 2 + implementation are the
next focused effort. This is the workstream's largest piece and warrants a
dedicated run.
