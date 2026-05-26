---
name: context-analyzer
description: Scan a project's SDD artifacts and build a context model (inventory, traceability graph, workflow position, upstream candidates) to inform new document creation. Use before authoring an artifact in an existing project.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    version: "0.2.0"
    framework_spec_version: "0.8.0"
    last_updated: "2026-05-23"
---

# context-analyzer

## Purpose

Scan a project's documentation and assemble a context model so a new artifact is
authored with full awareness of what already exists. It surfaces the artifact
inventory, parsed metadata, the traceability graph, current workflow position,
and the most relevant upstream documents — preventing missing references and
duplicate content.

## When to Use

Use `context-analyzer` when:

- Starting documentation work in an existing project.
- About to create an artifact that needs upstream references.
- You need to understand what documentation exists or where the gaps are.
- Preparing context for a `doc-*` skill invocation.

Do **not** use it on a project with no existing documentation, for a single
isolated document, or for deep traceability validation (use
`../trace-check/SKILL.md`).

## Behavior

Given a `project_root` (and optionally a `target_artifact_type` and a scan
`depth` of quick / standard / deep), the skill:

1. **Scans structure** — enumerates artifacts under `docs/<NN>_<X>/` (01_BRD …
   08_IPLAN) by type, ID, path, title, and status.
2. **Parses metadata** — extracts frontmatter and Document Control (status,
   version, last-updated, tags) per artifact.
3. **Extracts traceability** — reads each artifact's Traceability section into a
   bidirectional upstream/downstream graph.
4. **Determines workflow position** — maps artifacts to layers 1–8, identifies
   completed / current / next-required layers, and reports coverage gaps using
   the cumulative upstream rules (BRD→…→IPLAN).
5. **Identifies upstream candidates** — for a target type, ranks relevant
   upstream documents by directness, topic match, recency, and status.
6. **Extracts key terms** — builds project vocabulary from titles, headers, and
   glossaries.
7. **Returns the context model** — inventory counts, workflow position with
   gaps, ranked upstream candidates, key terms, and coverage gaps.

The model is consumed by `../skill-recommender/SKILL.md`,
`../workflow-optimizer/SKILL.md`, `../quality-advisor/SKILL.md`, and the
`doc-*` authoring skills. For deep traceability validation it defers to
`../trace-check/SKILL.md`.

## Related Resources

- Layer registry (layers, `can_reference`):
  `framework/registry/LAYER_REGISTRY.yaml`
- Traceability: `framework/governance/TRACEABILITY.md`
- ID & tag standards: `framework/governance/ID_NAMING_STANDARDS.md`
- Layer READMEs: `framework/layers/02_PRD/README.md` ·
  `framework/layers/05_ADR/README.md`
- Related skills: `../skill-recommender/SKILL.md` ·
  `../workflow-optimizer/SKILL.md` · `../quality-advisor/SKILL.md` ·
  `../trace-check/SKILL.md`
