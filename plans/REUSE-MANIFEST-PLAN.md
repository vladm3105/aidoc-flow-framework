# REUSE-MANIFEST-001 Plan — first-class reuse of an existing artifact (satisfied-by-reference)

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | REUSE-MANIFEST-001 (D54-F02, CONSUMER-FEEDBACK-001 PR-5)     |
| Type           | feature                                                      |
| Status         | IMPLEMENTED — 2026-06-29 (spec 0.32.0; 314 conformance+unit green; corpus baseline unchanged). Impl note: REUSE01/REUSE02 are emitted by a dedicated corpus-level `_check_reuse` (one per referenced doc, ALL layers — not just BRD/EARS/BDD), wired into `lint_path`; COV01/COV02 only *skip* referenced host docs. This is cleaner than emitting from each gate (no double-emit; a referenced PRD/ADR/SPEC is also surfaced) and faithful to the "one REUSE01 per referenced doc" intent. |
| Depends on     | ELEMENT-COVERAGE-001 (#209, element-level COV01/COV02 — the "covered" definition this hooks into); the stubbed `CoveredState.SATISFIED_BY_REFERENCE` |
| Feeds          | brownfield adoption (the make-or-break capability per the D54 triage) |
| Version impact | framework MINOR (new reuse convention + coverage/trace recognition) |

## Objective

Let a project **reuse an existing upstream artifact mid-chain** (e.g. build EARS
on top of an already-authored PRD) instead of re-authoring all 8 layers
greenfield. Today `active_layers` can only *disable* a layer (BDD/ADR), not
*satisfy it by reference*, and the trace/coverage engine treats a referenced
artifact as **orphan/missing**. This adds a **satisfied-by-reference** state: a
referenced element/layer passes coverage + traceability ("present + linked") but
is recorded as **reuse, not re-audited** — it does NOT earn an authored-layer
readiness score for free. The reference target must be **in-repo + pinned**
(deterministically verifiable); live external URLs are `@discoverability` hints
only, never the trace target.

## Scope

**In:**

- **Whole-layer reuse declaration** (the P1 brownfield need) — a frontmatter
  `reuse:` block: `state: referenced` + `target: <doc_id-or-path>@<commit>`.
  Marks every element the doc declares as `referenced`. (Element-granular
  per-element override is a documented extension, not built here — see Out of
  scope.)
- **`CoveredState.SATISFIED_BY_REFERENCE` logic** — wire the stubbed enum member:
  a referenced element classifies as `SATISFIED_BY_REFERENCE`, a **non-blocking**
  coverage state (like `DEFERRED`/`REALIZED_BY`).
- **Coverage-gate recognition** — `COV01`/`COV02` treat a referenced element as
  satisfied (it need not reach downstream realization — it IS reused as-is) and
  emit a **`REUSE01` advisory** recording "satisfied by reference (reuse, not
  re-audited)". (Trace resolution needs **no change** — under the full-prefix
  rule below, both directions resolve against in-repo copies.)
- **Full-prefix rule** — a referenced doc's upstream lineage must also be present
  in-repo and `referenced`, so its outbound `@`-tags resolve (Pass-2 F-1); reuse
  is the *chain up to the boundary*, not a dangling doc.
- **Target validation** — the `target` must be an **in-repo path or doc_id with
  a commit pin** (`@<7-40 hex>`); the linter verifies the path/doc resolves and
  the pin is well-formed. A live URL as a `reuse.target` is a finding (`REUSE02`)
  — URLs belong in `@discoverability` only.
- **Governance + template** — `framework/governance/` reuse contract (the
  satisfied-by-reference semantics + the "no free ≥90 readiness" rule for the
  authoring/audit skills) + a `reuse:` block in the layer index template(s).

**Out of scope (deferred):**

- **Element-granular per-element `authored|referenced` marking** — the
  whole-layer frontmatter form covers the P1 mid-chain-reuse need; per-element
  mixing is a documented future extension (REUSE-MANIFEST-002 if it surfaces).
- **Full commit-existence verification** — the linter checks pin *format* +
  target *resolves in-repo*; verifying the commit hash exists in git history is
  deferred (deterministic-format check is the floor).
- **The audit-skill readiness change** — the framework contract records "reuse,
  not re-audited"; making `doc-<layer>-audit` skills *withhold* a ≥90 score for a
  referenced layer is a plugin-skill follow-on (documented as a contract here,
  enforced in the skills later).
- Corpus example of reuse — the corpus is regenerated wholesale
  ([[project-examples-regenerated-wholesale]]); a reuse fixture lands then.

## Approach / Design

### The reuse declaration (whole-layer, frontmatter)

A reused layer's doc carries, in frontmatter (parallel to `id_state`):

```yaml
reuse:
  state: referenced
  target: PRD-01@a1b2c3d        # in-repo doc_id or path, pinned to a commit
  rationale: "reusing the platform PRD from the parent repo"
```

`reuse.state` defaults to `authored` (absent ⇒ authored; back-compatible). When
`referenced`, every element the doc declares is classified
`SATISFIED_BY_REFERENCE`. The linter reads it via `_extract_frontmatter` (the
same path `id_state` uses).

### What a referenced doc contains + the full-prefix rule (Pass-1 F1 / Pass-2 F-1)

A `reuse: {state: referenced}` doc **physically carries the reused elements**
(copied from the pinned source), each implicitly `referenced` via the whole-doc
frontmatter flag — it is NOT a bare pointer. So downstream `@<layer>:` citations
to those element IDs **resolve normally** (the IDs are present in-repo);
`reuse.target` is the **pinned provenance source** the copies came from (for
verification / re-sync), not a redirection the linter must dereference.

**Full-prefix rule (Pass-2 F-1):** a reused doc also carries its OWN outbound
upstream `@<layer>:` lineage tags (a reused PRD has `@brd:`). For those to
resolve, **the referenced doc's entire upstream prefix must also be present
in-repo and marked `referenced`** — you reuse the *chain up to the boundary*,
not a single dangling doc. Concretely: to build EARS on a reused PRD, copy in
BOTH the BRD and PRD, each `reuse: referenced`. Then every upstream tag resolves
against an in-repo copy and `_check_trace_resolution` is satisfied with **no
change** — a referenced doc whose upstream tag points at an **absent** doc is a
legitimate finding (incomplete reuse), not something to exempt. This is why
**no `trace_walk.py` / TRACE-RES-001 change is needed** (Pass-2 F-2): the
orphan/missing condition only arises under a bare-pointer model, which this
design rejects.

### Classification + coverage (gate-level, not `covered_state_of`) (Pass-1 F2)

`reuse` is **doc-level frontmatter**, but `covered_state_of(fr)` receives only an
`FRElement` (band/realized_by/elem_id) — it has **no access to the host doc's
frontmatter**. So the reuse check happens **at the gate**, keyed on the host
doc, NOT inside `covered_state_of`:

- Build a `doc_id → reuse_state` map from the corpus frontmatter (alongside the
  edge graph). `SATISFIED_BY_REFERENCE` is the *reported* state; the gates derive
  it from the host doc's `reuse.state`, not from `covered_state_of`.
- **COV01:** before the per-FR reach check, if the FR's **host BRD** is
  `referenced`, skip its FRs (satisfied by reference) and emit one `REUSE01`
  advisory for that doc.
- **COV02:** when enumerating `element_host` elements, skip any element whose
  **host doc** is `referenced`; emit one `REUSE01` per referenced host doc
  (deduped, not per element).
- This mirrors the placement of the existing `DEFERRED`/`REALIZED_BY` escapes
  (escape decision before the reach check) but sources the signal from the doc,
  not the element.
- **TRACE-RES-001 (no change):** both directions resolve in-repo — downstream
  citations against the referenced doc's carried elements, and the referenced
  doc's own upstream tags against the in-repo prefix copies (full-prefix rule).
  An upstream tag to an absent doc stays a finding (incomplete reuse).

### Target = in-repo + pinned (the verifiability rule)

`reuse.target` MUST be `(<doc_id> | <relative-path>)@<commit>`:

- in-repo doc_id (`PRD-01`) or path (`../parent/docs/02_PRD/PRD-01.md`) — the
  linter verifies it resolves (the doc exists in the corpus / on disk);
- `@<commit>` pin (7–40 lowercase hex) — format-validated (existence-in-git
  deferred);
- a `reuse.target` that is an `http(s)://` URL → **`REUSE02`** error: live URLs
  are non-authoritative `@discoverability` hints, never the trace target.

### Readiness contract (no free ≥90)

The reuse manifest **records** "reuse, not re-audited": a referenced layer is
*present + linked* but was not authored/audited in this repo, so the
authoring/audit flow MUST NOT grant it an authored-quality (≥90) readiness
score. This plan ships the contract as governance text (the deterministic lint
recognizes reuse as covered); enforcing the score-withholding in the
`doc-<layer>-audit` skills is the documented follow-on.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `tools/sdd_doc_lint/__init__.py` | read `reuse` frontmatter; `doc_id→reuse_state` map; COV01/COV02 escape (by host doc) + `REUSE01` advisory; `REUSE02` target-must-be-in-repo-pinned. (No TRACE-RES-001 change — full-prefix reuse resolves in-repo.) |
| `platforms/{claude-code-plugin,hermes}/sdd_doc_lint/__init__.py` | re-vendored byte-identical |
| `framework/governance/TRACEABILITY.md` (or a new `REUSE.md`) | satisfied-by-reference semantics + the full-prefix rule + the no-free-≥90 readiness contract |
| layer index template(s) (`*-00_index.TEMPLATE.md`) | optional `reuse:` frontmatter block + guidance |
| `tests/unit/test_reuse_manifest.py` (new), `tests/conformance/` | classification + gate-escape + target-validation + full-prefix-resolution cases |
| `framework/VERSION` + FSV pins + fanout | MINOR bump via `bump_version.py` |
| `CHANGELOG.md`, `plans/HANDOFF.md`, `plans/FRAMEWORK-TODO.md`, `plans/DECISIONS.md` | docs of record |

## Implementation sequence

### Task 1: reuse frontmatter read + `doc_id → reuse_state` map

- Read `reuse.state`/`reuse.target` via `_extract_frontmatter`; build a
  corpus-wide `doc_id → reuse_state` map (the gates consult it by host doc — NOT
  via `covered_state_of`, which has no doc context). `SATISFIED_BY_REFERENCE` is
  the reported state.
- **Test-first — [CODE]:** a `reuse: {state: referenced}` doc → map entry
  `referenced`; absent/`authored` → `authored` (default).

### Task 2: coverage-gate escape + `REUSE01`

- COV01/COV02 short-circuit a `SATISFIED_BY_REFERENCE` element (escape, before
  the reach check); emit one `REUSE01` advisory per referenced doc.
- **Test-first — [CODE]:** a referenced BRD FR not reaching SPEC/IPLAN is NOT a
  COV01 error (it's `REUSE01` advisory); a referenced EARS/BDD doc not reaching
  SPEC/TDD is NOT a COV02 finding.

### Task 3: target validation (`REUSE02`)

- Validate `reuse.target` is in-repo + commit-pinned; flag a URL target
  (`REUSE02`). Confirm (test, no code) that under the full-prefix rule both
  directions of `TRACE-RES-001` resolve in-repo with no change.
- **Test-first — [CODE]:** unresolvable/unpinned/URL target → `REUSE02`; a valid
  `PRD-01@<hex>` target → no finding; a full-prefix reuse (BRD+PRD both
  referenced) → the PRD's `@brd:` upstream tag resolves (no TRACE-RES-001);
  a referenced doc whose upstream tag points at an absent doc → TRACE-RES-001
  (incomplete reuse, correctly flagged).

### Task 4: governance + template + MINOR bump + docs

- Reuse contract doc (satisfied-by-reference + full-prefix rule + no-free-≥90
  rule); `reuse:` template block; `bump_version.py <MINOR>`; re-vendor
  byte-identical; CHANGELOG / HANDOFF / FRAMEWORK-TODO (close D54-F02) /
  DECISIONS.

## Verification

| #  | Check (command) | Expected | Maps to |
| -- | --------------- | -------- | ------- |
| V1 | `pytest tests/unit/test_reuse_manifest.py -q` | classification/gate/target/trace cases green | Tasks 1-3 |
| V2 | `pytest tests/conformance tests/unit -q` | all green | regression |
| V3 | a `reuse: {state: referenced}` BRD → its FRs are NOT COV01 errors; one `REUSE01` | per case | Task 2 |
| V4 | a referenced EARS/BDD doc → NOT a COV02 finding; one `REUSE01` | per case | Task 2 |
| V5 | `reuse.target` = URL → `REUSE02`; `PRD-01@<hex>` → resolves, no finding | per case | Task 3 |
| V6 | byte-identity canonical ↔ both vendored copies; FSV pins match | identical / match | D-0022 / bump |
| V7 | corpus baseline unchanged (no doc declares `reuse:` yet) | unchanged | regression |

## Docs to update

- [ ] `CHANGELOG.md`, `plans/HANDOFF.md`, `plans/FRAMEWORK-TODO.md` (close D54-F02)
- [ ] `plans/DECISIONS.md` (D-number: satisfied-by-reference semantics; in-repo-pinned-target rule; no-free-≥90 contract)
- [ ] the reuse governance doc + the layer index template

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | `SATISFIED_BY_REFERENCE` becomes a coverage **hole** (a doc marks itself referenced to escape the gate) | med | **Enforced this PR:** REUSE02 (target must be in-repo + commit-pin-format-valid), the full-prefix rule (the doc's upstream tags must still resolve in-repo, else TRACE-RES-001), and a visible REUSE01 advisory per referenced doc. This is a *visible, advisory-gated* escape — the deterministic-lint floor; semantic reuse-correctness (the carried elements really are the target's) and commit existence are NOT lint-verifiable. **Governance-only (NOT enforced this PR):** the no-free-≥90 readiness rule (skill follow-on). The plan does not claim the hole is closed — only that every reuse is surfaced and structurally constrained. |
| R2 | the escape ordering wrong — referenced element still flagged, or a real gap masked | med | mirror the existing `DEFERRED`/`REALIZED_BY` escape placement (escape check before reach check); V3/V4 assert both directions |
| R3 | URL/unpinned targets slip through as authoritative trace | low | `REUSE02` rejects URL targets + unpinned/​unresolvable targets; only in-repo+pinned resolves |
| R4 | scope creep into element-granular marking / commit-existence / skill-score enforcement | med | explicitly deferred (Out of scope); whole-layer frontmatter form + format/resolve checks + governance contract are the minimal sufficient core |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | `SATISFIED_BY_REFERENCE` is a declared `CoveredState` member, stubbed (no logic) — "PR-5 adds its logic" | `SATISFIED_BY_REFERENCE` | `tools/sdd_doc_lint/__init__.py:815` |
| 2  | `covered_state_of` classifies via escapes (`realized_by`→REALIZED_BY, `Future`→DEFERRED, else AUTHORED) and never returns SATISFIED_BY_REFERENCE today | `covered_state_of` | `tools/sdd_doc_lint/__init__.py:842` |
| 3  | escapes short-circuit the forward gate before the reach check (the pattern a reuse escape mirrors) | `covered_state_of(fr) != CoveredState.AUTHORED` | `tools/sdd_doc_lint/__init__.py:1604` |
| 4  | COV02 enumerates declared EARS/BDD elements and flags those not realized — where a referenced element must escape | `_check_backward_coverage` | `tools/sdd_doc_lint/__init__.py:1679` |
| 5  | the reuse escape is carried like `realized_by` (a token/field on the element) — FRElement already models such an escape | `FRElement` | `tools/sdd_doc_lint/__init__.py:727` |
| 6  | frontmatter is read via `_extract_frontmatter` (the `reuse:`/`id_state` read path) | `_extract_frontmatter` | `tools/sdd_doc_lint/__init__.py:969` |
| 5b | `covered_state_of` takes only an `FRElement` (no host-doc frontmatter) — so the doc-level reuse check must be at the gate, not inside it (Pass-1 F2) | `def covered_state_of` | `tools/sdd_doc_lint/__init__.py:842` |
| 7  | TRACE-RES-001 flags a citation to a missing doc as unresolvable — referenced docs must resolve as present | `_check_trace_resolution` | `tools/sdd_doc_lint/__init__.py:1395` |
| 8  | the triaged issue + fix shape (element-granular `authored\|referenced`; satisfied_by_reference passes coverage but "reuse not re-audited", no free ≥90; in-repo pinned target; URLs only `@discoverability`) | `D54-F02-REUSE-MANIFEST` | plans/FRAMEWORK-TODO.md:251 |
| 9  | the orchestration plan scopes PR-5 + sequences it AFTER PR-2's coverage semantics | `Reuse manifest` | plans/CONSUMER-FEEDBACK-001-PLAN.md:174 |
| 10 | examples are regenerated wholesale — no reuse corpus fixture now | `regenerated` | plans/FRAMEWORK-TODO.md:759 |

## Review log

### Pass 1 — 2026-06-29T00:00:00Z — self-review

- **F1 — what a referenced doc contains.** The plan didn't say whether a
  referenced doc is a bare pointer or carries the reused elements. A bare pointer
  would break TRACE-RES-001 (downstream citations to the target's element IDs
  wouldn't resolve). Resolved: a referenced doc **physically carries the reused
  elements** (marked referenced via the whole-doc flag); `reuse.target` is the
  pinned provenance source, not a redirection to dereference. Added the "What a
  referenced doc contains" subsection.
- **F2 — reuse must be checked at the gate, not in `covered_state_of`.**
  `covered_state_of(fr)` receives only an `FRElement`, with no access to the host
  doc's frontmatter — so it cannot see `reuse.state`. Reworked the design + Task 1
  to build a `doc_id → reuse_state` map and have COV01/COV02 escape by **host
  doc** (mirroring the existing escape placement). Added claim 5b.
- **F3 — REUSE01 deduped per doc.** COV02 iterates elements; the advisory must be
  one-per-referenced-host-doc, not per element. Noted in the COV02 bullet.

### Pass 2 — 2026-06-29T00:00:00Z — independent (fresh-context)

Independent reviewer verified the citations + traced the design through
`covered_state_of`, the gates, `_check_trace_resolution`, `build_edge_graph`, and
`trace_walk`. Confirmed SOUND: the gate-level escape design (Pass-1 F2 —
`covered_state_of` genuinely can't see the host doc; the `doc_id→reuse_state` map
is feasible), claims 1/2/3/5/5b/8/9, and the COV02 host-doc skip exempting
referenced elements in the downstream direction. Findings folded:

- **F-1 (load-bearing) — referenced docs' OWN upstream tags unhandled.** A reused
  PRD carries `@brd:` tags; `_check_trace_resolution` checks upstream tags and
  `trace_walk` follows them → the absent BRD is flagged orphan, breaking the very
  mid-chain-reuse case. Resolved with the **full-prefix rule**: the upstream
  prefix must also be in-repo + `referenced`, so everything resolves with no
  trace change; an upstream tag to an absent doc stays a (correct) finding.
- **F-2 (load-bearing) — `trace_walk.py` scope item was unreal.** Under F-1's
  full-prefix model the referenced doc is present on disk, so `trace_walk`
  orphans nothing and `_check_trace_resolution` resolves naturally — **no code
  change**. Cut the `trace_walk.py` / TRACE-RES-001 change from File-structure +
  Task 3/4; reframed to "no change needed."
- **F-3 (calibration) — R1 overstated enforcement.** Only REUSE01 (visibility) +
  REUSE02 (format/in-repo-resolve) + the full-prefix upstream-resolve requirement
  are enforced this PR; no-free-≥90 is governance-text-only. Re-baselined R1 to
  state the escape is visible/advisory-gated (the deterministic floor), not
  "closed".
- **F-4 — ledger line drift.** Fixed claims 4 (→:1679), 6 (→:969), 7 (→:1395).

### Pass 3 — 2026-06-29T00:00:00Z — independent (fresh-context, confirming)

Confirmed all 10 citations land on the right symbols (incl. the F-4 fixes
4→:1679, 6→:969, 7→:1395). Confirmed F-1/F-2: under the full-prefix model
`_check_trace_resolution` resolves both directions in-repo with **no code
change** (it checks element presence, not just doc presence — so a referenced
doc citing an upstream element the in-repo prefix copy doesn't declare correctly
fires TRACE-RES-001 = incomplete reuse, not a missed hole); all `trace_walk`/
TRACE-RES code-change scope cleanly cut, no dangling refs. Confirmed F-3 (R1
scopes enforcement to REUSE01 + REUSE02 + full-prefix-resolve; no-free-≥90 marked
governance-only; no "hole closed" overclaim). Gate-level `doc_id→reuse_state`
design coherent across Scope/Approach/Tasks/claims; V1-V7 map onto the post-cut
Tasks; Scope/File-structure/Tasks/Verification mutually consistent.

**No new load-bearing findings.**

**Result:** ready
