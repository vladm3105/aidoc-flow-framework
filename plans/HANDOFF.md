# Session Handoff

**One reader: a fresh session with zero context.** Current state, then what to do next.
**Rewritten wholesale each merge** — `git log -- plans/HANDOFF.md` is the archive; do not
restore prior states here. Settled traps live in `CLAUDE.md` § "Durable traps" and are
never repeated here.

**State:** framework spec **`0.50.0`**, plugin `0.25.0`, Hermes `0.12.1`; both platform
`FRAMEWORK_SPEC_VERSION` pins read `0.50.0`. `0.45.0` was **skipped** and never became a value
of `framework/VERSION` (`plans/DECISIONS.md` D-0082). Tag high-water mark is
**`framework/v0.49.0`** (cut and pushed 2026-09-01); `v0.50.0` is **not** cut — re-derive with
`git ls-remote --tags origin 'refs/tags/framework/*'`.

**Verified this session** (run, not asserted, on this branch): conformance **494 passed /
1033 subtests** via `python3 -m pytest tests/conformance -q`, **543** via
`python3 -m unittest discover -s tests/conformance -t tests/conformance` (CI's runner) — the
two count subtests differently, so cite the command with the number ·
acceptance-deterministic **64** · unit **209** · `sdd_doc_lint` **6** ·
`pre-commit run --all-files` green. **One conformance failure is expected pre-commit and is
not this change** — see #620 immediately below.

Phase 0 `lint-smoke` is a separate harness and is RED — corpus debt deferred to the wholesale
regen; use `--skip-lint-smoke`.

## ⚠️ #620 — a framework version bump cannot pass its own pre-commit

**Unsettled; hit this session and will hit the next spec release.**
`tests/conformance/test_release_record_integrity.py` (the #617/#618 phantom-release guard)
resolves `VERSION` values from **committed git history only** (`_version_values`), and
`.pre-commit-config.yaml:124-128` runs the conformance suite `always_run: true`. So the commit
that introduces a spec release — bumping `framework/VERSION` and adding the matching
`### Changed — Framework Spec` heading, exactly as `GATE-SPEC-E005`/`E008` require — is
blocked by the guard whose precondition that commit is about to satisfy.

Reproduced in a throwaway clone: **RED staged, GREEN once committed.** CI is unaffected (the PR
branch contains the commit). The only local way through is `git commit --no-verify`, which also
skips ruff, markdownlint, yamllint, detect-secrets and both sync hooks — so **run
`pre-commit run --all-files` immediately after and confirm green**, which is what this branch
did. Fix shape and reasoning are on **#620**; it is not a defect in this change.

## The backlog is GitHub issues

**Open issues: 32**, of which **14** are parked (measured 2026-09-02 on this branch, before
this PR closes issue 601). Re-derive rather than copy:
`gh issue list --state open --limit 300 --json number --jq 'length'` and
`gh issue list --state open --limit 300 --json number,labels --jq '[.[]|select(.labels[].name=="parked")|.number]'`.
In-progress work carries **`status: in progress`** — that label is currently on nothing.

**The parked set** — not pickable: 438, 467, 473, 483, 484, 507,
528, 543, 544, 545, 546, 547, 548 and **563** (numbers unprefixed deliberately — a line
starting `#NNN` is autofixed into an H1, see `CLAUDE.md` § "Durable traps"). Derive that set
from the label, not from a title scan — two of them name the gating decision only in the body.
Three are blocked externally: **#484** (gated on v1.0.0), **#473** (the umbrella owns the
submodule pointer), **#528** (product call).

## What this session did

**One branch, not yet merged: `fix/601-iplan-code-inventory-planned`** — framework spec
`0.49.0 → 0.50.0`, **GD-25**, closes **#601** and answers all three questions **#609** held
open. Two issues filed: **#620** (above) and **#621**.

**IPLAN `code_inventory` became a three-value lifecycle seeded at Draft.** The vocabulary is
`planned | created | modified`; a Draft `code_build`/`combined` IPLAN carries one `planned`
entry per §2 `file_manifest` path instead of an empty block. Four plugin IPLAN skills move
with it and **two reverse** — `doc-iplan` and `doc-iplan-autopilot` had instructed the empty
block, so spec and Platform B had already disagreed. **Read the owners, not this summary** —
`framework/governance/DECISIONS.md` GD-25 and the `0.49.0 → 0.50.0` entry at the top of
`CHANGELOG.md`.

**#609's three answers are on the record in GD-25**, including the one it was opened to hold:
`2943bf3b` **did** owe a version bump, and this release pays it. #609 had been closed by hand
on 2026-09-01 with no recorded disposition; do not re-open it.

**`code_inventory` lives in §6, not §8.** `traceability` is `# Section 6`;
`# Section 8` is `rollback_procedure`, and there is no Section 7. The template had mislabelled
it at two pre-existing sites; the branch sweeps all of them. If you are reading an older plan or
changelog entry that says "§8 `code_inventory`", it is wrong.

## #621 — the same defect one section up, filed not fixed

§5 `session_handoff.sessions[]` ships a worked example carrying `action: created` and
`status: IN_PROGRESS`, and `doc-iplan/SKILL.md` step 9 instructs seeding it **at Draft** — so an
agent copying it produces a Draft asserting a session that never ran. **The two engines already
disagree**: the plugin seeds the handoff, the other engine's IPLAN prompt initializes an empty
`sessions` array. #621 carries two candidate shapes and the reasoning; GD-25 names it in its
"not adopted" paragraph, so it is a deferral with an owner, not silence.

## ⚠️ #606 is closed but its fix is NOT on `main`

Re-verified on this branch: `.github/ai-review/config.json:2` still pins `$schema` at
`ci/v2.16.0` against a `ci/v3.0.0` caller, and `tests/conformance/test_ai_review_schema_pin.py`
does not exist.

**The work is on the remote.** `git ls-remote origin 'refs/heads/fix/606*'` returns
`cfb7b6e4`, so the disposition is *reopen PR #612 or open a new one*, never *push a branch*.
PR #612 went red only on the `ai-review` `ResponseShapeError` flake, which no longer gates
(D-0084) — verify with `gh pr checks 612`.

⚠️ **Do not replay the branch wholesale.** All three of its commits touch `plans/HANDOFF.md`
and/or `CHANGELOG.md`, and both have moved again on this branch. Carry forward only what is
unique to #606 — the `config.json` `$schema` edit, the guard test, and the
`CI-CANON-V4-MIGRATION-PLAN.md` step-6/V3b additions — onto a branch off current `main`, and
re-author the changelog entry rather than replay it.

Closure metadata: closed `COMPLETED` 32 seconds after PR #612 closed unmerged, with an empty
`closedByPullRequestsReferences`. Evidence and dispositions are on the issue; the reopen call is
the founder's. Nothing is failing today — `$schema` is advisory and no workflow step
dereferences it.

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
ResponseShapeError` (upstream `aidoc-flow-ci#543`). It is **not** the 402 this proxy is
otherwise known for, and not size-driven. Since it no longer gates, the cost is a lost verdict,
not a blocked merge.

## Unsettled — watch

**Intermittent DNS failure on this host.** #613 was filed and closed the same morning
(2026-09-02); a further self-recovering instance occurred that afternoon. One instance after
closure is not a trend — re-open #613 if it becomes one, do not re-file.

## What to do next — prioritized

1. **Land `fix/601-iplan-code-inventory-planned`.** Merge is human-only on this repo per
   `.github/ai-review/config.json`; the PR body carries `Closes #601`. #609 is already closed
   and needs no action.
2. **Decide #606's disposition** — the only item where the record and `main` disagree. Cheapest
   correct path: re-submit the branch, since the `ai-review` flake that killed PR #612 no longer
   gates.
3. **#620** — fix the phantom-release guard so a spec release can pass its own pre-commit. Every
   future framework bump pays the `--no-verify` cost until it lands, and that is the change class
   where skipping the other hooks is least acceptable.
4. **#621** — decide what a Draft's `sessions:` carries, and bring both engines onto it.
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

(#423 was the previous handoff's in-progress item. It **merged** as PR #619 at `3af7c173`
and is closed `COMPLETED`; nothing is marked in progress now.)
