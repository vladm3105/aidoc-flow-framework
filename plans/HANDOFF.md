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

## Where we are — 2026-07-30

Framework spec `0.40.0`, Claude Code plugin `0.24.0`, Hermes `0.12.0` — **no version
stream moved today**. **Open PRs: 0. Open issues: 2** —
[#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385) and
[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386), both unchanged.

**`doc-maintainer` is PAUSED, and CI is green again.**
[#397](https://github.com/vladm3105/aidoc-flow-framework/pull/397) set
`kill_switch: true`. Verified in production, not assumed: the merge's own `push` run
succeeded with `doc-maintainer kill_switch=true; exiting cleanly (no LLM cost incurred)`.
Only one other `push` run had gone green since adoption, and that one passed by
proposing nothing; this is the first that is green *by design*. The caller, its config
and its conventions all stay in place; resume is a one-line flip.

It had 23 failures / 47 runs across **four** independent upstream defects — not the two
previously recorded, and **not** the config mismatch this repo was blamed for (retracted;
see Next tasks item 2 and **D-0072 §2**). The full census lives in D-0072 and in
`.github/doc-maintainer-conventions.md`, which is kept current for the resume; do not
copy it here.

**Resume requires ci#352 AND ci#353** — #353 alone is 15 of the 23, so flipping on #352
alone returns a majority-red pilot. #352 is the smaller count and still the blocker for
*graduation*: no plan containing a low-risk edit can complete a dry run, which is the
path a dry-run pilot exists to validate.

**Pin-currency reader (#392/#394) shipped earlier; V10–V14 all passed, so PR 3 is
unblocked.** **V15 (schedule→`workflow_run` chain) is still unconfirmed** — it was never
a gate; V14 proved the chain off a *dispatched* upstream. Whoever sees the first Monday
`standards-drift` run should check a `pin-currency-reader` run followed it, then delete
this paragraph.

## Next tasks — prioritized

The full queue is `plans/FRAMEWORK-TODO.md` (`## Open`) and
`plans/HERMES-BACKLOG.md`. This is only the ordering a fresh session should use.

1. **`PIN-CURRENCY-NO-READER` — PR 3, then PR 4. Both are governance PRs; the founder
   merges.** The gate they waited on has passed.
   - **PR 3** = `plans/DECISIONS.md` (a new `D-00NN`: why the log and not annotations,
     why the reader fails loudly), `plans/FRAMEWORK-TODO.md` (the `PIN-CURRENCY-NO-READER`
     entry → `## Closed` with the merge ref), and this file. **That is Rule 1's cap of
     three.** ⚠️ CI's `call / ai-review` independently demands a `CHANGELOG.md`
     `[Unreleased]` entry for substantive changes; if it demands one here, that is a
     **fourth** surface and the fix is to move this file out into its own follow-up,
     **not** to exceed the cap.
   - **PR 4** = `CLAUDE.md` + the plan's Status → `IMPLEMENTED`. **Its chartered scope
     is unchanged** — the plan's §PR-sequencing table names two `CLAUDE.md` edits and
     both are still outstanding: the annotation-cap trap at the granularity M1
     supports (held in § "Unsettled trap" below precisely so PR 4 propagates it), and
     the concurrency inventory's **fourth** shape — `cancel-in-progress: false` under
     a fixed group, which `pin-currency-reader.yml` introduced. What is **no longer**
     PR 4's to carry is the "sixteen call sites" count: the previous handoff proposed
     folding that in here, and HANDOFF-OVER-SIZE landed it instead — `CLAUDE.md`
     § "Unified CI" now says **seventeen across sixteen** and carries the two
     re-count commands beside the figure.
   - The plan's §PR sequencing is the contract; read it rather than this summary.
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
3. **`FRAMEWORK-TODO.md` hygiene — bigger than "pick a convention".** The queue is
   unreliable in *two* directions: entries marked `✅ CLOSED` sit under `## Open` (so it
   **overstates** what is open), and `## Closed` holds unmarked entries that read as
   live backlog — `[gate] Component-decomposition gate missing between PRD and ADR`,
   `[harness] Cascade harness lacks --skip-lint-smoke flag`, `[template] IPLAN
   sub-types: code-build vs deploy` — so it also **hides** open work, which is worse.
   Scope the sweep to both, and pick one convention stated at the top of the file.

   **Re-run these rather than trusting any count written down** — this figure has gone
   stale twice inside the very text documenting it, because the file is append-at-top:

   ```sh
   awk '/^## Open/{o=1} /^## Closed/{o=0} o&&/✅ CLOSED/{n++} END{print n}' plans/FRAMEWORK-TODO.md
   awk '/^## Closed/{c=1} c&&/^### /{e++} c&&/✅ CLOSED/{m++} END{print e, m}' plans/FRAMEWORK-TODO.md
   ```

4. **[#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385) — the `#342`
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
5. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** The mechanism
   and the hand-edit hazard are in `CLAUDE.md` § "Durable traps → Local hooks and
   tooling"; do not restate them here. Outstanding here is only the **fix shape**:
   #389 fixed the plugin and Hermes tokens by detecting each from `CLAUDE.md` and
   writing only `CLAUDE.md`, but this one cannot take that shape unchanged, because
   its `prev` is load-bearing elsewhere. Derive the gating `prev` from a fanout target
   nobody hand-edits (`docs/PARITY.md`), and give `CLAUDE.md` its own block.
6. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
7. **Everything else** is in `FRAMEWORK-TODO.md` by tag (`[ci]`, `[lint]`,
   `[template]`, `[harness]`, `[example-corpus]`, `[docs]`, `[skill]`, `[sync]`),
   including the D54 and Engramory consumer-feedback batches. Nothing there is
   blocking.

**Standing:** the example corpus is regenerated wholesale after framework changes, so
corpus-remediation findings are deferred to that regen rather than fixed in place.
IPLAN ↔ iplanic integration is deferred (`plans/IPLAN-IPLANIC-DEFERRED.md`).

## Unsettled trap — not yet in `CLAUDE.md`

One item is deliberately held here because PR 4 above is chartered to propagate it.
Delete this whole section when PR 4 lands.

- **The check-run annotations API silently truncates at 10 warnings, keeping the
  earliest.** Measured on check-run `89950624082`: the job emitted **22** `##[warning]`
  lines and the API returns **10** — dropping all ten `pin-currency:` lines, because
  they are emitted at the drift script's tail. So **`gh api …/annotations` is not a
  substitute for the log** when the thing you want is emitted late.
  - **The response length is 11, not 10** — 10 `warning` plus 1 `notice`. Verify with
    `--jq 'group_by(.annotation_level)|map({(.[0].annotation_level):length})|add'`, not
    `length`, or this trap reads as false and gets discarded.
  - That surviving `notice` **is** evidence the cap is applied **per annotation level**:
    a full 10 warnings did not crowd it out. What stays unattributable from this run is
    per-step vs per-job vs per-run — the whole script is one `run:` step, so those three
    are indistinguishable here. PR 4 may claim per-level, not per-step.

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
| `plans/PLAN-*.md` as the governance-PR plan glob (`CHANGELOG.md`, `CI-CANON-V2.16-MIGRATION-PLAN.md:468`/`:784`) | **Fixed in `CLAUDE.md`** (#387/#390). The glob is a **suffix** — `plans/*-PLAN.md`. Merged plans and the CHANGELOG keep the old string as history; `CLAUDE.md` is the live rule |
