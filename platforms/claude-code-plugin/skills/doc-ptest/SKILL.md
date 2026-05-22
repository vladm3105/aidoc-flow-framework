---
name: doc-ptest
description: Author performance-focused Test-Driven Development (TDD, Layer 7) test cases for load, stress, endurance, and spike validation
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-performance-helper
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: performance
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

# doc-ptest

## Purpose

Author **performance-focused TDD (Layer 7)** test cases — validating system
behavior under Load, Stress, Endurance, and Spike conditions — within the
single unified TDD document.

This skill is a **TDD (Layer 7) specialization** for the performance-test
focus. It authors TDD test cases (Section 4 of the template) with a performance
emphasis and references the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`); it does **not**
define a separate artifact, template, or element-code.

**Layer**: 7 (TDD — performance focus)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4),
ADR (Layer 5), SPEC (Layer 6)

**Downstream**: IPLAN (Layer 8), Code

---

## Canonical References

Before authoring performance-focused TDD test cases, read:

1. Canonical artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
2. Layer overview: `framework/layers/07_TDD/README.md`
3. Parent TDD skill: `../doc-tdd/`
4. ID & tag standards: `framework/governance/ID_NAMING_STANDARDS.md`
5. Performance threshold rules: `framework/governance/THRESHOLD_NAMING_RULES.md`

---

## When to Use

Use `doc-ptest` when:
- You are authoring TDD test cases with a **performance** focus.
- SPEC (Layer 6) and ADR (Layer 5) performance constraints are primary.
- Performance thresholds and load-profile behavior are the core objective.

Use `../doc-tdd/` directly when:
- Authoring functional unit/integration/e2e test cases is primary.
- No performance-test specialization is needed.

---

## Performance Test-Case Content (within the single TDD template)

Performance test cases are TDD test cases (Section 4 of
`framework/layers/07_TDD/TDD-TEMPLATE.yaml`) carrying a `type` attribute and a
performance-focused content shape. They are NOT a separate artifact, subtype,
or element-code.

### Element ID Format

Performance test cases use the standard 4-segment TDD element ID:

**Pattern**: `TDD.{doc_id}.04.{hash}` — test cases live in Section 4.

**Example**: `TDD.01.04.a3c1`

Categorize the performance scenario with a content label (Load / Stress /
Endurance / Spike), NOT a separate ID code or separate document.

### Performance Scenario Categories

Capture each test case under one of the performance scenario categories:

| Category | Focus | Source constraint |
|----------|-------|-------------------|
| Load | Expected/peak concurrent demand | SPEC, ADR performance targets |
| Stress | Beyond-capacity breaking point | SPEC, ADR performance targets |
| Endurance | Sustained load over time (soak) | SPEC, ADR performance targets |
| Spike | Sudden burst of demand | SPEC, ADR performance targets |

### Performance Test-Case Shape

Each performance test case should declare:

- A **load scenario** (concurrency, duration, ramp profile).
- An `execution_profile` for complex scenarios (ramp-up, steady, ramp-down).
- Measurable **thresholds** referenced via `@threshold:` tags — define
  performance targets in BRD/PRD/ADR and reference them, per
  `framework/governance/THRESHOLD_NAMING_RULES.md` (e.g.
  `@threshold: ADR.NN.perf.api.p95`).

```yaml
performance_tests:
  cases:
    - id: "TDD.01.04.a3c1"
      name: "API sustains peak load within p95 target"
      type: e2e
      scenario: Load
      spec_ref: "@spec: SPEC-01"
      adr_ref: "@adr: ADR.01.03.e5b1"
      load_scenario:
        concurrency: 500          # virtual users
        duration_seconds: 300
        ramp_up_seconds: 60
      execution_profile:
        - phase: ramp-up
          seconds: 60
        - phase: steady
          seconds: 180
        - phase: ramp-down
          seconds: 60
      thresholds:
        - "@threshold: ADR.01.perf.api.p95"   # 200 ms
        - "@threshold: ADR.01.perf.api.p99"   # 500 ms
      expected_result:
        type: pass
        value: "p95 <= 200 ms under 500 concurrent users"
```

---

## Validation Checks (declarative)

The framework is spec-only — there are no validation scripts to run. This skill
*is* the validator: apply the checks below, with
`framework/layers/07_TDD/README.md` and `framework/governance/` as authority.

| Check | Description |
|-------|-------------|
| CHECK 1 | TDD document follows `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (7 sections) |
| CHECK 2 | Performance test cases use the 4-segment ID `TDD.NN.04.xxxx` |
| CHECK 3 | Each performance case carries a `type` and a scenario label (Load/Stress/Endurance/Spike) |
| CHECK 4 | Load scenario present; `execution_profile` present for complex scenarios |
| CHECK 5 | Thresholds are measurable and referenced via `@threshold:` tags from BRD/PRD/ADR |
| CHECK 6 | Cumulative upstream tags present: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@spec` (+ `@tdd` self-tag) |
| CHECK 7 | Parent SPEC reference valid and file exists |

---

## Output Quality Gate

- No schema/structure blockers; all 7 TDD template sections present.
- `@spec` and `@adr` performance constraints are explicit.
- Load scenarios and measurable, `@threshold:`-tagged targets are present.
- Traceability includes the required cumulative tags.
- IPLAN-Ready Score `>=90/100`.

---

## Related Skills

- `doc-ptest-autopilot`
- `doc-ptest-validator`
- `doc-ptest-reviewer`
- `doc-ptest-fixer`
- `doc-ptest-audit`
- `../doc-tdd/` (parent TDD authoring skill)

---

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Governance / ID & naming standards: `framework/governance/ID_NAMING_STANDARDS.md`
- Performance threshold rules: `framework/governance/THRESHOLD_NAMING_RULES.md`
- Parent TDD skill: `../doc-tdd/`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) performance-test specialization referencing the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no PTEST/TSPEC artifact, subtype code, or element-code). 4-segment IDs (`TDD.NN.04.xxxx`); performance scenarios (Load/Stress/Endurance/Spike) are content labels; thresholds via `@threshold:` tags. Upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN. Validation is this skill's declarative checklist (framework is spec-only). |
| 1.0 | 2026-02-27 | Initial PTEST authoring skill (pre-migration, legacy 12-layer model). |
