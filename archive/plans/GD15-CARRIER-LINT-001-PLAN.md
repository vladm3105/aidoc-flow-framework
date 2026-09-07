# GD15-CARRIER-LINT-001 — scope GD-15's instance mandate to its enablement (erratum)

| Field | Value |
| --- | --- |
| Plan state | **ABANDONED — 2026-08-28.** Superseded by `plans/INSTANCE-FORMAT-SSOT-001-PLAN.md`. Reason: two designs refuted in three passes (7/6/6 load-bearing findings, not converging) and the record accumulated blockers faster than it resolved them. Per the workspace rule, a mis-scoped record is **replaced**, not rewritten a third time. Retained in full as the evidence trail — Pass 1 killed the carrier design, Pass 3 killed the erratum's surface count. |
| Owner | framework |
| Issues | **#558** (release provenance). Re-scoped as *enablement*, not this plan: **#564**, **#565** |
| Version impact | framework **MINOR** `0.43.0 → 0.44.0` |
| Change level | **C2** (GATE-SPEC) |
| Unblocks | the first framework tag since `v0.41.3` |

> **This plan was cut, not patched.** Its first draft proposed making the linter carrier-aware.
> Pass 1 refuted the premise: the blocker is not a linter defect but a **normative contract**
> GD-15 explicitly deferred. The carrier work survives as a later, sequenced step under #564 —
> it is no longer this plan. The Pass 1 record is retained below as the justification.

## Objective

GD-15 (spec `0.43.0`) mandates YAML as the instance format for all eight layers **and, in the
same entry, declines to adopt the frontmatter contract that makes such an instance legible to
any rule** (Claim 1). The result is a spec that mandates a format its own gate rejects:
measured, a conformant YAML BRD produces 17 `STRUCT01` errors and a vacuous `COV01` pass
(Claims 8–10).

This plan makes the spec **self-consistent** by scoping the mandate to its enablement, so a
release can be tagged. It does not build the enablement.

## Scope

**In scope:**

1. **`GD-17`** — an erratum scoping GD-15's *instance-format* clause: YAML is the declared
   target format; the mandate takes normative effect when the frontmatter contract
   (`OKF-CONFORMANCE-001-DESIGN.md` D1, Claim 2) lands. Until then the **Markdown projection is
   the lint surface**, which is what the rules and the shipped corpus already are.
2. The same effective condition on **all three** normative carriers of the mandate
   (`NEW@pass2`): `DOC_GOVERNANCE_CORE.md` Principle 2 + §Template Policy — which is GD-15's
   own **named authority** (Claim 15) and the surface `LAYER_REGISTRY.yaml:19` defers to — plus
   scope notes in `LINT_RULES.md` and the `extensions` header. Missing Principle 2 would add a
   fourth disagreeing surface to the three-way disagreement GD-15 was written to end.
3. **#558** — the `0.44.0` CHANGELOG entry narrates the `0.42.0` / `0.43.0` provenance
   (founder decision: correct forward, edit no published record).
4. `VERSION` bump, fanout, `CHANGELOG` entry.
5. Re-pointing `TEMPLATE-COMPLETENESS-001` to `0.45.0` — **forward-looking mentions only**
   (Claim 6) — **and its four `GD-17` references to `GD-18`** (`NEW@pass2`, Claim 16). That plan
   already claims `GD-17`; this one lands first, so it takes `GD-17` and that plan shifts.

**Out of scope — this is the enablement programme, sequenced, one line each:**

- The frontmatter/document-identity contract — `OKF-CONFORMANCE-001-DESIGN.md` D1 owns it and
  is `Draft` (Claim 2). **Everything below depends on it.**
- `BRD-TEMPLATE.yaml` §7 `band` / `realized_by` keys and the status of `_authored_form`'s
  Markdown prescription — re-opens GD-14's counting rule (#564).
- The four carrier-aware primitives, plus the `scenarios:` path and the seed-fence stripper
  (#564).
- `FMT01` / `extensions` enforcement (#565). **Deliberately deferred:** with the mandate scoped
  to a later effective date, enforcing it now would enforce a rule that is not yet in force.
- The acceptance re-baseline: 30 `.md` fixtures against 3 manifests, plus 24 existing `.yaml`
  fixtures (Claims 4–5).

## Approach / Design

### D1 — The erratum names the real defect, and does not walk GD-15 back

GD-15's *reasoning* is sound and its template-scope half was already true. The defect is
narrower and stranger than "wrong decision": the same entry mandates an instance format **and**
records that it "does not adopt the frontmatter contract" (Claim 1). `GD-17` says exactly that,
and gives the mandate an effective condition rather than deleting it.

This is why "narrow GD-15 to templates" was rejected: it would discard a ratified decision and
leave instance format with no owner, when the decision is right and only its enablement is
missing.

### D2 — Markdown-as-lint-surface is a description, not a new claim

The erratum does not *introduce* a Markdown lint surface — it **describes the one that exists**.
Every structural rule already resolves through a Markdown carrier (Claim 3), the shipped corpus
is 100 % `.md`, and the 24 `.yaml` fixtures that exist are hybrids whose `## Heading` lines
double as YAML comments (Claim 5). The erratum's only change is to stop the spec asserting
otherwise.

### D3 — `extensions` keeps its value and gains a scope note, not an enforcer

All eight layers declare `[.yaml]` (Claim 7) and that stays: it is the declared **target**. What
changes is that the header says when it becomes enforceable. #565 stays open against the
enablement, so the field is not left silently unenforced-and-unexplained — which was its
original defect.

### D4 — `TEMPLATE-COMPLETENESS-001` moves to `0.45.0`; its history does not

Eleven lines mention `0.44.0` (Claim 6). **Three** are historical (`NEW@pass2` — Pass 2 corrected
this from two): `:253`, `:364` and `:370`. `:364` and `:370` sit inside the **same** dated
"Amendment — 2026-08-28" block, so re-pointing `:370` would edit the very record `:364` is
protected for; `:370`'s live twin is `:169`, which *is* re-pointed. The remaining eight are
forward-looking.

⚠️ `:253`'s `0.44.0` is in the row's **claim text** parenthetical, not in its PROBE command — the
PROBE there is a `gh release view` with no version in it. Do not go looking in the PROBE column.

The dated note recording the move must name **only** `0.45.0`; if it names `0.44.0` for
legibility, V7's expected count becomes `4`.

The blocker relief must precede the first tag, which is why this plan takes `0.44.0` rather than
queueing behind a non-blocker.

## File structure

### Modified

| Path | Change |
| --- | --- |
| `framework/governance/DOC_GOVERNANCE_CORE.md` | Principle 2 + §Template Policy gain the effective condition (`NEW@pass2`, Claims 15/19) |
| `framework/governance/DECISIONS.md` | `GD-17` erratum |
| `framework/governance/LINT_RULES.md` | scope note: carrier is Markdown until the contract lands |
| `framework/registry/LAYER_REGISTRY.yaml` | `extensions` header gains the effective-condition note |
| `framework/VERSION` | `0.43.0` → `0.44.0` |
| `CHANGELOG.md` | `0.44.0` entry + the #558 narration |
| `plans/TEMPLATE-COMPLETENESS-001-PLAN.md` | eight forward-looking `0.44.0` → `0.45.0` + four `GD-17` → `GD-18`; three historical mentions annotated, not edited |
| `plans/DECISIONS.md`, `plans/HANDOFF.md` | record the #558 decision; clear "needs a founder call" (`NEW@pass2`, Claim 18) |

**No hand-authored code or test changes** — but the claim "no test changes" would be false
(`NEW@pass2`, Claim 17): the version fanout mechanically rewrites the pinned literal in
`tests/conformance/platforms/test_plugin_release_metadata.py`, plus `docs/PARITY.md`,
`README.md`, both platform READMEs, `platforms/*/FRAMEWORK_SPEC_VERSION`, the 52 SKILL
frontmatters and the playbooks. Editing the three `framework/governance` + `registry` surfaces
also re-vendors the plugin bundle, which `test_plugin_framework_bundle.py` asserts byte-identical.
T4 runs both sync scripts, so none of this breaks silently — but it is the real surface count.

## Implementation sequence

### T1 — Task 1: `GD-17` erratum (D1)

State: what GD-15 decided; what it deferred (quoting `DECISIONS.md:101-104`); the measured
consequence (Claims 8–10); the effective condition; and the SemVer pair `0.43.0 → 0.44.0`
explicitly — GD-15 and GD-16 both omit theirs, and this entry repairs that too.

### T2 — Task 2: the two scope notes (D2, D3)

### T3 — Task 3: CHANGELOG `0.44.0` + #558 narration

Per the founder decision on #558: `0.42.0` was never a value of `framework/VERSION`, `0.43.0`
shipped untagged, `framework/v0.44.0` is the first tag since `v0.41.3`. **Edit no published
entry.**

### T4 — Task 4: version bump and fanout

⚠️ **Order is load-bearing** (Claim 11): `framework/VERSION` → `scripts/sync-version-refs.sh` →
**then** `tools/sync-plugin-framework.sh`.

⚠️ **Do not hand-edit the framework token in `docs/PARITY.md` first** (Claim 12) — it is both the
detector's source and a target, so editing it strands the fanout silently at exit 0.

### T5 — Task 5: re-point `TEMPLATE-COMPLETENESS-001` (D4)

### T5b — Task 5b: record the #558 founder decision (`NEW@pass2`)

⚠️ **T3 executes on a decision that is recorded nowhere in the repo** (Claim 18).
`plans/HANDOFF.md:32` still reads *"it needs a founder call"* and `plans/DECISIONS.md` carries
no entry for issue `#558`. The decision was taken in session on 2026-08-28 (option 3: tag
neither `0.42.0` nor `0.43.0`; the next release narrates the history; edit no published
record). Write it to
`plans/DECISIONS.md` **and** as a comment on #558 before T3 runs, and update
`plans/HANDOFF.md:18-34`, which will otherwise still declare #558 unresolved after this lands.

### T6 — Task 6: re-scope the enablement issues

Comment on #564 and #565 recording that they are now sequenced behind `OKF-CONFORMANCE-001`
D1, and that neither is a `0.43.0`/`0.44.0` blocker once `GD-17` lands.

## Verification

| # | Command | Expected | Task |
| --- | --- | --- | --- |
| V1 | `python3 -m pytest tests/conformance -q` | green — 375 passed / 796 subtests, unchanged | 1-4 |
| V2 | `python3 -m pytest tests/acceptance/deterministic -q` | green — 64 passed / 56 subtests, unchanged | 1-4 |
| V3 | `PYTHONPATH=tools python3 -m pytest tools/sdd_doc_lint/tests -q` | green — 6 passed, unchanged | 1-4 |
| V4 | `python3 -m sdd_doc_lint examples/url-shortener/docs/` | unchanged from `main` | 2 |
| V5 | `cat framework/VERSION platforms/*/FRAMEWORK_SPEC_VERSION` | all three read `0.44.0` | 4 |
| V6 | `git diff main -- CHANGELOG.md \| grep -c '^-[^-]'` | `0`. ⚠️ **Not `grep '^-'`** — the unified-diff header `--- a/CHANGELOG.md` matches that on every run, so the original form could never fail (measured; `NEW@pass2`) | 3 |
| V6b | `git diff -U0 main -- CHANGELOG.md \| grep '^@@'` | a single hunk at or above the `[Unreleased]` heading — zero deletions does not by itself prove no published entry was rewritten, since a mid-block insertion is all `+` lines (`NEW@pass2`) | 3 |
| V7 | `grep -c '0\.44\.0' plans/TEMPLATE-COMPLETENESS-001-PLAN.md` | `3` — the three historical mentions `:253`, `:364`, `:370` (`NEW@pass2`; was wrongly `2`). The dated re-point note must name **only** `0.45.0`, or this returns `4` | 5 |
| V7b | `grep -c 'GD-17' plans/TEMPLATE-COMPLETENESS-001-PLAN.md` | `0` (`NEW@pass2`, Claim 16) | 5 |
| V8 | `grep -n 'GD-17' framework/governance/DECISIONS.md` | entry present, with an explicit `0.43.0 → 0.44.0` pair | 1 |
| V9 | `pre-commit run --all-files` twice consecutively | clean both times | all |

All three suites must be **unchanged**, not merely green: this plan changes no code, so any
movement in V1-V4 means the erratum touched behaviour it should not have.

## Docs to update

- [ ] `CHANGELOG.md` — `0.44.0` entry + #558 narration
- [ ] `framework/governance/DECISIONS.md` — GD-17
- [ ] `framework/governance/DOC_GOVERNANCE_CORE.md` — Principle 2 + §Template Policy (`NEW@pass2`)
- [ ] `plans/DECISIONS.md` — the #558 founder decision (`NEW@pass2`)
- [ ] `CLAUDE.md` — framework current-state token (does **not** self-heal; Claim 12)
- [ ] `plans/HANDOFF.md` — regenerate

## Risks

| Risk | Mitigation |
| --- | --- |
| The erratum reads as walking GD-15 back | D1; the entry states the mandate survives with an effective condition |
| A reader takes Markdown-as-lint-surface as new policy | D2; the note says "describes existing behaviour" |
| Rewriting published history | V6 asserts zero CHANGELOG deletions |
| Falsifying TC-001's founder-decision record | D4; V7 pins the two historical mentions as surviving |
| Fanout stranded silently | T4 ⚠️ ordering + `docs/PARITY.md` trap |
| `GATE-SPEC-W003` fires — agent-facing governance change with no recorded `SECURITY_REVIEW.md` assessment | warning-only, but record the assessment in `GD-17` per the GD-05/GD-08 form (`NEW@pass2`) |
| Governance-PR surface budget | this PR exceeds the ≤3-surface cap. `plans/HANDOFF.md:101-102` records the standing exemption: a framework `VERSION` bump is unsplittable because `sync-version-refs.sh` writes three surfaces itself. **It also records that the bump needs a per-bump founder OK** — obtain and cite it in the commit message |

<!-- markdownlint-disable MD050 -->
<!-- MD050 (strong-style) rewrites `__init__.py` to `**init**.py`, which silently breaks
     every citation in the table below and makes the gate fail with the misleading
     `path '.py' does not exist`. Workaround per issue #408. Re-enabled after the table. -->

## Claim ledger

| # | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | GD-15 mandates the instance format **and** declines the frontmatter contract in the same entry | `frontmatter contract` | framework/governance/DECISIONS.md:101 |
| 2 | The frontmatter contract is owned by an unmerged `Draft` design | `D1` | plans/OKF-CONFORMANCE-001-DESIGN.md:110 |
| 3 | Required sections are resolved against `##` headings only | `_check_required_template_sections` | tools/sdd_doc_lint/__init__.py:1480 |
| 4 | The acceptance harness matches the warning multiset in both directions | `warning` | tests/acceptance/_harness.py:150 |
| 5 | `.yaml` layer fixtures already exist and lint green today | `doc_id` | tests/acceptance/fixtures/fullpath/golden_chain/06_SPEC/SPEC-01_golden.yaml:2 |
| 6 | `TEMPLATE-COMPLETENESS-001` mentions `0.44.0` on eleven lines, two of them historical | `founder` | plans/TEMPLATE-COMPLETENESS-001-PLAN.md:364 |
| 7 | All eight layers declare `extensions: [.yaml]` | `extensions` | framework/registry/LAYER_REGISTRY.yaml:33 |
| 8 | Nine rules and the trace graph gate on a frontmatter `doc_id` | `build_edge_graph` | tools/sdd_doc_lint/__init__.py:1762 |
| 9 | No layer template declares a top-level `doc_id` | `id: BRD-NN` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:18 |
| 10 | A YAML BRD produces 17 `STRUCT01` errors; the same content as Markdown produces none — blocks T1, whose erratum text must state this measured consequence | `STRUCT01` | PROBE: `PYTHONPATH=tools python3 -m sdd_doc_lint <tmp>/ytest/` → `17 error(s)` vs `<tmp>/mtest/` → `no structural findings`. already taken during the 0.43.0 cutoff review, so T1 is not gated on re-running it |
| 11 | A framework `VERSION` bump is gated and requires the fanout | `GATE-SPEC-E005` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:89 |
| 12 | `fw_prev` is detected from `docs/PARITY.md`, which is also a fanout target | `fw_prev` | scripts/sync-version-refs.sh:296 |
| 13 | `framework/VERSION` currently reads `0.43.0` | `0.43.0` | framework/VERSION:1 |
| 14 | The `0.43.0` CHANGELOG entry is headed `0.42.0 → 0.43.0` | `0.42.0 → 0.43.0` | CHANGELOG.md:23 |
| 15 | GD-15's own **Authority** names `DOC_GOVERNANCE_CORE.md` Principle 2 first (`NEW@pass2`) | `Authority` | framework/governance/DECISIONS.md:121 |
| 16 | `TEMPLATE-COMPLETENESS-001` already claims the `GD-17` identifier (`NEW@pass2`) | `GD-17` | plans/TEMPLATE-COMPLETENESS-001-PLAN.md:183 |
| 17 | The version fanout rewrites a conformance test, so "no test changes" is false (`NEW@pass2`) | `test_plugin_release_metadata` | scripts/sync-version-refs.sh:352 |
| 18 | The #558 founder decision is recorded nowhere in-repo; the handoff still calls it open (`NEW@pass2`) | `it needs a founder call` | plans/HANDOFF.md:32 |
| 19 | Principle 2 asserts the instance mandate unconditionally and is the third normative carrier (`NEW@pass2`) | `YAML is the mandatory format` | framework/governance/DOC_GOVERNANCE_CORE.md:6 |
| 20 | `LAYER_REGISTRY.yaml`'s header defers to Principle 2 as its authority (`NEW@pass2`) | `DOC_GOVERNANCE_CORE.md Principle 2` | framework/registry/LAYER_REGISTRY.yaml:19 |

**Expected gate warnings — do not "fix" them.** Rows 3 and 12 cite a precise line *inside* a
symbol that occurs more than once, so the gate resolves the symbol elsewhere and reports line
drift. The cited lines are the accurate ones; `check_plan.py --fix` would replace them with less
precise ones.

<!-- markdownlint-enable MD050 -->

## Review log

### Pass 1 — 2026-08-28 — independent

Dispatched `verified-planning-reviewer` against the gate-green draft. **Nine findings, seven
load-bearing.** Six of the seven are confirmed against source by the author; one is partly
wrong (F7, below). This is not a fold — the findings invalidate the plan's central design
claim, so per the fold discipline (growth is a defect signal) the plan is **cut, not patched**,
and the direction is escalated.

**F1 (confirmed, decisive) — there is a fifth carrier-dependent primitive, and it is undecided
spec.** Nine rules and the whole trace graph gate on a frontmatter-derived `doc_id`, not on
carrier parsing: `build_edge_graph` drops any doc without one
(`tools/sdd_doc_lint/__init__.py:1762`), and `COV01`, `CSC01`, `SEED01`, `STALE01`,
`REUSE01/02`, `ACC01`, `COV02`, `COV03` each re-gate on it. **No layer template declares a
top-level `doc_id`/`artifact_type`/`status`** — verified across all eight. So P1–P4 do **not**
restore those rules on a YAML instance; `fm.get("doc_id")` is `None` either way.

The repair is a normative frontmatter contract, which **GD-15 explicitly declined to adopt**:
`framework/governance/DECISIONS.md:101-104` — *"does not adopt the frontmatter contract (that
design's D1 owns it)"*, deferring it to `OKF-CONFORMANCE-001-DESIGN.md` D1. **This plan's
premise — that the blocker is a linter change — is therefore false.**

**F2 (confirmed) — `FMT01` at `warning` still reddens the acceptance tier; D3's rationale and
V5 are wrong.** `tests/acceptance/_harness.py:150-152` matches the warning multiset in **both**
directions and asserts zero errors. There are **30** `.md` fixtures under `valid/` against only
**3** manifests, so the first new warning fails targets that have no manifest.

**F3 (confirmed) — P2 has no YAML representation for `band` / `realized_by`.**
`BRD-TEMPLATE.yaml` §7 `_authored_form` normatively prescribes rendering §7 **as Markdown**,
and puts `realized_by` inside a band parenthetical; the structured `requirements[]` alternative
carries neither key. `covered_state_of` consumes exactly those two fields. Fixing it edits the
BRD template and re-opens GD-14's counting rule.

**F4 (confirmed, and understated) — existing `.yaml` layer instances already lint green and the
new branch changes them.** The reviewer counted 17; the true figure is **24**
(`find tests/acceptance/fixtures -name '*.yaml' | wc -l`). The `golden_chain/` files are
genuine two-document streams needing `safe_load_all`. The Risks row named the wrong risk.

**F5 (confirmed) — P4 is wrong on both carriers and would silently disarm `SEED01`.**
`scenarios:` is **not** top-level (it is nested under `scenario_structure:`), and `_YAML_FENCE`
has **three** consuming sites, not two: the third (`__init__.py:2548`) strips the seed ledger so
an `absorbed` target cannot self-declare and resolve to itself. With no fence to strip on YAML,
that check passes vacuously.

**F6 (confirmed) — `FMT01` as specified flags index docs the spec says are correctly `.md`.**
`LAYER_REGISTRY.yaml:23-27` scopes the `.md` index allowance explicitly. Task 2 must skip
`_is_index_doc`.

**F7 (count confirmed; ownership claim REFUTED) — D4's cost is 11 lines, not 3 — but the
collision is not the one reported.** `grep -c '0\.44\.0'` returns **11**. The reviewer states
`TEMPLATE-COMPLETENESS-001` "already owns writing the #558 correct-forward narration". It does
not: its `:159-162` and its founder decision at `:364` are the **#532 / GD-13** correct-forward
narration; #558 appears only as an explicitly out-of-scope note at `:167-169`. The two
narrations are different.

The real consequence runs the other way: two of the eleven lines are **history** — a gated claim
ledger's PROBE text (`:253`) and a recorded **founder decision** (`:364`) that names `0.44.0`
verbatim. **Re-pointing that plan would falsify a recorded founder decision, so D4 is wrong and
its sequencing must invert:** `TEMPLATE-COMPLETENESS-001` keeps `0.44.0`.

**F8, F9 (confirmed, minor).** The key walk emits `id`/`title`/`metadata` as sections and STY02
falls back to a flat 200-word budget for them (the author had independently found this before
Pass 1 returned). And Claim 16's `warning→error` is a **phase gradient inside one release**
(`build` vs `gate-code`), not a ship-advisory-then-escalate precedent — D3 cited it as the
latter.

**Not findings (verified by the reviewer, retained):** Task 6's ordering warnings are current,
not stale; Claims 15 and 24 hold; Claims 3 and 4 are numerically exact.

**Result: NOT ready — scope cut required, direction escalated to the founder.** The plan cannot
proceed as drafted: F1 shows its four-primitive design does not fix the blocker, and the actual
repair depends on a normative contract that GD-15 deliberately deferred to a separate unmerged
design. The cost of the chosen option was materially understated when the founder chose it, so
the choice is put back rather than folded around.

### Pass 2 — 2026-08-28 — independent

Dispatched against the **cut** plan. **Six load-bearing findings, all six confirmed against
source by the author** (Pass 1 was 7, so the trend is down and the findings are now mechanical
rather than foundational — the plan is converging). All folded; additions carry `NEW@pass2`.

**F1 — the erratum was incomplete.** The mandate has **three** normative carriers, not two.
`DOC_GOVERNANCE_CORE.md:6` (Principle 2) asserts it unconditionally, `:44` instructs readers to
resolve exactly this ambiguity in the opposite direction, `LAYER_REGISTRY.yaml:19` defers to it,
and **GD-15's own Authority line names it first** (`DECISIONS.md:121`). Scoping GD-15 without
touching its named authority would have added a fourth disagreeing surface. Folded: Principle 2

- §Template Policy are now in scope, the Modified table, docs-to-update, Claims 15/19/20 and a
verification row.

**F2 — `GD-17` was already taken.** `TEMPLATE-COMPLETENESS-001` claims it at `:28`, `:119`,
`:183`, `:211`; the highest existing entry is `GD-16`. Both plans were correct in isolation and
collide on landing. Folded: this plan lands first and keeps `GD-17`; T5 also re-points that
plan's four references to `GD-18`, pinned by **V7b**.

**F3 — "No code changes. No test changes." was false.** `scripts/sync-version-refs.sh:352`
rewrites the pinned literal in `tests/conformance/platforms/test_plugin_release_metadata.py`,
and the governance/registry edits re-vendor the plugin bundle that
`test_plugin_framework_bundle.py` asserts byte-identical. Folded: the sentence is replaced with
the real surface list.

**F4 — V6 could never fail.** `git diff … | grep '^-'` matches the unified-diff header
`--- a/CHANGELOG.md` on every run. **Measured:** on a pure-addition diff `grep -c '^-'` returns
`1` and `grep -c '^-[^-]'` returns `0`. Inherited verbatim from `TEMPLATE-COMPLETENESS-001:202`,
which carries the identical defect. Folded: V6 corrected, and **V6b** added — zero deletions
does not prove no published entry was rewritten, because a mid-block insertion is all `+` lines.

**F5 — the historical/forward split was 3/8, not 2/9.** `:364` and `:370` sit inside the *same*
dated Amendment block, so re-pointing `:370` would edit the record `:364` is protected for;
`:370`'s live twin is `:169`. Folded: V7 now expects `3`. Rider also folded — `:253`'s mention is
in the **claim text**, not the PROBE column, which D4 had mis-located.

**F6 — T3 executed on an unrecorded decision.** The #558 founder call is in no repo surface;
`plans/HANDOFF.md:32` still reads *"it needs a founder call"*. Folded as new task **T5b**, plus
Claim 18 and `plans/DECISIONS.md` / `plans/HANDOFF.md` in docs-to-update. The decision was also
captured as a comment on #558 the same day, so it cannot be lost with this branch.

**Rider folded (high value):** the effective condition must **name `doc_id`**. The string appears
nowhere in `OKF-CONFORMANCE-001-DESIGN.md`, whose D1 names required keys generically and
`artifact_type` explicitly — so a condition worded only "when D1 lands" could be satisfied by a
contract that does not lift the blockage.

**Also folded:** a `GATE-SPEC-W003` risks row (warning-only), and an explicit note that this PR
exceeds the ≤3-surface governance cap under the standing unsplittable-bump exemption at
`plans/HANDOFF.md:101-102` — which also requires a **per-bump founder OK**, to be cited in the
commit message.

**Verified by the reviewer, not findings:** Claim 1 is not overstated; Claim 5 holds; Claims 3,
4, 11, 13, 14 are semantically accurate; no conformance test asserts on the prose of the edited
surfaces; and the `FMT01`/#565 deferral reasoning is sound.

**Result:** folded; dispatching Pass 3.

### Pass 3 — 2026-08-28 — independent

**Six load-bearing findings. Pass 1 = 7, Pass 2 = 6, Pass 3 = 6 — the loop is not converging,
and Pass 3 is the OPS-0066 cap. Per the fold discipline, STOP: no fourth pass was dispatched
and the open items are escalated to the founder.**

**F1 (confirmed, decisive) — the carrier census is wrong, and the plan's objective sentence is
therefore false as shipped.** The plan claims the instance mandate has three normative carriers.
The reviewer found the layer surface — `framework/layers/01_BRD/README.md:123-127`, a section
headed **"Document Formats"**: *"BRDs are authored in YAML (`.yaml`)"*, with filename patterns
`BRD-NN_platform_{slug}.yaml` — while `:119` of the same README says `BRD-NN_*.md`.

The author then took the census the plan should have opened with. **18 files under `framework/**`
carry an instance-format assertion, and 6 of them assert *both* `.md` and `.yaml` instance
filenames within the same file** (`ID_NAMING_STANDARDS.md`, `BRD-00_index.TEMPLATE.md`,
`BRD-TEMPLATE.yaml`, `BRD-00`/`BDD-00`/`SPEC-00`/`TDD-00` index templates). The erratum scopes
**3 of 18**. After it landed, an author following the BRD README would still author `.yaml` and
still produce the 17 `STRUCT01` errors — so *"makes the spec self-consistent"* (Objective) would
be untrue.

This is the same failure as Pass 1, one layer out: a design premised on a surface count nobody
had measured.

**F2 (confirmed, author's fold miss) — two live surfaces still carry the pre-Pass-2 count.**
Claim 6 says "two of them historical" and the Risks row says "V7 pins the two historical
mentions", both contradicting the folded `Three are historical` and V7 = `3`. F5's fold patched
D4 and V7 and left the ledger row and the risk row behind — precisely the "fix the ledger, not
just the prose" defect the skill warns about.

**F3 (confirmed) — T5's re-point instruction is under-specified.** Two of the eight
forward-looking lines also carry the *from* version (`0.43.0 → 0.44.0`), so applying "re-point
`0.44.0` → `0.45.0`" literally yields `0.43.0 → 0.45.0`, which is false once this plan lands
`0.44.0`. V7 counts only `0.44.0` and cannot catch it.

**F4 (confirmed) — V7b has the identical hole D4 guards for V7.** Any provenance note explaining
the `GD-17` → `GD-18` renumber makes `grep -c 'GD-17'` non-zero and fails V7b.

**F5 (confirmed) — the retained Pass 1 F7 verdict contradicts the shipped design.** Pass 1
concluded *"sequencing must invert: `TEMPLATE-COMPLETENESS-001` keeps `0.44.0`"*; the plan now
does the reverse and never marked that conclusion superseded, so the log reads as a live
directive against the design.

**F6 (confirmed) — V6b cannot be satisfied as written.** Framework entries live *inside*
`## [Unreleased]` (`CHANGELOG.md:13`), so a new entry inserts below it and a `-U0` hunk header
can never start "at or above" that heading.

**Clean, recorded so they are not re-run:** no conformance test asserts on the prose of any
edited surface; the `GD-17` → `GD-18` renumber is coherent (`GD-17` appears in exactly four
lines, all in that one plan; `GD-18` appears nowhere; highest ratified is `GD-16`); V7 = `3` is
arithmetically right; MINOR at C2 is correctly graded; and every Pass-2 ledger row is
semantically accurate.

**Result: NOT ready. Cap reached, loop not converging, escalated.** Two designs have now been
refuted in sequence — "make the linter carrier-aware" (Pass 1) and "scope the mandate on three
surfaces" (Pass 3) — and both failed for the same reason: **the YAML instance mandate is diffuse
across 18 spec surfaces and no census existed.** That census is now the prerequisite artifact and
is filed separately. F2, F3, F4, F5 and F6 are cheap corrections held pending the scope decision;
fixing them before the scope is settled would be folding a fourth time into a plan whose
objective is unproven.
