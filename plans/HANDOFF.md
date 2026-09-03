# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.50.0`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.50.0`. `0.45.0` was **skipped** and never became a value
of `framework/VERSION` (`plans/DECISIONS.md` D-0082). Tag high-water mark is
**`framework/v0.50.0`**, cut 2026-09-03 at `07b52e02` — re-derive with
`git ls-remote --tags origin 'refs/tags/framework/*'`. **A cut tag is not a published Release
here:** `framework/v0.44.0` is the newest framework Release and so still shows as *Latest* while
the spec is `0.50.0`; `v0.46.0`–`v0.50.0` are tag-only.

**Verified 2026-09-03 on `main` at `06e0a641`** (run, not asserted): conformance **494 passed /
1034 subtests** via `python3 -m pytest tests/conformance -q`, and **543** via
`python3 -m unittest discover -s tests/conformance -t tests/conformance` (CI's runner) — the two
count subtests differently, so cite the command with the number. Acceptance-deterministic **64**,
unit **209**, `sdd_doc_lint` **6**, `pre-commit run --all-files` green. **0 failing.**

Phase 0 `lint-smoke` is a separate harness and is RED — corpus debt deferred to the wholesale
regen; use `--skip-lint-smoke`.

## What this session did

**Five merges, all on `main`.** PR #622 (closes #601, framework spec `0.49.0 → 0.50.0`, at
`07b52e02`); PRs #624 and #625 (handoff + tagging docs); and PR #626 (closes #623, re-enables
`ai-review`, at `06e0a641`). Three issues filed — **#620**, **#621**, **#623** — **#613
reopened**, and **`framework/v0.50.0` cut and pushed**. Nothing is left open from this thread.

**IPLAN `code_inventory` became a three-value lifecycle seeded at Draft.** Vocabulary is
`planned | created | modified`; a Draft `code_build`/`combined` IPLAN carries one `planned`
entry per §2 `file_manifest` path instead of an empty block, and `deploy` seeds none because it
requires no manifest. Four plugin IPLAN skills moved with it and **two reversed** — `doc-iplan`
and `doc-iplan-autopilot` had instructed the empty block, so spec and Platform B had already
disagreed. **Read the owners, not this summary** — `framework/governance/DECISIONS.md` **GD-25**
and the `0.49.0 → 0.50.0` entry in `CHANGELOG.md`.

**#609 is answered and closed; do not re-open it.** It held three questions and was closed by
hand on 2026-09-01 with no recorded disposition. GD-25 supplies all three, including the one it
existed for: `2943bf3b` **did** owe a version bump, and `0.50.0` pays it.

**`code_inventory` is in §6, not §8.** `traceability` is `# Section 6`; `# Section 8` is
`rollback_procedure`; there is no Section 7. The template had mislabelled it at two pre-existing
sites and #622 swept them. **Any older plan or changelog entry saying "§8 `code_inventory`" is
wrong.**

## ⚠️ #620 — a framework version bump cannot pass its own pre-commit

**Unsettled, and it will hit the next spec release.**
`tests/conformance/test_release_record_integrity.py` (the #617/#618 phantom-release guard)
resolves `VERSION` values from **committed git history only** (`_version_values`), and
`.pre-commit-config.yaml:124-128` runs the conformance suite `always_run: true`. So the commit
that introduces a spec release — bumping `framework/VERSION` and adding the matching
`### Changed — Framework Spec` heading, exactly as `GATE-SPEC-E005`/`E008` require — is blocked
by the guard whose precondition that commit is about to satisfy.

Reproduced in a throwaway clone: **RED staged, GREEN once committed.** CI is unaffected (the PR
branch contains the commit). The only local way through is `git commit --no-verify`, which also
skips ruff, markdownlint, yamllint, detect-secrets and both sync hooks — so **run
`pre-commit run --all-files` immediately after and confirm green**, which is what #622 did and
recorded in its PR body. Fix shape is on **#620**.

## `ai-review` is RE-ENABLED and verified working (D-0087, #623 closed)

**It was `disabled_manually` from 2026-09-01 to 2026-09-03** and produced no run, no verdict and
no check-run on any PR in that window — including PRs #619, #622, #624 and #625, all merged to
`main`. Nothing recorded the disable. **Read `plans/DECISIONS.md` D-0087 rather than this
summary**; the evidence that decided it is that four `ai-review` runs succeeded on three
branches between 02:45 and 03:12 on 2026-09-01, and the three failures that preceded the disable
were **all on one branch** (`fix/606-ai-review-schema-pin`, PR #612).

**Confirmed working, not merely re-enabled.** PR #626 — the change that re-enabled it — was
itself reviewed: a substantive `changes requested` (a missing CHANGELOG entry, which was
verified against the D-0084 changelog entry and correct), then `ai:review-passed` after the fold.
`composition` ran and passed alongside it. So the reviewer produces real verdicts on ordinary
PRs, and a red `call / ai-review` is the intended signal for `changes requested` rather than an
infrastructure error — check the PR comment before treating one as a break.

**Two traps from that window are worth keeping even though the state is fixed:**

- **`gh workflow list` showed `composition` as `active` throughout, and it was silent.** Its only
  PR-side triggers are `pull_request_review` and a `workflow_run` chained off **`ai-review`**
  completing, so disabling the parent silences the child while the listing still reads healthy.
  Check the child's *runs*, not its status.
- **D-0084 asserts "Both workflows still run", and that sentence was falsified two days after it
  was written.** It is annotated in place, not rewritten — a decision is accurate as of its date.
  Its gating half (the four required contexts, the restore command) was never affected.

Re-derive rather than trusting either: `gh workflow list --all` ·
`gh run list --workflow=ai-review.yml --limit 8`.

**Expect intermittent red, and it does not block.** `ai-review` is not a required context, so a
failure leaves a PR `UNSTABLE`. Upstream `aidoc-flow-ci#543` is **open** and its diagnosis does
not fit: it reports the failure as deterministic on a **many-file** diff and its own follow-up
retracts the file-count mechanism, but PR #612 is **5 files, +313/−40** and failed three times.
Neither file count, line count, nor the 400,000-byte input cap explains it. That evidence is now
a comment on #543; the discriminator is unmeasured and upstream-owned.

**#596's premise is restored.** Its items 1 and 2 were written assuming `ai-review` still runs;
that is true again, so they revert to their original form rather than resolving by deletion.

## CI gating — the branch-protection half of D-0084 still holds

**The four required contexts are:** `Framework + platform conformance`,
`call / Lint / format / security hooks`, `call / verify`, `Acceptance tier (deterministic)`.
Re-derive with
`gh api repos/vladm3105/aidoc-flow-framework/branches/main/protection/required_status_checks --jq '.contexts[]'`.
`GATE-SPEC` and `dep-scan` are **not** required — a red one leaves a PR `UNSTABLE`, not
`BLOCKED`. Branch protection requires **0** approving reviews, but merge is human-only on this
repo per `.github/ai-review/config.json`. D-0084 carries the one-call restore for the removed
contexts and that half is unchanged.

## The backlog is GitHub issues

**Open issues: 33**, of which **14** are parked (measured 2026-09-03, after #601 closed,
issues 620 / 621 / 623 were filed, and #613 reopened). Re-derive rather than copy:
`gh issue list --state open --limit 300 --json number --jq 'length'` and
`gh issue list --state open --limit 300 --json number,labels --jq '[.[]|select(.labels[].name=="parked")|.number]'`.
In-progress work carries **`status: in progress`** — that label is currently on nothing.

**The parked set** — not pickable: 438, 467, 473, 483, 484, 507,
528, 543, 544, 545, 546, 547, 548 and **563** (numbers unprefixed deliberately — a line
starting `#NNN` is autofixed into an H1, see `CLAUDE.md` § "Durable traps"). Derive that set
from the label, not from a title scan — two of them name the gating decision only in the body.
Three are blocked externally: **#484** (gated on v1.0.0), **#473** (the umbrella owns the
submodule pointer), **#528** (product call).

## #621 — the same defect one section up, filed not fixed

§5 `session_handoff.sessions[]` ships a worked example carrying `action: created` and
`status: IN_PROGRESS`, and `doc-iplan/SKILL.md` step 9 instructs seeding it **at Draft** — so an
agent copying it produces a Draft asserting a session that never ran. **The two engines already
disagree**: the plugin seeds the handoff, the other engine's IPLAN prompt initializes an empty
`sessions` array. #621 carries two candidate shapes; GD-25 names it in its "not adopted"
paragraph, so it is a deferral with an owner, not silence.

## ⚠️ #606 is closed but its fix is NOT on `main`

Re-verified 2026-09-03 at `07b52e02`: `.github/ai-review/config.json:2` still pins `$schema` at
`ci/v2.16.0` against a `ci/v3.0.0` caller, and `tests/conformance/test_ai_review_schema_pin.py`
does not exist.

**The work is on the remote.** `git ls-remote origin 'refs/heads/fix/606*'` returns `cfb7b6e4`,
so the disposition is *reopen PR #612 or open a new one*, never *push a branch*. PR #612 went red
only on the `ai-review` `ResponseShapeError` flake, which no longer gates (D-0084) — and per #623
no longer runs at all, so that flake cannot block a resubmission today.

⚠️ **Do not replay the branch wholesale.** All three of its commits touch `plans/HANDOFF.md`
and/or `CHANGELOG.md`, and both have moved again. Carry forward only what is unique to #606 — the
`config.json` `$schema` edit, the guard test, and the `CI-CANON-V4-MIGRATION-PLAN.md` step-6/V3b
additions — onto a branch off current `main`, and re-author the changelog entry rather than
replay it.

Closure metadata: closed `COMPLETED` 32 seconds after PR #612 closed unmerged, with an empty
`closedByPullRequestsReferences`. Evidence and dispositions are on the issue; the reopen call is
the founder's. Nothing is failing today — `$schema` is advisory and no workflow step
dereferences it.

## Unsettled — watch

**#613 REOPENED — the host DNS intermittent is a trend.** `call / dep-scan` failed twice on
2026-09-02 (17:03Z and 20:06Z, different SHAs of PR #622) with
`curl: (6) Could not resolve host: github.com`, self-recovering on re-run each time; the host's
own `gh` failed three times in the same windows with `error connecting to api.github.com`, and a
`git ls-remote` failed on 2026-09-03 with `ssh: Could not resolve hostname github.com`. That is
**eight instances across two days on two surfaces**. `call / trivy-scan` passed from the same
self-hosted pool in both windows, which still rules out a pool outage. The new evidence is
host-side: the fix belongs on the host's resolver, not in the runner image. Full table on #613 —
do not re-file.

## What to do next — prioritized

1. **Decide #606's disposition** — the only item where the record and `main` disagree. Cheapest
   correct path: re-submit the branch. ⚠️ **`ai-review` now runs again (D-0087), and PR #612 is
   the one branch it failed on** — three times, deterministically. Expect that failure to recur
   on a resubmission; it is non-blocking (`ai-review` is not a required context), and reproducing
   it deliberately would be useful evidence for upstream `aidoc-flow-ci#543`, whose stated
   diagnosis does not fit a 5-file diff.
2. **#620** — fix the phantom-release guard so a spec release can pass its own pre-commit. Every
   future framework bump pays the `--no-verify` cost until it lands, and that is the change class
   where skipping the other hooks is least acceptable.
3. **#621** — decide what a Draft's `sessions:` carries, and bring both engines onto it.
4. **#613** — reopened; the fix is host-side resolver work, not a repo change. Not blocking.
5. **#614** — does the seed tier get a registered `@seed:` provenance tag on the `@chg:`
   precedent? Suggested default is **no** unless a second `real-use` report arrives; the point of
   the issue is that the *reason* must be scope, never "a tag is lineage". Not blocking anything.
6. **#393 / `plans/CI-CANON-V4-MIGRATION-PLAN.md`** — still **BLOCKED** on two founder /
   infrastructure prerequisites (runner labels `ci`/`ephemeral` do not exist; `LLM_URL` /
   `LLM_API_KEY` do not exist and the caller still forwards three `LITELLM_*` names v4
   un-declares). ⚠️ **Its stated `--repin` remedy is insufficient**, not unsafe — the plan
   (`:35-37`) says `--repin` cannot deliver two of the five required changes; *unsafe* is this
   repo's word for `--update` (risk R2). Read the plan, not the issue body. If #606 is
   re-submitted, its `$schema` edit and this plan's step 6 / verification V3b must stay
   consistent.
7. **#588** — the identity-carrier split. Not startable alone; it is `OKF-CONFORMANCE-001`
   D1's to settle.
8. **#546** — **parked**, and splitting it is what unparks it. The `_required: false` half of
   the `STY02` defect is independently shippable and does not wait on the parked subtype
   decision; the correction that establishes this is in the issue's own comments. Re-title or
   split before picking it up, and drop `parked` from the shippable half.

`framework/v0.50.0` was cut this session and is off this list. `docs/TAGGING.md` still records
the tag-cut lag as a sanctioned backlog — **77 of 90** values untagged, all of them older than
`v0.46.0` — so the *older* backlog stays deferred; only the contiguous recent run is maintained.
