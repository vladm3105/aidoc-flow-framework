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
    framework_spec_version: "0.3.0"
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

1. **Template (source of truth):** `framework/layers/01_BRD/BRD-TEMPLATE.yaml`
2. **Layer README:** `framework/layers/01_BRD/README.md`
3. **ID & tag standards:** `framework/governance/ID_NAMING_STANDARDS.md`

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

- **Platform BRD** populates Section 3.6 (Technology Stack Prerequisites) and
  3.7 (Mandatory Technology Conditions).
- **Feature BRD** marks 3.6/3.7 as `N/A — See Platform BRD-NN §3.6/§3.7` and
  references the specific items.

### Required structure (18 sections)

`## Document Control` comes **first**, before all numbered sections (project
name, version, date `YYYY-MM-DD`, owner, prepared-by, status, revision-history
table). Then:

1. Introduction · 2. Business Objectives · 3. Project Scope · 4. Stakeholders ·
5. User Stories · 6. Functional Requirements · 7. Quality Attributes
(incl. **7.2 Architecture Decision Requirements**) · 8. Constraints &
Assumptions · 9. Acceptance Criteria · 10. Business Risk Management ·
11. Implementation Approach · 12. Support & Maintenance · 13. Cost-Benefit ·
14. Project Governance (incl. 14.5 Approval) · 15. Quality Assurance ·
16. Traceability · 17. Glossary (17.1–17.6) · 18. Appendices.

See `BRD-TEMPLATE.yaml` for per-section content and `cross_section_rules`.

### Section 7.2 — Architecture Decision Requirements (mandatory)

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

Each `Selected` topic carries a `BRD.NN.07.xxxx` element ID and includes a
status, business driver, business constraints, an **Alternatives Overview**
table (with cost estimates), a **Cloud Provider Comparison** (GCP/Azure/AWS), a
recommended selection, and the PRD requirements it implies. Layer separation:
BRD §7.2 = *what & why & how much*; PRD = *how to evaluate*; ADR = *the decision*.

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
   `framework/layers/01_BRD/BRD-00_index.TEMPLATE.md`.
4. **Document Control first**, then complete all 18 sections from the template.
5. **Handle 3.6/3.7** per type; **fill §7.2** across the 7 categories.
6. **Configure upstream mode** (`none` default; `ref` if from `docs/00_REF/`).
7. **Update the BRD index** `docs/01_BRD/BRD-00_index.md` in the same change.
8. **Validate** (below) and commit the BRD and index together.

## Validation

The framework ships no runtime code — **this skill is the validator**. Apply the
checklist against `framework/layers/01_BRD/README.md` and
`framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] Document Control is the first section.
- [ ] All 18 sections present and non-empty; 3.6/3.7 correct for the BRD type.
- [ ] §7.2 covers all 7 categories; no ADR numbers referenced.
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
defines product features and KPIs, and inherits the §7.2 architecture topics.


## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor only this skill's declared knobs:
`section_toggles` (include or omit template-declared **optional** sections)
and `glossary` (substitute preferred terms in generated prose). Ignore any
unknown or out-of-surface key; absent a profile, use framework defaults.
Authority: `framework/governance/ADAPTATION.md`.

## Related Resources

- Template / authoring rules: `framework/layers/01_BRD/BRD-TEMPLATE.yaml`
- Layer README: `framework/layers/01_BRD/README.md`
- Index template: `framework/layers/01_BRD/BRD-00_index.TEMPLATE.md`
- ID & tag standards: `framework/governance/ID_NAMING_STANDARDS.md`
- Quality gate: `../doc-brd-audit/SKILL.md` · Fixes: `../doc-brd-fixer/SKILL.md`
- Generation pipeline: `../doc-brd-autopilot/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Define business needs and objectives |
| **Layer** | 1 (entry point) |
| **Upstream tags** | None |
| **Key decision** | Platform vs Feature |
| **Must include** | Document Control (first), §7.2 (7 categories), 18 sections |
| **Next** | `doc-prd` |
