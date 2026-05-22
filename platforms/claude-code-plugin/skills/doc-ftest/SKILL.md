---
name: doc-ftest
description: Author functional-focused TDD (Layer 7) test cases - end-to-end scenarios and quality-attribute thresholds validating SPEC behavior contracts
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-functional-helper
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: TDD
    tdd_focus: functional
    deliverable_type: code
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-ftest

## Purpose

Author **functional-focused TDD (Layer 7)** test cases — end-to-end workflow
scenarios and quality-attribute thresholds (performance, reliability,
scalability, security) that validate SPEC behavior contracts through test
execution.

This skill is a **TDD (Layer 7) specialization** for the functional-test focus.
It authors TDD documents (and their Section 4 test-case definitions) against the
single canonical artifact contract `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
(see `../doc-tdd/`); it does **not** define a separate artifact, template, or
element-code.

**Layer**: 7 (TDD — functional focus)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4),
ADR (Layer 5), SPEC (Layer 6)

**Downstream**: IPLAN (Layer 8), Code

---

## Canonical References

Before authoring functional TDD test cases, read:

1. Canonical artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
2. Layer overview: `framework/layers/07_TDD/README.md`
3. ID & naming standards: `framework/governance/ID_NAMING_STANDARDS.md`
4. Parent TDD skill: `../doc-tdd/`

---

## When to Use

Use `doc-ftest` when:
- You are authoring TDD test cases with a **functional / end-to-end focus**.
- Quality-attribute threshold validation (performance, reliability,
  scalability, security) is a core objective.
- The behavior under test maps to full user workflows from BDD scenarios.

Use `doc-tdd` (the parent skill) instead when:
- You need the full unified TDD authoring contract across all test types.
- Unit/integration test-case authoring is the primary focus.

---

## TDD Functional-Test Contract

Functional test cases are **content within a TDD document**, not a separate
artifact. They live in the TDD template's Section 4 (Test Case Definitions),
typically as `e2e_tests` (end-to-end workflows) and optionally `security_tests`
(quality-attribute thresholds when SPEC or ADR mandates them).

### Structure

The single TDD template defines 7 sections (see `../doc-tdd/`):

1. Document Control
2. Test Pyramid
3. BDD Scenario to Test Mapping
4. Test Case Definitions — functional cases authored here
5. Test Thresholds — quality-attribute gates
6. TDD Execution Order
7. Traceability

### Element ID Format

Functional test cases use the 4-segment standard, NOT a legacy subtype code:

- Pattern: `TDD.NN.04.xxxx` (test cases live in Section 4)
- `xxxx` = 4-character hex content hash

A `type` attribute (`e2e` / `security`) marks the functional focus on each case —
there are no separate numeric type-codes or test-subtype documents.

### Functional Focus Specifics

| Concern | Where it goes in TDD |
|---------|----------------------|
| End-to-end workflow scenarios | Section 4 `e2e_tests` (numbered `workflow` steps, `timeout_seconds`, `cleanup`) |
| Quality-attribute thresholds | Section 5 Test Thresholds (`coverage_target`, `timeout_budget`, `fail_action`) |
| Security/threat validation | Section 4 `security_tests` (`threat`, `expected_result`) |

> **Coverage note**: Functional tests trace to **EARS / BDD / SPEC** — the
> behavior they validate. The legacy SYS coverage matrix is dropped (there is no
> SYS layer in the 8-layer model).

### Required Tags

- Cumulative upstream tags (Section 7 — Traceability): `@brd`, `@prd`, `@ears`,
  `@bdd`, `@adr` (element refs, dot notation) + `@spec: SPEC-NN` (document, dash).
- Self tag: `@tdd: TDD-NN` (document, dash).
- Functional test cases reference behavior via `@bdd:` (end-to-end scenarios)
  and `@spec:` (the validated contract).

### Threshold

- IPLAN-Ready score: `>=90/100`.

---

## Validation

The framework is spec-only — there are no validation scripts to run. This skill
*is* the validator: apply the declarative checklist below, with
`framework/layers/07_TDD/README.md` and `framework/governance/` as authority.

### Manual Checklist

- [ ] Document Control complete (Section 1)
- [ ] Functional cases in Section 4 carry a valid `type` (`e2e` / `security`)
- [ ] Each functional case has a `TDD.NN.04.xxxx` element ID
- [ ] End-to-end cases declare numbered `workflow` steps and a `timeout_seconds`
- [ ] Quality-attribute thresholds set in Section 5 (`coverage_target`,
      `fail_action`)
- [ ] Functional cases trace to EARS / BDD / SPEC (no SYS coverage)
- [ ] Cumulative upstream tags `@brd`..`@spec` present + `@tdd` self-tag
- [ ] IPLAN-Ready score meets target (>=90/100)
- [ ] Index updated (`docs/07_TDD/TDD-00_index.md`)

---

## Output Quality Gate

- All required TDD sections present (single 7-section template).
- Each functional test case carries explicit inputs/workflow and expected
  results.
- Quality-attribute thresholds are explicit and measurable (Section 5).
- Traceability includes the required cumulative upstream tags (no SYS).
- IPLAN-Ready score `>=90/100`.

---

## Related Skills

- `doc-ftest-autopilot`
- `doc-ftest-validator`
- `doc-ftest-reviewer`
- `doc-ftest-fixer`
- `doc-ftest-audit`
- `../doc-tdd/` (parent TDD authoring skill — full unified contract)

---

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent TDD skill: `../doc-tdd/`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Repositioned as a TDD (Layer 7) functional-test specialization referencing the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml` — no FTEST/TSPEC artifact, template, or numeric subtype-code. Functional/end-to-end scenarios and quality-attribute thresholds recast as TDD Section 4/5 content; element IDs `TDD.NN.04.xxxx`; upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN,Code; dropped SYS coverage (functional tests trace to EARS/BDD/SPEC); validation is now this skill's declarative checklist (framework is spec-only). |
| 1.0 | 2026-02-27 | Initial functional-test authoring skill (pre-migration legacy model). |
