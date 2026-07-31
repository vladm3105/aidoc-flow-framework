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

**Last merge: [#401](https://github.com/vladm3105/aidoc-flow-framework/pull/401) — PR 3
of `PIN-CURRENCY-NO-READER`, the close-out.** It recorded **D-0073** (rationale lives
there; not restated here) and moved the TODO entry to `## Closed` against the merges
that shipped the work, `d3d7f845` (#392) and `c77ff3f4` (#394). *(This file is written
inside the PR it describes, so it carries the PR number and no squash SHA — that SHA
does not exist until merge. `git log -1 -- plans/HANDOFF.md` gives it.)*

**Only PR 4 of that plan remains** — see Next tasks item 1. It is the sole reason the
`## Unsettled trap` section below still exists.

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

1. **`PIN-CURRENCY-NO-READER` — PR 4, the last of four. Governance PR; the founder
   merges.** Two surfaces, both still outstanding:
   - **`CLAUDE.md`** — (a) the annotation-cap trap, stated at the granularity M1
     actually supports, which is why § "Unsettled trap" below still exists; and (b) the
     concurrency inventory's **fourth** shape — `cancel-in-progress: false` under a
     fixed group, which `pin-currency-reader.yml` introduced. Today § "Unified CI"
     describes three shapes (absent block / `#329` allowlist / bare `true`) and calls
     it a three-way question; PR 4 makes it four. The rationale is in **D-0073 §7**,
     including the sentence it must *not* be written as.
   - **The plan's Status → `IMPLEMENTED`** (it reads `IN PROGRESS`, describing PR 2 as
     open — stale on both counts).
   - What is **not** PR 4's to carry: the call-site count (landed by
     `HANDOFF-OVER-SIZE`; `CLAUDE.md` says **seventeen across sixteen** with its
     re-count commands beside it) and any D-0073 content beyond the trap — the decision
     log already holds it.
   - **Also PR 4's, and easy to miss:** the plan's own `## Docs to update` boxes for
     PR 3 stay unticked after this merge (ticking them here would have been a fourth
     surface), and its **V1 row still says 17 tests** where the suite now runs 18 —
     `#394`'s regression guard. PR 4 is already editing that file, so both cost
     nothing.
   - The plan's §PR sequencing is the contract; read it rather than this summary.
2. **Watch [aidoc-flow-ci#351](https://github.com/vladm3105/aidoc-flow-ci/issues/351) —
   when canon ships its own reader, DELETE ours.** `.github/workflows/pin-currency-reader.yml`
   plus `scripts/read-pin-currency-log.sh` and `scripts/reconcile-pin-currency-issue.sh`
   are the "add a custom workflow" override mode, not a permanent local surface (plan
   R9). Nothing else in a live queue says so — the statement otherwise survives only
   inside the merged plan, which is why it is here.
3. **`doc-maintainer` — nothing to do here; it is paused and waiting on upstream.**
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
4. **`FRAMEWORK-TODO.md` hygiene — bigger than "pick a convention".** The queue is
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

5. **[#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385) — the `#342`
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
6. **[#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386) — the
   framework-spec token gates five files on `CLAUDE.md`'s own state.** The mechanism
   and the hand-edit hazard are in `CLAUDE.md` § "Durable traps → Local hooks and
   tooling"; do not restate them here. Outstanding here is only the **fix shape**:
   #389 fixed the plugin and Hermes tokens by detecting each from `CLAUDE.md` and
   writing only `CLAUDE.md`, but this one cannot take that shape unchanged, because
   its `prev` is load-bearing elsewhere. Derive the gating `prev` from a fanout target
   nobody hand-edits (`docs/PARITY.md`), and give `CLAUDE.md` its own block.
7. **Hermes parity — the residual arc.** `plans/HERMES-BACKLOG.md`: remaining
   plugin-vs-Hermes deltas plus quality-loop Phase 2 (cross-invocation resume / G-R1,
   the parallel-review global lock).
8. **Everything else** is in `FRAMEWORK-TODO.md` by tag (`[ci]`, `[lint]`,
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
