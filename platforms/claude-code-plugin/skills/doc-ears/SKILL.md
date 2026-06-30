---
name: doc-ears
description: Create EARS (Easy Approach to Requirements Syntax) formal requirements - Layer 3 of the SDD flow, translating PRD features into atomic, testable WHEN-THE-SHALL-WITHIN statements. Use after BRD and PRD exist.
metadata:
  tags:
    - sdd-workflow
    - layer-3-artifact
  custom_fields:
    layer: 3
    artifact_type: EARS
    skill_category: core-workflow
    upstream_artifacts: [PRD]
    downstream_artifacts: [BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.23.0"
    framework_spec_version: "0.32.4"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary]
---

# doc-ears

## Purpose

Create an **EARS (Easy Approach to Requirements Syntax)** document — Layer 3 of
the SDD flow. EARS formalizes BRD/PRD requirements into precise, atomic, testable
statements using **WHEN-THE-SHALL-WITHIN** syntax, ready for BDD translation.

**Layer**: 3 — a refinement step formalizing the Context (BRD) → Container (PRD)
transition; it has no C4 level of its own.
**Upstream**: PRD (Layer 2). (Upstream BRD lineage is reachable transitively
via the @-tag chain per the necessary-upstream contract.)
**Downstream**: BDD → ADR → SPEC → TDD → IPLAN → Code.

Each EARS statement must be **testable** (Given-When-Then derivable),
**measurable** (quantifiable constraints), **traceable** (`@prd`), and
**atomic** (one concept per statement).

## When to Use

Use `doc-ears` when:

- PRD (Layer 2) exists and you need formal requirements (the upstream BRD is
  reached transitively via the PRD's own `@brd` tags).
- Translating product features into precise behavioral statements.
- Establishing event-driven, state-driven, optional/feature-gated, error-handling, or system-wide rules.

For end-to-end generation from a PRD, a prompt, or an IPLAN, use
`../doc-ears-autopilot/SKILL.md`.

## Prerequisites

Before writing, read:

1. **Template (source of truth):** `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/EARS-TEMPLATE.yaml`
2. **Layer README:** `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/README.md`
3. **ID & tag standards:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
4. **Authoring style:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`
5. **Upstream PRD** that drives this EARS (and, via the PRD's own `@brd`
   tags, the BRD it derives from).

Confirm no ID collision: `ls docs/03_EARS/ 2>/dev/null`. Reference only upstream
documents that exist; never invent placeholders like `PRD-XXX` or `TBD`.

## Layer Guidance

### Required structure (5 numbered sections + glossary backmatter)

`document_control` is **Section 1** (status, version, dates `YYYY-MM-DD`,
priority, single `@prd:` source, BDD-Ready score, revision-history table).
Then:

2. Purpose & Context · 3. Requirements (the five patterns) · 4. Quality
Attributes (tabular) · 5. Traceability.

Plus a **Glossary** backmatter section (`glossary:` template key — required,
unnumbered). Section numbers and identifiers come from `EARS-TEMPLATE.yaml`'s
own `# Section N:` numbering — **the template is the source of truth**.

See `EARS-TEMPLATE.yaml` for per-section content and embedded authoring guidance.

### The five EARS patterns (Section 3)

| Pattern | Syntax | Use for |
|---------|--------|---------|
| **Event-Driven** | `WHEN [trigger], THE [component] SHALL [action] WITHIN [timing].` | user/API/timer events |
| **State-Driven** | `WHILE [state], THE [component] SHALL [behavior] WITHIN [context].` | continuous / mode-dependent behavior |
| **Optional** | `WHERE [feature enabled], THE [component] SHALL [behavior].` | feature-flagged / config-gated behavior |
| **Unwanted** | `IF [error], THE [component] SHALL [recovery] WITHIN [timing].` | failures, edge cases, fallbacks |
| **Ubiquitous** | `THE [component] SHALL [behavior] for [scope].` | global invariants, logging, audit |

A genuinely multi-condition requirement *composes* these (e.g.
`WHILE [state], WHEN [event], THE … SHALL …`) — composition, not a sixth pattern.
EARS uses `THE … SHALL …` as the response clause, never a `THEN` connective.

Each requirement is **atomic** (one testable concept) and carries an element ID
plus a per-requirement `@prd: …` traceability line. Use the **Boundary Value
Matrix**, **State Transition** (with error states), and **Fallback Path**
patterns from the template where they apply.

### Quantifiable language (Sections 3 / 4)

Use **SHALL / SHALL NOT / SHOULD / MAY** correctly. Replace vague timing with
percentiles: `real-time` → p50<100ms/p95<300ms/p99<1000ms; `immediately` →
<500ms; `fast`/`quickly` → exact latency. Section 4 (Quality Attributes:
Performance, Security, Reliability) is tabular with measurable targets; all
timing uses p50/p95/p99 notation. Carry changeable values as
`@threshold: PRD.NN.category.key` tags (no PRD section numbers in the tag).

### Element IDs and tags

- Hierarchical element IDs: `EARS.{doc_id}.{section_id}.{hash}` (e.g.
  `EARS.01.03.c4d8`; Requirements = section `03`, Quality Attributes = section
  `04`). `hash` = first 4 hex of `SHA256("{doc_id}:{section_id}:{title}:{description}")`,
  extend to 8 on collision.
- EARS is Layer 3, so it carries the required `@prd` upstream tag (per the
  necessary-upstream contract). One `@prd:` only in Document Control (extras go
  in per-requirement tags); no ranges. Upstream BRD lineage is reachable
  transitively via the PRD's own `@brd` tags — do not emit `@brd:` on EARS
  elements.
- **Removed patterns** (do not use): `Event-XXX`, `State-XXX`, `UB-XXX`,
  `REQ-XXX`; legacy 3-segment `EARS.NN.xxxx`; numeric type-code `EARS.NN.25.SS`;
  dash form `EARS-NN-XXX`.

## Creation Process

1. **Read upstream** — the PRD that drives these requirements (and, via its
   `@brd` tags, the BRD it derives from).
2. **Reserve ID** — next free `EARS-NN` (two digits: `EARS-01`, `EARS-99`,
   `EARS-102`).
   *Per-layer independence (CLEANUP-PR-F item 18):* pick the next-free
   number in YOUR layer's index — the upstream's number is NOT your number
   (doc numbers are per-layer sequential and independent; see
   `framework/governance/ID_NAMING_STANDARDS.md` §Cross-layer cardinality).
3. **Create the nested folder** — every EARS lives in
   `docs/03_EARS/EARS-NN_{slug}/` regardless of size. Monolithic:
   `EARS-NN_{slug}.md` inside it; section-based (>25 KB): `EARS-NN.S_{section}.md`
   - index from `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/EARS-00_index.TEMPLATE.md`.
4. **Document Control (Section 1) first**, then complete §2–§5 plus the
   glossary backmatter from the template.
5. **Categorize requirements** into the five patterns; write atomic
   `THE … SHALL …` statements (WITHIN timing where applicable) with
   `@threshold:` constraints.
6. **Fill Quality Attributes** (tabular, percentile timing) and **Traceability**
   (`@prd` per the necessary-upstream contract).
7. **Update the EARS index** `docs/03_EARS/EARS-00_index.md` in the same change.
8. **Validate** (below) and commit the EARS and index together.

## Validation

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/README.md` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] Document Control is the first section.
- [ ] All 5 sections present and non-empty.
- [ ] Every statement uses WHEN-THE-SHALL-WITHIN syntax; SHALL/SHOULD/MAY correct.
- [ ] Requirements categorized (Event, State, Optional, Unwanted, Ubiquitous) and atomic.
- [ ] Element IDs match `EARS.NN.SS.xxxx`; no removed patterns.
- [ ] Required upstream tag present: `@prd` (per the necessary-upstream
      contract); no ranges.
- [ ] Single `@prd:` in Document Control; quantifiable constraints (no "fast").
- [ ] No numeric downstream references to artifacts that do not yet exist.
- [ ] Traceability matrix / index created or updated; no broken links.

**Error codes** (all severity `error`): `XDOC-006` tag format invalid · `XDOC-008` broken internal link · `XDOC-009` missing traceability section.

**Quality gate (blocking):** BDD-Ready score ≥ 90/100 before moving on. If issues
are found, fix and re-check; if unfixable, log for manual review.

## Next Skill

`../doc-bdd/SKILL.md` — the BDD references this EARS (`@ears: EARS.NN.SS.xxxx`)
and turns each statement into executable Given-When-Then scenarios. (BDD's
required upstream is `@ears` only; further upstream lineage is reachable
transitively via the @-tag chain.)

## Adaptation

Read `.aidoc/profile.yaml`; honor only this skill's knobs
(`section_toggles`, `glossary`). Ignore unknown keys; absent a profile, use
framework defaults. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Template / authoring rules: `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/EARS-TEMPLATE.yaml`
- Layer README: `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/README.md`
- Index template: `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/EARS-00_index.TEMPLATE.md`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Quality gate: `../doc-ears-audit/SKILL.md` · Fixes: `../doc-ears-fixer/SKILL.md`
- Generation pipeline: `../doc-ears-autopilot/SKILL.md`
- Diagrams (state/sequence): `../charts-flow/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Formalize requirements with WHEN-THE-SHALL-WITHIN syntax |
| **Layer** | 3 (refinement; no C4 level) |
| **Upstream tags** | `@prd` (per necessary-upstream contract) |
| **Key rule** | One atomic, testable, quantifiable statement each |
| **Must include** | Document Control (first), five patterns, 5 sections |
| **Quality gate** | BDD-Ready ≥ 90/100 |
| **Next** | `doc-bdd` |
