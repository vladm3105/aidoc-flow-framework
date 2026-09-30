---
name: ship-it
description: >-
  Use after a PR you opened is running CI, but only when the repository explicitly authorizes agent auto-merge. Watch required checks, enforce carve-outs, merge when eligible, and clean up the branch; otherwise stop for explicit user direction.
metadata:
  mined-from: netresearch/git-workflow-skill v1.23.0 (MIT AND CC-BY-SA-4.0), 2026-08-12
---

# Ship it

> Framework adaptation — engine-agnostic copy of the canon global skill.
> Source: `aidoc-flow-claude-agents-config/skills/ship-it/SKILL.md` (private, 2026-09-27).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Where the canon names an engine-specific agent type or path, use your engine's equivalent and keep the independence contract.


The stretch between "PR is open" and "PR is merged" had no owner: `wrap-session`
starts *after* the merge, and the skill that gets you *to* the PR stops at
opening it. This is that stretch, and nothing else.

## 0. Precedence, and one seam worth knowing

| File | Owns | Beats |
|---|---|---|
| the owning repo's `AGENTS.md` chain | the **authorization and declaration** — whether agents may auto-merge, merge convention, protected branches, who may merge | global defaults |
| the owning repo's `AGENTS.md` chain | global safety carve-outs | this skill |
| this skill | the **mechanism** — how to watch, what "green" means, how to merge | — |

If this file and the owning repo's `AGENTS.md` chain disagree, the policy wins and the
disagreement is a defect **here**.

**The seam with `superpowers:finishing-a-development-branch`.** That skill's
rationalization table says *"Integration is your human partner's decision.
Present the menu and wait."* It is not in conflict with merge-on-green — it
governs a **different moment**:

| Moment | Governed by |
|---|---|
| implementation done; choose an integration route (merge locally / open a PR / leave it) | `finishing-a-development-branch` — present the menu, wait |
| a PR of yours is open and its checks are running | the repo's explicit auto-merge rule, if any — otherwise wait for user direction |

Read them as sequential, not competing. **Merge-on-green does not authorize
merging locally without a PR** — it presupposes an open PR and passing required
checks. Do not use this skill to skip the menu.

## 1. Watch the checks

**Read `mergeStateStatus` first — before any check rollup.** It is the only field
that sees a **missing required review**: `BLOCKED` ends the question regardless
of what the checks say, and no check-rollup field reports it.

```sh
gh pr view <N> --json mergeStateStatus --jq .mergeStateStatus   # CLEAN / BLOCKED / BEHIND / UNKNOWN
```

`BLOCKED` → the PR is not mergeable yet; find out whether it is checks or review
before reading any colour. Then watch:

```sh
gh pr checks --required --watch          # required checks only, blocks until they settle
gh pr checks --json name,state,bucket,workflow --jq '.[] | select(.bucket!="pass")'
```

Three things that make "green" a claim rather than an observation:

- **`--required` is the whole point.** Merge-on-green is worded *"all **required**
  checks pass"*. A repo with advisory or optional checks will show red or pending
  entries that do not gate the merge, and — worse — a repo whose important check
  is *not* marked required will look green when nothing verified anything.
  Check which is which before reading the colour.
- **`bucket`, not `state`.** `gh` normalises `state` into `pass` · `fail` ·
  `pending` · `skipping` · `cancel`. **`skipping` is not `pass`** — a required
  check that was skipped has verified nothing.
- **Exit code 8 means pending**, not failure. Do not read a non-zero exit as red.

**A zero-length rollup is a case to name, not a silence to fill.** `checks == 0`
means one of three things — no CI is configured (this repo's own declared
decision, verified in its `AGENTS.md` chain/workflows) · workflows exist but have not
fired yet on a fresh head (a race — wait and re-read) · the wrong PR/head was
queried. Say which one you are in; "nothing to wait for" is a conclusion only
the first case supports.

**The stale-SHA trap.** After a push, `gh pr checks` can still describe the
previous head. Confirm the checks belong to the commit you intend to merge:

```sh
gh pr view --json headRefOid --jq .headRefOid
git rev-parse HEAD
```

Different → the run you are reading is not the run that matters. Wait, or push
and re-watch. Reporting an earlier run's green as this commit's is the same
class of defect as `wrap-session`'s hardcoded summary: a result that no input
can falsify.

## 2. The merge decision — not yours to restate

The active repository must explicitly grant agent auto-merge. If it does not,
stop and ask the user. When it does, apply that declaration plus the global
safety carve-outs as a checklist:

| Carve-out | If it applies |
|---|---|
| the user said wait or hold | stop |
| **CI is red or incomplete** | **report + fix — never merge failing.** This one is a prohibition, not an approval request: no sign-off converts it into a go |
| it is not a PR you opened | stop |
| a repo rule reserves merge for a human | stop |
| you are unsure whether one applies | ask before merging |

`approval-gate` does not tier merging, deliberately — standing authorization is
not self-approval. That reasoning lives in `approval-gate`; do not re-derive it.

### 2.1 When CI is red — the loop the prohibition implies

"Report + fix — never merge failing" is the likeliest branch of the only phase
this skill owns, and it has steps:

1. **Diagnose, then fix on the branch, push, and re-enter §1 from the stale-SHA
   re-check** — the new head means every previous reading is void; confirm
   `headRefOid` before trusting any colour again.
2. **Bail out when** the same check is red twice after a fix attempt, or the fix
   is non-trivial (it touches things the PR does not own) — stop, report the
   diagnosis and the attempted fix to the human, and leave the PR open.
3. **Context running out mid-loop** → `context-handoff`; its gate matches
   (unfinished thread), and the PR number plus the diagnosis is what the
   successor needs.
4. **Cancelled checks are red here**, not a pass — re-run them (`gh pr checks
   --required --watch` re-triggers watching) before any merge decision.

## 3. Merge and clean up

Use the repo's declared convention — do not assume squash.

```sh
gh pr merge <N> --squash --delete-branch     # or --merge / --rebase, per the repo
gh pr view <N> --json state,mergedAt --jq '"\(.state) \(.mergedAt)"'   # read it back
```

**Read the merge back.** A merge command that printed a URL is not proof the PR
merged — the same read-back discipline `submit-feedback` applies to issue bodies.

If the PR body carried `Closes #N`, the merge closes the issue. **Do not close it
by hand afterwards** — that step is the one that gets forgotten, and doing both
is two records of one act.

**A PR closed unmerged is a named outcome, not a silent one.** Rejection usually
means the thread is *not* finished: report why it was closed (read the review or
close reason), and wrap only if the thread is actually finished without it.

## 4. Hand off

A merged PR is a wrap point: say so, and run `wrap-session` **in this session** —
the wrap must not wait for a fresh one. `wrap-session` takes it from here.

**This skill never writes a handoff, a changelog entry, or a memory.** If you are
reaching for one of those, you have already left this skill.

## Red flags

| Thought | Reality |
|---|---|
| "CI is green" | Required-green? Optional checks are noise; an unrequired important check is worse than noise. |
| "Checks passed" | On which SHA? Compare `headRefOid` to `HEAD`. |
| "A check was skipped, so it didn't fail" | `skipping` is not `pass`. It verified nothing. |
| "Non-zero exit, so it's red" | Exit 8 is pending. |
| "It's my PR, so I can merge" | Run the four carve-outs. One of them is a prohibition. |
| "The other skill said to wait for the human" | Different moment — see §0. And it does **not** license merging without a PR. |
| "Merged — now I'll close the issue" | `Closes #N` did it. Closing again is a second record. |
| "It printed a URL, so it merged" | Read the state back. |
| "Red — I'll just fix it forever" | Red twice, or a fix outside the PR's scope → stop and report. That is §2.1's bail-out, not persistence. |
| "Checks came back empty — green by vacuous truth" | Name the zero-case: no CI (declared?), not fired yet (race), or wrong head. Only the first is green. |
| "The PR was closed, so it's finished" | Closed ≠ merged. Report why; the thread usually is not finished. |
