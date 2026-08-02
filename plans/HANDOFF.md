# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here; open work lives in `plans/FRAMEWORK-TODO.md`, never here.

## Where we are — 2026-08-02

Framework spec `0.40.0`, **plugin `0.25.0`**, Hermes `0.12.1`.
**Open PRs: 0. Open issues: 5** — [#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386),
[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405),
[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412),
[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417),
[#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423).

**PLUGIN-PREPROD-001 is functionally COMPLETE — all 23 findings, including M6.** Five PRs
plus a five-stage PR 5. Merges: #424 (handoff), **#425 (`0.25.0` cut)**, **#426 (22
closures + M8 + D-0074)**, #427 (5e).

**M6 landed 2026-08-02 — the founder authorized it and it is done.** Annotated tag
`claude-code-plugin/v0.25.0` points at `e6c6539d` and is on the remote; the GitHub Release
is **published as a pre-release** (matching `v0.18.0`'s tier, since the plugin is a declared
pre-1.0 preview). Gate evidence at the tagged commit: conformance `361 passed, 769 subtests`,
and `VERSION` / `.claude-plugin/plugin.json` / `.claude-plugin/marketplace.json` all reading
`0.25.0` against `FRAMEWORK_SPEC_VERSION` `0.40.0` = `framework/VERSION`. ⚠️ The first two
are under `platforms/claude-code-plugin/`; **`marketplace.json` is at the REPO ROOT** — a
re-derivation that looks for it beside `plugin.json` gets "No such file" and reads this
evidence as fabricated. Verify with
`gh release view claude-code-plugin/v0.25.0` and `git rev-list -n1 claude-code-plugin/v0.25.0`.

**⚠️ THE ONE TASK LEFT IS A DOC RECONCILIATION, AND IT IS THE TOP PRIORITY.** The tag cut
falsified **seven** surfaces that still assert M6 is open. This was deliberately handed to a
fresh session rather than appended to the tagging session; it is task 1 below, and nothing
else picks it up. Until it lands the repo publicly contradicts its own Release.

**Consequences a fresh session must not misread:**

- The plan and both changelogs are **stale, not authoritative.** The tag exists; the files
  saying it does not are the defect. Do not "verify" against them.
- The seven surfaces, each with the exact false claim: (a)
  `plans/PLUGIN-PREPROD-001-PLAN.md:7` status row still `In Progress` + the M6 bullet at
  `:358` still says "founder-gated"; (b) `plans/FRAMEWORK-TODO.md` queue header still
  `⏳ OPEN ON RESIDUAL` with M6 its sole open member; (c) `docs/TAGGING.md:125` says "Tag
  **not yet cut**", and `:99-100` still gives the cut high-water mark as
  `claude-code-plugin/v0.20.1`; (d) `platforms/claude-code-plugin/CHANGELOG.md` keeps the
  `0.25.0` entry under `## [Unreleased]` with a bullet saying the tag is not part of the
  stage; (e) `CHANGELOG.md:47-51` says "No tag and no GitHub Release yet" **and**, at `:50-51`,
  that `VERSION` is "not a published release"; (f) `ROADMAP.md:126-129` says "The 23rd
  finding (M6) is open" **and** that the latest Release "remains
  `claude-code-plugin/v0.18.0`" — the most publicly visible of the seven.
- **(g) is different in kind and must not be edited like the others.**
  `plans/DECISIONS.md:93-97` (D-0074 §4) says the tag and Release "**remain** founder-gated"
  and that "`PREPROD-M6` **stays open** under `## Open`" — present-tense claims about live
  state, now false, inside an **append-only** log that is also a governance surface. Fix it
  with a **new dated entry or a `⚠️ superseded 2026-08-02` rider**, never by rewriting
  D-0074. It is also the first hit a fresh session gets from `grep -rn M6 plans/`, which is
  why it is listed rather than left to discovery.
- **It is a governance PR** (`plans/*-PLAN.md`, `plans/DECISIONS.md`), so the ≤3-surface cap
  applies — **three sequential PRs, not one.** Suggested split: (a)+(b)+(c) → (d)+(e) →
  (f)+(g)+this handoff. Re-derive every `:NNN` above before citing it; they were measured
  2026-08-02 and each PR shifts the next one's lines.
- **⚠️ Two `FRAMEWORK-TODO.md` items are FIXED-BUT-NOT-CLOSED, deliberately, because
  closing them would have been a 4th doc surface against the ≤3 cap on the initiative's
  last stage.** Neither blocks anything; both are ~2-line edits. (a)
  `PREPROD-PLAN-TESTPATH` — 5e corrected the path, but the entry still sits under
  `## Open` and both its `:378` citations now land on a blank line; move it to
  `## Closed` and re-cite the current line. (b) `PREPROD-M6`'s entry is now **closed by the
  tag cut**, not merely mis-stated — fold it into task 1's surface (b) rather than repairing
  its "six versions stale" heading, which the cut made moot. **5e was the last stage, so
  nothing later picks these up — they are yours.**

**⚠️ A plugin `VERSION` bump needs a hand-authored `docs/TAGGING.md` row, or conformance
goes red.** `tests/conformance/platforms/test_plugin_release_metadata.py:137` asserts the
file contains the current plugin tag string, and `scripts/sync-version-refs.sh` deliberately
does not write it (`:56-60` lists TAGGING/ROADMAP/HANDOFF release rows as human-authored).
Cost a conformance failure during 5c. **Not in the plan and not in any earlier handoff.**

**⚠️ The `sync-version-refs.sh` fanout reaches OUTSIDE this repo, and that write is broken.**
`:180` writes `../web-site/src/pages/index.astro`, a sibling repo with its own remote. The
badge there reads `Pre-release v0.20.1`; the script greps for the *previous* value, misses,
and `replace_in_file` returns 0 **without logging**. Self-sealing — no future bump repairs
it. A throwaway clone (the prescribed test method) has no sibling and is structurally blind
to it. [#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423); the founder
declined the repair during 5c, so **the public site still advertises `v0.20.1`.**

**⚠️ The `ai-review` gate WILL request changes on a code or CI PR with no root
`CHANGELOG.md` entry.** The ≤3-surface cap is a *ceiling*, not observed practice — what
passing PRs share is the changelog entry, not a surface count. A failing run **uploads a
verdict artifact** (`gh run download <id> -n ai-review-verdict`) — a run that fails *after*
producing it is a verdict, not an outage. Docs-of-record-only PRs need none — #424
(`plans/` only) and #426 (`plans/` **plus `ROADMAP.md`**) both passed without one.

**⚠️ Two tiers are RED on `main` for pre-existing reasons, neither CI-gated, neither
yours.** `Hermes pytest` — an unpinned `mcp[cli]>=1.0.0` floor, path-filtered, locally green
(570), see `HERMES-MCP-FLOATING-DEP`, do not re-diagnose. Phase 0 `lint-smoke` in
`tests/scripts/test-acceptance.sh` — example-corpus debt deferred to the wholesale regen;
use `--skip-lint-smoke`.

**V15 (schedule→`workflow_run` chain) is still unconfirmed** — never a gate; V14 proved the
chain off a *dispatched* upstream only. `standards-drift` runs Mondays 09:00 UTC, **first
observable 2026-08-03 (tomorrow).** On or past that date, confirm a `pin-currency-reader`
run followed it with `event=workflow_run`, then delete this paragraph. A failure there is a
new bug, not a reopened plan.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and `plans/HERMES-BACKLOG.md`.
This is only the ordering a fresh session should use.

1. **Reconcile the seven surfaces the M6 tag cut falsified — START HERE.** Enumerated with
   their exact false claims in § "Consequences" above. Three sequential governance PRs.
   The plan goes `In Progress` → `Completed`, the `FRAMEWORK-TODO.md` queue header
   `⏳ OPEN ON RESIDUAL` → `✅ CLOSED`, both changelog `0.25.0` entries out of
   `[Unreleased]` under a dated release heading, and `docs/TAGGING.md`'s high-water mark to
   `claude-code-plugin/v0.25.0`. **No discovery needed; no founder decision pending.**
2. **[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417) — namespace the
   plugin's agent dispatch references.** 29 `subagent_type=` occurrences across 20 files,
   none scoped — but most are `subagent_type=<mapped agent>` *placeholders*, so the bare
   names live in the per-skill lens→agent mapping tables and
   `platforms/claude-code-plugin/README.md:215+` (`:213` is the table header). Mechanical,
   but **verify first that `subagent_type` accepts `plugin:agent`**; the docs confirm the
   scoped form for `--agent` and @-mention but do not state it for `subagent_type`. If it
   does not, this reopens as a rename of the definitions. This is the live half of `L7`,
   which closed on documentation only.
3. **`PREPROD-B2-GATE-SCOPE` — a release gate that greps a literal stopped measuring.**
   `tests/release/test_marketplace_gate.py:42` forbids `--dangerously-skip-permissions` in
   `skills/**/SKILL.md`; PR 3 renamed the mechanism to `--allow-skip-permissions`, so the
   gate still passes and no longer measures anything live. Conformance *does* cover the
   property (`test_bypass_absent_by_default`, `test_flag_defaults_off`), so this is a
   gate-quality gap, not an exposure. Also `skill_dirs()` scans `skills/` only —
   `commands/` and `agents/` are outside both. Fix shape: assert the property, extend the
   scan. See **D-0074 §1**.
4. **`SDD-CORPUS-UNVERIFIED` — START WITH THE FOUNDER DECISION; it gates the plan.**
   Census in the `FRAMEWORK-TODO.md` entry. Two rules not there: **build the gate before
   touching content**, and this needs a `plans/` plan with the two-cycle gap review.
5. **[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412) — linting a
   single file reports every cross-document trace tag as a `TRACE-RES-001` ERROR.** Fix
   shape is the single-file gate `_check_forward_coverage` already carries
   (`tools/sdd_doc_lint/__init__.py:1972-1973`, documented at `:1965-1967`). ⚠️ An earlier
   handoff cited `:1961-1963` and was wrong — those are run-mode severity bullets.
   Re-derive a carried-forward line number before re-publishing it.
6. **[#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423) — the
   `web-site` badge.** Two halves: repair `Pre-release v0.20.1` by hand in a `web-site` PR,
   and make a grep miss on that path **warn** instead of returning silently. Keep it
   non-fatal — the sibling is legitimately absent in CI — and do **not** make
   `replace_in_file` warn globally; most of its misses are the benign idempotent case.
7. **Watch [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351) —
   when canon ships its own reader, DELETE ours.** `.github/workflows/pin-currency-reader.yml`
   plus `scripts/read-pin-currency-log.sh` and `scripts/reconcile-pin-currency-issue.sh`
   are an override, not a permanent local surface (plan R9). Nothing else says so.
8. **[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) —
   `sync-version-refs.sh` rewrites historical "shipped in vX" claims.** Corrupted
   `docs/PARITY.md:65` on three consecutive bumps. **Did NOT fire on the `0.25.0` plugin
   bump** — verified line by line during 5c, in the real tree. Still open for
   framework-spec bumps.
9. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** Outstanding is only
   the **fix shape** — #389's approach cannot be reused because this `prev` is load-bearing
   elsewhere; derive it from a fanout target nobody hand-edits (`docs/PARITY.md`).
10. **`doc-maintainer` — nothing to do; it is PAUSED** (`kill_switch: true`, #397), CI
   green. Resume requires `aidoc-flow-ci` #352 **AND** #353 — #353 alone is 15 of the 23
   failures. Census in D-0072. ⚠️ **Do not re-file the `high_risk_paths` / `allowed_paths`
   mismatch** — deliberate and documented; #396 recorded it as a bug and was wrong.
11. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`.
12. **Everything else** is in `FRAMEWORK-TODO.md` by tag. An entry under `## Open` with no
   `⏳ OPEN ON RESIDUAL` marker is genuinely open work (#403). Nothing there is blocking.

## Traps too fresh to have settled — not yet in `CLAUDE.md`

The four that had settled were **graduated into `CLAUDE.md` § "Durable traps → Process"**
by this stage, and are deliberately not repeated here. What remains:

- **A review fold authors its own false claims, and the pass that produced the fold never
  catches them.** Three on #422, each caught by the *next* cycle. Measured again this
  session at a larger scale: the 5d closure audit produced a finding ("the release gate no
  longer measures the invariant") that was **false** and had already been written into a
  decision-log draft before one `grep` refuted it — conformance covers the property; only
  the *gate's literal* is stale. **Re-verify folded text against source, not against the
  findings list**, and treat a subagent's finding as a claim, never as a result.
- **An absence is the easiest thing to assert and the hardest to verify** — and it is
  the shape agents produce most confidently. Two instances this session, both refuted by a
  single command: "nothing calls `test-plugin.sh`" (umbrella `release.yml:32` does) and the
  gate claim above. **Before writing "X does not happen", run the command that would show
  it happening.**
- **A self-citation inside a file you are editing is invalid the moment you edit it.**
  Correcting the plan shifted every line after `:292` — twice, because the follow-up edits
  shifted them again — silently invalidating eight `:NNN` references I had just written.
  **Derive self-references last, in one pass, after content is final**, and state the quote
  beside the number so a future reader can recover from the drift. The plan now carries that
  warning inline.
- **A document can name a channel, a control or a setting that does not exist, and nothing
  in CI will ever notice** — `SECURITY.md` pointed at private vulnerability reporting for
  months while it was disabled. Found only by running
  `gh api repos/<r>/private-vulnerability-reporting`. **When a doc tells a reader to go
  somewhere, go there.** Two scanning knobs are still off — `SYNC-SECRET-SCANNING-KNOBS`,
  founder decision.
- **A perfect first-try mutation kill rate is the symptom, not the result.** Two runs scored
  11/11 and 17/17 and **both were worthless** — one harness copied the module where its
  `sys.path` sibling did not resolve, so every mutant died of `ModuleNotFoundError`; the
  other ran against a red baseline. **Assert the unmutated baseline green *inside* the
  harness, and include a control mutant that must die.** Also: anything mutating source in
  place leaves the tree dirty in a way that reads as authored code — restore from a saved
  copy each iteration, **never in a `finally`** (killing a hung mutant skips it), bound each
  run with a timeout, and verify `git diff --quiet <path>` before any run you intend to trust.
- **When a fix has a *scope* and a *matcher*, changing one re-breaks the other.** The release
  gate's scope fix immediately failed against the PR's own changelog entry, because an entry
  documenting a placeholder check has to name the tokens it checks for. Ask which *other*
  dimension the change moved.
- **`check_plan.py` false-greens on a not-ready plan.** Its zero-findings check is a phrase
  match, and it accepted a Review log whose final pass said *"**Result:** NOT READY"* —
  because the surrounding prose contained "all folded". Canonical script is
  `~/.claude/skills/verified-planning/check_plan.py`; no repo-local copy. **Not filed.**

Also unresolved and blocking nothing: the founder flagged plugin `requirements-analyst`'s
`model: sonnet` as unratified. It now also declares an eight-tool allowlist (PR 4).

## Stale advice — a fresh session will find these referenced, and they are FIXED

| Stale claim | Reality |
|---|---|
| "`--admin` is required on every PR" ([aidoc-flow-ci#322](https://github.com/vladm3105/aidoc-flow-ci/issues/322)) | **Fixed at `ci/v2.16.0`.** Every PR since #378 has reached mergeable with no `--admin`. Do not re-add PR numbers to this row — it is the one that accretes |
| "Branch protection requires the phantom `Lint / format / security hooks`" | **Fixed.** The six required contexts are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` and `Hermes pytest` are **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| Three pin-currency claims: `NO-PIN-CURRENCY-CHECK`, `PIN-CURRENCY-NO-READER`, `PIN-CURRENCY-READER-PLAN.md:465`/`:469` | **All three dead.** The check runs on every weekly `standards-drift`; the reader SHIPPED at #392 and consumes the completed run's **log**; V14 exercised close-on-clean for real |
| The plan's PR 5 section as a guide to what PR 5 does | **Four of its claims were falsified by its own implementation** and are annotated in place (M7's "replace the list", ledger row 34, the README prerequisites row, the `--threshold` bullet). Read the annotations, not the original text |

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen. IPLAN ↔ iplanic integration is
deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`).
