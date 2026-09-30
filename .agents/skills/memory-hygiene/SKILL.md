---
name: memory-hygiene
description: >-
  Check and repair a project memory store: index drift, dangling links, slug titles, bloated hooks, content misplaced in MEMORY.md, and missing indexes. Not for task recall or deciding what deserves memory.
---

# Memory hygiene

> Muse project-skill instance — adapted from the canon global skill
> (`aidoc-flow-claude-agents-config/skills/memory-hygiene/`, private).
> Claude-specific-to-neutral wording mirrors
> `framework/skills/memory-hygiene/` (engine-agnostic adaptation of this same
> skill). Paths below use `<skills-root>` = the skills root for your engine
> (here: `.agents/skills/`).

Nothing reads the memory store except the loader, so drift is silent and
compounds. Measured on 2026-08-12 across 14 stores and 341 memories: one store
(`-opt-data-techtrend-AI-cost-monitoring`) had spent **six months** holding all
of its content inline in `MEMORY.md` with zero memory files, and three others
carried link or bloat defects. None of it surfaced, because nothing looked.

## Resolve the store

```sh
SLUG=$(printf '%s' "$PWD" | sed 's#[/_.]#-#g')
MEMDIR=<repo-declared-memory-store>
```

The slug maps `/`, `_` **and** `.` to `-` — verified against every store on
disk, including `…runner-local--work-…` (`_work`) and `-opt-data-trading-nexus-v4-2`
(`v4.2`). Case is preserved, not lowercased.

**The rule is derived from the directory names, not from harness source, so it
must fail loudly.** If `$MEMDIR` is absent, list `<repo-declared-memory-stores>/` and look
for a store whose slug matches before concluding there is none. *"Could not
resolve a store for this path"* and *"this project has no memories"* are
different statements and only the second may be acted on.

The slug keys on the session's **start directory**, not the repo, so one repo
can own several project directories. Counts here are per-directory.

## Run it

```sh
python3 <skills-root>/memory-hygiene/lint.py "$MEMDIR" --brief   # one line, read-only
python3 <skills-root>/memory-hygiene/lint.py "$MEMDIR"           # full report, exit 1 on any violation
python3 <skills-root>/memory-hygiene/lint.py "$MEMDIR" --fix     # deterministic repairs only — see the gate below
```

## What it checks

| Check | Defect | Remedy |
|---|---|---|
| `MEMORY.md` is an index | prose, tables or code where one-line pointers belong | **manual — never `--fix`** |
| index exists | memories on disk with no `MEMORY.md` | reindex |
| index 1:1 with files | orphan files · stale pointers · duplicates | reindex |
| `[[links]]` resolve | dangling wiki-links; unambiguous ones are auto-fixable | `--fix`, else manual |
| `name` == filename stem | frontmatter drifted from the filename | `--fix` |
| no slug titles | index titles that are filenames rather than prose | reindex / retitle |
| hook text ≤ 300 chars | an index line that has become the memory | compact |

## The `--fix` gate

**`--fix` does two things only: rewrite `name:` fields to match the filename,
and repoint unambiguous `[[links]]`.** It tars every file it is about to write
into `.backups/lint-fix-<ts>.tar.gz` first.

**It must never act on the content-in-index or missing-index checks, and does
not.** Splitting a content-bearing `MEMORY.md` is a judgement call about what is
still true — and that file is frequently the *only* copy of what it holds. The
techtrend store above is exactly that case: its index carries a GHES host, org,
project-board and field IDs recorded nowhere else. An automated repair there
destroys unbacked data. `--brief` flags it; a human splits it.

**Read `--brief` for a store before ever running `--fix` on it.** A store you
have not looked at is a store whose "drift" might be deliberate.

## Registering it as a hook

A `SessionStart` hook running `--brief` is safe — read-only, one line, `|| true`.

**A `SessionEnd` hook running `--fix` is not a routine change.** It is an
autonomous write across every store, which `approval-gate` § Tiers (the 🔴 row,
*"never autonomous … destructive data operations"*) tiers 🔴. Route it through `approval-gate`
rather than adding it as a step, and only after `--brief` has been read for
**every** store the hook would reach — not a sample.

Both live in the engine settings file, which is deliberately untracked, so a
hook is unversioned and invisible to review. Removing the skill directory does
**not** remove the hook; unregister it explicitly.

## Red flags

| Thought | Reality |
|---|---|
| "The store reported clean, so it's fine" | Clean means *these* invariants hold. Upstream reported the worst store clean because it had no check for its defect. |
| "I'll just `--fix` it" | `--fix` cannot repair the two defects that matter most, by design. |
| "No memory dir, so no memories" | You may have resolved the path wrong. Distinguish unresolved from empty. |
| "It's only an index" | For six months the index *was* the memory. Losing it loses the data. |
| "I'll enable the SessionEnd hook while I'm here" | That is a 🔴 autonomous write over 341 files. It needs a human. |

## Provenance

`lint.py` is adapted from
[`GlassOnTin/claude-memory-skills`](https://github.com/GlassOnTin/claude-memory-skills)
`skills/memory-lint/lint.py` (MIT), retrieved 2026-08-12. Three changes, each
prompted by running it against the real stores — an unguarded `MEMORY.md` open
that crashed on an index-less store, plus the two checks upstream lacks
(content-in-index, missing-index). The header of `lint.py` records them.
