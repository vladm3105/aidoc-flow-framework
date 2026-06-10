---
name: project-profile
description: Create and maintain a project's adaptation profile (.aidoc/profile.yaml) - the closed set of preferences the SDD skills honor. Use to tailor the flow to a project without forking the framework.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    upstream_artifacts: []
    downstream_artifacts: []
    version: "0.13.0"
    framework_spec_version: "0.17.0"
    last_updated: "2026-05-23"
---

# project-profile

## Purpose

Author and maintain a project's **adaptation profile** — the version-controlled
`.aidoc/profile.yaml` that tailors how the SDD skills author and audit
artifacts, without forking the framework. The profile is a *closed, declarative*
set of preferences; the authority for what may appear in it is
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md` and its machine-readable companion
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION_SURFACE.yaml`.

**Layer**: cross-cutting utility (precedes and informs the layer skills).

## When to Use

**Use when**:

- A project needs to deviate from framework defaults — run a leaner layer set,
  toggle an optional section, tighten an audit gate, or apply house terminology.
- Onboarding a project that has a developer house style to carry in (the
  user-global seed, below).
- Reviewing or refreshing an existing `.aidoc/profile.yaml`.

**Do NOT use to**:

- Author or audit an artifact — use the layer skills (`../doc-brd/SKILL.md` …).
- Promote a local adaptation upward into the framework — that is the
  `../knowledge-extractor/SKILL.md` job.

## Behavior

The framework ships no runtime code — this skill is the profile author. It
writes only keys that exist in the closed surface and silently drops the rest.

### 1. Resolve scopes

- **Project profile** — `.aidoc/profile.yaml` (the runtime input; what the
  skills read). Version-controlled, so audits stay reproducible in CI.
- **User-global seed** — `~/.aidoc/profile.yaml` (optional). A developer's
  cross-project house preferences. It is **not** read at runtime; it is merged
  in here, at authoring time, and the result is materialized into the project
  profile.

Effective precedence: `framework defaults < user-global seed < project answers`.

### 2. Infer the starting point

Lean on `../doc-flow/SKILL.md`'s context scan rather than re-scanning: use its
inventory to propose `active_layers` (which layers the project already uses),
spot recurring optional sections, and collect domain terms as `glossary`
candidates. Do not duplicate its scan.

### 3. Interview (within the closed surface only)

Confirm or adjust each of the four v1 knobs:

| Knob | Question | Constraint |
|------|----------|-----------|
| `active_layers` | Which layers are in play? | May disable only the **skippable** set (`ADAPTATION_SURFACE.yaml`: `BDD`, `ADR`); mandatory layers stay. |
| `section_toggles` | Any optional sections to include/omit? | Template-declared **optional** sections only. |
| `audit_threshold` | Any layer's quality gate to tighten? | **Raise-only** — a value must be `>=` the layer's framework default. |
| `glossary` | Preferred terms? | `default → project` term map; applied to generated prose only. |

### 4. Validate against the surface

Parse `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION_SURFACE.yaml` and enforce it:

- drop any key not in `knobs`;
- reject disabling a mandatory layer; apply the `cascade_rule` for any disabled
  skippable layer;
- reject (do not write) an `audit_threshold` below the framework default;
- keep only template-declared optional sections in `section_toggles`.

### 5. Materialize and write

Merge per the precedence above and write `.aidoc/profile.yaml`, including
`schema_version` (matching the surface's `schema_version`). The file is the
single runtime input — commit it. Example:

```yaml
schema_version: "1.0.0"
active_layers: [BRD, PRD, EARS, SPEC, TDD, IPLAN]   # BDD, ADR skipped (cascade applied)
section_toggles:
  ADR: { security: on }
audit_threshold:
  ADR: 95          # >= framework default
glossary:
  "user": "account holder"
```

### 6. Hand off

Report what changed and direct the user to `../doc-flow/SKILL.md`. From now on
the adapting skills consult `.aidoc/profile.yaml`; `../project-init/SKILL.md`
and `../project-adopt/SKILL.md` scaffold only the active layers.

## Related Resources

- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`
- Surface registry: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION_SURFACE.yaml`
- Context scan: `../doc-flow/SKILL.md`
- Scaffolding: `../project-init/SKILL.md`, `../project-adopt/SKILL.md`
- Promote adaptations upward: `../knowledge-extractor/SKILL.md`
- Next: `../doc-flow/SKILL.md`

## Quick Reference

| Step | Action |
|------|--------|
| 1 | Resolve project profile + user-global seed |
| 2 | Infer starting point via `doc-flow`'s context scan |
| 3 | Interview across the 4 knobs |
| 4 | Validate against `ADAPTATION_SURFACE.yaml` |
| 5 | Materialize + write `.aidoc/profile.yaml` (commit it) |
| 6 | Hand off to `doc-flow` |
