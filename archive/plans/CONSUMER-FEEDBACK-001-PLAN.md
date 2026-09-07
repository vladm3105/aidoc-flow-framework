# CONSUMER-FEEDBACK-001 — Orchestration Plan

> Multi-PR workstream draining the three consumer-feedback batches triaged
> into `plans/FRAMEWORK-TODO.md` (commit `3e0d80c5`, branch
> `docs/framework-todo-triage-3logs`, 2026-06-26): **D54** (CC Phase-1 manual
> build), **Engramory**, **BeeLocal** — **22 actionable items**. This is an
> **orchestration plan**: the catalogue, the grouping into child PRs, the
> dependency sequence, the per-cluster done criteria. Each child PR gets its
> own `plans/<NAME>-PLAN.md` with implementation detail (and its own mandatory
> two-cycle gap review) when it begins. No code changes ship in this PR.

| Field          | Value                                                         |
| -------------- | ------------------------------------------------------------- |
| Task           | CONSUMER-FEEDBACK-001                                          |
| Type           | orchestration (documentation; no impl in this PR)             |
| Status         | READY — 2026-06-26T00:00:00Z (converged: 3 independent + 3 self review passes) |
| Depends on     | Triage commit `3e0d80c5`; the Tier-2 feedback pipeline (`framework/governance/FRAMEWORK_FEEDBACK_LOG.md`); `plans/IPLAN-LANG-001-PLAN.md` (pre-existing, feeds **PR-6**) |
| Feeds          | Per-cluster child plans `CFB-PR-*-PLAN.md`                     |
| Version impact | None for this orchestration PR. Cumulative across children: ≥1 framework MINOR (new template fields / spec gates) + plugin/tooling PATCH-to-MINOR. Each child finalizes its own arithmetic. |

## Objective

Sequence the 22 triaged consumer-feedback items into small, themed,
independently-reviewable child PRs — each within the governance ≤3-doc-surface
cap (or explicitly flagged to split) — ordered so the one change that alters
how everyone reads the trace chain (`CFB-PR-1`, trace correctness) lands first
and the high-value capabilities (coverage engine, provisional IDs, reuse
manifest) build on a corrected base. This plan is the index for the child
plans, not the design for them.

## Scope

**In:**

- Triage-to-cluster mapping for all 22 open items across the three batches.
- Dependency sequence + wave grouping + per-cluster done criteria.
- Version-impact floor per cluster (finalized in each child plan).

**Out of scope (deferred — not designed here):**

- Implementation detail of any cluster (lives in the child plan).
- Items already dropped in the triage banners (D54 F10/F11 addressed,
  F03/F09 resolved-by-design; BeeLocal #3/#4 obsolete, #5/#8a addressed).
- Hermes-side breadth beyond `ENG-STALE-DEPTH-DOCS` (tracked in
  `plans/HERMES-BACKLOG.md` H-11).
- IPLAN ↔ iplanic integration (`plans/IPLAN-IPLANIC-DEFERRED.md`).

## Approach / Design

### Triage — all 22 open items → clusters

Source: `plans/FRAMEWORK-TODO.md` (the three dated 2026-06-26 banners;
9 D54, 6 Engramory, 7 BeeLocal = 22 total). `P*` is the triage priority recorded on
each entry. "Q" citations distinguish the two clarification rounds
(*Eng-Qn* = Engramory round, *BL-Qn* = BeeLocal round) to avoid the
duplicate-`Q2` ambiguity.

| Item (TODO id) | Tag | Pri | Cluster | Surface(s) |
|---|---|---|---|---|
| `BL-TAG-CHAIN-GATE-SYNC` | governance | P2 | **PR-1** | `GATE-08_IPLAN.md`, `TRACEABILITY.md` |
| `ENG-FWD-COVERAGE` (+ backward leg #54, matrix #52) | lint | P2 | **PR-2** | `sdd_doc_lint`, `SPEC-00_index` template, `GATE-06` |
| `D54-F13-PHASE-SCOPE-RECONCILIATION` | lint | P2 | **PR-2** | shares coverage engine |
| `D54-F05-BDD-COVERAGE-ROLLUP` | lint | P2 | **PR-2** | shares coverage engine |
| `D54-F07-TAG-SYNTAX-REFERENCE` | docs/lint | P2 | **PR-3** | tag-syntax page, `sdd_doc_lint` |
| `BL-REF-GRANULARITY` | lint | P2 | **PR-3** | `ID_NAMING_STANDARDS.md`, `sdd_doc_lint` |
| `BL-STATUS-SCOPE` | template/lint | P3 | **PR-3** | `ID_NAMING_STANDARDS.md`, `sdd_doc_lint` |
| `D54-F01-PROVISIONAL-IDS` | lint | P1 | **PR-4** | `ID_NAMING_STANDARDS.md`, templates, `sdd_doc_lint` |
| `D54-F02-REUSE-MANIFEST` | template | P1 | **PR-5** | new manifest schema, `trace_walk.py`, conformance |
| `D54-F06-IPLAN-PROJECT-TYPES` | template | P2 | **PR-6** | → `IPLAN-LANG-001-PLAN.md` |
| `BL-BRD-SET-WORDING` | docs | P3 | **PR-7** | `01_BRD/README.md`, `BRD-TEMPLATE.yaml` |
| `ENG-BRD-SKETCH-ROADMAP` | docs | P3 | **PR-7** | `01_BRD/README.md`, `BRD-00_index` template |
| `ENG-PLATFORM-ADR-TIMING` | template | P3 | **PR-7** | `BRD-TEMPLATE.yaml`, `PRD-TEMPLATE.yaml` |
| `BL-SIZE-UNITS` | docs | P3 | **PR-8** | `AUTHORING_STYLE.md` |
| `BL-VENDOR-NAME-SCOPE` | template | P3 | **PR-8** | `BRD-TEMPLATE.yaml` |
| `D54-F12-AGENTIC-ANTIPATTERNS` | template | P3 | **PR-8** | `BRD`/`PRD-TEMPLATE.yaml` antipatterns |
| `BL-READY-SCORE-ADVISORY` | template | P3 | **PR-9** | all layer templates (`_note`) |
| `ENG-SPEC-IPLAN-ID-EXEMPTION-NOTE` | template | P3 | **PR-9** | `SPEC`/`IPLAN-TEMPLATE.yaml` |
| `ENG-IPLAN-REGISTRY-README` | docs | P3 | **PR-10** | `08_IPLAN/README.md` |
| `ENG-STALE-DEPTH-DOCS` | hermes-parity | P2 | **PR-10** | Hermes orchestrator docs + published README (xref H-11) |
| `D54-F08-SKELETON-EMIT` | harness | P3 | **PR-11** | plugin tooling |
| `D54-F04-EARS-NONLATENCY-RUBRIC` | playbook | P3 | **PR-12** | `03_EARS` rubric + auditor playbook |

22 rows; 1:1 with the open TODO entries; no orphan, no double-count (V1).

### Cluster design — 12 child PRs, grouped into 4 waves

Wave order encodes dependency, not just priority. Coupling facts the
naive "PR-1 first, linear" reading misses, made explicit here:

- **PR-1 ↔ PR-2(e):** PR-1's corrected `TRACEABILITY.md` answers the reverse
  lookup ("which BRD is SPEC-07?") with the **manual transitive walk**
  (ADR/BDD/EARS→PRD→BRD) as the immediate answer, and names the *generated*
  matrix as a future convenience that PR-2(e) ships. This forward reference
  is deliberate and **non-blocking** — PR-1 stands alone; it does not require
  the matrix to exist.
- **PR-2 ↔ PR-3:** co-dependent, not one-way. PR-2's element-level coverage
  is only computable once `BL-REF-GRANULARITY` (PR-3) forbids doc-level refs
  in verification contexts; PR-3's granularity rule only *matters* because
  PR-2 computes coverage. Land them **together or back-to-back**, reviewed as
  a pair.
- **PR-3 ↔ PR-7:** both mutate the `status`-enum contract. PR-3
  (`BL-STATUS-SCOPE`) hardens per-context `status` enums + scope-aware
  validation; PR-7 (`ENG-BRD-SKETCH-ROADMAP`) introduces a **new BRD
  `status: Sketch` value**. If PR-3 lands first, PR-7's `Sketch` value must be
  registered in PR-3's enum framework and its trace-inert/lint-deferred
  exemption expressed in the scope-aware validation. Sequence PR-7 **after**
  PR-3, or land the `Sketch` enum registration as part of PR-3.

#### Wave 1 — Foundation (do first)

**PR-1 — Trace correctness** · `BL-TAG-CHAIN-GATE-SYNC` · P2 · doc-only

- Correct the stale `GATE-08-E003` resolution example to `[spec, tdd]` and
  resync the `TRACEABILITY.md` cumulative-tag diagram to immediate-upstream;
  state the transitive PRD/BRD path **explicitly as the reverse-lookup
  answer** (the generated matrix from PR-2(e) is named as a later
  convenience, not a prerequisite). **Do NOT re-add cumulative tags**
  (BL-Q1).
- Version floor: framework PATCH (human-readable doc correction; the
  machine-read contract in `LAYER_REGISTRY.yaml`/templates is already right).
- Done: both docs match `LAYER_REGISTRY.yaml` `required_tags` + live templates;
  conformance green; entry → Closed.

#### Wave 2 — High-value capabilities (P1/P2)

**PR-2 — Coverage engine** · `ENG-FWD-COVERAGE` + `D54-F13` + `D54-F05` · P2
· depends on PR-1 · co-dependent with PR-3

- One `@`-tag-graph engine serving: (a) forward gate (every BRD FR reaches
  at least one SPEC and at least one IPLAN; severity split per **Eng-Q2** — deferred=warning, in-scope
  missing-IPLAN=block, no-SPEC=block); (b) backward leg (`SPEC-00` `coverage`
  section + `deferred:` + GATE-06 check, BeeLocal #54); (c) phase tag +
  out-of-phase-leak=block, with the **scope ledger as a designated section of
  the existing BRD acceptance/index, NOT a new artifact** (D54-F13); (d) BDD
  doc-set EARS roll-up (D54-F05); (e) emitted BRD→…→IPLAN matrix (BeeLocal
  #52). Document-level binding for SPEC/TDD/IPLAN; multi-`@brd:` per EARS line
  pipe-delimited (xref `D54-F07`/PR-3).
- Version floor: framework MINOR (new template `coverage` section + GATE-06 +
  phase tag) + tooling. **>3 surfaces — child plan MUST split** into sub-PRs
  sharing the engine (forward / backward+roll-up / phase) if it exceeds cap.

**PR-3 — Lint hardening** · `D54-F07` + `BL-REF-GRANULARITY` + `BL-STATUS-SCOPE` · P2/P3
· co-dependent with PR-2 (land together/back-to-back)

- `taglint` in `sdd_doc_lint`: per-layer tag-syntax rules + a single
  tag-syntax reference page (`D54-F07`); the oracle-layer ⇒ element-level
  rule, **blocking at GATE-06** (`BL-REF-GRANULARITY`, **BL-Q2** field list);
  per-context `status` enums + scope-aware validation, **enum NOT rename**
  (`BL-STATUS-SCOPE`, **BL-Q3**). All land in `ID_NAMING_STANDARDS.md` +
  `sdd_doc_lint` + the new tag-syntax page.
- Version floor: framework MINOR (new standards section) + tooling.
- **3 surfaces (`ID_NAMING_STANDARDS.md`, `sdd_doc_lint`, tag-syntax page) —
  at the cap; child plan splits `BL-STATUS-SCOPE` out if a 4th surface appears.**
- *Doc-boundary with PR-1:* PR-1 owns the `TRACEABILITY.md` chain diagram +
  reverse-lookup prose; PR-3's **new tag-syntax page** owns per-layer
  punctuation/cardinality. The child plan must draw that line so the two
  trace-docs don't duplicate or contradict.

**PR-4 — Provisional IDs** · `D54-F01-PROVISIONAL-IDS` · P1 · independent

- `metadata.id_standard.state: provisional|canonical`; section-ordinal hex
  placeholder (crutch) + regex-valid `0000` literal; fix `sdd_doc_lint`
  lowercase-`xxxx` blind spot; lift the SHA-256 algorithm from
  `EARS-TEMPLATE.yaml:94-100` into `ID_NAMING_STANDARDS.md` as normative +
  a placeholders-until-canonical statement; `rehash` as an `sdd_doc_lint`
  subcommand (reference-aware), NOT a new CLI.
- *Independence caveat:* no hard sequencing dependency, but the child plan
  must resolve one interaction with PR-2/PR-3 — whether a **provisional-state
  element counts as "covered"** by PR-2's gate, and whether PR-3's taglint
  accepts the ordinal-hex/`0000` placeholder form. Coordinate the answer; do
  not assume full isolation.
- Version floor: framework MINOR + tooling.

**PR-5 — Reuse manifest** · `D54-F02-REUSE-MANIFEST` · P1 · **depends on PR-2**

- Element-granular reuse manifest (`authored | referenced`); whole-layer
  mid-chain reuse = "all elements referenced"; `satisfied_by_reference`
  passes coverage but records "reuse, not re-audited" (no free ≥90); target
  MUST be in-repo/pinned (path+commit); live URLs only as `@discoverability`
  hints. `trace_walk.py` + conformance recognize referenced as covered.
- **Not independent:** PR-5 and PR-2 both extend `trace_walk.py` and both turn
  on the *definition of "covered"* PR-2 establishes. Sequence PR-5 **after**
  PR-2 so it hooks into the existing coverage semantics rather than
  re-defining them (see R2). Own plan; the make-or-break brownfield feature.
- Version floor: framework MINOR.

#### Wave 3 — Docs / template clarifications (P2/P3; mostly parallelizable)

> Wave label is **P2/P3** — PR-6 (D54-F06) and PR-10's `ENG-STALE-DEPTH-DOCS`
> are P2; the rest P3.

**PR-6 — IPLAN project-types** · `D54-F06` · P2 · → `IPLAN-LANG-001-PLAN.md`

- Revive + merge the pre-existing `plans/IPLAN-LANG-001-PLAN.md`
  (language-neutral template inheriting `language:`/`dependencies:` from
  SPEC); extend with non-code deliverable scaffolds (plugin/infra/docs) only
  if SPEC-inheritance is insufficient. Cross-references the existing plan —
  do not duplicate.

**PR-7 — BRD lifecycle + authoring pattern** · `BL-BRD-SET-WORDING` +
`ENG-BRD-SKETCH-ROADMAP` + `ENG-PLATFORM-ADR-TIMING` · P3

- Reword "each BRD = one cycle" → "each BRD *set* = one cycle" + parent/child
  tree example; document the project-init step (cycle roadmap folded into
  `BRD-00_index` Planned-BRDs table, `status: Sketch` marker, trace-inert,
  recommend-not-mandate, lint deferred); reword platform-BRD "ADRs before
  PRD" to decision-provenance + the PRD-template manifestation.
- **>3 surfaces** (`01_BRD/README.md`, `BRD-TEMPLATE.yaml`, `BRD-00_index`
  template, `PRD-TEMPLATE.yaml`, and the top-level project-init README note)
  — **child plan MUST split**, e.g. **7a** = BRD-set wording + sketch/roadmap
  (BRD layer only); **7b** = platform-ADR-timing (BRD + PRD templates). The
  7a/7b boundary is illustrative — the child plan finalizes it (note
  `BRD-TEMPLATE.yaml` is touched by both, and the top-level project-init
  README note must be assigned to one sub-PR) so each stays ≤3 surfaces.
- Version floor: framework MINOR — `status: Sketch` is a new BRD-template
  enum value (schema change), not pure prose.

**PR-8 — Template ambiguities** · `BL-SIZE-UNITS` + `BL-VENDOR-NAME-SCOPE` +
`D54-F12-AGENTIC-ANTIPATTERNS` · P3

- Clarify words-vs-tokens relationship; clarify vendor names allowed in
  `recommended_selection` but not titles/business_driver; add agentic
  business-vs-technical examples to BRD/PRD antipatterns. 3 surfaces
  (`AUTHORING_STYLE.md`, `BRD-TEMPLATE.yaml`, `PRD-TEMPLATE.yaml`) — at cap.
- Version floor: framework PATCH/MINOR (prose + antipattern examples;
  no new field) — child finalizes.

**PR-9 — Advisory score + ID-exemption notes** · `BL-READY-SCORE-ADVISORY` +
`ENG-SPEC-IPLAN-ID-EXEMPTION-NOTE` · P3

- Mark `*_ready_score` advisory in every template + reword `target_score`
  (no rubric tool — **BL-Q4**); add `_note` cross-referencing the element-ID
  exemption in SPEC §5/§3 + IPLAN §4/§2 (keep the exemption — **Eng-Q7**).
- **Surface-cap reality:** `BL-READY-SCORE-ADVISORY` is a uniform mechanical
  `_note` across **all 8 layer templates** — by file-count it busts the ≤3
  cap. **Child plan MUST split:** **9a** = the ready-score `_note` sweep
  (one mechanical pattern, reviewable as a single logical change even though
  it touches 8 files — call this out for the reviewer); **9b** =
  `ENG-SPEC-IPLAN-ID-EXEMPTION-NOTE` (SPEC + IPLAN templates = 2 surfaces).
- Version floor: framework PATCH (prose `_note` only; no field/enum change).

**PR-10 — Docs hygiene** · `ENG-IPLAN-REGISTRY-README` + `ENG-STALE-DEPTH-DOCS` · P3/P2

- One-line `08_IPLAN/README.md` note on registry-vs-document schemas (lint
  already special-cases INDEX); reconcile the published GitHub README + two
  Hermes orchestrator docs to the single-path model. **Child plan MUST split
  if > 3 surfaces** — the Hermes leg may land under `HERMES-BACKLOG` H-11
  instead of here.
- Version floor: docs-only (framework PATCH; Hermes leg per its own stream).

#### Wave 4 — Standalone follow-on (P3)

**PR-11 — Skeleton emit** · `D54-F08` · P3 — `--skeleton` (strip
`_guidance`/`_example`/`_antipatterns`) in plugin tooling, not a new CLI.

**PR-12 — EARS non-latency rubric** · `D54-F04` · P3 — broaden the EARS-Ready
scoring criteria to count a quantified cycle/iteration/event-window bound as
"quantified" (`03_EARS` template + auditor playbook). Syntax already flexes.

### Dependency graph (text)

```
PR-1 (trace correctness)
   └─► PR-2 (coverage engine) ⇄ PR-3 (lint hardening; REF-GRANULARITY co-dependent)
          └─► PR-5 (reuse manifest; shares trace_walk.py + "covered" semantics)
PR-4 (provisional IDs)  ── independent
PR-6 .. PR-12           ── parallelizable docs/standalone (PR-6 & PR-10 are P2;
                           PR-7's sketch note conceptually references PR-2's gate
                           but is trace-inert + lint-deferred, so non-blocking)
```

## Implementation sequence

1. **Land PR-1 first** — every downstream reader depends on the corrected chain.
2. **PR-2 and PR-3 as a pair** (together or back-to-back) — the coverage
   engine and the granularity lint that makes element-level coverage
   computable are co-dependent.
3. **PR-5 after PR-2** — the reuse manifest hooks into PR-2's `trace_walk.py`
   coverage semantics; landing it earlier would force it to re-define
   "covered."
4. **PR-4 in parallel with Wave 2** — provisional IDs are independent.
5. **Wave 3 PRs (PR-6..PR-10)** — parallelizable docs/template clarifications,
   each its own PR within (or explicitly split to) the ≤3-surface cap.
6. **Wave 4 (PR-11, PR-12)** — standalone follow-on, lowest priority.
7. Each child PR: write `plans/CFB-PR-N-<slug>-PLAN.md`, complete its own
   two-cycle gap review, implement, verify, land, then move the TODO entries
   to **Closed** with the merge SHA (per `FRAMEWORK-TODO.md` rules).

## Cross-cutting child-PR contract

Beyond its own scope, **every** child PR that changes a lint rule, `@`-tag
semantics, the registry, a gate, a playbook, or a template inherits these
done-criteria (named once here so the cluster blocks stay short). Each child
plan must restate the ones that apply to it.

- **C-1 Corpus re-lint + regen-via-skills.** Per CLAUDE.md (Corpus
  cross-check + "never hand-edit example artifacts"): a child changing
  lint/`@`-tag/registry/template content (PR-2, PR-3, PR-4, PR-7, PR-8, PR-9)
  MUST run `python3 -m sdd_doc_lint examples/url-shortener/docs/` in one
  review pass. New **blocking** gates (PR-2 forward-coverage + phase-leak;
  PR-3 granularity) will fire fresh findings on the current corpus — the
  corpus must be **regenerated via the framework skills (`doc-<layer>-audit`/
  `-fixer`/cascade), never hand-edited**, and the child plan needs a
  migration note (e.g. a `--skip-lint-smoke` / env-bypass) for the transient
  pre-regen findings, mirroring the NECESSARY-UPSTREAM-001 / TRACE-RES-FIXUP
  pattern.
- **C-2 Platform-parity sync.** A child editing `tools/sdd_doc_lint/` (PR-2,
  PR-3, PR-4) MUST run `tools/sync-plugin-framework.sh` to propagate the
  canonical lint into the vendored platform copies; framework
  template/registry changes reach the plugin + Hermes by the same D-0013
  single-source rule (platforms consume `framework/layers/`, never copy). A
  lint change that skips the sync drifts the platforms and breaks conformance.
- **C-3 Conformance coverage.** Every new or changed gate ships
  `tests/conformance/` coverage in the same PR (PR-1 GATE-08 correction;
  PR-2 GATE-06 + phase-leak; PR-3 taglint/granularity; PR-4 provisional-ID
  lint). "Conformance is the runnable contract" — green is a done-criterion,
  and a new gate without a conformance test is incomplete.
- **C-4 Version-pin parity.** A child that bumps `framework/VERSION`
  (the framework-MINOR ones) MUST keep **both** `platforms/<name>/FRAMEWORK_SPEC_VERSION`
  pins equal to it (conformance checks this) and let `sync-version-refs.sh`
  fan the string into the docs. R3 covers collision; this names the parity.
- **C-5 Child branch basis + revertibility.** Each child branches from
  `origin/main` (NOT from this orchestration branch), is independently
  testable and revertible, and its `CFB-PR-N` plan completes its own two-cycle
  gap review before opening. PR-2 and PR-5 imply a multi-hour **live cascade
  regen** — budget for it in those child plans.

**Per-cluster `Done:`** = the cluster's own done line (where given) **+** the
applicable C-1…C-4 above **+** the TODO entry moved to **Closed** with the
merge SHA.

**Workstream close-out.** CONSUMER-FEEDBACK-001 is complete when all **22**
TODO entries are Closed-with-SHA and all 12 child PRs (PR-1…PR-12, with any
7a/7b/9a/9b splits) have landed; at that point this orchestration plan moves
to a done state and the three TODO banners can be archived to the Closed
section.

## Verification

| #  | Check (observable) | Expected | Maps to |
| -- | ------------------ | -------- | ------- |
| V1 | Every open item in the three 2026-06-26 banners appears exactly once in the triage table | **22/22** (9 D54 + 6 ENG + 7 BL), no orphans, no double-count | Objective |
| V2 | Every cluster is either ≤3 doc surfaces OR carries an explicit "child plan MUST split" flag | true for all PRs (PR-2/7/9/10 flagged) | Scope |
| V3 | Dependency claims hold: PR-1 stands alone (matrix forward-ref non-blocking); PR-2⇄PR-3 co-dependent; PR-5 depends on PR-2's coverage semantics; PR-4 independent | consistent (DAG ⇄/► match the sequence + R-rows) | Approach |
| V4 | Each cluster's one-liner matches the resolved fork-decision in `FRAMEWORK-TODO.md` (incl. disambiguated Eng-Q/BL-Q citations) | no contradiction | Approach |
| V5 | `python3 -m sdd_doc_lint examples/url-shortener/docs/` still green (this PR changes no spec) | zero unexpected findings | Out-of-scope guard |
| V6 | Every gate/lint/template-changing child (PR-2/3/4/7/8/9) inherits the applicable C-1…C-4 cross-cutting criteria | named in the Cross-cutting contract | Approach |

## Docs to update (this orchestration PR)

- [x] `plans/FRAMEWORK-TODO.md` — carries the 22 triaged entries (commit `3e0d80c5`).
- [ ] `plans/HANDOFF.md` — add the CONSUMER-FEEDBACK-001 workstream + next step (land PR-1).
- [ ] `plans/DECISIONS.md` — record the non-obvious call: `BL-TAG-CHAIN-GATE-SYNC` fixes the docs in the *opposite* direction the feedback author proposed (keep necessary-upstream; correct the stale gate/diagram).
- [ ] `CHANGELOG.md` / `ROADMAP.md` — not in this PR (no shipped behavior); each child PR updates them.

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Coverage engine (PR-2) over-scopes — forward + backward + phase + roll-up in one PR | med | V2 + the explicit "child plan MUST split" flag on PR-2. |
| R2 | PR-5 (reuse manifest) and PR-2 collide on `trace_walk.py` + the meaning of "covered" | **high** | Sequence PR-5 after PR-2 (impl-sequence step 3); PR-5's child plan extends PR-2's engine, never re-defines coverage. |
| R3 | Multiple framework-MINOR child PRs collide on `VERSION` / docs sync | low | Sequential landing; `sync-version-refs.sh` handles version-string fanout. |
| R4 | A child PR's fork-decision drifts from the triage record | low | V4 + each child re-reads its `FRAMEWORK-TODO.md` entry as the contract. |
| R5 | A surface-cap-flagged PR (2/7/9/10) is implemented without splitting | med | V2 makes the split a done-criterion; the child plan's own review re-checks Rule 1. |
| R6 | A lint/template child lands without corpus re-lint+regen → ships orphan findings into the cascade (the NECESSARY-UPSTREAM-001 trap) | **high** | C-1 makes corpus re-lint + regen-via-skills a per-child done-criterion; V6. |
| R7 | A `tools/sdd_doc_lint/` change skips `sync-plugin-framework.sh` → vendored platform copies drift, conformance breaks | med | C-2 names the parity sync; C-3 requires conformance coverage in the same PR. |
| R8 | A framework-MINOR child bumps `framework/VERSION` but not both `FRAMEWORK_SPEC_VERSION` pins | low | C-4 makes pin parity a done-criterion (conformance checks it). |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1 | 22 items triaged across three dated banners (9+6+7) | banners | `plans/FRAMEWORK-TODO.md` @ `3e0d80c5` (banners at lines ~126 / ~269 / ~423) |
| 2 | Stale cumulative-tag docs contradict the live contract (PR-1) | `GATE-08-E003` | `framework/governance/chg/gates/GATE-08_IPLAN.md` (resolution §) vs `framework/registry/LAYER_REGISTRY.yaml` `required_tags` |
| 3 | `trace_walk.py` is backward-only today (PR-2 adds forward; PR-5 also edits it) | `trace_walk.py` | `tools/trace_walk.py` (docstring) |
| 4 | IPLAN-LANG-001 plan exists, feeds PR-6 | plan file | `plans/IPLAN-LANG-001-PLAN.md` |
| 5 | Hermes stale depth tables exist (PR-10) | depth table | `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/root-docs/README.md` |
| 6 | `ENG-STALE-DEPTH-DOCS` Hermes leg already parked | H-11 | `plans/HERMES-BACKLOG.md` |

## Review log

> Per CLAUDE.md: ≥2 passes before the plan PR opens; ≥1 independent
> fresh-context. Each pass re-reads the whole plan, lists findings, folds
> fixes back. Cycle N+1 re-validates N's edits. Continue until a pass
> surfaces nothing.

### Pass 1 — 2026-06-26 — self-review

- *Surface-cap creep:* PR-2 bundles four capabilities. → Added R1 + "may
  split" note.
- *Dependency under-stated:* `BL-REF-GRANULARITY` (PR-3) feeds PR-2's
  element-level coverage. → Added ordering note + V3.
- *Direction-reversal must not get lost:* the `BL-TAG-CHAIN-GATE-SYNC`
  opposite-direction call. → Added to `DECISIONS.md` docs-to-update + V4.
- *Completeness:* re-counted — **miscounted as 21** (see Pass 2 F-A).

### Pass 2 — 2026-06-26 — independent (fresh-context, `Plan` agent)

Six blocking + several minor findings; all folded:

- **F-A (count):** real total is **22, not 21** (9+6+7); five "21" mentions +
  V1 + Claim 1 were wrong. → Corrected to 22 throughout; V1 now "22/22".
- **F-B (PR-1↔PR-2(e) inverted dependency):** PR-1's reverse-lookup pointed at
  a matrix only PR-2 ships. → Reworded PR-1 so the **manual transitive walk**
  is the immediate answer and the matrix is a named-but-non-blocking forward
  reference; documented the coupling in the cluster preamble.
- **F-C (PR-2↔PR-3 arrow contradiction):** DAG said one-way, V3 said the
  other. → Represented as **co-dependent (⇄)**; "land together/back-to-back"
  in the preamble, DAG, sequence, and V3.
- **F-D (PR-5 not independent):** PR-5 + PR-2 share `trace_walk.py` + the
  "covered" definition. → PR-5 now **depends on PR-2**; added R2 (high) +
  sequence step 3 + DAG edge.
- **F-E (PR-7 cap breach mislabeled "3 surfaces"):** actually 4–5. → Relabeled
  ">3 surfaces — MUST split into 7a/7b"; added the `status: Sketch` MINOR
  version floor.
- **F-F (PR-9 all-templates cap breach, unflagged):** 8 templates. → Added the
  split into 9a (mechanical `_note` sweep) / 9b (SPEC+IPLAN exemption note)
  with the reviewer call-out.
- **F-G (IPLAN-LANG-001 metadata says PR-8, table says PR-6):** → Fixed
  metadata "feeds **PR-6**".
- *Minors folded:* D54-F13 scope-ledger-in-BRD detail restored to PR-2(c);
  `Eng-Q2`/`BL-Q2` citation disambiguation across the plan; Wave-3 label
  corrected to **P2/P3**; PR-7 version floor + PR-3 cap note added.

### Pass 3 — 2026-06-26 — self re-validation (of Pass-2 edits)

- Re-counted the triage table after edits: 22 rows, 1:1 with the banners. ✓
- Re-read the DAG, implementation sequence, and V3 together: PR-1 standalone,
  PR-2⇄PR-3, PR-5→PR-2, PR-4 independent — now consistent across all three. ✓
- Every cap-breaching cluster (PR-2/7/9/10) carries an explicit split flag;
  PR-3/PR-8 noted at-cap. V2 satisfied. ✓
- No new load-bearing findings.

### Pass 4 — 2026-06-26 — independent (fresh-context, `Plan` agent) — confirming

- Re-counted the triage table independently: 22 rows (9+6+7); every prose /
  metadata / V1 / Claim-1 mention agrees. ✓
- All six Pass-2 blocking findings verified RESOLVED with no residue; the
  fixes introduced no new contradictions (DAG ↔ sequence ↔ V3 consistent;
  version floors consistent; Q-citations disambiguated). ✓
- Four [MINOR] polish items surfaced and folded: `BL-Q1` citation-format
  consistency; PR-10 "MUST split if > 3" wording; PR-7 7a/7b illustrative-
  boundary note; the #52/#54 sub-leg assumption confirmed correct (they are
  folded sub-legs of `ENG-FWD-COVERAGE`, not standalone TODO entries — the 7
  BeeLocal count is the 7 standalone entries).
- **Verdict: READY.**

### Pass 5 — 2026-06-26 — independent (fresh-context, `Plan` agent) — gap scan

A deliberately different mandate from Pass 2/4: hunt for **omitted
cross-cutting scope**, not internal consistency. Four blocking + six minor
gaps; all folded:

- **G-A (corpus regen/cross-check):** the plan named the example corpus only
  as the orchestration PR's own out-of-scope guard (V5), never as a per-child
  done-criterion — yet PR-2/3/4/7/8/9 change exactly the lint/`@`-tag/registry/
  template content the CLAUDE.md Corpus rule governs, and the new blocking
  gates will fire fresh findings requiring **regen-via-skills**. → Added
  **C-1** + R6 + V6.
- **G-B (platform-parity sync):** silent on `sync-plugin-framework.sh`
  propagation of `tools/sdd_doc_lint/` changes to vendored platform copies.
  → Added **C-2** + R7.
- **G-C (conformance tests for new gates):** required conformance only for
  PR-5; the new gates in PR-1/2/3/4 had none. → Added **C-3**.
- **G-D (`FRAMEWORK_SPEC_VERSION` pin parity):** R3 covered VERSION collision
  but not the two-platform spec-pin parity. → Added **C-4** + R8.
- **G-F1 (PR-3⇄PR-7 status-enum collision):** PR-7's new `status: Sketch`
  value collides with PR-3's status-enum hardening. → Added the PR-3⇄PR-7
  coupling bullet + "sequence PR-7 after PR-3."
- *Minors folded:* per-cluster `Done:` formula + workstream close-out
  (close-out paragraph); child branch-basis from `origin/main` + cascade-cost
  budget (**C-5**); PR-4 provisional-ID-vs-coverage independence caveat
  (G-F3); PR-1↔PR-3 trace-doc boundary note (G-F4).

### Pass 6 — 2026-06-26 — self re-validation (of Pass-5 edits)

- The C-1…C-5 contract is named once and referenced by V6 / R6-R8 / the
  per-cluster `Done:` formula — no per-PR duplication. ✓
- New couplings (PR-3⇄PR-7, PR-4 caveat, PR-1↔PR-3 doc boundary) are
  consistent with the DAG's existing edges; none contradict the sequence. ✓
- No new load-bearing findings.

**Result:** READY. Three independent fresh-context passes (Pass 2 internal,
Pass 4 confirming, Pass 5 gap-scan) plus three self passes; the gap scan's
four blocking omissions are folded into a single Cross-cutting child-PR
contract (C-1…C-5). Plan PR may open.
