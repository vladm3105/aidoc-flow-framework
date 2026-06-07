---
name: doc-tdd
description: Create a Test-Driven Development guide (TDD) - Layer 7 of the SDD flow, defining test cases, BDD-to-test mapping, and quality thresholds from SPEC component contracts. Use after SPEC, before IPLAN.
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
  custom_fields:
    layer: 7
    artifact_type: TDD
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN]
    version: "0.6.4"
    framework_spec_version: "0.13.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, glossary]
---

# doc-tdd

## Purpose

Create a **Test-Driven Development guide (TDD)** — Layer 7 of the SDD flow.
A TDD defines test cases validating the SPEC component contract: maps BDD
scenarios to concrete tests (inputs, expected outputs, edge cases), sets
per-type quality thresholds, declares Red → Green → Refactor order. Test type
(unit / integration / functional / perf / security) is a `type` attribute on
each case — no separate artifacts.

**Layer**: 7 (after SPEC, before IPLAN). **Downstream**: IPLAN → Code.

One TDD per SPEC component.

## When to Use

Use `doc-tdd` when:

- BRD through SPEC (Layers 1–6) are complete and you are defining tests.
- You need concrete test cases, a BDD→test mapping, and quality thresholds
  before implementation.
- Following the test-first (Red → Green → Refactor) workflow.

For end-to-end generation from a SPEC, a prompt, or an IPLAN, use
`../doc-tdd-autopilot/SKILL.md`. To create the upstream SPEC, use
`../doc-spec/SKILL.md`.

## Prerequisites

Before writing, verify upstream artifacts exist and read the contracts:

1. **List upstream:** `ls docs/01_BRD/ docs/02_PRD/ docs/03_EARS/ docs/04_BDD/ docs/05_ADR/ docs/06_SPEC/ 2>/dev/null`
2. **Template (source of truth):** `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-TEMPLATE.yaml`
3. **Layer README:** `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/README.md`
4. **ID & tag standards:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
5. **Authoring style:** `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`

The **primary source is SPEC** (the component contract); **BDD is the source of
truth for behavior** — TDD maps BDD scenarios to tests, it does not duplicate
them. Reference only documents that exist; never invent placeholders like
`TDD-XXX`, `SPEC-XXX`, or `TBD`. Do not create missing upstream artifacts.

## Layer Guidance

### Required structure (7 sections)

The TDD is a **single unified template** — no test subtypes, no separate test
artifacts. Per `TDD-TEMPLATE.yaml`:

1. **Document Control** — status, version, dates, author, component, SPEC ref,
   IPLAN-Ready score.
2. **Test Pyramid** — effort distribution (defaults: unit 70 / integration 20 /
   e2e 10; targets, not quotas).
3. **BDD Scenario → Test Mapping** — each `@bdd:` scenario maps to test types,
   files, and functions; declares where tests will live.
4. **Test Case Definitions** — concrete cases, each with an element ID and a
   `type` attribute.
5. **Test Thresholds** — coverage targets and pass/fail criteria per type.
6. **TDD Execution Order** — Red → Green → Refactor phases.
7. **Traceability** — cumulative upstream tags + downstream IPLAN.

### Test types (content categories, not subtypes)

Each Section 4 case carries a `type` attribute — not a separate ID code or
document.

| Type | Validates | Primary source |
|------|-----------|----------------|
| unit | individual functions/methods, data-model constraints | SPEC §3–4 |
| integration | component interactions, state transitions, error handling | SPEC §5 |
| functional | feature behavior against acceptance criteria | EARS/BDD |
| e2e | full workflows mapped from acceptance scenarios | BDD (Layer 4) |
| smoke | critical-path sanity (post-build/deploy) | BDD critical scenarios |
| performance | latency/throughput against `@threshold` targets | EARS quality attributes |
| security | optional — threat/vulnerability paths | SPEC/ADR (only if mandated) |

Unit cases carry `target`, `inputs`, `expected_output`, `edge_cases`.
Integration cases add `contract`, `setup`, `action`, `expected_state`,
`error_paths`. E2E cases add a `bdd_ref`, numbered `workflow`, `timeout_seconds`,
`cleanup`. Security cases add a `threat` ref and `expected_result`.

### Test thresholds (Section 5)

| Type | Coverage target | Fail action |
|------|-----------------|-------------|
| unit | ≥90% | block merge |
| integration | ≥85% (contract validation passes) | block merge |
| e2e | ≥75% of happy paths (≤300s budget) | block deploy to staging |
| security (optional) | all auth/authz paths; no OWASP Top 10 | block deploy |

### TDD execution order (Section 6)

The order the AI must follow when generating code: 1) Write Tests → 2) Run Tests
(Red, confirm failure) → 3) Implement → 4) Verify (Green) → 5) Refactor. Test
files are generated **before** implementation files.

### Element IDs and tags

- Test-case element IDs: `TDD.{doc_id}.{section_id}.{hash}` (4-segment) — test
  cases live in Section 4, so `TDD.NN.04.xxxx` (e.g. `TDD.01.04.a3c1`; `hash` =
  first 4 hex of SHA256 of the case content, extend to 8 on collision).
- TDD is Layer 7, so it carries **cumulative upstream tags**: `@brd @prd @ears
  @bdd @adr @spec`. BRD/PRD/EARS/BDD/ADR use dot element form; `@spec: SPEC-NN`
  is document-level dash form. Self-tag: `@tdd: TDD-NN`.
- **Removed patterns** (do not use): `TC-XXX`, `UT-XXX`, `IT-XXX`, `ST-XXX`,
  `FT-XXX`, and the legacy 3-segment `TDD.NN.xxxx`.

## Creation Process

1. **Read upstream** — SPEC (component contract) + BDD (behavior scenarios).
2. **Reserve ID** — next free `TDD-NN` (two digits: `TDD-01`, `TDD-99`); one TDD
   per SPEC component, `docs/07_TDD/TDD-NN_{component_slug}.yaml`.
3. **Document Control first**, then complete all 7 sections from the template.
4. **Set the test pyramid**; **map each BDD scenario** to test types/files.
5. **Write test cases** — element ID `TDD.NN.04.xxxx`, `type`, `spec_ref` (and
   `bdd_ref` for e2e), inputs/outputs, edge cases/error paths.
6. **Set thresholds**; **confirm Red → Green → Refactor** order.
7. **Add cumulative tags** (@brd…@spec) + @tdd self-tag + downstream IPLAN.
8. **Update the TDD index** `docs/07_TDD/TDD-00_index.md` in the same change.
9. **Validate** (below) and commit the TDD and index together.

## Validation

**This skill is the validator** (no runtime code). Apply against `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/README.md` and `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

- [ ] Document Control complete; all 7 sections present and non-empty.
- [ ] Test pyramid set; BDD→test mapping complete (Section 3).
- [ ] Each case has a `TDD.NN.04.xxxx` ID and a valid `type`
      (unit/integration/e2e/security); no removed patterns.
- [ ] Inputs/expected outputs present per case; edge cases / error paths
      documented; e2e cases carry a `bdd_ref`.
- [ ] Thresholds set per type (Section 5); execution order present (Section 6).
- [ ] Cumulative tags @brd through @spec plus @tdd self-tag; parent SPEC exists.
- [ ] Index updated; no broken links. Diagrams via `../charts-flow/SKILL.md`.

**Error codes** (all severity `error`): `XDOC-006` tag format invalid · `XDOC-008` broken internal link · `XDOC-009` missing traceability section.

**Quality gate (blocking):** IPLAN-Ready score ≥ 90/100 before moving on.

## Next Skill

`../doc-iplan/SKILL.md` — the IPLAN references this TDD (`@tdd: TDD-NN`),
inherits the full upstream tag chain, and orchestrates the build, enforcing test
files before implementation files.

## Adaptation

Read `.aidoc/profile.yaml`; honor only this skill's knobs
(`section_toggles`, `glossary`). Ignore unknown keys; absent a profile, use
framework defaults. Authority:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Template / authoring rules: `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer README: `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/README.md`
- Index template: `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-00_index.TEMPLATE.md`
- ID & tag standards: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Quality gate: `../doc-tdd-audit/SKILL.md` · Fixes: `../doc-tdd-fixer/SKILL.md`
- Generation pipeline: `../doc-tdd-autopilot/SKILL.md`
- Upstream: `../doc-spec/SKILL.md` · Downstream: `../doc-iplan/SKILL.md`

## Quick Reference

| | |
|---|---|
| **Purpose** | Define test cases from SPEC contracts |
| **Layer** | 7 (after SPEC, before IPLAN) |
| **Upstream tags** | @brd @prd @ears @bdd @adr @spec |
| **Element ID** | `TDD.NN.04.xxxx` (test cases live in Section 4) |
| **Test types** | unit · integration · e2e · security (a `type` attribute) |
| **Must include** | Document Control (first), 7 sections, BDD→test mapping |
| **Next** | `doc-iplan` |
