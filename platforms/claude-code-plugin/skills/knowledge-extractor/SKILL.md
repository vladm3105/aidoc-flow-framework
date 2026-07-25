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
    version: "0.23.4"
    framework_spec_version: "0.38.0"
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
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md` §7). Diff the profile against framework
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

- **Spec target → a CHG record.** Shape it to
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml` with `change_source: spec`,
  `entry_gate: GATE-SPEC`, and a `semver_impact` (additive → `minor`, breaking →
  `major`); carry **provenance** (the learnings entries + profile keys that
  motivated it) in `change_description.why` / `.trigger`. Hand it to
  `../doc-chg/SKILL.md` to complete the record and `../gate-check/SKILL.md` to
  run **GATE-SPEC**, the framework-spec change gate
  (`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md`). A human approves;
  the extractor never opens a PR or grants approval.
- **Engine-guidance target → a PR-ready change description.** Name the file, give
  a before/after, and carry the same provenance. This is an ordinary platform
  change, **not** a CHG record (per `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md` §7).

### 5. Hand off

Present the drafts grouped by path, with the idiosyncratic items listed as
"kept local". Never apply, open, or approve — a human decides.

## Output contract

| Target | Artifact | Carries | Status |
|--------|----------|---------|--------|
| framework spec | CHG record (`change_source: spec` → GATE-SPEC) | provenance | ready for GATE-SPEC review |
| engine guidance | PR-ready change description | provenance (file, before/after) | ready for ordinary review |
| neither | "kept local" note | rationale | no action |

## Related Resources

- Signal source: `../project-profile/SKILL.md`, `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md` (§7 learnings log)
- CHG authoring: `../doc-chg/SKILL.md`; template `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml`
- Spec gate: `../gate-check/SKILL.md` → `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md`

## Quick Reference

| Step | Action |
|------|--------|
| 1 | Read profile + learnings; diff vs defaults |
| 2 | Judge generalizable vs idiosyncratic (recurrence ↑, conflict ↓) |
| 3 | Classify owner: spec → CHG/GATE-SPEC, guidance → PR |
| 4 | Draft + provenance (spec record routed to GATE-SPEC) |
| 5 | Hand off; never apply/approve |
