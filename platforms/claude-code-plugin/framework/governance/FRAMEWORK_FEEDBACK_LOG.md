# Framework Feedback Log — Governance

> Codifies the two-tier feedback pipeline introduced by
> `DOC_GOVERNANCE_CORE.md` Principle 9 (example-driven / project-driven
> framework improvement).

## Why this exists

Examples are the system-under-test (see [`AIDOC.md`](../docs/AIDOC.md) — the
seed examples double as acceptance tests). Every consumer
project applying the framework is an additional empirical test of the
spec. Friction discovered during use — lint-rule misfires, harness
flag absences, engine prose that contradicts the spec, sync-script
gotchas, missing convenience features — is **new knowledge about the
framework itself**. Without a deliberate capture mechanism, that
knowledge evaporates between sessions and each new project
rediscovers the same pain.

## Two-tier pipeline

### Tier 1 — Consumer project: `framework-feedback-log.md`

**Who owns it:** the team building a project that uses the framework.

**Where it lives:** at the consumer project's root (alongside
`README.md` / `CLAUDE.md` / `plans/`). One log per project.

**What it records:** every framework friction the project hits while
applying the framework. Examples (non-exhaustive):

- A lint rule fires on an artifact that semantically should pass
- A harness flag is missing for a workflow the project needed
- An engine's prose contradicts the current spec
- A sync script's behavior is unexpected (silent overwrite, wrong
  direction, missing target)
- A template field has unclear semantics
- An auditor playbook lens scores the project's artifact in a way that
  doesn't reflect the spec's intent
- A workflow gap (e.g., no fixer for a class of finding) forces the
  project to either bypass or hand-edit (the latter being forbidden —
  never hand-edit example artifacts — so the gap itself
  goes in the feedback log)

**Update cadence:** inline as discovered, the moment friction surfaces.
No "later PR" — the entry IS the capture moment. Same discipline as
the framework-side TODO (see Tier 2 below).

**Surfacing upstream:** periodically (per release, per milestone, or on
demand) the project owner reviews their `framework-feedback-log.md`
and surfaces actionable entries back to the framework via PR or
upstream issue on the framework repository's issue tracker. Stale, project-specific, or
already-resolved entries can be archived locally without surfacing.

### Tier 2 — Framework repo: GitHub issue tracker

**Who owns it:** the framework maintainer.

**Where it lives:** on the framework repository's issue tracker.

**What it records:** the framework's own backlog, sourced from:

- The framework team's own example-driven testing (cascading against
  `examples/<NAME>/` corpora — the canonical acceptance tests).
- Surfaced items from consumer-project `framework-feedback-log.md`
  files when they bubble up via PR / issue / explicit submission.

**Lifecycle:** issues are triaged → designed in a formal
`plans/<NAME>-PLAN.md` when large enough to design → shipped as PRs.
Merged PRs close issues with `Closes #N`.

### Tier 2: capture and publication on the tracker

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

## Entry format (both tiers)

One bullet per issue, ≤ 3 lines:

```markdown
- **<TAG> — Short title.** One-line statement of the issue.
  *Context:* link to commit / PR / plan / cascade-run that surfaced it.
  *Fix shape:* one-line description of what would resolve it.
```

Tags (non-exhaustive — use what fits):

- `[lint]` — `sdd_doc_lint` rule misfire / gap
- `[harness]` — `tests/scripts/test-acceptance.sh` or cascade flow
- `[skill]` — an engine capability/prompt contradicts the spec
- `[template]` — a layer template field is wrong / unclear
- `[sync]` — a sync script behaviour is unexpected
- `[plan-review]` — plan-review process / verified-planning skill gap
- `[docs]` — framework documentation gap
- `[platform-parity]` — parity gap deferred from a change in one platform implementation
- `[example-corpus]` — issue with an `examples/<NAME>/` corpus
- `[governance]` — issue with a governance doc / principle

## Don't double-track / don't gold-plate

- If a plan or issue already exists for an item, cross-reference it
  instead of creating a new entry.
- Entries are **observations, not designs**. 3-line cap. Designs go in
  `plans/<NAME>-PLAN.md`.
- An entry without a clear *Context* or *Fix shape* is incomplete and
  will be hard to triage. Spend the 30 seconds to capture both.

## Template for consumer projects

A scaffold for the project-side `framework-feedback-log.md` ships at
[`../templates/framework-feedback-log.template.md`](../templates/framework-feedback-log.template.md).
Projects copy that template into their root + start logging.

## Relationship to other governance docs

- **Principle 8 (Change-of-record discipline):** the feedback log is a
  *doc-of-record* in any project that maintains one. Updates to it
  follow the same in-PR discipline.
- **`REVIEW_TEAM.md`:** auditor findings that surface framework gaps
  (vs. artifact gaps) belong in the feedback log, not just the audit
  report. The audit report flags the artifact; the feedback log flags
  the framework.
- **`DECISIONS.md`:** non-obvious decisions made while addressing a
  feedback entry get an ISO-stamped decision record. The feedback
  entry references the decision; the decision rationale lives in
  `DECISIONS.md`.
