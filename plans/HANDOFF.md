# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here; open work lives in `plans/FRAMEWORK-TODO.md`, never here.

## Where we are — 2026-08-02

Framework spec `0.40.0`, **plugin `0.25.0`**, Hermes `0.12.1`.
**Open issues: 5** — [#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386),
[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405),
[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412),
[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417),
[#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423).
Re-derive with `gh issue list --state all --limit 200` — never `--search`, and never the
default `--limit 30` (this repo is past #430).

**PLUGIN-PREPROD-001 is COMPLETE and reconciled. Nothing about it is left.** All 23
findings closed, the plan is `Completed`, and the seven surfaces the tag cut falsified
were repaired across three governance PRs: **#429** (plan + `FRAMEWORK-TODO` +
`docs/TAGGING.md`), **#430** (both changelogs), and **the PR carrying this file**
(`ROADMAP.md` + `DECISIONS.md` rider + this handoff).

The release itself: annotated tag `claude-code-plugin/v0.25.0` → `e6c6539d`, on the
remote; GitHub Release published as a **pre-release** (matching `v0.18.0`'s tier — the
plugin is a declared pre-1.0 preview). Verify with
`git rev-list -n1 claude-code-plugin/v0.25.0` and
`gh release view claude-code-plugin/v0.25.0`.

**`plans/DECISIONS.md` D-0074 §4 is superseded, not edited.** It still reads
"remain founder-gated" / "`PREPROD-M6` stays open" in its own text; a dated rider
directly below it records that the gate opened. That is deliberate — the log is
append-only. Do not "fix" the original prose.

**⚠️ This repo does not auto-merge.** `.github/ai-review/config.json:22` records it as
deliberately omitted from the **operations-side** `auto_merge.repos` allowlist — it is the
spec/governance repo, `tier:spec`, human-always. ⚠️ That allowlist is read from
`trust_config_repo` (`vladm3105/aidoc-flow-operations@main`), **not** from this repo, so
do not go looking for it here. `CLAUDE.md` separately excepts any PR touching a governance
surface (`plans/*-PLAN.md`, `plans/DECISIONS.md`, `CLAUDE.md`, `.github/ai-review/`) from
the AI auto-merge default. The three PRs above merged on **explicit founder authorization
given in-session**. Ask; do not infer standing approval from the fact that they merged.

**⚠️ A plugin `VERSION` bump needs a hand-authored `docs/TAGGING.md` row, or conformance
goes red.** `tests/conformance/platforms/test_plugin_release_metadata.py:137` asserts the
file contains the current plugin tag string, and `scripts/sync-version-refs.sh`
deliberately does not write it (`:56-60` lists TAGGING/ROADMAP/HANDOFF release rows as
human-authored). ⚠️ That assertion is a **bare substring check**, so it is satisfied by
the § "Release inventory" preamble as well as by the inventory row — see
`TAGGING-GATE-SUBSTRING-ONLY`.

**⚠️ The `sync-version-refs.sh` fanout reaches OUTSIDE this repo, and that write is
broken.** `:180` writes `../web-site/src/pages/index.astro`, a sibling repo with its own
remote. The badge there reads `Pre-release v0.20.1`; the script greps for the *previous*
value, misses, and `replace_in_file` returns 0 **without logging** — self-sealing, so no
future bump repairs it, and a throwaway clone (the prescribed test method) has no sibling
and is structurally blind to it. The founder declined the repair, so **the public site
still advertises `v0.20.1`** ([#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423)).

**⚠️ The `ai-review` gate WILL request changes on a code or CI PR with no root
`CHANGELOG.md` entry.** Docs-of-record-only PRs need none — #424, #426 and #429 all
passed without one. Measured this session: **nothing on the PR path enforces it
mechanically** — `tests/release/` is invoked by nothing on *this* repo's PR path, only by
`tests/scripts/test-plugin.sh:317`, which the **umbrella** runs on `v*` tags; and
GATE-SPEC E008 is diff-aware and skips when `framework/` is untouched. The pressure is
the LLM verdict, not a rule.

**⚠️ Two tiers are RED on `main` for pre-existing reasons, neither CI-gated, neither
yours.** `Hermes pytest` — an unpinned `mcp[cli]>=1.0.0` floor, path-filtered, locally
green (570), see `HERMES-MCP-FLOATING-DEP`, do not re-diagnose. Phase 0 `lint-smoke` in
`tests/scripts/test-acceptance.sh` — example-corpus debt deferred to the wholesale regen;
use `--skip-lint-smoke`.

**V15 (schedule→`workflow_run` chain) is still unconfirmed** — never a gate; V14 proved
the chain off a *dispatched* upstream only. `standards-drift` runs Mondays 09:00 UTC,
**first observable 2026-08-03 (tomorrow).** On or past that date, confirm a
`pin-currency-reader` run followed it with `event=workflow_run`, then delete this
paragraph. A failure there is a new bug, not a reopened plan.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`, 46 entries) and
`plans/HERMES-BACKLOG.md`. This is only the ordering a fresh session should use.
**Nothing below is blocked, and nothing is mid-flight.**

1. **[#417](https://github.com/vladm3105/aidoc-flow-framework/issues/417) — namespace the
   plugin's agent dispatch references.** 29 `subagent_type=` occurrences across 20 files,
   none scoped — but most are `subagent_type=<mapped agent>` *placeholders*, so the bare
   names live in the per-skill lens→agent mapping tables and
   `platforms/claude-code-plugin/README.md:215+` (`:213` is the table header). Mechanical,
   but **verify first that `subagent_type` accepts `plugin:agent`**; the docs confirm the
   scoped form for `--agent` and @-mention but do not state it for `subagent_type`. If it
   does not, this reopens as a rename of the definitions. This is the live half of `L7`,
   which closed on documentation only.
2. **Gates that stopped measuring — `PREPROD-B2-GATE-SCOPE` + `TAGGING-GATE-SUBSTRING-ONLY`
   (filed #429). One pass; same class.** (a) `tests/release/test_marketplace_gate.py:39`
   forbids `--dangerously-skip-permissions`, but PR 3 renamed the mechanism to
   `--allow-skip-permissions`, so the gate passes and measures nothing; `skill_dirs()` also
   scans `skills/` only, missing `commands/` and `agents/`. Conformance *does* cover the
   property, so this is gate quality, not exposure (**D-0074 §1**). (b) Four gates in
   `tests/conformance/platforms/test_plugin_release_metadata.py` assert only that a token
   appears *somewhere* in a doc. ⚠️ **They share the weakness but NOT the remedy** — the
   token sits in a table row (`docs/TAGGING.md`), a third table cell (`README.md`), a
   blockquote (`docs/PARITY.md`) and a prose line (`CLAUDE.md`). One regex will not do it;
   assuming otherwise turns green required checks red.
3. **`SDD-CORPUS-UNVERIFIED` — START WITH THE FOUNDER DECISION; it gates the plan.**
   Census in the `FRAMEWORK-TODO.md` entry. Two rules not there: **build the gate before
   touching content**, and this needs a `plans/` plan with the two-cycle gap review.
4. **[#412](https://github.com/vladm3105/aidoc-flow-framework/issues/412) — linting a
   single file reports every cross-document trace tag as a `TRACE-RES-001` ERROR.** Fix
   shape is the single-file gate `_check_forward_coverage` already carries
   (`tools/sdd_doc_lint/__init__.py:1972-1973`, documented at `:1965-1967`). ⚠️ An earlier
   handoff cited `:1961-1963` and was wrong — those are run-mode severity bullets.
   Re-derive a carried-forward line number before re-publishing it.
5. **[#423](https://github.com/vladm3105/aidoc-flow-framework/issues/423) — the
   `web-site` badge.** Two halves: repair `Pre-release v0.20.1` by hand in a `web-site` PR,
   and make a grep miss on that path **warn** instead of returning silently. Keep it
   non-fatal — the sibling is legitimately absent in CI — and do **not** make
   `replace_in_file` warn globally; most of its misses are the benign idempotent case.
6. **Watch [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351) —
   when canon ships its own reader, DELETE ours.** `.github/workflows/pin-currency-reader.yml`
   plus `scripts/read-pin-currency-log.sh` and `scripts/reconcile-pin-currency-issue.sh`
   are an override, not a permanent local surface (plan R9). Nothing else says so.
7. **[#405](https://github.com/vladm3105/aidoc-flow-framework/issues/405) —
   `sync-version-refs.sh` rewrites historical "shipped in vX" claims.** Corrupted
   `docs/PARITY.md:65` on three consecutive bumps. **Did NOT fire on the `0.25.0` plugin
   bump** — verified line by line in the real tree. Still open for framework-spec bumps.
8. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** Outstanding is only
   the **fix shape** — #389's approach cannot be reused because this `prev` is load-bearing
   elsewhere; derive it from a fanout target nobody hand-edits (`docs/PARITY.md`).
9. **`doc-maintainer` — nothing to do; it is PAUSED** (`kill_switch: true`, #397), CI
   green. Resume requires `aidoc-flow-ci` #352 **AND** #353 — #353 alone is 15 of the 23
   failures. Census in D-0072. ⚠️ **Do not re-file the `high_risk_paths` / `allowed_paths`
   mismatch** — deliberate and documented; #396 recorded it as a bug and was wrong.
10. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`.
11. **Everything else** is in `FRAMEWORK-TODO.md` by tag. An entry under `## Open` with no
   `⏳ OPEN ON RESIDUAL` marker is genuinely open work (#403). Nothing there is blocking.

## Traps too fresh to have settled — not yet in `CLAUDE.md`

- **A documentation edit can disarm a gate, and it looks like an improvement.** A draft of
  #429 added a "these marks go stale" warning to `docs/TAGGING.md` that quoted the current
  tag. The gate guarding that file is a bare `assertIn`, so the new prose would have
  satisfied it on its own — letting a future bump ship with the inventory row missing.
  Caught before push only because the added sentence claimed "nothing in CI checks this
  paragraph" and that absence was verified rather than assumed. **Before adding text that
  contains a token some gate greps for, find the gate and read its assertion.**
- **A shared weakness does not imply a shared remedy.** Four gates had the identical bare-
  substring defect; the row-matching fix drafted for them was valid for exactly one,
  because the guarded token sits in a different structure in each file. A fix shape written
  once and prescribed for a class is a claim about every member of that class.
- **A review fold authors its own false claims, and the pass that produced the fold never
  catches them.** Measured again on #429: the fold of pass 1 introduced *two* new false
  statements — a fix shape valid for one of three gates, and a claim that a plan's
  `:343-345` "records the correction" when it was an unexecuted open instruction. Both were
  caught only by a second, independent pass over the folded diff. **Re-verify folded text
  against source, not against the findings list**, and treat a subagent's finding as a
  claim, never as a result.
- **A self-citation inside a file you are editing is invalid the moment you edit it.**
  `PLUGIN-PREPROD-001-PLAN.md` cites its own lines ~13 times. Two edits to it had to be
  made **line-count neutral** (874 → 874, verified against `git show HEAD:`) because a
  one-line drift moved `:389` off the row two other documents cite. **Check
  `wc -l` against `HEAD` before pushing any edit to a self-citing file.**
- **A document can name a channel, a control or a setting that does not exist, and nothing
  in CI will ever notice** — `SECURITY.md` pointed at private vulnerability reporting for
  months while it was disabled. **When a doc tells a reader to go somewhere, go there.**
  Two scanning knobs are still off — `SYNC-SECRET-SCANNING-KNOBS`, founder decision.
- **A perfect first-try mutation kill rate is the symptom, not the result.** Assert the
  unmutated baseline green *inside* the harness, with a control mutant that must die.
  Restore source from a saved copy each iteration, **never in a `finally`** (killing a
  hung mutant skips it), and verify `git diff --quiet <path>` before any trusted run.
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
| `PLUGIN-PREPROD-001-PLAN.md`'s PR 5 section as a guide to what PR 5 did | **Six of its claims were falsified by its own implementation** and are annotated in place. Read the annotations, not the original text |
| Any handoff or plan text saying M6 / the tag / the Release is open or pending | **Dead.** The cut happened 2026-08-02 and every surface is reconciled. `DECISIONS.md` D-0074 §4 still *reads* that way by design — see its rider |

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen. IPLAN ↔ iplanic integration is
deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`). All **17** `aidoc-flow-ci` call sites across
16 files are pinned `@ci/v2.16.0` — re-count with
`grep -rho 'aidoc-flow-ci/\.github/workflows/[^@]*@ci/v[0-9.]*' .github/workflows/ | wc -l`.
