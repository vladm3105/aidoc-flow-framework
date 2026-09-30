---
name: recall
description: >-
  Retrieve only memories relevant to the current task through a read-only subagent. Use after task selection, before writing memory, or before governance and release actions; not for memory-store repair.
---

# Recall

> Muse-local instance of the recall workflow. Engine-agnostic wording follows
> `framework/skills/recall/` (itself adapted from the canon
> `aidoc-flow-claude-agents-config/skills/recall/SKILL.md`); where the canon
> names a Claude-specific agent type or path, use the Muse equivalent below and
> keep the independence contract.

`MEMORY.md` is auto-loaded, but it is an index and it grows without bound — 127
lines in one store on 2026-08-12, and nothing trims it. So a standing
instruction can be **in the store and absent from context**, which is the worst
of the two failure modes: it looks like the memory system ran.

This skill spends a subagent's context instead of yours. The subagent reads the
whole store; you receive the handful that matter.

## 1. Resolve the store

```sh
SLUG=$(printf '%s' "$PWD" | sed 's#[/_.]#-#g')
MEMDIR=<repo-declared-memory-store>
```

**`memory-hygiene` owns this rule** — its § *Resolve the store* carries the
derivation, the verified cases and the fallback. Two things from it are
load-bearing here:

- If `$MEMDIR` is absent, **list `<repo-declared-memory-stores>/` and match** before
  concluding anything.
- *"Could not resolve a store"* and *"this project has no memories"* are
  different results. Only the second may be acted on. Reporting the first as
  the second is precisely the failure this skill exists to prevent.

## 2. Establish the task

In order:

1. the argument passed to this skill;
2. else the issue picked in `start-session` §3;
3. else the most recent user request, in one line;
4. else **no-task mode** — see §5.

## 3. Dispatch the triage

One read-only subagent (your engine's `Explore` equivalent; if no named
read-only type exists, a delegate with read-only file tools and an explicit
model — never an untier-ed default):

```
Read every *.md in <MEMDIR>, plus MEMORY.md. For each file, read its frontmatter
`name` and `description`, and open the body only when the description looks
relevant. Task: <the task>.
Return ONLY the memories that bear on that task.
Per hit: name · one line on why it is relevant · the body verbatim if under ~15
lines, else the path. Return nothing rather than padding.
```

The subagent's context absorbs the store. Yours does not.

## 4. Report

State which of the three results you got, in these words:

| Result | Means |
|---|---|
| `N relevant memories` | the store was read and these bear on the task |
| `no relevant memories` | the store was read and none bear on the task |
| `could not resolve a store` | §1 failed — **not** the same as empty |

**Return nothing rather than something weak.** A padded recall teaches the
reader to skim it, and a skimmed recall is worse than none because it looks like
the check ran.

## 5. No-task mode

At cold session start there may be no task yet. Then return the store's
**standing instructions** only — memories whose `metadata.type` is `feedback`
(measured 2026-08-12: 195 across all stores) — and defer task-scoped triage
until work is picked.

`type` is nested under `metadata`, not top-level. The values in use are
`feedback`, `project` and `reference`; **`user` is schema-valid but has zero
instances**, so do not filter on it alone and conclude the store is empty.

## Red flags

| Thought | Reality |
|---|---|
| "Memory is auto-loaded, so I have it" | The index is loaded. The store is bigger than the index, and the index truncates. |
| "No memory dir, so no memories" | You may have resolved the path wrong. Distinguish unresolved from empty. |
| "I'll read MEMORY.md myself" | That spends your context on the index and still misses the bodies. Dispatch. |
| "I'll include these five, they might help" | Padding trains the reader to skim. Return the ones that bear on the task. |
| "The store looks fine" | Integrity is `memory-hygiene`. This skill does not check it. |
