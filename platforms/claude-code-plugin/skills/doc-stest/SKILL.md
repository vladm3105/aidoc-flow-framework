---
name: doc-stest
description: Author TDD (Layer 7) test cases with a smoke-test focus for deployment critical-path validation, health checks, and rollback readiness
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-smoke-helper
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: smoke
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

# doc-stest

## Purpose

Author **TDD (Layer 7)** test cases with a **smoke-test focus** — deployment
critical-path validation, post-deploy health checks, and rollback readiness,
with strict fail-fast pass/fail outcomes.

This skill is a **TDD (Layer 7) specialization** for the smoke-test focus. It
authors test cases inside the single canonical TDD document contract and does
**not** define a separate artifact, template, or element-code. Smoke tests are
TDD test cases (`type: e2e` / `type: integration`) whose intent is rapid
critical-path verification of a deployed system.

**Layer**: 7

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4),
ADR (Layer 5), SPEC (Layer 6)

**Downstream**: IPLAN (Layer 8), Code

---

## Canonical References

Before authoring smoke-focused TDD test cases, read:

1. Canonical artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
2. Layer overview: `framework/layers/07_TDD/README.md`
3. ID & tag standards: `framework/governance/ID_NAMING_STANDARDS.md`
4. Parent TDD skill: `../doc-tdd/`
5. Shared standards: `../doc-flow/SHARED_CONTENT.md`

---

## When to Use

Use `doc-stest` when:
- You are authoring TDD test cases with a **smoke / deployment critical-path** focus.
- `@ears`, `@bdd`, and `@spec` constraints drive the critical paths under test.
- Deployment smoke validation, health checks, and rollback readiness are the core objective.

Use `doc-tdd` instead when:
- Authoring the full TDD test suite across unit/integration/e2e/security types.
- Cross-focus normalization or whole-document TDD work is primary.

---

## Smoke-Focus Contract

### Where smoke tests live in the TDD document

Smoke test cases are authored in **Section 4 (Test Case Definitions)** of the
single TDD document (`framework/layers/07_TDD/TDD-TEMPLATE.yaml`), typically as
`integration` or `e2e` cases that exercise the deployment critical path. They
are mapped from BDD scenarios in Section 3 and gated by thresholds in Section 5.

### Required Tags

- Cumulative upstream tags (Layer 7): `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@spec`
- TDD self-tag: `@tdd: TDD-NN`
- Critical-path test cases must trace to `@bdd` and `@spec`.

### Deployment Gate Requirements (smoke focus)

- Total smoke timeout budget should be `<=300s` (max 300s / <5 minutes).
- Critical-path quality target is `100%` (every critical-path scenario passes).
- Every critical-path test case declares a rollback procedure (`cleanup` /
  rollback action).
- Pass/fail criteria must be binary and fail-fast.

### Element IDs

- Document: `TDD-NN`
- Test cases (Section 4): `TDD.NN.04.xxxx` (4-segment; `xxxx` = 4-char hex hash).
- Smoke focus is expressed as test-case content/`type`, NOT as a separate ID code.

### Folder Rule

- `docs/07_TDD/TDD-NN_{slug}.yaml` (one TDD per SPEC component).

---

## Validation (declarative — framework is spec-only)

The framework ships no validation scripts; this skill *is* the validator. Apply
the checklist below, with `framework/layers/07_TDD/README.md` and
`framework/governance/` as authority:

1. TDD document follows the 7-section template and parses as YAML.
2. Smoke test cases use `TDD.NN.04.xxxx` element IDs with a `type`
   (`integration` / `e2e`).
3. Cumulative upstream tags present (`@brd`..`@spec`) plus the `@tdd` self-tag.
4. Critical-path cases trace to `@ears`, `@bdd`, and `@spec`.
5. Smoke timeout budget markers present (`max 300s` or `<=300s`).
6. Rollback / cleanup declared for every critical-path case.
7. Binary, fail-fast pass/fail criteria are explicit for critical paths.

---

## Output Quality Gate

- No schema/structure blockers; all 7 TDD sections present.
- `@ears`, `@bdd`, and `@spec` mappings explicit for critical paths.
- Smoke timeout and rollback constraints present.
- Binary pass/fail criteria explicit for critical paths.

---

## Related Skills

- `doc-stest-autopilot`
- `doc-stest-validator`
- `doc-stest-reviewer`
- `doc-stest-fixer`
- `doc-stest-audit`
- `../doc-tdd/` (full-suite TDD authoring)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Repositioned as a TDD (Layer 7) smoke-focus specialization referencing `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; documents are `TDD-NN`, test cases `TDD.NN.04.xxxx`. Dropped the retired upstream layers and the legacy smoke-test subtype identity, numeric subtype code, legacy flow paths, and dead validation scripts (now a declarative checklist). Upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN. |
| 1.0 | 2026-02-27 | Initial smoke-test authoring skill (pre-migration). |
