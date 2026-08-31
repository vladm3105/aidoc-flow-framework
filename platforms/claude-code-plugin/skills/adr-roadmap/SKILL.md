---
name: adr-roadmap
description: Generate a phased implementation roadmap from a set of Architecture Decision Records, with dependencies, timeline, risk, and testing strategy. Use when coordinating delivery of multiple ADRs.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    upstream_artifacts: [ADR]
    downstream_artifacts: [SPEC, TDD, IPLAN]
    version: "0.25.0"
    framework_spec_version: "0.47.0"
    last_updated: "2026-05-23"
---

# adr-roadmap

## Purpose

Analyze a project's Architecture Decision Records (ADRs, Layer 5) and produce a
phased implementation roadmap: dependency mapping, critical path, phase
decomposition, timeline estimates, per-phase risk assessment, and a testing and
technical-debt strategy. Engine-agnostic — works for any domain (web, mobile,
data, ML, infrastructure, embedded).

**Upstream**: ADR. **Downstream**: feeds SPEC → TDD → IPLAN delivery sequencing.

## When to Use

Use `adr-roadmap` when:

- A project has roughly five or more ADRs that need coordinated, phased rollout.
- You need visibility into architectural dependencies and the critical path.
- Stakeholders need a timeline, milestones, and an executive summary derived
  from ADR complexity.

Do **not** use it for a single ADR with a trivial implementation, for
informational ADRs with no build work, when planning from requirements (use
`../doc-brd/SKILL.md` / `../doc-prd/SKILL.md` / `../doc-ears/SKILL.md`), or when
you only need diagrams (use `../charts-flow/SKILL.md`).

## Behavior

1. **Inventory ADRs** — read every `ADR-*.md`, extract ID, title, status,
   complexity (1–5), effort, and dependencies; warn on missing complexity or
   broken dependency references; error if no ADRs are found.
2. **Build the dependency graph** — classify hard / soft / no dependencies,
   detect cycles (error), compute the critical path, and find clusters that can
   run in parallel.
3. **Estimate effort** — map complexity to base effort, sum across ADRs, apply a
   risk buffer (~20%), and flag high-risk ADRs (complexity 4–5 with many deps).
4. **Form phases** — apply the chosen phase model (`poc-mvp-prod` default,
   `iterative`, or `waterfall`), respecting dependencies, capping phase length
   (default 8 weeks), isolating risk, and ending phases on natural milestones.
   Adapt for greenfield, brownfield/migration (add rollback + dual-run), or
   refactoring (module-by-module) projects.
5. **Build the timeline** — derive phase durations from effort and team size,
   add inter-phase buffers, and produce a Gantt chart (via
   `../charts-flow/SKILL.md`) with milestones.
6. **Write the roadmap** at `{adr_dir}/ADR-00_IMPLEMENTATION-ROADMAP.md`:
   Document Control, executive summary, per-phase sections (objectives, ADRs,
   architecture diagram, order, deliverables, success/exit criteria, risk),
   dependency matrix, technical-debt management, risk assessment, testing
   strategy, and traceability back to upstream (BRD–BDD) and downstream
   (SPEC/TDD/IPLAN) artifacts.

**Constraints**: use ADR decisions as-is (make no technology choices); map every
ADR to exactly one phase; never exceed the phase cap; keep language objective;
require rollback plans for production phases. Keep each document under 100k
tokens.

## Related Resources

- ADR layer: `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/README.md` ·
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-TEMPLATE.yaml`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Traceability: `${CLAUDE_PLUGIN_ROOT}/framework/governance/TRACEABILITY.md`
- Diagrams: `../charts-flow/SKILL.md`
- Downstream generation: `../doc-spec/SKILL.md` · `../doc-tdd/SKILL.md` ·
  `../doc-iplan/SKILL.md`
- Traceability check: `../doc-validator/SKILL.md`
