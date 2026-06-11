---
name: doc-bdd
description: Create Behavior-Driven Development (BDD) scenarios - Layer 4 of the SDD flow, translating EARS requirements into executable Given-When-Then acceptance scenarios with req-to-SPEC trace links. Use after EARS, before ADR.
metadata:
  tags:
    - sdd-workflow
    - layer-4-artifact
  custom_fields:
    layer: 4
    artifact_type: BDD
    skill_category: core-workflow
    upstream_artifacts: [EARS]
    downstream_artifacts: [ADR, SPEC, TDD, IPLAN]
    version: "0.15.0"
    framework_spec_version: "0.18.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary]
---

# doc-bdd

## Purpose

Create **Behavior-Driven Development (BDD)** scenarios — Layer 4 of the SDD
flow. A BDD suite translates EARS formal requirements into executable
Given-When-Then (Gherkin) scenarios, each carrying the required upstream
trace tag (`@ears`) and a `spec_trace` link forward to the SPEC sections it
exercises.

**Layer**: 4. **Upstream**: EARS (per the necessary-upstream contract;
upstream PRD/BRD lineage is reachable transitively via the @-tag chain).
**Downstream**: ADR → SPEC → TDD → IPLAN → Code.

BDD scenarios are the acceptance source of truth that TDD (Layer 7) maps to
concrete test cases. **Execution is QA-staging only — never run BDD in CI**
(use TDD unit/integration tests for CI).

## When to Use

Use `doc-bdd` when:

- EARS (Layer 3) exists and you need executable acceptance scenarios.
- Validating EARS requirements with concrete Given-When-Then behaviors.
- Defining the req-to-SPEC trace bridge (`spec_trace`) before ADR/SPEC.

For end-to-end generation from EARS, a prompt, or an IPLAN, use
`../doc-bdd-autopilot/SKILL.md`. Create upstream artifacts first; never invent
placeholders like `EARS-XXX` or reference documents that do not yet exist.

## Prerequisites

BDD is Layer 4, so the required upstream EARS must already exist. Confirm it
and read the spec before writing:

1. **Template (source of truth):** `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-TEMPLATE.yaml`
2. **Layer README:** `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/README.md`
3. **ID & tag standards:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
4. **Authoring style:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`

Verify upstream and check for ID collision:
`ls docs/03_EARS/ docs/04_BDD/ 2>/dev/null`. Reference only existing EARS
elements in trace tags; upstream PRD/BRD lineage is reachable transitively
via the EARS document's own @-tag chain.

## Layer Guidance

### Required structure (5 sections)

Per `BDD-TEMPLATE.yaml`, every BDD document carries:

1. **Document Control** — version, status, dates, author, priority, the
   required upstream reference `@ears`, plus the ADR-Ready score.
2. **Feature Definition** — feature name matching the EARS requirement, an
   `As a / I want / So that` description, and a `Background` (system state +
   IANA timezone, default `America/New_York`).
3. **Scenario Structure** — the Given-When-Then scenarios across the five
   categories (below).
4. **Traceability** — required upstream tag (`@ears`), downstream expectations,
   and the health/coverage score.
5. **Glossary** — flat list of project-specific terms.

See `BDD-TEMPLATE.yaml` for per-section content and scenario conventions.

### Scenario categories (Section 3)

Every scenario carries `@scenario-type:{category}`, a priority tag
(`@p0-critical` … `@p3-low`), a `@scenario-id:BDD.NN.03.xxxx` tag, executable
Given-When-Then steps, threshold references for timing, and a `spec_trace` list.

| Category | Tag | Min | Priority |
|----------|-----|-----|----------|
| success | `@scenario-type:success` | 1 / EARS | P0–P1 |
| error | `@scenario-type:error` | 1 / error | P1–P2 |
| recovery | `@scenario-type:recovery` | 1 / circuit-breaker | P1 |
| parameterized | `@scenario-type:parameterized` | 1 / multi-value | P1–P2 |
| optional | `@scenario-type:optional` | 1 / optional param | P2–P3 |

### Gherkin and threshold rules

- Tags are **Gherkin-native**, on separate lines **before** `Feature:` — never
  in comments. No spaces after the colon in tags: `@ears:EARS.01.03.5e2a`.
- Times include seconds (`HH:MM:SS`) with IANA timezones (`America/New_York`),
  never abbreviations like `EST`.
- Quantitative values use `@threshold:` keys (e.g.
  `WITHIN @threshold:PRD.NN.perf.api.p95`) — no hardcoded magic numbers.
- Keep scenarios atomic (one behavior each). Single `.feature` per module up to
  ~50,000 tokens; beyond that, start a new self-contained BDD document — do not
  split into sectioned files.

### Element IDs and upstream tags

- Hierarchical element IDs: `BDD.{doc_id}.{section_id}.{hash}` (e.g.
  `BDD.01.03.d7a2`; `hash` = first 4 hex of SHA256 of
  `"{doc_id}:{section_id}:{title}:{description}"` from BDD content, extend to 8
  on collision). Scenarios live in section `03`.
- BDD is Layer 4, so it carries the required upstream tag `@ears` (per the
  necessary-upstream contract). Downstream artifacts tag it:
  `@bdd: BDD.01.03.8f4c`. Upstream PRD/BRD lineage is reachable transitively
  via the EARS document's own @-tag chain — do not emit `@brd:`/`@prd:` on
  BDD elements.
- **Removed patterns** (do not use): `SCENARIO-XXX`, `SCEN-XXX`, `TS-XXX`,
  `STEP-XXX`, numeric type-codes, and the legacy 3-segment `BDD.NN.xxxx`.

### Downstream trace (spec_trace)

Each scenario records the SPEC sections it maps to, e.g.
`spec_trace: ["SPEC Section 3 (Interfaces)", "SPEC Section 5 (Behavior)"]`.
This is the req-to-SPEC bridge that downstream layers consume.

## Creation Process

1. **Read upstream** — the EARS that drives this BDD (and, via its @-tag
   chain, the PRD/BRD it derives from) to understand the behaviors to test.
2. **Reserve ID** — next free `BDD-NN` (two digits, no extra leading zero:
   `BDD-01`, `BDD-99`, `BDD-102`).
3. **Create the document** from `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-TEMPLATE.yaml`;
   complete all 5 sections, Document Control first.
4. **Write scenarios** per EARS requirement across the five categories; add
   Background, threshold references, and `spec_trace` for each.
5. **Add the required upstream tag** `@ears` (Gherkin-native, before
   `Feature:`) and `@scenario-id` per scenario.
6. **Update the BDD index** `docs/04_BDD/BDD-00_index.md` in the same change.
7. **Validate** (below) and commit the BDD and index together.

## Validation

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/README.md` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] Document Control is the first section; all 5 sections present and non-empty.
- [ ] Required upstream tag `@ears` present, Gherkin-native, no spaces after
      colon (per necessary-upstream contract).
- [ ] Every scenario has `@scenario-type`, a priority tag, `@scenario-id`,
      Given-When-Then steps, and a `spec_trace`.
- [ ] All five scenario categories represented; scenarios atomic and executable.
- [ ] Quantitative values use `@threshold:` keys; times are `HH:MM:SS` with IANA
      timezones.
- [ ] Element IDs match `BDD.NN.SS.xxxx`; no removed patterns.
- [ ] Traceability section / index updated; no broken links.
- [ ] Diagram contract: sequence-diagram tag present if a scenario flow is
      illustrated (use `../charts-flow/SKILL.md`).

**Error codes** (all severity `error`): `XDOC-006` tag format invalid · `XDOC-008` broken internal link · `XDOC-009` missing traceability section.

**Quality gate (blocking):** ADR-Ready score ≥ 90/100 before moving on. If
issues are found, fix and re-check; if unfixable, log for manual review.

## Next Skill

`../doc-adr/SKILL.md` — the ADR references this BDD (`@bdd: BDD.NN.SS.xxxx`)
along with its required `@ears`, records architecture decisions in
Context-Decision-Consequences form, and cites the BDD scenarios that validate
each decision.

## Adaptation

Read `.aidoc/profile.yaml`; honor only this skill's knobs
(`section_toggles`, `glossary`). Ignore unknown keys; absent a profile, use
framework defaults. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Template / authoring rules: `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-TEMPLATE.yaml`
- Layer README: `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/README.md`
- Index template: `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-00_index.TEMPLATE.md`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Quality gate: `../doc-bdd-audit/SKILL.md` · Fixes: `../doc-bdd-fixer/SKILL.md`
- Generation pipeline: `../doc-bdd-autopilot/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Executable Given-When-Then acceptance scenarios |
| **Layer** | 4 |
| **Upstream tags** | `@ears` (per necessary-upstream contract) |
| **Key idea** | EARS → Gherkin scenarios with `spec_trace` to SPEC |
| **Must include** | Document Control (first), 5 scenario categories, thresholds |
| **Execution** | QA staging only — never CI |
| **Next** | `doc-adr` |
