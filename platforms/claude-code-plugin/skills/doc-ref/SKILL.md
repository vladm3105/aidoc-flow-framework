---
name: doc-ref
description: Create Reference Documents (REF) - free-format supplements for BRD and ADR that sit outside the formal traceability chain. Use for project overviews, strategic vision, or technology/infrastructure summaries.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    upstream_artifacts: [BRD, ADR]
    downstream_artifacts: []
    version: "0.2.0"
    framework_spec_version: "0.9.1"
    last_updated: "2026-05-23"
---

# doc-ref

## Purpose

Create **Reference Documents (REF)** — free-format supplementary documents that
support a **BRD or ADR** without participating in the formal traceability
chain. REF documents provide context (overviews, summaries, guides); they carry
no element IDs, cumulative tags, ready-scores, or quality gates.

**Layer**: cross-cutting utility — REF documents are limited to **BRD and ADR
parent types only**.

## When to Use

**Use** `doc-ref` for supplements such as:

- **BRD-REF** — project overviews, executive summaries, strategic vision,
  stakeholder guides.
- **ADR-REF** — technology-stack summaries, architecture overviews,
  infrastructure guides.

**Do NOT use** for: anything that should participate in traceability; core
artifacts (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN — use their `doc-*` skills); or
any parent type other than BRD or ADR.

## Behavior

### Naming and location

- File name: `{TYPE}-REF-NN_{slug}.md` (`TYPE` ∈ {BRD, ADR}); H1:
  `# {TYPE}-REF-NN: Title`.
- `NN` is a variable-length sequence (2+ digits), independent per parent type:
  `BRD-REF-01`, `BRD-REF-102`, `ADR-REF-01` are separate sequences.
- Located inside the parent type directory, e.g.
  `docs/01_BRD/BRD-REF-01_project_overview.md`,
  `docs/05_ADR/ADR-REF-01_technology_stack_summary.md`.
- Regex — file: `^(BRD|ADR)-REF-[0-9]{2,}_[a-z0-9_]+\.md$`;
  H1: `^#\s(BRD|ADR)-REF-[0-9]{2,}:.+$`.

### Creation process

1. **Determine the parent type** — business context → BRD-REF; architecture
   context → ADR-REF.
2. **Allocate the next number** — `ls docs/01_BRD/*-REF-* 2>/dev/null` (or
   `05_ADR`) and take the next free `NN`.
3. **Draft from the parent template, stripped to REF essentials** — start from
   `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml` (BRD-REF) or
   `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-TEMPLATE.yaml` (ADR-REF) and keep only the four
   mandatory sections, dropping the traceability scaffolding.
4. **Place** the file in the parent type directory with the correct H1.

### Required sections (4, mandatory)

1. YAML frontmatter (`artifact_type: REF`).
2. Document Control (version, date, author, status).
3. Document Revision History.
4. Introduction (purpose and scope).

Optional: Related Documents (cross-references encouraged) and any content
sections the reference material needs.

### Validation (this skill is the validator)

Blocking checks only: H1 matches `{TYPE}-REF-NN: Title`; Document Control,
Revision History, and Introduction sections are present. **Exempt** (not
checked): cumulative tags, full traceability, quality gates, ready-scores —
REF documents do not participate in the chain. No element IDs apply.

## Related Resources

- Parent templates: `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-TEMPLATE.yaml`
- Naming authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md` ·
  `../doc-naming/SKILL.md`
- Governance & per-layer authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/` and each
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/NN_<X>/README.md`
- Parent skills: `../doc-brd/SKILL.md` · `../doc-adr/SKILL.md`
- Workflow routing: `../doc-flow/SKILL.md`
- Diagrams: `../charts-flow/SKILL.md`
