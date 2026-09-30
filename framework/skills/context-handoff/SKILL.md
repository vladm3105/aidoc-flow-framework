---
name: context-handoff
description: >-
  Use when context is running out while the current task remains unfinished. Capture findings, record resumable state on the active work item, and confirm persistence without closing the task or performing a session wrap.
---

# Context handoff

> Framework adaptation — engine-agnostic copy of the canon global skill.
> Source: `aidoc-flow-claude-agents-config/skills/context-handoff/SKILL.md` (private, 2026-09-27).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Where the canon names an engine-specific agent type or path, use your engine's equivalent and keep the independence contract.


Use this only when both conditions hold: the task is unfinished and context is
about to end. A finished thread uses `wrap-session`; an unfinished task with
enough context keeps going.

## 1. Read the repository declaration

Identify the active task surface, handoff policy, remote persistence rules, and
authorization for comments, commits, and pushes. Do not assume every repository
uses GitHub issues or permits autonomous remote writes.

## 2. Capture durable findings first

Route each actionable defect or improvement through `submit-feedback` before
writing resume state. A task-scoped note dies when the task finishes and is not
a durable defect tracker.

## 3. Record resumable task state

Use the repository's declared in-progress work item. Prefer a comment on the
active issue when GitHub is authorized; otherwise use its declared WIP or local
handoff mechanism. Do not edit the session handoff unless the repository says it
also owns mid-task state.

The resume record contains:

```markdown
## Resume state — YYYY-MM-DD, context boundary

- Done and verified: <work plus verification>
- Done, not verified: <remaining checks>
- In flight: <files and partial state>
- Not started: <remaining scope>
- Next action: <one action requiring no rediscovery>
- Blockers: <reason and clearing condition>
- Assumptions: <each unverified claim>
```

When posting a GitHub comment, use `--body-file -` and read the comment back.
Writing to an external tracker requires repository or user authorization.

## 4. Preserve the work

If changes are uncommitted, state that plainly. Commit or push a WIP checkpoint
only when requested or authorized by repository policy. Never use `git add -A`
without first separating pre-existing changes from the current task.

When a push is authorized, verify the intended remote contains the checkpoint;
a local commit or successful command is not proof of persistence.

## 5. Report

Return the work-item identifier or local record path, read-back or persistence
evidence, remaining uncommitted state, and the exact next action. State that this
was a context handoff, not a wrap: the task remains open and nothing was closed.
