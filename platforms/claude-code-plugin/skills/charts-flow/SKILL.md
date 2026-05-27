---
name: charts-flow
description: Create and manage Mermaid architecture diagrams as separate, traceable files linked to their parent SDD documents. Use when adding or migrating diagrams for BRD, PRD, ADR, SPEC, or IPLAN documents.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    version: "0.2.0"
    framework_spec_version: "0.8.1"
    last_updated: "2026-05-23"
---

# charts-flow

## Purpose

Generate and maintain Mermaid architecture diagrams for SDD documents. Diagrams
live in separate `diagrams/` files next to their parent document — keeping the
parent lean to render — and stay traceable back to that parent through a stable
diagram ID and a back-reference link.

This is the single diagram skill for the plugin: all Mermaid generation,
validation, and SVG rendering lives here.

## When to Use

Use `charts-flow` when:

- Adding an architecture diagram (flowchart, sequence, class, state, component,
  or deployment) to a BRD, PRD, ADR, SPEC, or IPLAN.
- Migrating an existing inline `mermaid` block into a separate diagram file.
- A parent document renders slowly because of complex inline diagrams, or a
  diagram needs to be reused across documents.

Do **not** use it for simple tables/lists (use markdown), tiny diagrams that
render fine inline, or non-architecture charts (Gantt, pie) that fall outside
the SDD diagram contract.

## Behavior

**Create a new diagram**

1. Derive the parent document ID from its filename (e.g. `PRD-01`) and locate
   its folder.
2. Create `diagrams/` beside the parent if absent, and write
   `{PARENT-ID}-diag_{description}.md` containing a Document Control block
   (parent link, diagram type, dates), an overview, the `mermaid` block, and a
   References section linking back to the parent.
3. Render an SVG (`mmdc` CLI if available, otherwise Mermaid Live), validate the
   syntax, and embed the SVG preview in the parent inside a collapsible
   `<details>` block with a link to the diagram file.

**Migrate inline diagrams**

- Scan the parent for `mermaid` blocks, move each into its own diagram file
  (numbering multiples), then replace the original block with the SVG preview
  plus a reference link, preserving document flow.

**Supported types**: flowchart/graph, sequence, class, state, component, and
deployment. Each diagram file follows the same Document Control + References
structure so cross-references resolve in both directions.

**Diagram contract (per layer)**: diagrams attach to the layers that own visual
models — BRD (C4 L1 + DFD L1), PRD (C4 L2 + DFD L2 + key sequence), ADR
(decision sequences), SPEC (C4 L3 + DFD L3). Use the `@diagram:` tags the layer
template specifies and follow `${CLAUDE_PLUGIN_ROOT}/framework/governance/DIAGRAM_STANDARDS.md`.

**Quality gates**: diagram file in the correct `diagrams/` folder; name matches
`{PARENT-ID}-diag_{description}.md`; Document Control with parent back-link;
valid Mermaid syntax; SVG embedded; all cross-references resolve; SVG < 1 MB.

## Related Resources

- Diagram standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/DIAGRAM_STANDARDS.md`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Layer templates that own diagrams:
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/PRD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Roadmap visuals: `../adr-roadmap/SKILL.md`
- Mermaid: <https://mermaid.js.org/> · <https://mermaid.live>
