---
name: workflow-optimizer
description: Determine current position in the 8-layer SDD workflow and recommend prioritized next steps, parallel-work opportunities, and progress metrics. Use after completing an artifact or when unsure what to create next.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    version: "0.2.0"
    framework_spec_version: "0.4.0"
    last_updated: "2026-05-23"
---

# workflow-optimizer

## Purpose

Guide a user through the 8-layer SDD workflow (BRD → PRD → EARS → BDD → ADR →
SPEC → TDD → IPLAN → Code). It locates the current position from completed
artifacts, recommends prioritized next steps with rationale, surfaces work that
can proceed in parallel, and reports progress — removing the friction of
manually deciding what to build next.

## When to Use

Use `workflow-optimizer` when:

- You just completed an artifact and need next-step guidance.
- You are starting documentation and want a workflow overview.
- You want to find parallel-work opportunities or a progress report.

Do **not** use it to pick a skill for a specific task (use
`../skill-recommender/SKILL.md`), to gather project context (use
`../context-analyzer/SKILL.md`), or to validate artifacts (use
`../trace-check/SKILL.md` or `../quality-advisor/SKILL.md`).

## Behavior

Given a `project_root` (and optionally a just-completed artifact and a focus
filter), the skill:

1. **Analyzes project state** — discovers artifacts and extracts status (Draft,
   In Review, Approved, Superseded, Deprecated) from Document Control, producing
   counts by type.
2. **Determines workflow position** — maps artifacts to layers 1–8 (each with a
   single-layer prerequisite per the cumulative chain), marking layers as
   completed, in-progress, ready, or blocked, and computes a progress
   percentage.
3. **Identifies required next steps** — uses the dependency chain to list
   mandatory next artifacts, prioritized P0/P1/P2 with rationale and what each
   unblocks.
4. **Finds parallel opportunities** — independent BRD/PRD tracks, ADRs that can
   be drafted concurrently, and BDD scenarios that can start once EARS
   requirements exist; notes items blocked by missing upstream layers.
5. **Calculates progress metrics** — per-layer status and the critical path
   (EARS → BDD → ADR → SPEC → TDD → IPLAN).
6. **Generates recommendations** — concrete next actions naming the layer skill
   to run (e.g. `../doc-ears/SKILL.md`), parallel suggestions, blocked items
   with unblock paths, and a progress summary.

## Related Resources

- Layer registry (layers & prerequisites):
  `framework/registry/LAYER_REGISTRY.yaml`
- Traceability: `framework/governance/TRACEABILITY.md`
- Layer skills: `../doc-brd/SKILL.md` … `../doc-iplan/SKILL.md`
- Related skills: `../context-analyzer/SKILL.md` ·
  `../skill-recommender/SKILL.md` · `../doc-flow/SKILL.md`
