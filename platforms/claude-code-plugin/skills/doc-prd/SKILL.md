---
name: doc-prd
description: Create a Product Requirements Document (PRD) - Layer 2 of the SDD flow, defining product features, personas, success metrics, and acceptance criteria from an upstream BRD. Use after a BRD exists and before EARS.
metadata:
  tags:
    - sdd-workflow
    - layer-2-artifact
  custom_fields:
    layer: 2
    artifact_type: PRD
    skill_category: core-workflow
    upstream_artifacts: [BRD]
    downstream_artifacts: [EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.22.0"
    framework_spec_version: "0.23.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary]
---

# doc-prd

## Purpose

Create a **Product Requirements Document (PRD)** — Layer 2 of the SDD flow.
A PRD defines product features, personas, success metrics, and acceptance
criteria at the **C4 Container** level (what the product does, not how).

**Layer**: 2 (Container level). **Upstream**: BRD.
**Downstream**: EARS → BDD → ADR → SPEC → TDD → IPLAN → Code.

One PRD per BRD iteration cycle (MVP → PROD → new MVP). New scope gets a new
PRD; link cycles with `@depends: PRD-NN`.

## When to Use

Use `doc-prd` when:

- A BRD exists and you need to define product features and user requirements.
- Translating business needs into product capabilities, personas, and KPIs.
- Elaborating BRD §8 architecture topics into technical options for ADR.

For end-to-end generation from a BRD, a prompt, or an IPLAN, use
`../doc-prd-autopilot/SKILL.md`.

## Prerequisites

PRD requires an upstream BRD. Before writing, read:

1. **Upstream BRD** — the BRD that drives this PRD. If it is split into section
   files (`docs/01_BRD/BRD-NN_{slug}/`), read **all** files as one logical
   document.
2. **Template (source of truth):** `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/PRD-TEMPLATE.yaml`
3. **Layer README:** `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/README.md`
4. **ID & tag standards:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
5. **Authoring style:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`

Confirm no ID collision: `ls docs/02_PRD/ 2>/dev/null`. Reference only BRD
elements that exist; never invent placeholders like `BRD-XXX` or `TBD`. The PRD
ID need not match the BRD ID (PRD-09 may implement BRD-16).

## Layer Guidance

### Content boundaries (decide what belongs here)

PRD is the **Container** level. Keep product capabilities, user journeys, and
error handling; push everything else downstream.

| Content | Belongs in |
|---------|-----------|
| Product features, personas, KPIs, journeys | **PRD** (this layer) |
| `WHEN-THE-SHALL-WITHIN` formal requirements | EARS (Layer 3) |
| `Given-When-Then` executable scenarios | BDD (Layer 4) |
| Architecture decisions | ADR (Layer 5) |
| Schemas, endpoints, infra config | SPEC (Layer 6) |

### Required structure (15 sections)

`document_control` comes **first** (product name, version, status, dates,
author/reviewer/approver, `@brd:` reference, EARS-Ready score, revision
history). Then:

2. Executive Summary (incl. MVP hypothesis) · 3. Problem Statement ·
4. Target Audience & User Personas · 5. Success Metrics & KPIs ·
6. Goals & Objectives · 7. Scope & Requirements · 8. User Stories & User Roles ·
9. Functional Requirements (incl. **user journey** + diagram contract) ·
10. **Customer-Facing Content & Messaging** · 11. Acceptance Criteria ·
12. Constraints & Assumptions · 13. Risk Assessment · 14. Traceability
(incl. **ADR topic elaboration**) · 15. Glossary.

See `PRD-TEMPLATE.yaml` for per-section content and embedded `_guidance`.

### Section 8 — User Stories (layer separation, mandatory note)

Hold **role definitions and story summaries** (`As a [role], I want
[capability] so that [benefit]`) with product-level acceptance criteria only.
Include the note: *detailed behaviors live in EARS; executable scenarios live
in BDD.* Do **not** write WHEN-THE-SHALL or Given-When-Then here.

### Section 10 — Customer-Facing Content (mandatory, blocking)

Must carry substantive content in **at least 3** categories: product
positioning, key messaging, feature descriptions, documentation, help text,
error messages, success confirmations, onboarding, release notes.
Placeholder-only content is a blocking error.

### Section 14 — ADR topic elaboration

Elaborate BRD §8 topics with **technical options and evaluation criteria**.
Layer separation: BRD = *what & why* · PRD = *how to evaluate* · ADR = *the
decision*. **Do not reference ADR numbers** — ADRs do not exist yet.

### Element IDs and tags

- Hierarchical element IDs: `PRD.{doc_id}.{section_id}.{hash}` (e.g.
  `PRD.01.09.b3f2`; `hash` = first 4 hex of SHA256 of
  `"{doc_id}:{section_id}:{title}:{description}"` from PRD content, extend to 8
  on collision). `SS` is the **section the element lives in** — no numeric
  type-codes.
- PRD is Layer 2, so it carries **`@brd:`** tags (e.g.
  `@brd: BRD.01.07.a7f3`). Downstream artifacts tag it: `@prd: PRD.01.09.b3f2`.
- **Removed patterns** (do not use): `FR-XXX`, `US-XXX`, `AC-XXX`, `F-XXX`, and
  the legacy 3-segment `PRD.NN.xxxx`.
- Quantitative values that may change use `@threshold: PRD.NN.{category}.{key}`
  (categories: quota, risk, perf, timeout, rate).

## Creation Process

1. **Read the parent BRD** — all section files as one document; extract
   objectives, stakeholders, success criteria, and §8 topics.
2. **Reserve ID** — next free `PRD-NN` (two digits: `PRD-01`, `PRD-99`,
   `PRD-102`).
   *Per-layer independence (CLEANUP-PR-F item 18):* pick the next-free
   number in YOUR layer's index — the upstream's number is NOT your number
   (doc numbers are per-layer sequential and independent; see
   `framework/governance/ID_NAMING_STANDARDS.md` §Cross-layer cardinality).
3. **Create the nested folder** — every PRD lives in
   `docs/02_PRD/PRD-NN_{slug}/` regardless of size. Monolithic:
   `PRD-NN_{slug}.md` inside it; section-based (>25 KB): `PRD-NN.S_{section}.md`
   - index from `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/PRD-00_index.TEMPLATE.md`.
4. **Document Control first**, then complete all 15 sections from the template.
5. **Fill §10** (≥3 customer-facing categories); **elaborate §14** ADR topics
   without ADR numbers.
6. **Add `@brd:` tags** resolving to existing BRD elements.
7. **Update the PRD index** `docs/02_PRD/PRD-00_index.md` and add this PRD to
   the parent BRD's Downstream Artifacts in the same change.
8. **Validate** (below) and commit the PRD, index, and BRD update together.

## Validation

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/README.md` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] Document Control is the first section, with `@brd:` reference and
      EARS-Ready score.
- [ ] All 15 sections present and non-empty.
- [ ] §10 has substantive content in ≥3 categories (not placeholders).
- [ ] §8 holds PRD-level summaries only, with the layer-separation note.
- [ ] §14 elaborates ADR topics; no ADR numbers referenced.
- [ ] Element IDs match `PRD.NN.SS.xxxx`; `SS` equals the host section; no
      removed patterns.
- [ ] `@brd:` tags resolve to existing BRD elements.
- [ ] Traceability / index updated; parent BRD updated; no broken links.
- [ ] Diagram contract: `@diagram: c4-l2` and `@diagram: dfd-l2` present (use
      `../charts-flow/SKILL.md`); sequence diagrams include `alt/else`.

| Code | Meaning | Severity |
|------|---------|----------|
| XDOC-002 | Missing required upstream tag (`@brd`) | error |
| XDOC-006 | Tag format invalid | error |
| XDOC-008 | Broken internal link | error |
| XDOC-009 | Missing traceability section | error |

**Quality gate (blocking):** EARS-Ready score ≥ 90/100 before moving on. If
issues are found, fix and re-check; if unfixable, log for manual review.

## Next Skill

`../doc-ears/SKILL.md` — the EARS references this PRD (`@prd: PRD.NN.SS.xxxx`)
and formalizes PRD features into `WHEN-THE-SHALL-WITHIN` requirements. (Per the
necessary-upstream contract, EARS itself only requires `@prd`; upstream BRD
lineage is reachable transitively via the @-tag chain.)

## Adaptation

Read `.aidoc/profile.yaml`; honor only this skill's knobs
(`section_toggles`, `glossary`). Ignore unknown keys; absent a profile, use
framework defaults. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Template / authoring rules: `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/PRD-TEMPLATE.yaml`
- Layer README: `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/README.md`
- Index template: `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/PRD-00_index.TEMPLATE.md`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Upstream BRD: `../doc-brd/SKILL.md`
- Quality gate: `../doc-prd-audit/SKILL.md` · Fixes: `../doc-prd-fixer/SKILL.md`
- Generation pipeline: `../doc-prd-autopilot/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Define product features, personas, and KPIs |
| **Layer** | 2 (Container) |
| **Upstream tags** | `@brd` (per necessary-upstream contract) |
| **Key decision** | What stays PRD-level vs pushes downstream |
| **Must include** | Document Control (first), §10 (≥3 categories), §14 ADR topics, 15 sections |
| **Next** | `doc-ears` |
