---
name: doc-brd
description: Create a Business Requirements Document (BRD) - Layer 1 of the SDD flow, defining business needs, objectives, and success criteria. Use when starting a new project or feature.
metadata:
  tags:
    - sdd-workflow
    - layer-1-artifact
  custom_fields:
    layer: 1
    artifact_type: BRD
    skill_category: core-workflow
    upstream_artifacts: []
    downstream_artifacts: [PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.8.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary]
---

# doc-brd

## Purpose

Create a **Business Requirements Document (BRD)** — Layer 1 of the SDD flow.
A BRD captures business objectives, stakeholder needs, scope, and success
criteria in business language, before any product or technical detail.

**Layer**: 1 — entry point, no upstream artifacts.
**Downstream**: PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code.

Each BRD represents **one MVP iteration** (5–15 focused requirements). New
features get a new BRD rather than expanding an existing one; link cycles with
`@depends: BRD-NN`.

## When to Use

Use `doc-brd` when:

- Starting a new project or feature and defining business requirements.
- Documenting strategic alignment, market context, and success criteria.
- Translating an implementation plan back into business-language requirements.

For end-to-end generation from reference docs, a prompt, or an IPLAN, use
`../doc-brd-autopilot/SKILL.md`. For a new project skeleton, run
`../project-init/SKILL.md` first.

## Prerequisites

BRD is the entry point, so there are no upstream artifacts to verify. Before
writing, read:

1. **Template (source of truth):** `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml`
2. **Layer README:** `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/README.md`
3. **ID & tag standards:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`

Confirm no ID collision: `ls docs/01_BRD/ 2>/dev/null`. Never invent
placeholders like `BRD-XXX` or reference documents that do not yet exist.

## Layer Guidance

### Platform vs Feature BRD (decide first)

| Signal | Type |
|--------|------|
| Defines infrastructure, technology stack, or cross-cutting concerns | **Platform** |
| Other BRDs will depend on its architectural choices | **Platform** |
| Describes one user-facing workflow / feature | **Feature** |
| Builds on capabilities an existing Platform BRD established | **Feature** |

- **Platform BRD** — file `BRD-NN_platform_{slug}`; ADRs are created **before**
  the PRD to validate architectural choices; §8 (Architecture Decision Topics)
  is populated with the Selected categories that downstream BRDs will depend on.
- **Feature BRD** — file `BRD-NN_{feature_slug}`; standard layer flow
  (BRD → PRD → EARS → BDD → ADR); §8 references the Platform BRD's adopted
  topics rather than introducing new architectural decisions.

### Required structure (15 sections)

`document_control` is **Section 1** (project name, version, date `YYYY-MM-DD`,
owner, prepared-by, status, revision-history table). Then:

2. Executive Summary (OPTIONAL — derived; toggled by `section_toggles`) ·
3. Introduction · 4. Business Objectives · 5. Project Scope · 6. Stakeholders ·
7. Functional Requirements · 8. Architecture Decision Topics (`adr_topics`) ·
9. Quality Expectations · 10. Constraints and Assumptions ·
11. Acceptance Criteria and Success Validation · 12. Business Risk Management ·
13. Approval · 14. Traceability · 15. Glossary.

The template additionally defines two structural blocks alongside the numbered
sections: a **Diagrams Registry** (`diagrams:`) and a **Lifecycle Reference**
appendix (`appendix:`) — see those template keys for the required shape. Section
numbers and section identifiers come from the template's own numbering and
top-level YAML keys; **the template is the source of truth**, and this skill's
list is a navigation aid, not a parallel definition.

See `BRD-TEMPLATE.yaml` for per-section content and `cross_section_rules`.

### Section 8 — Architecture Decision Topics (mandatory)

Identify architectural topics needing decisions, with cost-focused,
alternatives-based analysis, across the 7 categories. **Do not reference ADR
numbers** — ADRs do not exist yet.

| # | Category | When N/A |
|---|----------|----------|
| 1 | Infrastructure | Pure data/analytics project |
| 2 | Data Architecture | No persistent data |
| 3 | Integration | Standalone system |
| 4 | Security | Internal tool, no sensitive data |
| 5 | Observability | MVP/prototype only |
| 6 | AI/ML | No AI/ML components |
| 7 | Technology Selection | Using an existing stack |

Each `Selected` topic carries a `BRD.NN.08.xxxx` element ID and includes a
status, business driver, business constraints, an **Alternatives Overview**
table (with cost estimates), a **Cloud Provider Comparison** (GCP/Azure/AWS), a
recommended selection, and the PRD requirements it implies. Layer separation:
BRD §8 = *what & why & how much*; PRD = *how to evaluate*; ADR = *the decision*.

### Element IDs and tags

- Hierarchical element IDs: `BRD.{doc_id}.{section_id}.{hash}` (e.g.
  `BRD.01.07.a7f3`; `hash` = first 4 hex of SHA256 of
  `"{doc_id}:{section_id}:{title}:{description}"`, extend to 8 on collision).
- BRD is Layer 1, so it carries **no `@` upstream tags**. Downstream artifacts
  tag it: `@brd: BRD.01.06.a7f3`.
- **Removed patterns** (do not use): `AC-XXX`, `FR-XXX`, `BO-XXX`, `BC-XXX`,
  and the legacy 3-segment `BRD.NN.xxxx`.

### Upstream source configuration

Most BRDs are authored from stakeholder input — keep the default
`upstream_mode: "none"`. Only when content derives from `docs/00_REF/` docs set
`upstream_mode: "ref"` and list `upstream_ref_path` (relative to the BRD file).

## Creation Process

1. **Determine type** — Platform vs Feature (table above).
2. **Reserve ID** — next free `BRD-NN` (two digits, no leading zero beyond two:
   `BRD-01`, `BRD-99`, `BRD-102`).
3. **Create the nested folder** — every BRD lives in `docs/01_BRD/BRD-NN_{slug}/`
   regardless of size. Monolithic: `BRD-NN_{slug}.md` inside it; section-based
   (>25 KB): `BRD-NN.S_{section}.md` + index from
   `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-00_index.TEMPLATE.md`.
4. **Document Control (Section 1) first**, then complete the 14 remaining
   required sections + the diagrams registry + appendix per template; toggle §2
   (Executive Summary) per `section_toggles`.
5. **Fill §8** (Architecture Decision Topics) across the 7 categories.
6. **Configure upstream mode** (`none` default; `ref` if from `docs/00_REF/`).
7. **Update the BRD index** `docs/01_BRD/BRD-00_index.md` in the same change.
8. **Validate** (below) and commit the BRD and index together.

## Validation

The framework ships no runtime code — **this skill is the validator**. Apply the
checklist against `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/README.md` and
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] Document Control (Section 1) is the first section.
- [ ] All required template sections present and non-empty: §1, §3–§15, plus
      the diagrams registry and appendix; §2 Executive Summary only when
      `section_toggles` includes it. Enumerate by reading `BRD-TEMPLATE.yaml`.
- [ ] §8 covers all 7 ADR-topic categories; no ADR numbers referenced.
- [ ] Element IDs match `BRD.NN.SS.xxxx`; no removed patterns.
- [ ] Traceability matrix / index created or updated; no broken links.
- [ ] Diagram contract: `@diagram: c4-l1` and `@diagram: dfd-l1` present (use
      `../charts-flow/SKILL.md`); add a sequence tag if a sequence diagram
      exists.

| Code | Meaning | Severity |
|------|---------|----------|
| XDOC-006 | Tag format invalid | error |
| XDOC-008 | Broken internal link | error |
| XDOC-009 | Missing traceability section | error |

**Quality gate (blocking):** PRD-Ready score ≥ 90/100 before moving on. If
issues are found, fix and re-check; if unfixable, log for manual review.

> **BRD-REF documents** (`BRD-REF-NNN_{slug}.md`, via `../doc-ref/SKILL.md`) are
> free-format reference targets — exempt from ready-scores, cumulative tags, and
> quality gates.

## Next Skill

`../doc-prd/SKILL.md` — the PRD references this BRD (`@brd: BRD.NN.SS.xxxx`),
defines product features and KPIs, and inherits the §8 architecture topics.

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor only this skill's declared knobs:
`section_toggles` (include or omit template-declared **optional** sections)
and `glossary` (substitute preferred terms in generated prose). Ignore any
unknown or out-of-surface key; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Template / authoring rules: `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml`
- Layer README: `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/README.md`
- Index template: `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-00_index.TEMPLATE.md`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Quality gate: `../doc-brd-audit/SKILL.md` · Fixes: `../doc-brd-fixer/SKILL.md`
- Generation pipeline: `../doc-brd-autopilot/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Define business needs and objectives |
| **Layer** | 1 (entry point) |
| **Upstream tags** | None |
| **Key decision** | Platform vs Feature |
| **Must include** | §1 Document Control, §3–§15 required sections, §8 (7 categories), diagrams registry, appendix |
| **Next** | `doc-prd` |
