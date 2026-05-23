---
name: knowledge-extractor
description: On demand, mine a project's adaptation profile + learnings log, judge which local adaptations are generalizable, and draft a promotion proposal routed to the right governance owner. Use when a proven local tweak might belong in the framework.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    upstream_artifacts: []
    downstream_artifacts: []
    version: "0.2.0"
    framework_spec_version: "0.1.0"
    last_updated: "2026-05-23"
---

# knowledge-extractor

## Purpose

Promote proven local adaptations *upward* — turn a project's accumulated
adaptation into a **drafted promotion proposal**, routed to the governance owner
that actually controls the target. It is **manual and on-demand**: a developer
runs it when a local tweak looks generally useful. It **only drafts and routes**
— it never edits the framework, never opens a PR, and never approves anything.

**Layer**: cross-cutting utility (governance-facing; not a lifecycle layer).

## When to Use

**Use when**:
- A project's `.aidoc/profile.yaml` / `.aidoc/learnings.md` shows a recurring
  adaptation that might belong in the framework.
- Reviewing whether local deviations should be standardized.

**Do NOT use to**:
- Create or maintain the profile — that is `../project-profile/SKILL.md`.
- Author a change record or run a gate yourself — this skill *drafts* the input;
  `../doc-chg/SKILL.md` and `../gate-check/SKILL.md` own the CHG process.

## Behavior

The framework ships no runtime code — this skill is the analyst. It reads,
classifies, and drafts; a human takes each draft into the right path.

### 1. Read the signal

Load `.aidoc/profile.yaml` and `.aidoc/learnings.md` (entry shape:
`framework/governance/ADAPTATION.md` §7). Diff the profile against framework
defaults to list the project's active deviations.

### 2. Judge generalizability (manual)

For each deviation decide *generalizable* vs *project-idiosyncratic*. Weigh —
do not let either decide alone:
- **`recurrence`** (higher → stronger signal it is not a one-off);
- **`conflict: true`** (the project overrode the developer's own seed → weaker;
  a per-project exception is less likely to be universal);
- whether the rationale is project-specific or speaks to the artifact in general.

Idiosyncratic items **stay local** — say so explicitly and stop there.

### 3. Classify the target owner

For each generalizable item, decide what it would actually change:

| If the change is to… | Owner | Path |
|----------------------|-------|------|
| a template, a governance rule, or the registry (`framework/`) | framework spec | **CHG** (change management) |
| how an engine *guides authoring* (a skill's checklist/wording) | the platform | **ordinary platform review (PR)** |

### 4. Route and draft

- **Spec target → a CHG draft.** Shape it to
  `framework/governance/chg/CHG-TEMPLATE.yaml`, carry **provenance** (the
  learnings entries + profile keys that motivated it), and stamp it
  **`BLOCKED — needs the CHG spec-change gate (not yet built)`**: the spec-change
  gate does not exist yet, so this draft cannot be run through `../gate-check/`
  today. Hand the draft to `../doc-chg/SKILL.md` for a human to carry forward
  when the gate lands.
- **Engine-guidance target → a PR-ready change description.** Name the file, give
  a before/after, and carry the same provenance. This is an ordinary platform
  change, **not** a CHG record (per `framework/governance/ADAPTATION.md` §7).

### 5. Hand off

Present the drafts grouped by path, with the idiosyncratic items listed as
"kept local". Never apply, open, or approve — a human decides.

## Output contract

| Target | Artifact | Carries | Status |
|--------|----------|---------|--------|
| framework spec | CHG draft (CHG-TEMPLATE shape) | provenance | blocked on spec-change gate |
| engine guidance | PR-ready change description | provenance (file, before/after) | ready for ordinary review |
| neither | "kept local" note | rationale | no action |

## Related Resources

- Signal source: `../project-profile/SKILL.md`, `framework/governance/ADAPTATION.md` (§7 learnings log)
- CHG authoring: `../doc-chg/SKILL.md`; template `framework/governance/chg/CHG-TEMPLATE.yaml`
- Gate (spec path, once built): `../gate-check/SKILL.md`

## Quick Reference

| Step | Action |
|------|--------|
| 1 | Read profile + learnings; diff vs defaults |
| 2 | Judge generalizable vs idiosyncratic (recurrence ↑, conflict ↓) |
| 3 | Classify owner: spec → CHG, guidance → PR |
| 4 | Draft + provenance (spec draft stamped blocked-on-gate) |
| 5 | Hand off; never apply/approve |
