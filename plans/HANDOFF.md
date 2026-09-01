# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.49.0`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.49.0`. `0.45.0` was **skipped** and never became a value
of `framework/VERSION` (`plans/DECISIONS.md` D-0082). `framework/v0.44.0` is the most recent
**tag** — ⚠️ **already false**: `framework/v0.46.0`–`v0.49.0` were cut and pushed 2026-09-01
(they are tags, not a PR artifact, so they exist regardless of #618's state). The high-water
mark is **`framework/v0.49.0`**; re-derive with `git ls-remote --tags origin 'refs/tags/framework/*'`.
See "Release provenance" below.

**Verified this session** (run, not asserted, on `main` at **`29619057`** — i.e. after
PR #615 merged): conformance **473 passed / 950 subtests** via
`python3 -m pytest tests/conformance -q`, and **509** via
`python3 -m unittest discover -s tests/conformance -t tests/conformance` (CI's runner) — the
two count subtests differently, so cite the command with the number ·
acceptance-deterministic **64** via
`python3 -m unittest discover -s tests/acceptance/deterministic -t .` · unit **196** via
`python3 -m unittest discover -s tests/unit -t .` · `sdd_doc_lint` **6** via
`PYTHONPATH=tools python3 -m unittest discover -s tools/sdd_doc_lint/tests` ·
`pre-commit run --all-files` 19 green, rc=0. **0 failing.**

Phase 0 `lint-smoke` is a separate harness and is RED — corpus debt deferred to the wholesale
regen; use `--skip-lint-smoke`.

## Release provenance — #558 CLOSED (D-0078)

**Founder decision 2026-08-28 (option 3):** correct forward, rewrite no published entry.
Executed — `framework/v0.44.0` cut at `2c69a402`.

**The sharper half of #558 is now filed as #617.** `GATE-SPEC` has no release step —
`E001..E008` are all diff-local, so nothing checks that a superseded version was ever published,
and the gate is satisfied by *any* bump rather than the right one. It is recorded durably in
`plans/DECISIONS.md` D-0078 ("Standing consequence") and in the **`framework/v0.44.0` GitHub
release body** under "Known gap this tag does not close" — that string exists in **no file in
this repo**, so grepping for it finds nothing; read it with `gh release view framework/v0.44.0`.
It had no *tracker* home until #617, which is why it kept being re-typed into this file.

## The backlog is GitHub issues

**Open issues: 31**, of which **14** are parked (re-measured 2026-09-01 after PR #615). The
previous handoff said 34 open and 13 parked; both were stale on arrival, so re-derive rather
than copy:
`gh issue list --state open --limit 300 --json number --jq 'length'` and
`gh issue list --state open --limit 300 --json number,labels --jq '[.[]|select(.labels[].name=="parked")|.number]'`.
In-progress work carries **`status: in progress`** — currently only **#423**.

**The parked set** — not pickable: 438, 467, 473, 483, 484, 507,
528, 543, 544, 545, 546, 547, 548 and **563** (numbers unprefixed deliberately — a line
starting `#NNN` is autofixed into an H1, see `CLAUDE.md` § "Durable traps"). Derive that set
from the label, not from a title scan — two of them name the gating decision only in the body.
Three are blocked externally: **#484** (gated on v1.0.0), **#473** (the umbrella owns the
submodule pointer), **#528** (product call).

## What this session did

**One merge: #615 (closes #602), framework spec `0.48.0 → 0.49.0`.** One issue filed and left
open: **#614**.

**The ADR `alternatives` block stopped mandating a per-option cost.** `estimated_cost` and
`fit` became optional, a new optional `prior_analysis` prose field lets an author cite a survey
that already exists (typically the project's `seed/` stakeholder documents) instead of restating
it, and `architect.md` C2 was extended to accept a compressed rationale without opening a
citation loophole. Two adjacent defects shipped with it: the alternatives count and
`consequences.cost_estimate`. **Read the owners, not this summary** —
`framework/governance/DECISIONS.md` GD-24 and the `0.48.0 → 0.49.0` entry at the top of
`CHANGELOG.md`.

**#614 owns the one question GD-24 deliberately did not settle**, and carries the trap worth
having in front of you: the reporter asked for `source: "@seed: ARCH-NN"`, and an early GD-24
draft declined it because "a tag is lineage". **That is false** — `governance/TAG_SYNTAX.md`
registers `@chg: CHG-NN` as an explicitly *non-lineage* **provenance** tag for an overlay that is
likewise not one of the 8 registry layers. An `@seed:` class would be at least the **tenth**, and
is architecturally coherent; the decline rests on scope alone. It nearly merged as precedent
contradicting the file it cited. Not blocking anything.

## ⚠️ #606 is closed but its fix is NOT on `main`

Measured at `29619057`: `.github/ai-review/config.json:2` still pins `$schema` at
`ci/v2.16.0` against a `ci/v3.0.0` caller, and `tests/conformance/test_ai_review_schema_pin.py`
does not exist.

**The work is not lost, and it is already on the remote.**
`git ls-remote origin 'refs/heads/fix/606*'` returns `cfb7b6e4` — the branch is pushed, so the
disposition is *reopen PR #612 or open a new one*, never *push a branch*. (An earlier version of
this paragraph and of the first comment on #606 said "never pushed"; both are corrected. PR #612
existing was itself proof, and the negative was asserted without running the one command that
settles it.) Tip **`cfb7b6e4`**: `25b02cdd` (retarget the pin to the caller's tag, plus
`tests/conformance/test_ai_review_schema_pin.py`), `3f5b4dc1`, `cfb7b6e4`. PR #612 went red only
on the `ai-review` `ResponseShapeError` flake, which no longer gates (D-0084) — verify with
`gh pr checks 612`.

⚠️ **Do not replay the branch wholesale.** `git show --stat 25b02cdd 3f5b4dc1 cfb7b6e4` shows all
three touch `plans/HANDOFF.md` and/or `CHANGELOG.md`, and both have since moved on `main`:
`CHANGELOG.md` gained the `0.48.0 → 0.49.0` entry, and this file was rewritten wholesale.
Replaying `3f5b4dc1` would **resurrect the superseded issue figures** this refresh just
re-measured. Carry forward only what is unique to #606 — the `config.json` `$schema` edit, the
guard test, and the `CI-CANON-V4-MIGRATION-PLAN.md` step-6/V3b additions — onto a branch off
current `main`, and re-author the changelog entry rather than replay it. The branch is also
behind: it sits on `dce4a1ef`, `main` is `29619057`.

Closure metadata (`gh issue view 606 --json state,stateReason,closedAt,closedByPullRequestsReferences`):
closed `COMPLETED` at `06:21:36Z`, 32 seconds after PR #612 closed unmerged at `06:21:04Z`, with
an empty `closedByPullRequestsReferences`. Evidence and dispositions are on the issue; the reopen
call is the founder's. Nothing is failing today — `$schema` is advisory and no workflow step
dereferences it.

## The open call in #609

A direct push to `main` (`2943bf3b`) bypassed `GATE-SPEC` entirely — the mechanism is now in
`CLAUDE.md` § "Durable traps" and is not repeated here. **#609 owns the three questions that
travel together** and is still open: does that edit owe a version bump + GD entry, is
`IPLAN-TEMPLATE.yaml:163` reconciled with `:300` (`:163` documents that carrier's vocabulary as
`created | modified`; `:300` declares `created | modified | planned`), and is **#601** actually
satisfied by a comment-only edit. Founder deferred it as "unblock now, decide later".

## CI gating — `ai-review` and `composition` no longer gate (D-0084)

**Read `plans/DECISIONS.md` D-0084 rather than this summary.** Both were removed from `main`'s
required status checks; both still run and still post verdicts. This is **server state that
lives in no git repository**, and D-0084 carries the one-call restore.

**The four required contexts are:** `Framework + platform conformance`,
`call / Lint / format / security hooks`, `call / verify`, `Acceptance tier (deterministic)`.
Re-derive with
`gh api repos/vladm3105/aidoc-flow-framework/branches/main/protection/required_status_checks --jq '.contexts[]'`.
`GATE-SPEC` and `dep-scan` are **not** required — a red one leaves a PR `UNSTABLE`, not
`BLOCKED`.

**`ai-review` fails intermittently** with `litellm: proxy request failed after 3 attempts:
ResponseShapeError` (upstream `aidoc-flow-ci#543`) — observed again this session, then passing
on a re-run of the same branch. It is **not** the 402 this proxy is otherwise known for, and
not size-driven. Since it no longer gates, the cost is a lost verdict, not a blocked merge.

## Unsettled — watch

**Intermittent DNS failure on this host — the previous handoff's "do not yet file" is
discharged.** It said a fourth instance warranted an issue; **#613 was filed and closed the
same morning** (05:49Z → 06:21Z — `gh issue view 613 --json state,createdAt,closedAt`), so do
not re-file. A **further** instance occurred this
session at ~13:2xZ — `gh` returned `error connecting to api.github.com` on a `pr checks` call
and succeeded on immediate retry, matching #613's self-recovering pattern. Not re-opened:
one self-recovering instance after closure is not yet a trend. Re-open #613 if it becomes one.

## What to do next — prioritized

1. **Decide #606's disposition** — the only item where the record and `main` disagree. The
   issue is closed `COMPLETED`, its fix is not on `main`, and the work sits unpushed on
   `fix/606-ai-review-schema-pin` (`cfb7b6e4`). Three dispositions are laid out in the comment
   on #606. Cheapest correct path: re-submit the branch, since the `ai-review` flake that
   killed PR #612 no longer gates.
2. **#618** — closes #617 with the phantom-version guard and records **D-0086** (the
   `hermes/v0.1.1` tagged phantom: a cut, immutable release tag on a commit whose VERSION reads
   `0.1.0`). The four framework tags it describes are **already pushed**; the PR carries the
   guard, `docs/TAGGING.md` and the decision record, not the tags.
3. **#609** — the deferred founder call: does `2943bf3b` owe a framework version bump + GD
   entry, is `IPLAN-TEMPLATE.yaml:163` reconciled, and is **#601** actually satisfied by a
   comment-only edit? All three travel together, because reconciling `:163` is itself a
   `framework/**` edit that trips `GATE-SPEC-E005`.
4. **#614** — new, unstarted: does the seed tier get a registered `@seed:` provenance tag on
   the `@chg:` precedent? Suggested default is **no** unless a second `real-use` report
   arrives; the point of the issue is that the *reason* must be scope, never "a tag is
   lineage". Not blocking anything.
5. **#393 / `plans/CI-CANON-V4-MIGRATION-PLAN.md`** — still **BLOCKED** on two founder /
   infrastructure prerequisites (runner labels `ci`/`ephemeral` do not exist; `LLM_URL` /
   `LLM_API_KEY` do not exist and the caller still forwards three `LITELLM_*` names v4
   un-declares). ⚠️ **Its stated `--repin` remedy is insufficient**, not unsafe — the plan
   (`:35-37`) says `--repin` cannot deliver two of the five required changes; *unsafe* is this
   repo's word for `--update` (risk R2). Read the plan, not the issue body. If #606 is re-submitted, its `$schema` edit and this plan's step 6 / verification V3b
   must stay consistent.
6. **#588** — the identity-carrier split. Not startable alone; it is `OKF-CONFORMANCE-001`
   D1's to settle.
7. **#546** — **parked**, and splitting it is what unparks it. The `_required: false` half of
   the `STY02` defect is independently shippable and does not wait on the parked subtype
   decision; the correction that establishes this is in the issue's own comments. Re-title or
   split before picking it up, and drop `parked` from the shippable half.
8. **#423** — the only issue marked in progress. `origin/fix/423-site-badge-selfheal` carries
   `f05dfc0d`. Needs a rebase onto current `main`, a finalized commit message and a PR.
