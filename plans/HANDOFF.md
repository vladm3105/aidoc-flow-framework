# Session Handoff

**Purpose:** everything a *fresh* session needs to start work here with zero prior
context — current state, and what to do next. Nothing else.

**This file is regenerated, not appended.** Status that is appended rots, and a wrong
cause left standing gets re-read as fact by every later session. **Git is the archive** —
prior states live in `git log -- plans/HANDOFF.md`. Do not restore them here.

## What lives where — do not duplicate across these

| Surface | Holds | Lifespan |
|---|---|---|
| `CHANGELOG.md` | what shipped | permanent, append |
| `plans/DECISIONS.md` | why a non-obvious choice was made (`D-NNNN`) | permanent, append |
| `framework/governance/DECISIONS.md` | spec-tier decisions (`GD-NN`) | permanent, append |
| `plans/FRAMEWORK-TODO.md` | **the** open-task queue | until closed |
| `plans/HERMES-BACKLOG.md` | Hermes-parity queue | until closed |
| `CLAUDE.md` | the durable working agreement **and every settled trap**, auto-loaded every session | permanent |
| **this file** | current state + next tasks + traps too fresh to have settled | **rewritten each merge** |

**Traps live in `CLAUDE.md` § "Durable traps — do not re-derive these", not here.**
That section owns merging/CI mechanics, reading CI output, local hooks and tooling, the
acceptance harness, writing to GitHub from a script, and the process lessons — plus, in
§ "Unified CI", the `--repin` vs `--update` distinction, `LITELLM_BASE_URL`,
`secret-scan`'s history scope, `GITHUB_TOKEN`-triggered events, check-run rollup
semantics, the runner split, and the `#329` concurrency allowlist by *shape*. A trap
recorded there is **never** repeated here; this file carries only what has not settled
yet, and graduates it once it has.

## Where we are — 2026-07-31

Framework spec `0.40.0`, Claude Code plugin `0.24.0`, Hermes `0.12.0` — **no version
stream moved today**. **Open PRs: 0. Open issues: 2** —
[#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385) and
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386), both unchanged.

**Last merge: [#403](https://github.com/vladm3105/aidoc-flow-framework/pull/403), squash
`b44279a1` — the `FRAMEWORK-TODO.md` status-hygiene sweep.** The queue is now
trustworthy in both directions and states its own convention. *(This refresh ships as
its own follow-up PR, so `git log` shows one commit after `b44279a1` touching only this
file. That is expected, not a missed merge.)*

**`plans/FRAMEWORK-TODO.md` is a reliable input again — Open 52 → 30, Closed 37 → 60,
90 entries throughout.** Three defects, not the two the last handoff named: 7 `✅ CLOSED`
entries sat under `## Open`; 22 entries under `## Closed` carried no heading marker at
all; and **22 more declared their state only in a body `*Status:*` line** — the form
nobody had named. That third form does not pattern-match (`SHIPPED`, `CORE SHIPPED`,
`CORE SUBSUMED`, `DOC LEG ✅ SHIPPED, enforcement leg deferred`, `Closed by …`), and the
deferral that keeps an entry open is often a trailing clause on an otherwise
finished-looking line. Each was read in full: 16 closed, **6 carry live legs** and now
say so in the heading under a new `⏳ OPEN ON RESIDUAL (…)` marker. The file's
`> **Rules:**` block states the whole contract — read it before touching the queue;
do not re-derive it from here.

Also landed there: 18 `PR #TBD, merge SHA TBD` placeholders resolved (`CLEANUP-PR-A`…`-F`
= PRs #129/#131/#130/#133/#132/#135, non-sequential), and the new `[ci]`
`PIN-CURRENCY-READER-HAS-NO-READER` entry that the last session flagged as held by no
queue.

**`doc-maintainer` is PAUSED, and CI is green again.**
[#397](https://github.com/vladm3105/aidoc-flow-framework/pull/397) set
`kill_switch: true`. Verified in production, not assumed: the merge's own `push` run
succeeded with `doc-maintainer kill_switch=true; exiting cleanly (no LLM cost incurred)`.
Only one other `push` run had gone green since adoption, and that one passed by
proposing nothing; this is the first that is green *by design*. The caller, its config
and its conventions all stay in place; resume is a one-line flip.

It had 23 failures / 47 runs across four independent upstream defects; the census lives
in D-0072 and in `.github/doc-maintainer-conventions.md`, kept current for the resume.

**Resume requires ci#352 AND ci#353** — #353 alone is 15 of the 23, so flipping on #352
alone returns a majority-red pilot. #352 is the smaller count and still the blocker for
*graduation*: no plan containing a low-risk edit can complete a dry run, which is the
path a dry-run pilot exists to validate.

**V15 (schedule→`workflow_run` chain) is still unconfirmed** — it was never a gate; V14
proved the chain off a *dispatched* upstream only. `standards-drift` runs Mondays at
09:00 UTC, first observable **2026-08-03**. **If today is on or past that date**, read
the latest `standards-drift` run and check a `pin-currency-reader` run followed it with
`event=workflow_run`, then delete this paragraph. A failure there is a new bug against
the merged workflow, not a reopening of the plan.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and
`plans/HERMES-BACKLOG.md`. This is only the ordering a fresh session should use.

1. **Watch [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351) —
   when canon ships its own reader, DELETE ours.** `.github/workflows/pin-currency-reader.yml`
   plus `scripts/read-pin-currency-log.sh` and `scripts/reconcile-pin-currency-issue.sh`
   are the "add a custom workflow" override mode, not a permanent local surface (plan
   R9). Nothing else in a live queue says so — the statement otherwise survives only
   inside the merged plan, which is why it is here.
2. **`doc-maintainer` — nothing to do here; it is paused and waiting on upstream.**
   Watch `aidoc-flow-ci` #352 and #353. When **both** ship in a released `ci/vX.Y.Z`:
   re-pin this caller, flip `kill_switch` → `false` in `.github/doc-maintainer.json`,
   and watch the next few `push` runs. Do **not** flip on #352 alone.

   ⚠️ **Do not re-file the `high_risk_paths` / `allowed_paths` mismatch as a defect.**
   It is deliberate, inert, and documented in the config itself; #396 recorded it as a
   bug and was wrong. D-0072 point 2 explains why the error message manufactures that
   misreading.

   `gh secret list` shows `LITELLM_BASE_URL` **and** `LITELLM_DOC_API_KEY` present here;
   only `AIDOC_FLOW_BOT_ID` / `AIDOC_FLOW_BOT_KEY` are absent, and those are **live-mode
   only**. Verify with `gh secret list` before repeating any secrets claim.
3. **[#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385) — the `#342`
   regression guard scans less than it claims.**
   `tests/conformance/platforms/test_no_inprompt_hashing.py:99`/`:103` use
   `glob("doc-*/SKILL.md")` and a non-recursive `glob("*.md")`, so **41 of 52** plugin
   SKILLs and **36 of 39** Hermes references are scanned. The 3 unscanned Hermes files
   are all of `references/batch-brd-processing/`, and
   `batch-remediation-script.md:24` still computes element IDs with its own
   `hashlib.sha256` routine that diverges from the normative transform on four points.
   The 11 unscanned plugin SKILLs are clean today — that half is latent. The guard's own
   docstring (`:92`) forbids narrowing coverage by glob, which is what happened. Fix is
   `rglob` both + point the script at `rehash --compute`; the issue carries the census
   command. **A green run of this guard is not evidence that no surface hashes.**
4. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** The mechanism
   and the hand-edit hazard are in `CLAUDE.md` § "Durable traps → Local hooks and
   tooling"; do not restate them here. Outstanding here is only the **fix shape**:
   #389 fixed the plugin and Hermes tokens by detecting each from `CLAUDE.md` and
   writing only `CLAUDE.md`, but this one cannot take that shape unchanged, because
   its `prev` is load-bearing elsewhere. Derive the gating `prev` from a fanout target
   nobody hand-edits (`docs/PARITY.md`), and give `CLAUDE.md` its own block.
5. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
6. **Everything else** is in `FRAMEWORK-TODO.md` by tag (`[ci]`, `[lint]`,
   `[template]`, `[harness]`, `[example-corpus]`, `[docs]`, `[skill]`, `[sync]`),
   including the D54 and Engramory consumer-feedback batches. **30 open entries, and
   the section now means what it says** (#403) — an entry under `## Open` with no
   `⏳ OPEN ON RESIDUAL` marker is genuinely open work. Nothing there is blocking.

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen rather than fixed in place.
IPLAN ↔ iplanic integration is deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`).

## Stale advice — a fresh session will find these referenced, and they are FIXED

Older plans, TODO entries and commit messages still describe these as live. They are
not. Every row below still has at least one live source in the repo; rows whose only
remaining source was this file have been deleted rather than carried forward.

| Stale claim | Reality |
|---|---|
| "`--admin` is required on every PR" (the `ai-review` self-cancel, `aidoc-flow-ci#322`) | **Fixed at `ci/v2.16.0`.** #378, #380, #392 and #394 all reached mergeable with no `--admin` |
| "Branch protection requires the phantom `Lint / format / security hooks`, so every PR is BLOCKED" | **Fixed.** The six required contexts, read from the API on 2026-07-30, are `call / Lint / format / security hooks`, `call / composition`, `call / ai-review`, `call / verify`, `Framework + platform conformance`, `Acceptance tier (deterministic)`. `call / trust` is **not** required |
| `AIDOC-CI-COMPOSITION-CHECK-PRHEAD` — "`call / composition` is structurally unsatisfiable on a PR head" | **Stale.** composition reports success on PR heads. A reviewer once read this entry as proof that required checks gate nothing here, and it nearly killed a correct plan |
| "the acceptance deterministic tier has 3 pre-existing failures on `main`" | **Fixed** (#365, #371/#372). 0 failures / 64, and the tier is now a **required** context |
| `NO-PIN-CURRENCY-CHECK` — "this repo runs `check-pin-currency.sh` nowhere" | **Retracted, it was false** — the check runs on every weekly `standards-drift`. The generalised lesson is in `CLAUDE.md` § "Durable traps → Process" |
| `PIN-CURRENCY-NO-READER` — "the fix is a workflow that **runs the script** and opens an issue" | **Superseded and now SHIPPED** (#392). Running the script would be the second detector the same entry forbids; the reader consumes the completed run's **log** |
| `PIN-CURRENCY-READER-PLAN.md:465`/`:469` — "a live `clean` check is deliberately absent … the `clean` path is verified only by V4's stub" | **Overtaken by events.** Canon `main` and every caller here are both `ci/v2.16.0`, so a live run reports `clean` — V14 exercised close-on-clean for real. This is the stale row most likely to be hit, because item 1 above sends the next session into that same plan |
| `FRAMEWORK-TODO.md`'s closed `HANDOFF-OVER-SIZE` entry — "the check-run annotation-cap trap **stays** in the handoff, because `PIN-CURRENCY-READER-PLAN.md` PR 4 is chartered to propagate it" | **Done — PR 4 is the merge described above.** The trap now lives in `CLAUDE.md` § "Durable traps → Reading CI output" and is gone from here. That TODO line is history inside a `✅ CLOSED` entry and was deliberately left unedited: correcting it would have made a fourth doc surface against Rule 1's cap of three |
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`** (#387/#390). The glob is a **suffix** — `plans/*-PLAN.md`. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |
