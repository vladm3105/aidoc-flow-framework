# PIN-CURRENCY-NO-READER Plan — give the existing pin-currency output a reader

| Field          | Value                                                                  |
| -------------- | ---------------------------------------------------------------------- |
| Task           | `PIN-CURRENCY-NO-READER` (`plans/FRAMEWORK-TODO.md`, `[ci]`)            |
| Type           | feature                                                                |
| Status         | IN PROGRESS — 2026-07-30. PR 1 merged (plan); **PR 2 open** (scripts, workflow, fixtures, tests, registration shim). PR 3 gated on V10–V14; PR 4 last. Reviewed over 5 passes, zero load-bearing findings outstanding |
| Depends on     | D-0070 (`@ci/v2.16.0` pins), D-0071 (CANON-PARITY-001)                 |
| Feeds          | an upstream feature request on `aidoc-flow-ci`                          |
| Version impact | none — no version stream moves (local CI surface only)                  |

## Objective

The weekly `standards-drift` run already detects stale `@ci/v*` pins correctly and
names the remedy. Nothing reads it. This plan gives that **existing** output a
destination — a single auto-maintained tracking issue — without adding a second
detector, and files the generalizable half upstream.

Canon is not silent on this: `standards-drift-self.yml` runs a **fleet** pin audit
against this repo every Monday (C13) and discards the verdict with `|| true`. So the
gap is not "no audit exists" but "**no audit anywhere has a reader**" — on either side.
That strengthens the upstream ask and is why Task 3 is not optional politeness.

## Scope

**In:**

- Two parse/reconcile scripts under `scripts/`, unit-tested against checked-in
  fixtures, plus the thin `workflow_run` wrapper that calls them.
- One auto-maintained tracking issue: created, edited in place, reopened, closed when clean.
- An upstream issue on `vladm3105/aidoc-flow-ci` carrying the five measured defects.
- TODO closure + doc-of-record updates, **split across sequential PRs** per Rule 1
  (see §PR sequencing).

**Out of scope (deferred):**

- A second pin-currency detector, or a pre-commit hook variant — rejected in the TODO
  entry, and M1/M2 strengthen the rejection.
- `strict: true` on the weekly run — C7/C8: it cannot go red for stale pins at all.
- A general reader for the **drift** and **fetch/scope** dimensions. The 8 expected
  drift warnings are a founder settings step, not a queue item; the issue body carries
  their counts as one line and does no per-control triage.
- Parsing canon's **fleet** output format (C13) — different format (C14), different
  repo, different owner. The local parser is in-repo-format-only and says so.
- Fixing the SHA-pin false green (C15) — it is canon's defect and this repo pins by
  tag, so it cannot bite here today. Filed upstream, not worked around locally.

## Approach / Design

### What the measurements changed about the TODO entry's assumptions

The TODO entry's fix shape said "a small local workflow that **runs the script** and
opens or updates a single tracking issue." Running the script locally would have been
the second detector the same entry forbids. So the reader must consume the run that
already happened — and only one of four candidate input surfaces carries the signal:

| Candidate input surface | Verdict |
| --- | --- |
| Reusable job `outputs:` | **Does not exist.** Canon's reusable declares `inputs:` only (C2), so a caller receives nothing |
| Check-run annotations API | **Structurally loses the signal.** Capped at 10 warnings; the run emitted 22, and 0 of the 10 stale-pin warnings survived (M1) |
| `$GITHUB_STEP_SUMMARY` | **Never written** — no such call anywhere in the drift script (C6) |
| The run **log** | **Complete.** All 10 stale-pin lines present, plus the tail count (M1) |

Reading the log is not a preference — it is the only surface carrying the data. The
plan's upstream half asks canon to change that.

### Chosen shape

1. **`scripts/read-pin-currency-log.sh`** — log path in, `GITHUB_OUTPUT`-style
   key/values out (`verdict`, `stale_count`, `canon`, `stale_files`, `drift_summary`).
   No network, no GitHub context, so it is unit-testable. **Four verdicts:**

   **`skipped` is defined by the absence of a *verdict* line, not by the absence of
   `pin-currency:`** — an earlier draft used the latter and hard-failed on a real,
   benign log shape (C28).

   **`skipped` additionally requires positive evidence that the drift script ran**, and
   the order of checks is fixed: the `could not resolve canon VERSION` marker is tested
   **before** the no-verdict-line fallback, so `unresolved` is never swallowed by
   `skipped` (whose definition it would otherwise satisfy). Positive evidence is canon's
   summary line (C39) or a `stop_uncheckable` warning (C40) — canon always emits one or
   the other, and every `stop_uncheckable` path emits both its warning and a coverage
   line. **Grep the common prefix `check-standards-drift:` rather than either full
   marker:** all three shapes carry it, including the bash-4 preflight bail that predates
   both named markers, so one substring closes every completed-run path for free. The
   requirement applies to `unresolved` as well as `skipped` — a genuine `unresolved` log
   always carries the summary line, since the pin script exits 0 and the drift script runs
   to completion, so extending it costs nothing and removes the last case where a
   truncated log could impersonate a verdict. A log with **no** `check-standards-drift:`
   line is truncated, empty, or from the wrong run, and exits non-zero.

   Without this marker the multi-state expansion would have quietly defeated R3: absence
   of signal used to hard-fail, and would otherwise have parsed as a benign `skipped`.

   | `verdict` | Trigger | Reader behavior |
   | --- | --- | --- |
   | `stale` | `N stale pin(s)` with N > 0 **and** a `canon` token matching `^ci/v[0-9]+\.[0-9]+\.[0-9]+$` | open/edit/reopen the issue |
   | `clean` | `all pins current ✅` **and** a well-formed `canon` token | close the issue if open |
   | `unresolved` | `could not resolve canon VERSION` (C28) — canon's `curl` of `main`'s `VERSION` failed; the script exits 0 before it ever audits | exit 0, stamp "last verified" (R11), do **not** touch open/closed state |
   | `skipped` | no verdict line at all: the C12 `::notice::` skip, or `stop_uncheckable` exiting 0 before the tail (C11) | same as `unresolved` |

   Anything else — truncated, or a verdict line whose `canon` token is malformed — exits
   **non-zero**. The token check is load-bearing, not defensive tidiness: if the `curl`
   returns an error page rather than failing, `ver_cmp` compares non-numeric fields,
   every comparison falls through to `0`, and the script prints **`all pins current ✅`**
   (C29). A parser that trusted that string would close the tracking issue on a
   transient. This is the fifth defect Task 3 files upstream.
2. **`scripts/reconcile-pin-currency-issue.sh`** — takes the parse output, reconciles
   exactly one issue. This repo has **no existing `gh issue create/list/edit/close`
   precedent in any workflow or script**, so this logic is new and gets the same
   treatment as the parse rather than living inline in YAML.

   **It takes its `gh` binary from `GH="${GH:-gh}"`, adopting canon's own injection
   point (C30).** This is what makes `--dry-run` real: the test substitutes a stub that
   emits a canned `gh issue list` response, so create-vs-edit-vs-reopen is driven by a
   fixture rather than by a live authenticated read. Without it the test needs `gh`,
   auth and network — and because the suite it registers into runs on **every commit**
   (C31), that would fail an offline contributor's commit.
3. **`.github/workflows/pin-currency-reader.yml`** — `workflow_run` on
   `standards-drift` completion (local precedent C9), plus `workflow_dispatch` with a
   `run_id` input. Downloads the log **with retry** (R7), runs the two scripts. The
   job's `if:` must be the precedent's **full** form — `github.event_name ==
   'workflow_dispatch' || github.event.workflow_run.conclusion == 'success'` (C10) —
   because on a dispatch run `github.event.workflow_run.conclusion` is empty, so a
   conclusion-only filter skips the job, and a skipped job is green: V10–V13 would report
   "no issue created" against a passing run.
4. **Upstream issue** on `aidoc-flow-ci` — five defects: M1 (annotation cap makes
   tail-emitted warnings unreachable), C6 (no step summary), C7/C8 (`strict` cannot
   fire for stale pins), C15 (in-repo mode false-greens a SHA-pinned caller while the
   fleet path handles it — two paths in one script disagree), and C29 (an unvalidated
   canon token turns a `curl` hiccup into `all pins current ✅`). Proposed fix: write the
   verdict to `$GITHUB_STEP_SUMMARY`, expose `stale_pins` as a reusable `output`, and
   validate the resolved canon token before comparing.

**Why extract both halves.** `workflow_run` and `workflow_dispatch` both require the
file on the **default branch**, so nothing end-to-end runs on the PR branch that
introduces it (R1). Extraction is what makes the load-bearing logic testable
pre-merge; the YAML that remains is a wrapper. This is the sole reason for the extra
files — the first draft extracted only the parse and left the branchier reconcile
inline, which was the wrong half to trust.

### Issue-reconciliation contract

- **Title (exact, the idempotence key):** `CI canon drift — stale @ci/v* pins`
- **Label:** `ci` — live-verified present (M3). Applied **non-fatally**: an unknown
  label makes `gh issue create` error, and this runs unattended.
- **Lookup must not go through the search index.** `gh issue list --search` is
  tokenized and eventually consistent, so a just-created issue can be invisible and
  the next run duplicates it. Use
  `gh issue list --state all --limit 200 --json number,title,state,body,author` and an
  **exact string compare in `jq`**. Do not filter on author as the primary key: if an
  author filter silently matches nothing, every run creates a new issue.
  - **`--limit 200` is load-bearing, not caution.** `gh issue list` defaults to 30 and
    this repo is past #382, so a tracking issue closed a while ago falls off the first
    page, the exact-title compare finds nothing, and the run **creates a duplicate** —
    defeating the reopen contract below.
  - **`body` is in the field list because the body is the only persistent store** of the
    prior verdict. The comment trigger compares the previous `stale_count` and stale set
    against the current one, so the body carries a **machine-readable block** — a fenced
    `pin-currency-state` region holding `verdict`, `stale_count`, `canon` and the sorted
    file list — that the reconcile parses. The human-facing content below it is free to
    change without affecting the comparison.
- **`--state all`, not `--state open`, and `stale` after a `clean` REOPENS.** Searching
  only open issues means the stale → clean → stale cycle creates a fresh issue each
  time, and C26/R5 make that cycle recur **once per canon release** — so "one tracking
  issue" would have become one per release. Reopen is the specified behavior; create
  only when no issue with that title has ever existed.
- Body carries: canon tag, stale files with current pins, the `--repin` remedy (C16),
  the source run URL, the counts caveat (C17), a **`last verified <ISO>`** line (R11),
  and a generated-by note.
- **"Comment only on verdict change" is defined by the verdict and the stale set, not by
  the body.** The body embeds a run URL that changes weekly, so body-diffing would
  comment every run. Comment on exactly three transitions: `clean`/absent → `stale`
  **where that reopens an existing issue**, a change in `stale_count` or the stale file
  set while open, and `stale` → `clean` (closing). A re-run with an identical verdict and
  identical stale set edits the body silently. Without the middle transition, a count
  going 10 → 15 would be a silent edit with no notification, which defeats R8.
  - **Creating the issue is itself the notification, so a create emits no comment.**
    An issue opened and assigned already notifies; a comment restating the body it was
    created with is noise. A reopen is the case that needs one, because reopening alone
    is quiet. *(Clarified during PR 2 — the original "(opened or reopened)" read as
    requiring both, which V10 never asked for and V12 asked for only on reopen.)*
- **Assignee is set *after* creation, via `gh issue edit --add-assignee`** (R8) — a
  `github-actions[bot]` issue notifies only repo watchers, and `GITHUB_TOKEN` authorship
  fires no `issues`-triggered automation, so an assignee is needed. But
  `gh issue create --assignee <user>` **errors when the user is not assignable**, which
  would fail the create and its retry alike and produce no issue at all. Setting it
  post-creation makes that failure non-fatal by construction.
- **The label is applied non-fatally by retry, not by `|| true`.** `gh issue create
  --label ci … || true` would make the *whole* creation non-fatal — reintroducing the
  invisibility this plan closes. Required behavior: attempt with `--label ci`; on
  failure, retry the create **without** the label and emit a `::warning::`. The retry
  drops the label only; the assignee is not on the create call at all, per the row
  above. Verified by V13.
- **A stamp-only write must PRESERVE the `pin-currency-state` block verbatim.**
  Regenerating the body from a template on an `unresolved` or `skipped` week would clear
  the stored stale set, so the next identical `stale` reading would look like
  `clean → stale` and emit a spurious comment. Edit the `last verified` line in place;
  touch nothing else.
- **`--limit 200` ages out, and that is accepted.** The issue is created once and ages, so
  after ~200 newer issues the exact-title compare misses again. Revisit only if it does;
  raising the limit is a one-token change.
- **When a silent verdict finds no issue, the stamp is a no-op.** `skipped` and
  `unresolved` write the `last verified` line into an existing issue; if none exists —
  the normal steady state, since creation happens only on `stale` — there is no artifact
  to stamp, so the reconcile emits a `::notice::` and exits 0. R11's visibility claim is
  scoped to the case where the issue exists; it does not manufacture one.

### Measured evidence

Run `30257877863` (`standards-drift`, `schedule`, `success`, 2026-07-27T10:23:34Z);
commands re-run 2026-07-29.

**Version provenance — read this before trusting M1/M2 against today's behavior.**
That run executed the drift script at **`ci/v2.14.0`** (380 lines), not the
`ci/v2.16.0` copy (523 lines) this plan's ledger cites — the notice in its log reads
`adopted canon pin …@ci/v2.14.0`. The repo has since re-pinned to `v2.16.0` (D-0070),
so the next run executes the newer script. Two consequences, both checked:

- `emit_coverage` **does not exist** at `v2.14.0`, which is why the run's warning
  census closes exactly at 22 with no coverage line. At `v2.16.0` it exists at C18 and
  its non-clean branch emits a `::warning::` **after** pin-currency — so "pin-currency
  is emitted last" is true of the measured run and **will stop being true** from the
  next run on. It does not affect the design: the cap keeps the earliest warnings, so
  one more at the tail changes nothing about which survive.
- `check-pin-currency.sh` is **byte-identical** across the two tags
  (`diff <(git show ci/v2.14.0:sync/check-pin-currency.sh) sync/check-pin-currency.sh`
  → no output), so the pin-currency **line format** the parser targets is stable. True
  by measurement, not by design — re-check it when canon's minor moves.
- **But byte-identity of the pin script does not make the surrounding log identical**,
  and the first draft wrongly concluded it did. The pin script does not emit the log it
  sits in: at `v2.16.0` every log gains a trailing coverage `::warning::` after
  pin-currency (C18). So the stale fixture must be brought to **`v2.16.0` shape** —
  append that tail — or a second stale fixture added in that shape. Task 1 requires it.
- **A third consequence, unchecked and now scoped out.** The `8 drift, 4 fetch/scope`
  counts quoted in M2 are also `v2.14.0`-derived, and CI-0018 — the same change that
  introduced `emit_coverage` — reworked how absent admin-only `repo-settings` fields are
  reported, routing them through `warn_uncheckable` instead of `canon=false actual=null`
  (C32). This repo's own caller comment predicts **two** warnings, not eight (C33).
  Nothing in the design depends on the figure — the issue body carries whatever the
  parse yields — so this is not re-measured here, but no document produced by this plan
  may quote 8/4 as current behavior.

**M1 — the annotation cap drops the entire pin-currency signal.**

```sh
R=vladm3105/aidoc-flow-framework
gh api repos/$R/check-runs/89950624082/annotations \
  --jq 'group_by(.annotation_level)|map({(.[0].annotation_level): length})|add'
# → {"notice":1,"warning":10}
gh api repos/$R/check-runs/89950624082/annotations --jq '.[].message' | grep -c pin-currency
# → 0
gh run view 30257877863 -R $R --log > drift.log
grep -c '##\[warning\]' drift.log               # → 22
grep -c '##\[warning\]pin-currency:' drift.log  # → 10
grep -c '::warning::' drift.log                 # → 0   ← see R3
grep -o '##\[warning\][^ ]*' drift.log | sed 's/##\[warning\]//' | sort | uniq -c
# → 10 pin-currency:, 4 check-standards-drift:, 8 repo-settings.* — census closes at 22
```

Ten of 22 warnings reach the API; all ten pin-currency lines are absent. **The cap's
granularity is not attributable from this measurement** — the whole script is one
`run:` step in one job (C19), so per-step, per-job and per-run are indistinguishable
here, and "the surviving ten are the first ten emitted" is an inference from log order,
not a platform guarantee. The design needs only the measured fact: 10 surface, 0 of
them pin-currency. Do not state the granularity as fact upstream or in `CLAUDE.md`.

**M2 — the drift script's own summary line reports stale pins as zero.**

```sh
grep 'check-standards-drift: .* drift' drift.log
# → check-standards-drift: 8 drift, 4 fetch/scope error(s), 0 pin error(s) (warning-only)
```

`0 pin error(s)` on a run with 10 stale pins: `PIN_ERRORS` counts script *failures*,
and the script always exits 0 (C4, C7).

**M3 — the `ci` label exists.**

```sh
gh label list -R vladm3105/aidoc-flow-framework --limit 200 --json name --jq '.[].name' \
  | grep -iE '^(ci|area: ci|workflows)$'
# → ci
# → area: ci
# → workflows
```

Recorded with its output because an earlier review pass asserted from canon's template
and `.github/labeler.yml` that no such label existed. Those are not the live label set;
`gh label list` is.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `scripts/read-pin-currency-log.sh` | parse a `standards-drift` log → `stale` / `clean` / `unresolved` / `skipped` verdict |
| `scripts/reconcile-pin-currency-issue.sh` | reconcile the single tracking issue; `--dry-run` capable |
| `.github/workflows/pin-currency-reader.yml` | run both per completed `standards-drift` run |
| `tests/unit/fixtures/standards_drift_stale.log` | run `30257877863`, in **`v2.16.0` shape** (coverage tail appended) — 10 stale pins |
| `tests/unit/fixtures/standards_drift_clean.log` | `all pins current ✅` |
| `tests/unit/fixtures/standards_drift_skipped.log` | the C12 `::notice::` skip path |
| `tests/unit/fixtures/standards_drift_unresolved.log` | the C28 `could not resolve canon VERSION` path |
| `tests/unit/fixtures/gh_stub_issue_open.json` | canned `gh issue list` response driving the reconcile's edit/reopen branches (C30) |
| `tests/unit/test_pin_currency_reader.py` | `unittest` tests for both scripts, per the C20 subprocess precedent |
| `tests/conformance/test_repo_scripts.py` | the registration shim — see R6. `unittest discover -s tests/conformance` (C27) does **not** reach `tests/unit/`, so this module explicitly loads that test into the conformance suite |

**Every fixture keeps the raw `gh run view --log` line prefixes**
(`job⇥step⇥timestamp`). The excerpt quoted in the TODO entry is already stripped of
them (C34); checking in a stripped fixture would let V1/V3 pass on anchored patterns and
V10 fail post-merge on the real download — exactly the failure class R1 exists to prevent.
The garbage/truncated case is constructed inline in the test, not checked in.

### Modified

| Path | Change |
| ---- | ------ |
| `plans/FRAMEWORK-TODO.md`, `plans/DECISIONS.md`, `plans/HANDOFF.md`, `CHANGELOG.md`, `CLAUDE.md`, **this plan file** | see §PR sequencing — **not** all in one PR |

## PR sequencing — Rule 1 compliance

`CLAUDE.md` §"Governance PR discipline" Rule 1 caps a governance PR at **3 doc
surfaces**, and this work touches five plus the plan. It also requires the plan PR to
**merge before implementation starts** (§Development workflow item 2). Sequence:

| PR | Contents | Doc surfaces | Governance PR? |
| -- | -------- | :----------: | -------------- |
| 1 | this plan file only; merges **before** implementation starts | 1 | **yes** — a plan file. Rule 2 self-review applies; not auto-mergeable |
| 2 | the three new source files, five fixtures, the test, the registration shim, `CHANGELOG.md`, and this plan's Status → **`IN PROGRESS`** | 2 | **yes** — it touches the plan file |
| 3 | `plans/DECISIONS.md` (`D-00NN`), `plans/FRAMEWORK-TODO.md` (→ `## Closed`), `plans/HANDOFF.md`. **Opens only after V10–V14 pass** | 3 | **yes** — `DECISIONS.md` |
| 4 | `CLAUDE.md` (the annotation-cap trap at the granularity M1 supports, plus the concurrency inventory's **fourth** shape), and this plan's Status → **`IMPLEMENTED`** | 2 | **yes** — `CLAUDE.md`; founder-merge |

**All four are governance PRs and none is auto-mergeable.** An earlier draft named only
PR 4 as excluded. `CLAUDE.md` defines a governance PR as one touching `DECISIONS.md`,
plan files, `CLAUDE.md`, `.github/ai-review/` or `ai-review.yml` (C35), and the
auto-merge exception list is defined **by reference to that same list** (C36) — so PRs 1,
2 and 3 are excluded too. Each needs the Rule 2 adversarial self-review before push, and
none may be auto-merged on green.

**The Status transition needs two PRs, not one** — the repo requires a plan's status to
move in the same change as the state change, and forbids `IMPLEMENTED` on unverified
work. PR 2's end-to-end verification (V10–V15) runs only *after* it merges (R1), so PR 2
can set only `IN PROGRESS`; `IMPLEMENTED` (C37) belongs to PR 4, once V10–V14 have
actually passed. PR 3 cannot absorb it — it is already at Rule 1's cap of three surfaces.
PR 2 and PR 4 sit at two each.

**PR 3 is gated on verification, and V15 is not part of that gate.** The TODO entry must
not close on unverified work, so PR 3 opens only after **V10–V14** pass. V15 waits for
the first real Monday `schedule` run — up to seven days — so it is recorded as a
post-hoc observation, never as a merge gate.

**V15's record needs an owner, because every PR here may merge before the first Monday.**
It is the only confirmation of the `schedule` → `workflow_run` chain (R4), which has no
local precedent, so it does not get to evaporate: PR 3 lands a one-line
`pending — V15 (schedule→workflow_run chain) unconfirmed until the first Monday run`
entry in `HANDOFF.md`, and whoever observes the run clears that line. If V15 fails, it is
a new bug against the merged workflow, not a reopening of this plan.

The upstream `aidoc-flow-ci` issue (Task 3) is filed alongside PR 2 and referenced by
PR 3's DECISIONS entry.

**Own-repo tracker: stays TODO-only, deliberately.** The source entry says "Promote when
someone picks it up" (C38), and this plan is that pickup. It stays TODO-only anyway
because GOV-TODO-ISSUE-SPLIT's three-test bar is about gaps that outlive their capture:
here the entry closes on the same merge that ships the fix (PR 3), so an issue opened at
PR 1 would exist only to be closed days later. The *upstream* defects do meet the bar and
are filed as the `aidoc-flow-ci` issue. Recorded so the promote instruction is disposed
of rather than ignored.

## Implementation sequence

### Task 1: the parse script, test-first

- **Test-first:** write `tests/unit/test_pin_currency_reader.py` with six cases — stale
  (`stale_count=10`, `canon=ci/v2.15.0`, 10 files), clean, skipped, unresolved (all
  exit 0), truncated/garbage (**non-zero**), and a well-formed verdict line carrying a
  **malformed** `canon` token (**non-zero**, per C29). Confirm all six fail first.
- Use `unittest`, not `pytest`: the repo's suites are `unittest` and `pytest` is not a
  declared dependency (C21).
- Build the four log fixtures. Derive the stale one from the live log now, while run
  `30257877863` is inside the retention window (R2), **keeping the raw `--log` prefixes
  and appending the `v2.16.0` coverage tail** (C18, C34), then check it in so the test
  never reads the live run.
- **Register the test on a surface that runs** (R6) via `tests/conformance/test_repo_scripts.py`
  — `unittest discover` does not reach `tests/unit/` (C27), so the shim loads it
  explicitly.
- Write the script until the tests pass. Grep `##[warning]`, never `::warning::` (R3).

### Task 2: the reconcile script + the workflow

- `reconcile-pin-currency-issue.sh` with `GH="${GH:-gh}"` (C30) and `--dry-run`. Extend
  the test to assert the dry-run call sequence, driven by the `gh` stub, for: stale +
  no prior issue → **create**; stale + open issue, same set → **edit, no comment**;
  stale + open issue, changed count → **edit + comment**; stale + *closed* issue →
  **reopen + comment**; clean + open → **close + comment**; `skipped`/`unresolved` →
  last-verified stamp only, no state change.
- Also assert the label fallback: a stub whose labelled `create` fails must still
  produce an issue, via an unlabelled retry plus a `::warning::` (V13).
- Set the assignee as a **separate `gh issue edit --add-assignee` step after** the create,
  never as a `--assignee` flag on it, per the contract above; assert in the stub that a
  failing assignee step leaves the issue in place.
- Workflow: `permissions: { contents: read, actions: read, issues: write }`.
- `concurrency: { group: pin-currency-reader, cancel-in-progress: false }`. **Record the
  serialization rationale, not a cancellation one** — a named group with `false`
  serializes reader runs, which is what stops a `workflow_run` and a concurrent
  `workflow_dispatch` from both finding no open issue and creating duplicates. Do *not*
  write "nothing to cancel, so nothing to fix": that is verbatim the argument this repo
  uses to justify **no `concurrency:` block at all** (C22), so a future sweep reading it
  would delete the block and reintroduce the race. Put the reasoning in a comment inside
  the workflow file, per the same convention.
- Scope `workflow_run.workflows: ["standards-drift"]` so the reader never triggers on
  itself, and use the precedent's **full** `if:` including the `workflow_dispatch`
  clause (C10) — a conclusion-only filter green-skips every dispatch.
- Retry the log download (R7). Fail the job with `::error::` on a genuine fetch or
  parse failure — the reader is deliberately **not** warning-only, unlike the contract
  at C23; that property is what made the original signal invisible.

### Task 3: upstream issue on `aidoc-flow-ci`

- One issue, **five** defects: M1, C6, C7/C8, C15, C29.
- **Correct the "what is NOT broken" paragraph.** Detection is *not* wholly correct —
  there are **two** false-green paths in the same script: C15 (a SHA-pinned caller is
  invisible to the in-repo grep) and C29 (an unvalidated canon token turns a `curl`
  hiccup into `all pins current ✅`). State precisely that the *tag-pinned* in-repo
  detection path with a resolvable canon token is correct, and that both other paths
  report a green that is not one.
- Include blast radius (every adopter of the caller template; canon's own fleet job at
  C13 discards its verdict too), reproduction (M1/M2 with the version-provenance note),
  and what is genuinely not broken.
- Publish with `--body-file -`; read back with
  `gh issue view <N> -R vladm3105/aidoc-flow-ci --json body --jq '.body | length'`.

### Task 4: close out

- PR 3 and PR 4 per §PR sequencing.
- Each commit carries the phrase `pre_push_check.sh` greps —
  `Multi-agent self-review per OPS-0065 (<agents>): <verdict>` (C24). It satisfies the
  required `call / verify` **context**, but the grepped string is the OPS-0065 phrase;
  the context name is not itself the phrase.

## Verification

Split by what can run before the merge and what structurally cannot (R1).

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python3 -m unittest tests.unit.test_pin_currency_reader -v` | 17 pass: 8 parse cases (4 verdicts + 4 must-fail shapes) and 9 reconcile cases (six scenarios, the label fallback, and two asserting generated body content). Grew from 6 + 7 during PR 2's self-review — see §Review log Pass 6 | Task 1, Task 2 |
| V2 | `python3 -m unittest discover -s tests/conformance` before vs. after the registration shim | the test count **increases** by the new cases, proving the shim reaches `tests/unit/` | R6 |
| V3 | `bash scripts/read-pin-currency-log.sh tests/unit/fixtures/standards_drift_stale.log` | `verdict=stale`, `stale_count=10`, `canon=ci/v2.15.0` | Task 1 |
| V4 | `GH=<stub> bash scripts/reconcile-pin-currency-issue.sh --dry-run` across the six scenarios in Task 2 | the expected create / edit / edit+comment / reopen / close / stamp-only sequence; **zero** live API writes, and no `gh` or network needed | Task 2 |
| V5 | Run V1 with no network and no `gh` on `PATH` | passes — confirms C31's every-commit hook cannot break an offline contributor | C31 |
| V6 | `actionlint .github/workflows/pin-currency-reader.yml` — installed directly or via the pre-push hook | clean. **Not** via `pre-commit run --all-files`: this repo runs no actionlint hook (C25) | Task 2 |
| V7 | `pre-commit run --all-files` after any manual conflict resolution | clean | repo rule |
| V8 | `python3 -m unittest discover -s tests/conformance` | no new failures; count as raised by V2 | repo rule |
| V9 | `tests/acceptance/deterministic` | 0 failures / 64 — the baseline belongs to **this** suite, not to conformance | repo rule |
| V10 | **post-merge:** `gh workflow run pin-currency-reader.yml -f run_id=30257877863` | issue created; body lists 10 files, the `--repin` command, and a `last verified` line | Task 2 |
| V11 | **post-merge:** re-dispatch V10 unchanged | body edited in place; **no** duplicate issue, **no** new comment | idempotence |
| V12 | **post-merge:** close the issue by hand, then re-dispatch V10 | the **same** issue is reopened and commented — not a second issue | reopen contract |
| V13 | **post-merge:** dispatch once with the label deliberately misspelled in a scratch branch copy, or assert via the V4 stub | the issue is still created, unlabelled, with a `::warning::` | label fallback |
| V14 | **post-merge:** dispatch `standards-drift` and watch for a reader run created **by the `workflow_run` chain**, not by dispatch | a reader run appears with `event=workflow_run` | R4 |
| V15 | **post-merge:** first real Monday `schedule` run produces a reader run | confirms the schedule→`workflow_run` chain, which has no local precedent (C9/C10 both chain off `pull_request`) | R4 |
| V16 | Upstream issue body read-back | length > 0 | Task 3 |

**A live `clean` check is deliberately absent.** "Dispatch against an all-current run →
`clean`" is not under this repo's control: the drift script invokes the pin script with
no `--canon`, so `resolve_canon` falls through to canon **`main`**'s `VERSION` (C26). The
moment canon tags `ci/v2.17.0`, an all-`v2.16.0` repo reports every pin stale. That is
correct behavior, but the `clean` path is verified only by V4's stub until a canon
release aligns — and it is why the stale → clean → stale cycle recurs per canon release,
which is what forces the reopen contract rather than create-on-stale (R5).

## Docs to update

Per §PR sequencing, not in one PR.

- [x] `CHANGELOG.md` — entry *(PR 2)*
- [ ] `plans/DECISIONS.md` — `D-00NN`: why the log, why not annotations, why the reader
      fails loudly *(PR 3)*
- [ ] `plans/FRAMEWORK-TODO.md` — entry → `## Closed` with the merge ref *(PR 3)*
- [ ] `plans/HANDOFF.md` — regenerate volatile part; add the annotation-cap trap and the
      version-provenance trap *(PR 3)*
- [ ] `CLAUDE.md` — the annotation cap, stated at the granularity M1 actually
      supports, **and** the concurrency inventory's fourth shape *(PR 4, founder)*
- [ ] `ROADMAP.md` — not applicable (no milestone moves)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | `workflow_run` / `workflow_dispatch` need the file on the **default branch**, so nothing end-to-end runs pre-merge | certain | Extract both halves so the logic is unit- and dry-run-tested pre-merge (V1–V4); V10–V14 gate the close-out per §PR sequencing, and V15 is a non-gating post-hoc observation |
| R2 | Log retention expires run `30257877863`, breaking the fixture source | low, then permanent | Check the fixtures **in** during Task 1; no test reads the live run |
| R3 | A reader written for `::warning::` silently matches nothing — the downloaded log renders it `##[warning]` (measured: 0 vs 22) | high if unguarded | The garbage-input test asserts non-zero exit, so a zero-match parse fails loudly instead of reporting "0 stale" |
| R4 | The `schedule` → `workflow_run` chain is never exercised by V10–V13, which use dispatch; and no local precedent chains off a scheduled upstream | medium | V14 dispatches the upstream to exercise the real chain; V15 confirms on the first Monday run |
| R5 | Weekly issue churn — and a forced stale→clean→stale cycle once per canon release, via C26 | medium | Single fixed-title issue, looked up with `--state all` and **reopened** rather than recreated; comment only on the three defined transitions (V11, V12) |
| R11 | Every upstream failure mode is silent to the reader: `skipped`, `unresolved`, and a *failed* drift run all produce no signal — the same unwatched-surface invisibility this plan closes, one level up | medium | The reader stamps a **`last verified <ISO>`** line into the issue body on every reading, including the silent ones, so staleness of the *reader* is visible in the artifact it maintains. Escalation on N consecutive silent readings is explicitly deferred, not assumed away |
| R6 | `tests/unit/` is run by **no** hook and **no** workflow (C27), so a test placed there guards nothing after merge | certain if unaddressed | Task 1 registers the test on a surface that executes; V2 proves it appears in that suite's count |
| R7 | `gh run view --log` 404s while a just-completed run's log archive is still assembling — exactly when `workflow_run: completed` fires | medium | Bounded retry with backoff before declaring a fetch failure; without it the dominant failure mode is a red workflow on an unwatched surface — the same invisibility, inverted |
| R8 | A bot-authored issue notifies only watchers, and `GITHUB_TOKEN` authorship triggers no `issues` automation (`CLAUDE.md`) | medium | Set an explicit assignee; the objective is visibility, not just a record |
| R9 | Canon ships its own reader, making this local workflow redundant drift | medium | Task 3 files the request; the local file is the documented override mode and is deleted when canon's lands |
| R10 | Scope widening into a general drift reader, tempted by the 8 drift + 4 fetch/scope warnings | medium | Explicitly out of scope; the issue body carries counts as one line, no per-control triage |

## Claim ledger

Gate command — canon citations are cross-repo, prefixed `aidoc-flow-ci/`. The local
canon checkout is content-identical to `ci/v2.16.0` (`git diff --stat ci/v2.16.0 HEAD`
is empty), so these line numbers are valid at the pinned tag. **They are not valid for
the `v2.14.0` script the measured run executed** — see §"Version provenance".

```sh
python3 ~/.claude/skills/verified-planning/check_plan.py \
  --root /opt/data/aidoc-flow plans/PIN-CURRENCY-READER-PLAN.md
```

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| C1 | The local caller's **scheduled** path is unattended — weekly cron, no push/PR trigger; its `workflow_dispatch` path is attended and is the one V14 uses | `cron: '0 9 * * 1'` | `.github/workflows/standards-drift.yml:46` |
| C2 | Canon's reusable declares `inputs:` only and no `outputs:`, so a caller job cannot receive the counts | `workflow_call` | `aidoc-flow-ci/.github/workflows/standards-drift.yml:36` |
| C3 | The reusable's job token is `contents: read` — it could not open an issue even if it wanted to | `contents: read` | `aidoc-flow-ci/.github/workflows/standards-drift.yml:63` |
| C4 | `check-pin-currency.sh` always exits 0 | `exit 0` | `aidoc-flow-ci/sync/check-pin-currency.sh:103` |
| C5 | pin-currency runs at the **tail** of the drift script, after every settings/label check has emitted its warnings | `--- pin-currency (companion drift dimension) ---` | `aidoc-flow-ci/sync/check-standards-drift.sh:499` |
| C6 | The drift script writes nothing to `$GITHUB_STEP_SUMMARY` — verified by grep over all 523 lines **and** over the `check-pin-currency.sh` it fetches; the surface does not exist | `emit_coverage()` | `aidoc-flow-ci/sync/check-standards-drift.sh:90` |
| C7 | `PIN_ERRORS` increments only on a non-zero exit from the pin script — which C4 says never happens | `PIN_ERRORS=$((PIN_ERRORS + 1))` | `aidoc-flow-ci/sync/check-standards-drift.sh:507` |
| C8 | The `strict` gate sums `DRIFT + FETCH_ERRORS + PIN_ERRORS`, so stale pins are absent from the fail condition | `[ "$STRICT" -eq 0 ]` | `aidoc-flow-ci/sync/check-standards-drift.sh:522` |
| C9 | This repo already runs a `workflow_run`-triggered workflow scoped by workflow name | `workflow_run:` | `.github/workflows/composition.yml:19` |
| C10 | The local precedent filters on the upstream run's conclusion — the shape this plan adopts | `workflow_run` | `.github/workflows/auto-merge-ai-prs.yml:52` |
| C11 | `stop_uncheckable` can exit 0 in non-strict mode **before** the pin-currency tail runs, producing a successful drift run with no pin-currency line | `stop_uncheckable()` | `aidoc-flow-ci/sync/check-standards-drift.sh:115` |
| C12 | Canon emits a documented `::notice::` skip when the pin script is unavailable at the tag — a third verdict state, not a parse failure | `check-pin-currency.sh not available at` | `aidoc-flow-ci/sync/check-standards-drift.sh:513` |
| C13 | Canon runs a **fleet** pin audit against this repo weekly and discards the verdict, so canon's own audit is unread too | `--fleet` | `aidoc-flow-ci/.github/workflows/standards-drift-self.yml:85` |
| C14 | The fleet output format differs from the in-repo format the parser targets, so the parser is in-repo-only | `⚠️ STALE` | `aidoc-flow-ci/sync/check-pin-currency.sh:76` |
| C15 | In-repo mode greps `@ci/v…` literally, so a SHA-pinned caller is invisible and reports a **false green** — while the fleet path at `:71` does match SHA pins. Two paths in one script disagree | `grep -oE '@ci/v[0-9]+\.[0-9]+\.[0-9]+'` | `aidoc-flow-ci/sync/check-pin-currency.sh:62` |
| C16 | The `--repin` remedy the reader surfaces is the script's own wording | `install/install.sh <this-repo> --repin` | `aidoc-flow-ci/sync/check-pin-currency.sh:101` |
| C17 | `sort -u` per file means the count is **files**, not call sites — `links.yml`'s two same-tag pins collapse to one, so a fully-stale repo reports 15, not 16 | `sort -u` | `aidoc-flow-ci/sync/check-pin-currency.sh:62` |
| C18 | At `v2.16.0` `emit_coverage` is invoked **after** pin-currency and its non-clean branch is a `::warning::`, so "pin-currency is last" expires with the re-pin | `emit_coverage` | `aidoc-flow-ci/sync/check-standards-drift.sh:520` |
| C19 | The entire script is one `run:` step in one job, so the cap's per-step / per-job / per-run granularity is not attributable from M1 | `Fetch canon drift script + run against the caller repo` | `aidoc-flow-ci/.github/workflows/standards-drift.yml:72` |
| C20 | Driving a repo shell script from `tests/unit/` via `subprocess` is the established precedent here — the precedent targets `tools/sync-plugin-framework.sh`, not `scripts/`, so the pattern carries but the directory does not | `subprocess` | `tests/unit/test_sync_scripts.py:4` |
| C21 | The repo's suites are `unittest`, and the conformance requirements declare only `PyYAML` + `jsonschema` — `pytest` is not a dependency | `jsonschema` | `tests/conformance/requirements.txt:5` |
| C22 | The local convention is to record concurrency reasoning as a comment **inside** the workflow file, per D-0070 | `concurrency` | `.github/workflows/audit-trail.yml:15` |
| C23 | `WARNING-ONLY, NEVER BLOCKS` is the upstream script's stated contract, so the reader failing loudly is a deliberate departure | `WARNING-ONLY, NEVER BLOCKS` | `aidoc-flow-ci/sync/check-pin-currency.sh:10` |
| C24 | The pre-push gate greps the OPS-0065 self-review phrase; `call / verify` is the required *context* name, not the grepped string | `OPS-0065` | `scripts/pre_push_check.sh:204` |
| C25 | This repo's pre-commit config runs `check-yaml` + `yamllint`, **not** actionlint — so V6 cannot lean on `pre-commit run --all-files` | `yamllint` | `.pre-commit-config.yaml:72` |
| C26 | With no `--canon` passed, `resolve_canon` falls through to canon `main`'s `VERSION`, so "all pins current" is not a state this repo controls | `resolve_canon()` | `aidoc-flow-ci/sync/check-pin-currency.sh:32` |
| C27 | The pre-commit test hook discovers `tests/conformance` only — nothing runs `tests/unit/` | `unittest discover` | `.pre-commit-config.yaml:106` |
| C28 | A failed `curl` of canon `main`'s `VERSION` makes the pin script warn and **exit 0 before auditing**, producing a log with a `pin-currency:` line but no verdict line — the fourth real shape | `could not resolve canon VERSION` | `aidoc-flow-ci/sync/check-pin-currency.sh:87` |
| C29 | If that `curl` returns a non-`ci/v` body instead of failing, `ver_cmp`'s numeric tests all fall through to `0`, so nothing is stale and the script prints `all pins current ✅` — a **false clean** the reader must not honour | `ver_cmp()` | `aidoc-flow-ci/sync/check-pin-currency.sh:39` |
| C30 | Canon's own injectable-binary pattern, adopted so the reconcile is testable without `gh`, auth or network | `GH="${GH:-gh}"` | `aidoc-flow-ci/sync/check-pin-currency.sh:21` |
| C31 | The conformance suite the new test registers into runs on **every commit** via an `always_run` local hook — so the test must not require network or `gh` | `always_run` | `.pre-commit-config.yaml:109` |
| C32 | CI-0018 — the same change that added `emit_coverage` — rerouted absent admin-only `repo-settings` fields through `warn_uncheckable`, so the `8 drift` figure is `v2.14.0`-era | `CI-0018` | `aidoc-flow-ci/CHANGELOG.md:651` |
| C33 | This repo's own caller comment predicts **two** warnings after the migration, not eight — corroborating C32 | `expect` | `.github/workflows/standards-drift.yml:37` |
| C34 | The log excerpt in the source TODO entry is already stripped of `gh run view --log`'s line prefixes, which is why a fixture built from it would diverge from a real download | `pin-currency: auditing ./.github/workflows against canon` | `plans/FRAMEWORK-TODO.md:92` |
| C35 | A governance PR is defined as one touching `DECISIONS.md`, plan files, `CLAUDE.md`, or the ai-review config | `governance PR` | `CLAUDE.md:545` |
| C36 | The auto-merge exception list is defined **by reference to** that governance list, so plan-file and `DECISIONS.md` PRs are excluded too | `governance PR list per the` | `CLAUDE.md:631` |
| C37 | Repo precedent moves a plan's Status through an implemented state, so the transition needs a named PR | `IMPLEMENTED` | `plans/ELEMENT-ID-LAYER-CONTRACT-001-PLAN.md:7` |
| C38 | The source TODO entry defers its own tracker promotion to whoever picks it up — disposed of in §PR sequencing | `Promote when someone picks it up` | `plans/FRAMEWORK-TODO.md:124` |
| C39 | Canon always prints a summary line at the end of a completed drift run — the positive marker that separates `skipped` from a truncated log | `check-standards-drift: $DRIFT drift,` | `aidoc-flow-ci/sync/check-standards-drift.sh:518` |
| C40 | The other positive marker: `stop_uncheckable` emits a warning before exiting early, so an aborted-but-real run is still distinguishable from no run at all | `stop_uncheckable` | `aidoc-flow-ci/sync/check-standards-drift.sh:116` |

**Measured, not file-resolvable.** M1, M2 and M3 are runtime behaviors with no
`file:line`; each carries its exact reproducing command and output in §"Measured
evidence". Called out here so a reviewer does not read them as claims smuggled past the
ledger. M1's *granularity* is explicitly **not** claimed (C19).

## Review log

### Pass 1 — 2026-07-29 — self-review

- The TODO entry's own fix shape ("a workflow that **runs the script**") would have
  built the second detector the same entry forbids. Rewritten so the reader consumes
  the completed run's output.
- First draft used the check-run annotations API as the input. Measuring it (M1) showed
  it returns **0** of the 10 stale-pin warnings. Rewrote around the log and added the
  input-surface table so the rejected option is on the record with its reason.
- Verifying C4 produced M2/C6/C7/C8: the summary line prints `0 pin error(s)` on a
  10-stale-pin run, so `strict: true` cannot fire for stale pins. This adds a second,
  stronger reason to the TODO entry's rejection of `strict`.
- Split verification pre/post-merge once R1 made clear V8+ cannot run pre-merge.
- Added R3 from the measurement that the log contains **zero** `::warning::`
  occurrences, tied to a required failing test rather than a comment.

### Pass 2 — 2026-07-29 — independent (fresh-context)

Dispatched `verified-planning-reviewer`. Eleven load-bearing findings; nine accepted
outright, one partly rejected on measurement, one corrected in a different direction
than reported.

- **Accepted — `tests/unit/` is executed by nothing** (C27). The extraction's entire
  justification was "unit-tested pre-merge," but no hook or workflow runs that
  directory, and `pytest` is not even a declared dependency (C21). Added R6, a
  registration step in Task 1, V2 to prove it, and switched V1 to `unittest`. This was
  the most valuable finding: it would have shipped a guard that guards nothing.
- **Accepted — a successful run can legitimately have no `pin-currency:` line**
  (C11, C12). The two-verdict contract would have turned canon's documented skip into a
  red reader. Added the third `skipped` verdict, a fourth fixture, and the
  upstream-conclusion filter (C10).
- **Accepted — "detection itself is correct" was false** (C15). In-repo mode
  false-greens a SHA-pinned caller while the fleet path handles it. Became a fourth
  upstream defect and a correction to Task 3's "what is NOT broken" paragraph. Out of
  scope locally: this repo pins by tag, so it cannot bite here today.
- **Accepted — a fourth input surface exists and already names this repo** (C13, C14).
  Canon's `standards-drift-self.yml` runs a fleet audit weekly and drops it with
  `|| true`. The Objective's "canon has no adopter-facing reader at all" was
  overstated; reframed to "no audit anywhere has a reader," which is both true and a
  stronger upstream argument.
- **Accepted — extract the reconcile too.** The first draft extracted the parse and
  left the branchier create/edit/close logic inline in YAML, verified only post-merge
  and live, with no `gh issue` precedent anywhere in this repo. Added
  `reconcile-pin-currency-issue.sh` with `--dry-run` and V4.
- **Accepted — the idempotence key was not safely lookup-able.** `--search` goes
  through a tokenized, eventually-consistent index; a fresh issue can be invisible and
  duplicate on the next run. Switched to `--json` plus an exact `jq` compare, and
  demoted the author filter from primary key.
- **Accepted — Rule 1 (≤3 doc surfaces) was violated and unaddressed**, as was the
  plan-PR-merges-first sequencing. Added §PR sequencing with a four-PR split.
- **Accepted — nothing verified the trigger chain itself** (R4). V8/V9 use dispatch and
  never exercise `workflow_run`; neither local precedent chains off a *scheduled*
  upstream. Added V10 and V11.
- **Accepted — the log-archive race** (R7). `--log` 404s exactly when
  `workflow_run: completed` fires. Added bounded retry; without it the dominant failure
  mode is a red workflow on an unwatched surface.
- **Rejected on measurement — the `ci` label does exist.** The finding asserted no
  `ci`/`area: ci` label exists, reasoning from canon's `labels.json`, this repo's
  `.github/labeler.yml` and the issue templates. Those are not the live label set:
  `gh label list` returns `ci`, `area: ci` **and** `workflows` (M3). Kept the label,
  switched from `area: ci` to plain `ci`, recorded M3 **with its output** since the
  parenthetical form invited the doubt, and adopted the finding's sound residual point —
  apply the label non-fatally, because an unknown label hard-errors in an unattended run.
- **Corrected, but not as reported — the "emitted last" claim.** The finding predicted a
  23rd warning from `emit_coverage` and concluded the measured 22 must be wrong. Direct
  re-census confirms **22** (10 + 4 + 8) with **no** coverage line at all. Cause: the
  measured run executed the drift script at **`ci/v2.14.0`**, where `emit_coverage` does
  not exist — the repo has re-pinned to `v2.16.0` since (D-0070). So the census stands
  and the underlying point still lands, one version later: from the next run on,
  `emit_coverage` (C18) emits a warning *after* pin-currency. Added the
  §"Version provenance" block, which also flagged a defect neither pass had caught —
  the ledger cites `v2.16.0` line numbers while M1/M2 measured `v2.14.0` output. Checked
  the consequence: `check-pin-currency.sh` is byte-identical across the two tags, so the
  fixture format is valid. True by measurement, not by design.
- **Accepted (non-load-bearing):** the `call / verify` context-vs-grepped-phrase
  conflation (C24); V5's actionlint fallback validates nothing (C25); the concurrency
  justification used the snapshot argument `CLAUDE.md` deprecates and skipped the
  in-file comment convention (C22); M1's cap granularity is unattributable (C19) and is
  now explicitly not claimed; `resolve_canon` falls through to canon `main` so the
  `clean` path is not this repo's to produce (C26, and V-clean is now deliberately
  absent with R5 restated); the count is files not call sites (C17); C1's wording
  contradicted its own premise; no notification path was specified (R8).

### Pass 3 — 2026-07-29 — independent (fresh-context)

Dispatched a second `verified-planning-reviewer` with Pass 2's dispositions in scope, to
re-validate the folds. It **upheld both places where Pass 2 was overridden**, and
corroborated them from checked-in artifacts rather than taking the author's word: the
`ci` label is confirmed by `.github/labeler.yml:39` — the very file Pass 2 had cited as
proof of its absence — and the version-provenance redirect is confirmed by canon's
`CHANGELOG.md:651`, which places `emit_coverage` (CI-0018) in the **`ci/v2.15.0`**
section, so it cannot have existed in the `v2.14.0` script the run executed. Ten new
load-bearing findings, all accepted:

- **The three-verdict contract missed a real log shape, and one variant produced a false
  `clean`** (C28, C29). A failed `curl` of canon's `VERSION` exits 0 *before* auditing —
  a `pin-currency:` line with no verdict — which the "absence of `pin-currency:`"
  definition of `skipped` sent straight to hard-fail. Worse: if that fetch returns an
  error page instead of failing, `ver_cmp` compares non-numeric fields, everything falls
  through to equal, and the script prints `all pins current ✅` — which the reader would
  have honoured by **closing the tracking issue** on a transient. Redefined `skipped` by
  absence of a *verdict* line, added an `unresolved` verdict, and made a well-formed
  `canon` token a precondition for honouring either verdict. This is the fifth upstream
  defect.
- **`--dry-run` had no injection point** (C30, C31), so V4 would have needed live `gh`,
  auth and network — inside a suite that runs on **every commit** via an `always_run`
  hook, which would have broken offline contributors. Adopted canon's own
  `GH="${GH:-gh}"` pattern with a stub fixture, and added V5 to prove the offline path.
- **The fixture would not have matched what the reader parses**, twice over (C18, C34):
  `gh run view --log` prefixes every line and the TODO entry's excerpt is already
  stripped, so anchored patterns would pass V1/V3 and fail V8 on the real download; and
  a `v2.14.0`-shaped fixture lacks the coverage warning that now trails pin-currency.
  This finding also punctured the provenance block's own conclusion: byte-identity of
  the pin script does **not** make the surrounding log identical, because that script
  does not emit the log it sits in. Fixtures now keep raw prefixes and carry the
  `v2.16.0` tail.
- **§PR sequencing misidentified which PRs are auto-merge-excluded** (C35, C36). All
  four are governance PRs, not just PR 4, because the exception list is defined by
  reference to the governance list — which includes plan files and `DECISIONS.md`.
- **No PR carried this plan's own Status transition** (C37), which the status-governance
  rule requires in the same change as the state change. Assigned to PR 2, which stays
  inside Rule 1 at two surfaces.
- **The `skipped` verdict contradicted the plan's own stated principle** (R11). It exits
  0 and logs a notice onto the same unwatched surface this plan exists to give a reader —
  and so does a *failed* drift run under the new conclusion filter. Every upstream
  failure mode was silent. Added a `last verified` stamp written on every reading so the
  reader's own staleness is visible in the artifact it maintains; explicitly deferred
  N-consecutive escalation rather than assuming it away.
- **The reconcile was undefined on the closed-issue case, and "comment only on verdict
  change" was vacuous.** `--state open` plus create-on-stale meant the per-canon-release
  cycle (C26) would produce one issue per release, not one issue. Switched to
  `--state all` + reopen, and defined the comment trigger on the verdict and stale set
  rather than the body — which embeds a weekly-changing run URL, so body-diffing would
  have commented every run. A count moving 10 → 15 would otherwise have been a silent
  edit, defeating R8.
- **"Applied non-fatally" was ambiguous exactly where it mattered** (C39 territory): the
  natural `|| true` would have made the whole issue creation non-fatal. Specified the
  labelled-then-unlabelled retry, moved it into Task 2, and added V13.
- **The concurrency rationale argued for deleting the block** (C22). "Nothing to cancel"
  is verbatim this repo's justification for shipping *no* `concurrency:` block, so a
  future sweep would have removed it. The real reason is serialization — it prevents a
  `workflow_run` and a concurrent dispatch from both finding no open issue and creating
  duplicates. Rationale replaced.
- **The conclusion filter would have green-skipped every dispatch** (C10). On a
  `workflow_dispatch` run `github.event.workflow_run.conclusion` is empty, so V10–V13
  would have reported "no issue created" against a passing run. Adopted the precedent's
  full `if:` including the `workflow_dispatch` clause.
- **Minors, all folded:** fixture count reconciled (four logs + one stub, garbage case
  built inline); `test_repo_scripts.py` moved from Modified to Created with its
  discovery mechanism stated (C27); the `8 drift, 4 fetch/scope` counts flagged as still
  `v2.14.0`-derived and barred from any document this plan produces (C32, C33); V7's
  `0/64` split out as V9 because that baseline belongs to the acceptance tier while V2
  requires the conformance count to *rise*; and the source entry's "promote when someone
  picks it up" instruction (C38) disposed of explicitly rather than ignored.

### Pass 4 — 2026-07-29 — independent (fresh-context) — **OPS-0066 cap reached**

Third and final independent pass. It re-read all 38 ledger rows at their cited lines and
found **no claim whose cited symbol fails to support its assertion** — C22's "Nothing to
cancel, so nothing to fix" is verbatim in `audit-trail.yml:18`, and it independently
re-traced `ver_cmp` with a non-numeric canon to confirm C29's false-`clean`. It also
answered the over-build question directly: **not over-built by this repo's own signal**,
because the documented failure mode is scope *without a named issue*, and every artifact
here traces to a cited finding. Seven load-bearing items, all folded:

- **`skipped` had no discriminator from truncated, which silently defeated R3.** Both are
  "no verdict line", so a truncated or wrong-run download would have parsed as a benign
  `skipped` — exit 0, no signal — where it used to hard-fail. Added the positive-evidence
  requirement (C39, C40) and fixed the check order so `unresolved` is not swallowed.
- **The lookup could not implement the comment contract, and would duplicate issues.**
  `body` was absent from the `--json` field list although the body is the only persistent
  store of the prior stale set, and there was no `--limit` — the default 30 would miss a
  long-closed tracking issue on a repo past #382 and create a duplicate, defeating the
  reopen contract. Added both, plus a machine-readable `pin-currency-state` block.
- **The assignee carried the label's hard-error failure mode with no fallback.**
  `gh issue create --assignee` errors on a non-assignable user, failing both the create
  and its label-dropping retry — no issue at all. Moved to `gh issue edit --add-assignee`
  after creation, non-fatal by construction.
- **R11's stamp was vacuous in the steady state.** With no issue ever created there is no
  artifact to stamp, and that case was unspecified. Scoped the claim and defined the
  no-op.
- **The Status transition needed two PRs.** `IMPLEMENTED` cannot ship in PR 2 because
  V10–V15 run only after it merges; PR 3 is at Rule 1's cap, so `IMPLEMENTED` went to
  PR 4 and PR 2 sets `IN PROGRESS`.
- **Nothing gated the close-out PRs on the post-merge verification**, so the TODO could
  have closed on unverified work. PR 3 now opens only after V10–V14, with V15 explicitly
  a post-hoc observation rather than a gate — it waits up to seven days for a Monday run.
- **Seven V-references did not survive the renumbering** and pointed at pre-merge rows
  where post-merge rows were meant. Swept.
- **Folded from the non-blocking set:** verdict-precedence ordering; the "three verdicts"
  header above a four-row table; C20's directory claim (the precedent targets
  `tools/`, not `scripts/`); the reconcile case count; "four" → "five" upstream defects;
  and PR 4 also refreshing `CLAUDE.md`'s concurrency inventory, which this workflow takes
  from three shapes to four.

**Not folded, and left as open items** — both are judgment calls the founder owns, not
defects:

1. **The registration shim is the one genuinely reducible piece.** It is a new pattern
   with no precedent, and it guards one file while ~30 existing `tests/unit/` modules stay
   unguarded. Cheaper alternatives: put the test directly in `tests/conformance/`, or add
   a `tests/unit` entry to `.pre-commit-config.yaml` and fix the class instead of the
   instance — arguably its own FRAMEWORK-TODO entry.
2. **`unresolved` and `skipped` have identical reader behavior**, so they could collapse
   into one verdict with a reason field, saving a fixture and a case. Keeping them apart
   is only worth it if the distinction is surfaced where a human reads it, which it
   currently is not.

**Result:** folds complete, pending validation — the OPS-0066 three-pass cap was reached
here and escalated to the founder rather than resolved by another dispatch. The founder
authorized a fourth independent cycle (Pass 5) instead of accepting the folds unvalidated.

### Pass 5 — 2026-07-30 — independent (fresh-context) — founder-authorized fourth cycle

Scoped to validating the Pass 4 folds rather than a fresh audit. It **confirmed all seven
are substantively correct** and did the work to prove the riskiest one: it traced *every*
`exit` in canon's drift script (`:41`, `:56`, `:118`, `:119`, `:522`, `:523`) and every
`stop_uncheckable` call site, establishing that the C39/C40 discriminator holds — any run
past preflight reaches the summary line, every `stop_uncheckable` path emits **two**
markers, and the `unknown arg` exit-2 path fails the upstream run so the reader's
conclusion filter never sees it. That last point *strengthens* the fold: "no drift output
at all" logs correspond to failed upstream runs the reader already skips.

Three text-level blocking items, all folded:

- **Task 3 still said "four defects."** The five-defect fold had reached §Scope, §Chosen
  shape and the C29 narrative but not the task that actually files the issue — so
  following Task 3 as written would have omitted C29, the false-`clean` defect. Its
  "what is NOT broken" correction now names **both** false-green paths (C15 and C29).
- **R1's mitigation still read "V10–V15 run … before the task is called done,"**
  contradicting §PR sequencing where the gate is V10–V14 and V15 is explicitly
  non-gating. This was the one stale V-reference the Pass 4 sweep missed; Pass 5
  re-checked every live-prose V- and R- reference and found no others.
- **The Status and Result blocks described the pre-Pass-5 state** — and PR 1's entire
  content is this file, so it cannot open asserting its own review state is incomplete.

Free residuals folded because they cost nothing and close real gaps:

- **Grep the common prefix `check-standards-drift:`** rather than either full marker. Pass
  5 found one literal exception to C39/C40 — the bash-4 preflight bail at `:39-42` emits
  neither named marker — unreachable on this repo's pinned `ubuntu-latest` runner and
  failing in the *safe* direction, but the shared prefix closes it for free.
- **Extend the positive-evidence requirement to `unresolved`**, not just `skipped`. A
  genuine `unresolved` log always carries the summary line, so this removes the last case
  where a truncated log could impersonate a verdict.
- **A stamp-only write must preserve the `pin-currency-state` block verbatim.** Otherwise
  an `unresolved` week regenerating the body would clear the stored stale set, and the
  next identical `stale` reading would look like `clean → stale` and emit a spurious
  comment.
- **`--limit 200` ages out** — accepted and stated rather than discovered later.
- **Task 2 now names the separate `--add-assignee` step**, which the contract required but
  the task list omitted.
- **V15's post-hoc record was ownerless** — every PR may merge before the first Monday, so
  PR 3 now lands an explicit `pending — V15 unconfirmed` line in `HANDOFF.md` for whoever
  observes the run to clear.
- **The `CLAUDE.md` docs-to-update entry** now carries the concurrency-inventory item its
  own PR 4 row already listed.

Pass 5's three blocking items were a defect count, a version range, and a status line —
deterministic, self-verifiable corrections rather than judgment calls, so they are folded
and verified in place rather than sent to a fifth cycle. Both open items the founder
already accepted (the registration shim's reducibility; `unresolved`/`skipped` sharing
behavior) remain open by decision, not oversight.

**Result:** ready — no load-bearing findings outstanding.

### Pass 6 — 2026-07-30 — PR 2 implementation self-review (Rule 2, 3 agents)

Not a plan review: the mandatory adversarial review of the **implementation** diff,
dispatched per governance Rule 2 / OPS-0067 across three agents (shell correctness,
workflow + test fidelity, governance + dead refs). Fourteen load-bearing findings, all
fixed before push. The four that would have shipped real defects:

- **The completion gate proved the wrong thing.** Pass 5 authorized grepping the common
  prefix `check-standards-drift:` as positive evidence that the drift script ran. It is
  not a terminal marker: the script emits an opening `repo=… tier=…` header and a
  `cannot check <family>` warning per unreadable family under that same prefix — the
  first of them **24 lines ahead** of pin-currency in the measured log. So a log
  truncated anywhere in that window satisfied the gate, parsed as `skipped`, and exited
  0 with ten stale pins in the real run. Reachable, not theoretical: `workflow_run:
  completed` fires while the log archive is still assembling and a partial archive is
  non-empty. Now gated on the summary line **or** the `coverage —` line, both of which
  only appear at termination. The plan's own C39/C40 wording was right and the
  "one substring for free" optimisation was what broke it.
- **The `--repin` remedy was swallowed into the markdown table.** `$(render_table)`
  inside a heredoc — command substitution strips trailing newlines, so the blank line
  meant to terminate the GFM table could not survive, and the remedy paragraph rendered
  as two junk table rows. On **every issue the tool would ever open**.
- **A `workflow_dispatch` `run_id` reached three `run:` blocks by interpolation**, with
  `GH_TOKEN` in scope and `issues: write` on the job token. Now `env:`-only, plus a
  digits check. `actionlint` does not flag this, so V6 could never have caught it.
- **A failed `jq` read routed to CREATE.** `gh --jq` uses gh's built-in jq, so the
  `|| die` on the list call passes even when the external `jq` the extractions use is
  broken — leaving `issue_number` empty, which is indistinguishable from "no issue
  exists". A read failure could open a duplicate. Now `|| die` per extraction.

Also fixed: the stamp silently no-opped (and reported success) on a body whose
`last verified` line had been hand-edited away; `clean` closed the issue with a body
headed "Stale @ci/v\* pins" reporting 0 stale files; a CRLF body from a web-UI edit
blanked every previous-verdict field and would have commented weekly; a value-less
trailing option hung the arg parser forever with no `timeout-minutes` above it; and
`sort` was locale-dependent on a string compared **across** runs.

**The fixtures were vindicated, the filter was not.** A reviewer flagged the fixtures as
unfaithful because they carry `^[` rather than raw `0x1b`. Measured against the live
download: `gh run view --log` emits **zero** raw ESC and 68 literal `^[`, so the fixtures
are byte-faithful and the *filter* was wrong — `grep -v $'\x1b'` matched nothing, making
a guard the script documented as load-bearing into dead code.

**Four test guards were vacuous and are now mutation-verified.** The `gh` stub ignored
`--state all` / `--limit 200`, so removing either kept the suite green while production
opened duplicates; the `--add-assignee` assertion tested a dry-run `printf` literal, not
the shipping branch; and no test read a single generated body, leaving both the
state-block round trip and Pass 5's "stamp preserves the block verbatim" fold unlocked.
Every guard added here was mutation-tested — the defect reintroduced, the guard confirmed
to fail, the defect reverted.

**Verified and NOT changed:** Rule 1 compliance (2 doc surfaces); the diff matching PR 2's
declared contents exactly, with no PR 3 or PR 4 leak; `permissions:`, the dual-trigger
`if:`, and the retry loop's control flow under the runner's `bash -e`; and every
cross-file claim in the new comments, checked against canon at the pinned tag.
