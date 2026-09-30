---
name: start-session
description: >-
  Use at the beginning of a working session or when asked what to do next. Reconstruct ground truth from the repository-declared handoff and tracker, verify claims, select work, and update state only on repositories that authorize those writes.
---

# Start session

> Framework adaptation — engine-agnostic copy of the canon global skill.
> Source: `aidoc-flow-claude-agents-config/skills/start-session/SKILL.md` (private, 2026-09-27).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Where the canon names an engine-specific agent type or path, use your engine's equivalent and keep the independence contract.


A handoff records the previous session's belief before its last actions settled.
Treat it as a lead and reconstruct current state before choosing work.

## 1. Read the repository declaration

Open the active repository's `AGENTS.md` chain (falling back to `CLAUDE.md` where
the repo has not migrated yet) and determine its declared:

- handoff surface, if any;
- task tracker and in-progress mechanism;
- merge and release state sources;
- authorization for issue, project, or other external writes.

Do not invent a GitHub handoff for a file-based repository, or a file handoff
for a tracker-based repository. If no handoff is declared, use recent commits,
open issues, and open PRs and say that the state was derived.

## 2. Read without inheriting

For a file handoff, read the declared file. For a tracker handoff, identify the
single current item using the repository's label or query. Zero open handoffs is
not automatically an error: inspect the most recent closed or superseded item
and current in-progress work before concluding state is missing.

Extract claims, not conclusions:

- what supposedly shipped;
- what remains in progress;
- blockers and their clearing conditions;
- the proposed next task;
- assumptions explicitly marked unverified.

## 3. Re-verify current state

Use primary evidence:

```bash
git status --short
git log --oneline -5
gh pr list --state open --limit 20        # when GitHub is the declared tracker
gh issue list --state open --limit 50
```

Check relevant PR state, merge commit, deployed version, tests, and cited files
as needed. Distinguish merged from deployed. Record contradictions between the
handoff and current evidence.

Run the shadowing detector in the repo being worked, so a same-name project
skill or undeclared project agent is caught at session open rather than by
accident later (pass `--check-remote` after a fetch when a hit needs a
COMMITTED-vs-LOCAL classification):

```bash
framework/skills/_shared/scripts/check-skill-shadowing.sh [repo-path]
# exit 0 clean; 1 collision defect; 2 incomplete scan or usage error
```

Adopt an open PR before selecting unrelated work when it is clearly the active
thread. A stale proposal in a spent handoff never outranks current repository
state.

## 4. Select and take custody

Choose one bounded task from the declared tracker. State why it is next and what
evidence makes it actionable.

Where the tracker records a finding's origin, a `real-use` item — one a real
project hit while doing its own work — outranks a `review` item that was found
by looking. Take the `real-use` item first, or state which of exactly two
conditions applies: the `review` item blocks the `real-use` fix, or no
`real-use` item is actionable. Those two are exhaustive. Origin is not
severity — that a `review` item feels more urgent is not one of them.

Only when authorized, mark it in progress using the repository's declared
mechanism. Transfer custody before closing or superseding a handoff; closing
first creates a gap where neither surface owns the work.

Do not modify a handoff merely to show that it was read. Close or supersede it
only when the repository declares that lifecycle and the work it carried has
been picked up or replaced.

## 5. Recall relevant memory

After selecting the task, use `recall` with that task as its query. Memory can
add standing constraints, but live source and repository governance remain the
authority.

## 6. Report

Return:

- verified current state;
- contradictions or unresolved assumptions;
- selected task and its tracker identifier;
- state changes made, with read-back confirmation;
- the immediate next action.

Do not begin implementation until this pickup is complete.
