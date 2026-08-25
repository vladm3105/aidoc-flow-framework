---
name: doc-chg
description: Author a Change Management (CHG) record - classify the change level, route by source to the entry gate, assess cross-layer cascade impact, and register the change. Use when modifying an existing SDD artifact across any of the 8 layers. Single-document authoring primitive; for end-to-end or batch generation the autopilot (`doc-chg-autopilot`) drives this skill.
metadata:
  tags:
    - sdd-workflow
    - change-management
  custom_fields:
    artifact_type: CHG
    skill_category: core-workflow
    version: "0.25.0"
    framework_spec_version: "0.42.0"
    last_updated: "2026-05-23"
---

# doc-chg

## Purpose

Author a **Change Management (CHG)** record — the governance overlay for
modifying existing SDD artifacts. CHG is **NOT a lifecycle layer**: no layer
number, no readiness score. Triggered on-demand when an artifact must change;
quality bar is **gate approval**, not a numeric score.

**Cross-layer scope**: a CHG can touch any artifact along
`BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code`. Job: classify,
route to the correct gate, trace the cascade, keep the registry honest.

## When to Use

Use `doc-chg` when:

- An existing artifact (any layer) needs a correction, refinement, or
  cross-layer change.
- A production incident forces an emergency fix that must be documented.
- An external trigger (regulatory, vendor, market) requires a controlled change.

Do **not** use it to author a brand-new artifact — use the relevant layer skill
(`../doc-brd/SKILL.md` … `../doc-iplan/SKILL.md`). For end-to-end CHG drafting
with minimal prompts, use `../doc-chg-autopilot/SKILL.md`.

## Prerequisites

Before writing, read:

1. **Template (source of truth):** `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml`
2. **CHG overview:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md`
3. **Index template:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-00_index.TEMPLATE.md`
4. **Authoring style:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`
5. **The entry gate** for the change source (see routing below), under
   `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/`.

Confirm no ID collision: `ls docs/governance/chg/ 2>/dev/null`. Reserve the next
free `CHG-NN` (dash form — CHG carries no hierarchical 4-segment element IDs).

## Change-Level Classification (decide first)

Classification drives the entire process. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml` (`metadata.change_level`).

| Level | Scope | Gate | Process |
|-------|-------|------|---------|
| **C1** | Typo, formatting, clarification | None | Fix → commit → done |
| **C2** | Section update, requirement refinement | Peer review | Assess impact → update → verify |
| **C3** | Cross-layer change, new requirements | Formal gate | Full CHG process + `GATE_APPROVAL_FORM` |
| **Emergency** | Critical production issue (P0/P1) | Post-hoc gate + post-mortem | Fix → deploy → document → post-mortem within 48h |

- **C1** needs no CHG document beyond the commit; record it if a registry trail
  is wanted, otherwise just commit.
- **C2** requires a CHG document with impact assessment, a rollback plan, and
  peer review.
- **C3** requires the full document plus a formal gate run — hand off to
  `../gate-check/SKILL.md`.
- **Emergency** uses ID format `CHG-EMG-YYYYMMDD-HHMM`, populates the
  `emergency_change` block, deploys the fix, then completes a post-mortem
  (`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/templates/POST_MORTEM-TEMPLATE.md`) and a **post-hoc
  gate** within 48 hours. All normal CHG sections are still filled retroactively.

## Source → Gate Routing

Where the change originates determines the **entry gate**. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md` and `CHG-TEMPLATE.yaml`
(`metadata.change_source`).

| Source | Trigger | Entry Gate | Cascade direction |
|--------|---------|-----------|-------------------|
| **Upstream** | BRD/PRD change cascading down | GATE-01 | downstream |
| **External** | Regulatory, vendor, market | GATE-01 | full assessment |
| **Midstream** | EARS/BDD/ADR change affecting neighbors | GATE-03 | lateral + down |
| **Design** | SPEC/TDD change | GATE-06 | downstream |
| **Execution** | IPLAN change | GATE-08 | downstream |
| **Feedback** | Production feedback, user/defect issues | GATE-CODE | bubble-up |
| **Spec** | Change to the `framework/` spec (template/governance/registry/VERSION) | GATE-SPEC | meta — no cascade |

Gate definitions live in `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/`
(`GATE-01_BUSINESS_PRODUCT.md`, `GATE-03_REQUIREMENTS_ARCHITECTURE.md`,
`GATE-06_DESIGN_TEST.md`, `GATE-08_IPLAN.md`, `GATE-CODE_IMPLEMENTATION.md`,
`GATE-SPEC_FRAMEWORK.md`). Running a gate is the job of `../gate-check/SKILL.md`;
`doc-chg` only selects the entry gate and records it.

**`Spec` is target-based, not layer-based.** A change to the `framework/`
spec itself sets `change_source: spec`, `entry_gate: GATE-SPEC`, and a
`semver_impact` (`major` → C3; `minor`/`patch` may be C2; spec change is
never C1). It does **not** cascade into artifact gates. A platform's own
authoring guidance / runtime is *not* a spec change — ordinary platform PR.

## Cross-Layer Cascade Assessment

The most common CHG failure is incomplete impact assessment. Trace the change
along the chain:

```
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
```

- **Upstream/External** changes cascade **downstream** — a BRD edit can ripple
  all the way to Code.
- **Feedback** changes **bubble up** from Code toward the layer that holds the
  root cause (the defect may live in TDD, SPEC, ADR, or higher).
- **Midstream** changes are **lateral** (EARS↔BDD↔ADR) plus downstream.

For every affected artifact, record in `impact_assessment.affected_layers`:
artifact ID, what changes, `cascade_direction`. Avoid the template's listed
anti-patterns (e.g. SPEC change without checking upstream ADR/BDD; BRD change
without cascading the full chain).

## Creation Process

1. **Classify** the change level (C1/C2/C3/Emergency) with justification.
2. **Identify the source** and **route** to the entry gate (table above).
3. **Reserve the ID** — next free `CHG-NN`, or `CHG-EMG-YYYYMMDD-HHMM` for
   Emergency.
4. **Populate `CHG-TEMPLATE.yaml`**: `metadata` (level, source),
   `change_control`, `change_description` (what/why/trigger),
   `impact_assessment` (affected layers + cascade direction + risk),
   `implementation`, `verification`. Add `rollback_plan` for C2/C3,
   `gate_approval` for C3, and `emergency_change` for Emergency.
5. **Register** the change in `CHG-00_index.md` (from
   `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-00_index.TEMPLATE.md`) in the same change.
6. **For C3/Emergency**, hand off to `../gate-check/SKILL.md` to run the formal
   gate and complete `GATE_APPROVAL_FORM`. For Emergency, also schedule the
   post-mortem.
7. **Validate** (below) and commit the CHG record and index together.

## Validation

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md`.

- [ ] `change_level` is one of C1/C2/C3/Emergency and matches the actual scope.
- [ ] `change_source` set and `entry_gate` matches the routing table.
- [ ] `impact_assessment.affected_layers` lists **every** affected artifact;
      `cascade_direction` is correct for the source.
- [ ] `rollback_plan` present for C2/C3; `gate_approval` present for C3;
      `emergency_change` block complete for Emergency (incl. `post_mortem_due`).
- [ ] Change registered in `CHG-00_index.md`; no broken links.
- [ ] CHG IDs use dash form `CHG-NN` (or `CHG-EMG-YYYYMMDD-HHMM`); no
      hierarchical element IDs.

| Code | Meaning | Severity |
|------|---------|----------|
| CHG-E001 | Change level missing or mismatched to scope | error |
| CHG-E002 | Entry gate does not match change source | error |
| CHG-E003 | Incomplete cascade / impact assessment | error |
| CHG-E004 | Missing rollback (C2/C3) or post-mortem schedule (Emergency) | error |

**Quality bar (not a score):** CHG passes by **gate approval**, not a ≥90
readiness score. C1 self-approves; C2 needs peer review; C3/Emergency need a
formal/post-hoc gate via `../gate-check/SKILL.md`.

## Next Skill

- C3/Emergency → `../gate-check/SKILL.md` (formal gate + `GATE_APPROVAL_FORM`).
- Validate the record → `../doc-chg-audit/SKILL.md`.
- After approval, edit the affected artifacts using their layer skills
  (`../doc-brd/SKILL.md` … `../doc-iplan/SKILL.md`).

## Related Resources

- Template: `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-TEMPLATE.yaml`
- Overview: `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/README.md`
- Index template: `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/CHG-00_index.TEMPLATE.md`
- Gates: `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/gates/`
- Post-mortem: `${CLAUDE_PLUGIN_ROOT}/framework/governance/chg/templates/POST_MORTEM-TEMPLATE.md`
- Gate runner: `../gate-check/SKILL.md`
- End-to-end: `../doc-chg-autopilot/SKILL.md` · Audit:
  `../doc-chg-audit/SKILL.md` · Fix: `../doc-chg-fixer/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Govern a change to an existing SDD artifact |
| **Lifecycle layer?** | No — cross-cutting governance overlay |
| **Element IDs** | `CHG-NN` (dash) / `CHG-EMG-YYYYMMDD-HHMM` |
| **Key decision** | Change level (C1/C2/C3/Emergency) + source routing |
| **Quality bar** | Gate approval, not a readiness score |
| **Next** | `gate-check` (C3/Emergency) |
