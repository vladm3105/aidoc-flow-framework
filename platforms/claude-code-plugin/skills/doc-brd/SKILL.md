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
    version: "0.23.0"
    framework_spec_version: "0.33.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary, review_mode]
---

# doc-brd

## Purpose

Create a **Business Requirements Document (BRD)** — Layer 1 of the SDD flow.
A BRD captures business objectives, stakeholders, scope, and success criteria
in business language, before any product or technical detail.

**Layer**: 1 (entry point, no upstream).
**Downstream**: PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code.

One BRD = one MVP iteration (5–15 focused requirements). New features get a
new BRD; link cycles with `@depends: BRD-NN`.

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
4. **Authoring style:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`

Confirm no ID collision: `ls docs/01_BRD/`. Never invent placeholders like
`BRD-XXX` or reference non-existent documents.

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

- Element IDs: `BRD.{doc_id}.{section_id}.{hash}` — hash = first 4 hex of
  SHA256(`{doc_id}:{section_id}:{title}:{description}`), extend to 8 on collision.
- Layer 1 carries **no `@` upstream tags**; downstream tags it (`@brd: BRD.01.06.a7f3`).
- **Removed patterns**: `AC-XXX`, `FR-XXX`, `BO-XXX`, `BC-XXX`, legacy 3-segment `BRD.NN.xxxx`.

### Upstream source configuration

Most BRDs are authored from stakeholder input — keep the default
`upstream_mode: "none"`. Only when content derives from `docs/00_REF/` docs set
`upstream_mode: "ref"` and list `upstream_ref_path` (relative to the BRD file).

## Creation Process

1. **Determine type** — Platform vs Feature (table above).
2. **Reserve ID** — next free `BRD-NN` (two digits, no leading zero beyond two:
   `BRD-01`, `BRD-99`, `BRD-102`).
   *Per-layer independence (CLEANUP-PR-F item 18):* pick the next-free
   number in YOUR layer's index — the upstream's number is NOT your number
   (doc numbers are per-layer sequential and independent; see
   `framework/governance/ID_NAMING_STANDARDS.md` §Cross-layer cardinality).
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

## Draft mode (saga-driven)

When invoked via the saga-driven autopilot subprocess pattern (per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md` and the
saga loop in `../doc-brd-autopilot/SKILL.md`), this skill is the entry
point for the **draft phase** of the create→review→revise loop. The
invocation looks like:

```sh
claude --plugin-dir "$PLUGIN_DIR" -p \
  "/aidoc-flow:doc-brd Draft BRD-<id> at <path>; use BRD-TEMPLATE.yaml + the source input at <seed-path>. Write to docs/01_BRD/BRD-<id>_<slug>/."
```

Because `claude -p` has no `subagent_type` CLI parameter, the
persona binding (`business_analyst` lens → `requirements-analyst`
agent per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_CREWS.yaml`
plus the lens-to-agent table in `../review-team/SKILL.md`) moves
INTO this SKILL's prompt. When the invocation brief contains the word
`Draft` (case-insensitive) — indicating a saga-driven draft phase —
dispatch the author this way:

1. Dispatch ONE `Task` subagent with `subagent_type=requirements-analyst`,
   acting as the `business_analyst` lens (BRD author per
   `REVIEW_CREWS.yaml`'s BRD crew).
2. Brief: the BRD-TEMPLATE.yaml + the source input (REF / prompt /
   IPLAN seed file at the path passed in) + this SKILL's
   `## Creation Process` (above) as authoring rules.
3. The subagent writes the BRD to the nested folder
   `docs/01_BRD/BRD-<id>_<slug>/` per the standard layout.
4. After the subagent returns, write the saga.json transition
   recording the draft completion: append `{"ts": "<now>", "from":
   "FANOUT_STARTED", "to": "BRANCH_COMPLETED", "scope":
   "branch:business_analyst"}` to `transitions[]` if a saga.json
   exists at `.aidoc/review/01_BRD/<BRD-id>/saga.json`. (If no
   saga.json exists, this is a standalone invocation — skip the saga
   write per `REVIEW_SAGA.md` §"FRAMEWORK_SPEC_VERSION semantics"
   declaration-vs-implementation rule.)

When invoked outside the saga loop (a user runs `/aidoc-flow:doc-brd`
directly to author a BRD), follow the `## Creation Process` above
without dispatching the Task subagent (the user is the author in
that case). The two modes coexist; the trigger is the presence of
`Draft` in the brief AND an existing `<path>` argument.

## Validation

**Validator framing (`review_mode`-aware).** The structural checks below are the **deterministic floor** and run in every mode. In `team` mode the *content-quality* review is performed by `../doc-brd-audit/SKILL.md` fanning out the BRD crew (`architect`/`business_analyst`/`auditor`/`chaos_engineer`/`security_engineer`); in `single_pass` mode the audit applies every lens in one pass. Either way this skill (the author) does not score the artifact — it produces it.

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/README.md` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

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

**Error codes** (all severity `error`): `XDOC-006` tag format invalid · `XDOC-008` broken internal link · `XDOC-009` missing traceability section.

**Quality gate (blocking):** PRD-Ready score ≥ 90/100 before moving on.

> **BRD-REF documents** (via `../doc-ref/SKILL.md`) are free-format references
> — exempt from ready-scores, cumulative tags, and quality gates.

## Next Skill

`../doc-prd/SKILL.md` — the PRD references this BRD (`@brd: BRD.NN.SS.xxxx`),
defines product features and KPIs, and inherits the §8 architecture topics.

## Adaptation

Read `.aidoc/profile.yaml`; honor only this skill's knobs
(`section_toggles`, `glossary`). Ignore unknown keys; absent a profile, use
framework defaults. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

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
