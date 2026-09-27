---
name: wrap-session
description: >-
  Use when the current work thread is finished or the user explicitly asks to wrap. Update only the handoff, tracker, changelog, memory, and remote surfaces declared and authorized by the active repository.
---

# Wrap session

A wrap transfers completed work and remaining state to the repository's declared
owners. It is not a generic requirement to create issues, edit changelogs, or
push commits in every project.

## 1. Confirm this is a wrap point

Wrap when the thread is finished, the user asks to wrap, or an authorized merge
finishes the thread. Do not wrap an unfinished task; use `context-handoff` when
context is running out mid-task.

A merged stage in a tightly coupled staged set may refresh continuity and then
continue in-session. The discriminator is whether the thread is finished, not
whether a commit or PR exists.

## 2. Read the repository declaration

Read the repository declaration (the `AGENTS.md` chain) and identify:

- task tracker and completion state;
- handoff form, if any;
- changelog policy;
- memory policy;
- remote persistence and merge rules;
- authorization for every external write.

Where no surface is declared, skip it. Never create a GitHub handoff beside a
declared handoff file or vice versa.

## 3. Verify accumulated status

Use evidence collected during the session and refresh only the state that can
have changed:

```bash
git status --short
git log --oneline -5
```

When GitHub is in use, read back the relevant PR and issue state. Distinguish:

- committed, pushed, merged, and deployed;
- passing tests from tests not run;
- verified facts from assumptions;
- current-session changes from pre-existing worktree changes.

Do not sweep unrelated changes into the wrap.

## 4. Update each declared owner once

Apply the carrier rule:

| Fact | Owner |
|---|---|
| shipped change | declared changelog |
| architecture decision | ADR, plan, or decisions log |
| gotcha or hard-won reason | auto-memory |
| convention or procedure | repository docs |
| remaining task or decision | declared tracker |
| commit history | git |

For a completed issue, let `Closes #N` or `Fixes #N` close it on merge when that
is the repository convention. Remove an in-progress marker only after confirming
the task is complete. A partially advanced issue stays open with a concise
progress update.

Update a changelog only when the repository declares one and the change meets
its inclusion policy. Before writing memory, use `recall`; update an existing
memory rather than creating a duplicate.

## 5. Write the declared handoff

If the repository uses a handoff, write it for one fresh reader:

1. completed work with stable identifiers;
2. verified current state;
3. blockers and what clears them;
4. the next actionable item or tracker filter;
5. explicit assumptions and what was not changed.

Keep history out. For a file handoff, replace stale session state rather than
appending a diary. For a tracker handoff, follow the repository's declared
create/close lifecycle and read the result back. Transfer custody to the tracker
before closing a predecessor.

## 6. Persist and verify

Commit or push wrap changes only when requested or authorized by repository
policy. Capture the commit identifier after committing, then verify that the
intended remote contains it. A local commit, command URL, or successful exit code
is not proof of remote persistence.

If the wrap spans repositories, verify each independently. Do not claim a clean
tree if pre-existing changes remain; name them as untouched.

## 7. Final report

Return:

- completed work and stable identifiers;
- verification commands and results;
- tracker, changelog, memory, and handoff updates actually made;
- remote persistence status;
- remaining work and blockers;
- surfaces skipped because they were undeclared or unauthorized.

After a finished thread, start unrelated work in a fresh top-level session.
