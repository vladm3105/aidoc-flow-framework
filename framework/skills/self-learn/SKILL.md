---
name: self-learn
description: >-
  Capture, consolidate, and apply durable lessons from session work. Use after significant work, when corrected, on a schedule, or at session start to apply prior lessons; not for one-off facts that belong in memory or a handoff.
---

# Self-learn

> Framework adaptation — engine-agnostic copy of the canon global skill.
> Source: `aidoc-flow-claude-agents-config/skills/self-learn/SKILL.md` (private, 2026-09-27).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Engine mapping: Claude Code `<skills-root>/<name>/`, Codex `<skills-root>/<name>/`, generic `<skills-root>/<name>/`.
> Where the canon names a Claude-specific agent type, use your engine's focused read-only subagent equivalent and keep the independence contract.


A lesson learned twice and written nowhere will be learned a third time. This
skill is the shared loop over the repo-declared memory store (project memory,
session checkpoint, `recall`, `memory-hygiene`): where the active repository
declares its own learning spec or store, that declaration is authoritative for
categories, qualification, and file paths, and this skill defers to it.

The loop has three modes. Run only the mode the situation calls for.

| Mode | When | Cost |
|---|---|---|
| `apply` | session start, after task selection | cheap — read, don't write |
| `capture` | mid-work, when a correction or hard-won gotcha lands | cheap — one entry, one place |
| `consolidate` | after significant work, on schedule, when patterns recur | expensive — full cycle §4–§7 |

## 1. Resolve the stores

| Store | Location | Purpose |
|---|---|---|
| Learnings | `.aidoc/learning/learnings.md` (repo-owned system of record, by PR) | this loop's home — harness memory is the scratch inbox, resolved per `recall` §1 |
| Session state | the harness's session checkpoint / notes (filenames resolved at runtime, never assumed) | extraction sources |
| Verbatim recovery | the harness's trajectory store, if it exposes one | exact payloads when memory paraphrases |
| Project learning log | only where the repository declares one (own path, own schema) | repo-owned audit trail |

Portable sources work everywhere: `git log`, the repo tracker, and the current
session's own notes. Harness-specific rows above are best-effort — when the
harness exposes no checkpoint, notes, or trajectory store, run the loop on the
portable sources alone rather than failing. Memory summaries keep intent but
drop literals; real evidence lives in the session's discovered-knowledge and
errors-and-fixes records, the trajectory store's tool-input rows (when one
exists), and `git log`.

If the store has no consolidated knowledge yet, that is a finding
(`no learnings yet`), not an error.

## 2. Apply (session start)

After `start-session` (the `recall` step with the selected task), add one step:
check consolidated learnings for the same task. Same query, narrower scope —
read headings and open only entries whose category or title bears on the task.
Standing governance (the repository's `CLAUDE.md`, `AGENTS.md`, declared
governance docs) remains the authority; a learning never overrides it.

Report in the same words as `recall`: `N relevant learnings` or `no relevant
learnings` (or `no learnings yet`). Return nothing rather than something weak —
a padded injection trains the reader to skim it.

## 3. Capture (mid-work)

A pattern qualifies when: observed 2+ times across sessions, **or** caused a
user correction, **or** required a governance rule. A user saying "don't do X"
or "do Y instead" always qualifies, first occurrence.

Write the entry where it survives the session, exactly once:

| Fact | Owner |
|---|---|
| correction or hard-won gotcha, not yet a pattern | harness session checkpoint / notes (candidate, not yet learning) |
| confirmed pattern | consolidated learnings in the project memory store (entry below) |
| durable cross-session fact | project memory via the `wrap-session` carrier |
| actionable defect in owned code/docs | `submit-feedback`, never only a learning entry |

Entry format (match the store's existing schema — do not invent a new one):

```markdown
## [category] Title
- **First seen**: YYYY-MM-DD
- **Last seen**: YYYY-MM-DD
- **Count**: N
- **Lesson**: What to do / avoid
- **Evidence**: file:line or command, verified against source
- **Governance rule**: file §section, or omit if none yet
```

Suggested categories: `error`, `workflow`, `tool-usage`, `project-rule`,
`preference`, `governance`. Use the system clock for dates — a future-dated
entry is a defect.

## 4. Consolidate (full cycle)

### 4.1 Gather evidence

1. Note error-heavy and correction-heavy recent sessions (from the handoff,
   tracker, or `git log`). Skip incomplete trajectories.
2. For each flagged session, read its session checkpoint (discovered knowledge,
   errors and fixes) and notes using whatever filenames the harness provides.
   For verbatim payloads (exact IDs, hashes, revision text) query the harness
   trajectory store when one is exposed — curated memory keeps intent but drops
   literals. With no trajectory store, reconstruct from `git log` (hashes,
   files, commands) and the session's own notes.
3. Verify every candidate against source before writing: `grep` the cited
   `file:line`, re-parse config after quoting the claim, confirm counts from the
   files rather than from prose. Index documents and prior summaries drift;
   **audit citations you author yourself, not just a subagent's.**
4. Run `recall` with the consolidation scope before writing — update an
   existing entry or memory rather than creating a duplicate.

### 4.2 Update learnings

- New pattern: add an entry per §3.
- Recurrence: bump `Count`, set `Last seen`, keep the latest verified evidence.
- Stale: entries unobserved for 30+ days archive (per `memory-hygiene`), never
  vanish by deletion.
- Promote entries with count >= 5 to durable project memory (routing resolved
  per `recall` §1) — and only those.

### 4.3 Update governance (when warranted)

Only for governance-relevant patterns: a missing rule, a broken process, a new
constraint. Rules:

1. **Only add, never remove** safety invariants unless provably wrong.
2. **Cite the learning** in the update.
3. **Keep updates small** — one rule or sentence per learning.
4. Critical rules violated 2+ times need multi-location enforcement (learnings
   + project memory + `AGENTS.md`/`CLAUDE.md` + governance doc) — a single
   location does not hold. Rules without an enforcement mechanism (lint,
   validation, pre-commit check) stay advisory.
5. **Pass the owning repo's authorization gate first.** Governance writes go
   through whatever plan or approval gate the repository declares — a learning
   never exempts itself from it.

### 4.4 File feedback for governance changes

Route each change to owned code, docs, or upstream dependencies through
`submit-feedback` (search before filing; safe body-file mechanics; read back
the write). Changes that belong to another repository go to that repository's
tracker, never silently into this one.

### 4.5 Hygiene

- After editing, validate: structured files still parse, no secrets or PII in
  any entry.
- Record the cycle (new / updated / aged-out counts, governance files modified
  with what changed, feedback issue URLs) where the next session will find it:
  session notes and the memory store, or the repository's declared learning log.

## 5. Write discipline

- The primary agent captures and consolidates. **Subagents do not write to the
  consolidated store** — they report findings to the parent, which verifies and
  writes.
- One owner per write: a learning entry, a memory promotion, and a governance
  update for the same lesson land in one pass, by one agent — not scattered
  across concurrent siblings.
- Verify critical writes by reading back: at least 3 specific changes for file
  writes, issue-view read-back for filed feedback.

## 6. Authorization

Route through `approval-gate` before:

- 🟡 editing governance docs beyond the additive one-rule scope, or any edit
  the repository policy reserves to the user;
- 🟡 filing any external issue (prepare the draft, then stop and surface it
  unless standing authorization covers self-learn feedback);
- 🔴 touching stores outside the active project, running `--fix`-class repairs
  (that's `memory-hygiene`), or force-pushing anything.

Standing authorization, where granted in writing, executes the prior decision —
it is not self-approval. When unsure of the tier, take the higher one.

## 7. Report

Return:

- mode run and scope (sessions/dates covered);
- N new / N updated / N aged-out learnings;
- N memory promotions (target files);
- N governance modifications (file + one-line what-changed each);
- N feedback issues (identifiers + read-back result, or drafts held for
  approval with exactly which approval is missing);
- hygiene actions (archives written, validation results).

## Red flags

| Thought | Reality |
|---|---|
| "The trajectory log shows what happened" | It shows metadata. Evidence is in the session knowledge/error records, the trajectory store (when one exists), and git. |
| "I'll write learnings straight from the summary" | Summaries paraphrase; verify every `file:line`, count, and ID against source first. |
| "The subagent can append its finding directly" | Subagents report; the parent verifies and writes. Direct appends bypass dedupe. |
| "This rule is documented, so it's enforced" | Documented without lint/validation is advisory. Add the mechanism or say advisory. |
| "One place is enough for a critical rule" | Violated-twice rules need all locations. Single-location updates already failed elsewhere. |
| "A `result: Pass` from before my edit still holds" | Re-earn verification after the last edit. Inherited passes are stale. |
| "Self-learn can write governance docs directly" | It trips the owning repo's authorization gate. §4.3 rule 5 first. |
