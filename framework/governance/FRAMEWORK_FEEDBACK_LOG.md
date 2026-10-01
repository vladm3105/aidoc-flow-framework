# Framework Feedback Log — Governance

## Document Control

| Field | Value |
|-------|-------|
| Version | 2.0 |
| Status | Approved |
| Last Updated | 2026-09-30 |
| Author | Framework Maintainer |
| Framework Version | 0.68.3 |

> v2.0 (0.67.0, CHG-23): Tier-1 consumer-project log retired — no operator
> since the example corpus was removed and consumer platforms archived; the
> issue tracker is the single capture surface. Filing discipline and the
> open-items surface are unchanged.

## Why this exists

Every project applying the framework is an empirical test of the spec.
Friction discovered during use — lint-rule misfires, harness flag absences,
engine prose that contradicts the spec, sync-script gotchas, missing
convenience features — is **new knowledge about the framework itself**.
Without a deliberate capture mechanism, that knowledge evaporates between
sessions and each new project rediscovers the same pain.

## The surface: GitHub issue tracker

**Who owns it:** the framework maintainer.

**Where it lives:** on the framework repository's issue tracker.

**Lifecycle:** issues are triaged → designed in a formal
`plans/<NAME>-PLAN.md` when large enough to design → shipped as PRs.
Merged PRs close issues with `Closes #N`.

### Capture and publication on the tracker

The people and agents a gap affects — consumer projects, other maintainers, a future
contributor — need visible tracking. Backlog capture and publication are unified
directly on the framework's issue tracker:

**An issue carries evidence, not a symptom.** Reproduction at `file:line`
plus the command that exercised it; blast radius (who else is affected —
check, do not assume); why it was hard to diagnose, when the symptom
misnames the cause; a concrete suggested fix; and what is **NOT** broken,
where that was checked. The last two are what make an issue actionable by
a non-finder, which is the whole point of opening one.

**One issue per defect.** Group only trivially-related items, and say
so up front. If an issue already exists, add the new evidence as a
**comment** rather than opening a second one. Closed issues are not reopened;
regressions get a new issue cross-linking the prior one.

**Verify what you published.** Filing tools can succeed while publishing an
empty body. Read the artifact back after filing or commenting and confirm
the body length is non-trivial; an empty issue discharges nothing.

**This applies to the framework's own gaps.** Defects owned by *another*
repo are a separate obligation — they get an issue on the owning repo,
because the fix belongs in that repo's files and recording it here would
reach nobody who can act on it.

## Entry format

One bullet per issue, ≤ 3 lines:

```markdown
- **<TAG> — Short title.** One-line statement of the issue.
  *Context:* link to commit / PR / plan / cascade-run that surfaced it.
  *Fix shape:* one-line description of what would resolve it.
```

Tags (non-exhaustive — use what fits):

- `[lint]` — `sdd_doc_lint` rule misfire / gap
- `[skill]` — an engine capability/prompt contradicts the spec
- `[template]` — a layer template field is wrong / unclear
- `[sync]` — a sync script behaviour is unexpected
- `[plan-review]` — plan-review process / verified-planning skill gap
- `[docs]` — framework documentation gap
- `[governance]` — issue with a governance doc / principle

## Don't double-track / don't gold-plate

- If a plan or issue already exists for an item, cross-reference it
  instead of creating a new entry.
- Entries are **observations, not designs**. 3-line cap. Designs go in
  `plans/<NAME>-PLAN.md`.
- An entry without a clear *Context* or *Fix shape* is incomplete and
  will be hard to triage. Spend the 30 seconds to capture both.

## Recorded upstream threads

Upstream issue references recorded here so a future session finds the
thread instead of rediscovering the defect as a fresh bug
(SELF_LEARNING.md §7.4 step 3). Session-start duty: review the open
threads below before planning work (§7.4 step 4).

| Thread | Status |
|--------|--------|
| CHG-23 vehicle (Tier-1 retirement + worktree-mandate, 0.67.0) | In progress |

## Relationship to other governance docs

- **Principle 8 (Change-of-record discipline):** upstream threads recorded
  here follow the same in-PR discipline.
- **`REVIEW_TEAM.md`:** auditor findings that surface framework gaps
  (vs. artifact gaps) belong on the tracker, not just the audit
  report. The audit report flags the artifact; the tracker flags
  the framework.
- **`DECISIONS.md`:** non-obvious decisions made while addressing a
  feedback entry get an ISO-stamped decision record. The tracker entry
  references the decision; the decision rationale lives in
  `DECISIONS.md`.
