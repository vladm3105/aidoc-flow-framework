---
name: doc-bdd
description: Create Behavior-Driven Development (BDD) scenarios - Layer 4 of the SDD flow, translating EARS requirements into executable Given-When-Then acceptance scenarios with req-to-SPEC trace links. Use after EARS, before ADR. Single-document authoring primitive; for end-to-end or batch generation the autopilot (`doc-bdd-autopilot`) drives this skill.
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
    version: "0.23.4"
    framework_spec_version: "0.36.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary]
---

# doc-bdd

## Purpose

Create **Behavior-Driven Development (BDD)** scenarios — Layer 4 of the SDD
flow. A BDD suite translates EARS formal requirements into structured **YAML
scenarios** (Given/When/Then phase lists carried in a ` ```yaml ` block, NOT
Gherkin `@`-tags), each carrying an **element-level `ears:` trace list** and a
`spec_trace` link forward to the SPEC sections it exercises. (If a runner ever
needs `.feature` files, the YAML is the source of record and a `.feature`
emitter can be authored on demand — no such emitter ships today; the only
shipped transcoder is the one-off reverse-direction `tools/gherkin_to_bdd_yaml.py`
used to migrate legacy Gherkin into the YAML form.)

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

1. **Document Control** — version, status, dates, author, priority, plus the
   ADR-Ready score. (No `@ears`/`@prd`/`@brd` reference rows — upstream trace
   lives on each scenario's `ears:` list.)
2. **Feature Definition** — a ` ```yaml ` `feature:` block: name matching the
   EARS requirement, an `As a / I want / So that` description, and a `background`
   (bare step text + IANA timezone, default `America/New_York`). The feature
   carries **no `ears`** — its EARS coverage is the union of its scenarios.
3. **Scenario Structure** — a ` ```yaml ` `scenarios:` flat list (Given/When/Then
   phase lists), each with a `type:` across the five categories (below).
4. **Traceability** — the derived coverage summary + downstream expectations and
   the health/coverage score.
5. **Glossary** — flat list of project-specific terms.

See `BDD-TEMPLATE.yaml` for per-section content and the normative scenario schema.

### Scenario categories (Section 3)

Every scenario is a YAML mapping with `id: BDD.NN.03.xxxx`, `name`, `type`,
`priority` (`p0-critical` … `p3-low`), an element-level `ears:` list, `given` /
`when` / `then` phase lists, and a `spec_trace` list (`notes` optional).

| Category | `type:` value | Min | Priority |
|----------|---------------|-----|----------|
| success | `success` | 1 / EARS | p0–p1 |
| error | `error` | 1 / error | p1–p2 |
| recovery | `recovery` | 1 / circuit-breaker | p1 |
| parameterized | `parameterized` | 1 / multi-value | p1–p2 |
| optional | `optional` | 1 / optional param | p2–p3 |

A `parameterized` scenario adds `outline: true` + `examples: {headers, rows}`.

### Scenario YAML rules

- Scenarios are **structured YAML**, not Gherkin `@`-tags. Trace is the
  `ears:` list (element-level only — `REFGRAN01` rejects doc-form `EARS-NN`);
  `id`/`type`/`priority` are fields, not tags.
- Times include seconds (`HH:MM:SS`) with IANA timezones (`America/New_York`),
  never abbreviations like `EST`.
- Quantitative values use `@threshold:` keys written **inline in the step
  prose** (e.g. `… WITHIN @threshold:PRD.NN.perf.api.p95`) — no magic numbers.
- Keep scenarios atomic (one behavior each). One BDD document per module up to
  ~50,000 tokens; beyond that, start a new self-contained BDD document.

### Element IDs and upstream trace

- Hierarchical element IDs: `BDD.{doc_id}.{section_id}.{hash}` (e.g.
  `BDD.01.03.d7a2`; `hash` = first 4 hex of SHA256 of
  `"{doc_id}:{section_id}:{title}:{description}"` from BDD content, extend to 8
  on collision). Scenarios live in section `03`, in each scenario's `id:` field.
- BDD's required upstream trace is each scenario's element-level `ears:` list
  (per the necessary-upstream contract — satisfies `required_tags: [ears]`).
  Downstream artifacts cite BDD scenarios with `@bdd: BDD.01.03.8f4c` tags
  (unchanged). Upstream PRD/BRD lineage is reachable transitively via the EARS
  document's own @-tag chain — do not emit `@brd:`/`@prd:`/`@ears` tags on BDD.
- **Removed patterns** (do not use): `SCENARIO-XXX`, `SCEN-XXX`, `TS-XXX`,
  `STEP-XXX`, numeric type-codes, the legacy 3-segment `BDD.NN.xxxx`, and
  Gherkin `@ears`/`@scenario-type`/`@scenario-id` tags (now YAML fields).

### Downstream trace (spec_trace)

Each scenario records the SPEC sections it maps to, e.g.
`spec_trace: ["SPEC Section 3 (Interfaces)", "SPEC Section 5 (Behavior)"]`.
This is the req-to-SPEC bridge that downstream layers consume.

## Creation Process

1. **Read upstream** — the EARS that drives this BDD (and, via its @-tag
   chain, the PRD/BRD it derives from) to understand the behaviors to test.
2. **Reserve ID** — next free `BDD-NN` (two digits, no extra leading zero:
   `BDD-01`, `BDD-99`, `BDD-102`).
   *Per-layer independence (CLEANUP-PR-F item 18):* pick the next-free
   number in YOUR layer's index — the upstream's number is NOT your number
   (doc numbers are per-layer sequential and independent; see
   `framework/governance/ID_NAMING_STANDARDS.md` §Cross-layer cardinality).
3. **Create the document** from `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-TEMPLATE.yaml`;
   complete all 5 sections, Document Control first.
4. **Write the `feature:` block + the `scenarios:` list** (YAML) per EARS
   requirement across the five categories; each scenario carries `id`, `type`,
   `priority`, an element-level `ears:` list, `given`/`when`/`then` phase lists,
   inline `@threshold:`, and `spec_trace`. Add the feature `background`.
5. **Set each scenario's element-level `ears:` list** (this is the required
   upstream trace) and a unique `id:` — no Gherkin `@`-tags.
6. **Update the BDD index** `docs/04_BDD/BDD-00_index.md` in the same change.
7. **Validate** (below) and commit the BDD and index together.

## Validation

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/README.md` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] Document Control is the first section; all 5 sections present and non-empty.
- [ ] Every scenario carries an element-level `ears:` list (satisfies the
      necessary-upstream contract); the feature has **no** `ears`.
- [ ] Every scenario has `id`, `type`, `priority`, `given`/`when`/`then` phase
      lists, and a `spec_trace` (BDD-SCHEMA-001 clean).
- [ ] All five scenario `type` categories represented; scenarios atomic.
- [ ] Quantitative values use inline `@threshold:` keys; times are `HH:MM:SS`
      with IANA timezones.
- [ ] Element IDs match `BDD.NN.SS.xxxx`; no removed patterns / Gherkin tags.
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
| **Purpose** | Structured YAML Given/When/Then acceptance scenarios |
| **Layer** | 4 |
| **Upstream trace** | scenario `ears:` lists (per necessary-upstream contract) |
| **Key idea** | EARS → YAML scenarios with `spec_trace` to SPEC |
| **Must include** | Document Control (first), 5 scenario categories, thresholds |
| **Execution** | QA staging only — never CI |
| **Next** | `doc-adr` |
