---
name: doc-spec
description: Create a Technical Specification (SPEC) - Layer 6 of the SDD flow, defining component interfaces, data models, and behavior contracts. Use when ADR decisions are settled and you need an implementation-ready spec before TDD.
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
  custom_fields:
    layer: 6
    artifact_type: SPEC
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN]
    version: "0.6.5"
    framework_spec_version: "0.13.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary]
---

# doc-spec

## Purpose

Create a **Technical Specification (SPEC)** — Layer 6 of the SDD flow. A SPEC is
the implementation-ready, C4-L3 (Component) contract for a single software
component: its interfaces, data models, and behavior — written before any
downstream test or code.

**Layer**: 6 — the unified specification. A SPEC subsumes what older revisions
split into component/data/ux/risk/process specs; there is now **one** SPEC
artifact per component.
**Upstream**: BRD → PRD → EARS → BDD → ADR (ADR is the primary source).
**Downstream**: TDD → IPLAN → Code.

## When to Use

Use `doc-spec` when:

- Architecture decisions (ADR) are settled and you need to specify a component.
- Turning EARS/BDD acceptance contracts into concrete interfaces, data models,
  and behavior rules.
- You need an implementation-ready contract before writing TDD test cases.

For end-to-end generation from BDD/ADR, a prompt, or an IPLAN, use
`../doc-spec-autopilot/SKILL.md`.

## Prerequisites

SPEC sits at Layer 6, so verify the upstream chain exists before writing.
Reference only documents that already exist; never invent placeholders like
`SPEC-XXX` or `ADR-XXX`. Before writing, read:

1. **Template (source of truth):** `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
2. **Layer README:** `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/README.md`
3. **ID & tag standards:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
4. **Authoring style:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`
5. **Upstream ADR (primary)** plus the BDD/EARS acceptance contracts the
   component must satisfy.

Confirm existing upstream artifacts and no ID collision:
`ls docs/05_ADR/ docs/06_SPEC/ 2>/dev/null`.

## Layer Guidance

### C4-L3 scope (stay at the component level)

SPEC is the **Component** level. Describe component interfaces and contracts,
not architecture decisions (ADR) or source code (Code).

| Stay here (PASS) | Out of scope (FAIL) |
|------------------|---------------------|
| `AuthService`, `UserRepository`, `NotificationQueue` | `auth_service.py`, `async def validate_token()` |
| interface signatures, typed data models | concrete SQL tables, Redis key formats |
| behavior rules, state transitions, error contracts | Kubernetes pod configs, deployment manifests |

Required diagram tags: `@diagram: c4-l3`, `@diagram: dfd-l3` (use
`../charts-flow/SKILL.md`). Sequence diagrams must include `alt/else` for error
paths; never embed C4-L4 code/class diagrams.

### Required structure (8 sections)

`document_control` comes **first** (status, version, date, author, component,
`tdd_ready_score`). Then:

1. Document Control · 2. Component Overview (description, `@adr` decision,
language, dependencies) · 3. Interfaces (exports: signatures, types, errors) ·
4. Data Models (typed fields, no SQL/ORM) · 5. Behavior (validation rules,
state transitions, error handling — each sourced from `@ears`/`@bdd`) ·
6. Implementation Notes (constraints, patterns, performance considerations) ·
7. Downstream TDD Contracts (`@tdd: TDD-NN`, test-file map) · 8. Traceability.

See `SPEC-TEMPLATE.yaml` for per-section content. Format is **YAML**.

### Element IDs and tags

- **SPEC is a DOCUMENT-level artifact** — reference it in dash form `SPEC-NN`
  (two digits, no extra leading zero: `SPEC-01`, `SPEC-99`, `SPEC-102`).
  Downstream artifacts tag it `@spec: SPEC-12`. There is **no** dotted
  `SPEC.NN.SS.xxxx` element form for SPEC itself.
- **Cumulative upstream tags** (the Layer 6 chain): hierarchical refs use the
  4-segment element form — `@brd: BRD.NN.SS.xxxx`, `@prd: PRD.NN.SS.xxxx`,
  `@ears: EARS.NN.SS.xxxx`, `@bdd: BDD.NN.SS.xxxx`; document-level `@adr: ADR-NN`.
- **Thresholds:** never hardcode performance/timeout/rate-limit values — use
  `@threshold:` registry references.
- **Removed patterns** (do not use): `STEP-XXX`, `IF-XXX`, `INT-XXX`, `DM-XXX`,
  `MODEL-XXX`, `VR-XXX`, 3-digit `SPEC-NNN`, numeric element-type-code tables,
  and the deleted SYS/REQ/CTR upstream layers.

## Creation Process

1. **Read upstream** — ADR decisions plus the BDD/EARS contracts the component
   satisfies.
2. **Reserve ID** — next free `SPEC-NN` under `docs/06_SPEC/`.
3. **Create the nested folder** — every SPEC lives in
   `docs/06_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml`, regardless of size. Never
   place a SPEC file directly in `docs/06_SPEC/`.
4. **Document Control first**, then complete all 8 sections from the template.
5. **Define interfaces and data models** with typed signatures; **specify
   behavior** with each rule sourced from `@ears`/`@bdd`.
6. **Add the cumulative upstream tags** (`@brd @prd @ears @bdd @adr`) and the
   downstream `@tdd: TDD-NN` contract.
7. **Update the SPEC index** `docs/06_SPEC/SPEC-00_index.md` in the same change.
8. **Validate** (below) and commit the SPEC and index together.

## Validation

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/README.md` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] YAML parses; Document Control is the first section.
- [ ] All 8 sections present and non-empty; format is YAML (not markdown).
- [ ] Component-level only (no code/SQL/deployment detail; C4-L3 scope holds).
- [ ] Document ID is dash form `SPEC-NN`; no dotted SPEC element IDs; no removed
      patterns.
- [ ] Cumulative upstream tags present (`@brd @prd @ears @bdd @adr`); downstream
      `@tdd: TDD-NN` contract present.
- [ ] Quantitative values use `@threshold:` references (no magic numbers).
- [ ] Diagram contract: `@diagram: c4-l3` and `@diagram: dfd-l3` present (use
      `../charts-flow/SKILL.md`).
- [ ] Traceability matrix / index created or updated; no broken links.

| Code | Meaning | Severity |
|------|---------|----------|
| XDOC-006 | Tag format invalid | error |
| XDOC-007 | Gap in cumulative tag chain | error |
| XDOC-008 | Broken internal link | error |
| XDOC-009 | Missing traceability section | error |

**Quality gate (blocking):** TDD-Ready score ≥ 90/100 before moving on. If
issues are found, fix and re-check; if unfixable, log for manual review.

## Next Skill

`../doc-tdd/SKILL.md` — the TDD references this SPEC (`@spec: SPEC-NN`), inherits
the cumulative tags (`@brd` through `@spec`), and defines test cases, inputs,
expected outputs, and thresholds for the SPEC contracts.

## Adaptation

Read `.aidoc/profile.yaml`; honor only this skill's knobs
(`section_toggles`, `glossary`). Ignore unknown keys; absent a profile, use
framework defaults. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Template / authoring rules: `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer README: `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/README.md`
- Index template: `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Upstream decisions: `../doc-adr/SKILL.md` · Downstream tests: `../doc-tdd/SKILL.md`
- Quality gate: `../doc-spec-audit/SKILL.md` · Fixes: `../doc-spec-fixer/SKILL.md`
- Generation pipeline: `../doc-spec-autopilot/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Specify a component: interfaces, data models, behavior |
| **Layer** | 6 (C4-L3 Component) |
| **Upstream tags** | `@brd @prd @ears @bdd @adr` |
| **Document ID** | Dash form `SPEC-NN` (document-level; no dotted element IDs) |
| **Must include** | Document Control (first), 8 sections, `@threshold` for numbers |
| **Format** | YAML |
| **Next** | `doc-tdd` |
