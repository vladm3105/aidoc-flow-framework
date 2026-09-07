# 07_TDD — Test-Driven Development Guide

## C4 Model Position

TDD is part of the **Implementation Bridge** (L7-L8, no C4 level). It defines test cases that validate SPEC (C4-L3 Component) contracts through test execution. C4-L4 (Code) ownership belongs to the source code layer, referenced by IPLAN.

## Purpose

Defines test cases that validate SPEC component contracts. Each TDD document maps BDD acceptance scenarios to concrete tests with inputs, outputs, edge cases, and quality thresholds. Positioned after SPEC (L6) and before IPLAN (L8).

## Design Decisions

- **L7 position** — Logical: SPEC defines what to build, TDD defines how to test it, IPLAN orchestrates the build.
- **Test case definitions embedded** — Section 4 of template provides concrete test inputs, expected outputs, and edge cases.
- **Single template, no subtypes** — unified TDD authoring contract.
- **Test-first enforcement** — test files are generated BEFORE implementation files
- **BDD as source of truth** — no new behavior descriptions; maps existing BDD scenarios (with spec_trace links) to test types
- **Acceptance pairing is normative (GD-08)** — every BDD scenario MUST be paired to a TDD **test case**: named in a `bdd_scenario` mapping entry or an e2e-case `bdd_ref` (in a rendered Markdown TDD, the equivalent §3 mapping row or §4 e2e line carrying the test-case id). A scenario named only in the §7 traceability block is not paired. Enforced by `ACC01` (`../../governance/LINT_RULES.md`): `warning` in `build`, `error` in `gate-code`. Stricter than `COV02` (which a SPEC-only citation satisfies).
- **One document per SPEC component** — same granularity as SPEC for minimal maintenance
- **Test strategy defines HOW tests are written** — Section 2 provides conventions for test organization, naming, mocking, and execution that IPLANs follow

## Element IDs

Hash-based, content-derived IDs scoped to TDD content. TDD is one of the six layers that **MUST** carry element IDs on every distinct content unit (`../../governance/ID_NAMING_STANDARDS.md`); SPEC (L6) and IPLAN (L8) are the two documented exemptions.

> The SHA-256 form is the **canonicalization target**: engines emit stable opaque strings that *should* match it. `rehash --check` verification is shipped for BRD §7 only (PROVISIONAL-IDS-002 Phase 1); extraction for this layer is Phase 2+. See `ID_NAMING_STANDARDS.md`.

```text
Format: TDD.{doc_id}.{section_id}.{hash}
Example: TDD.01.04.f19c
```

Test cases live in **Section 4**, so authored test-case IDs carry `04` as the `{section_id}` segment.

Algorithm: SHA256 of `"{doc_id}:{section_id}:{norm(title)}:{norm(description)}"`, first 4 hex chars (the canonicalization target; not verified until `rehash --check`). `norm()` is the normalization transform, and `governance/ID_NAMING_STANDARDS.md` is its **single source** — along with the byte-exact input assembly. Do not re-specify it here.

Which test-case field supplies `title` and which supplies `description` is **not defined**: a TDD case declares `name` / `spec_ref` / `target` / `test_file` / `test_function` and carries neither field. Naming a mapping would be a new normative contract rather than a documentation fix, so it is deferred to PROVISIONAL-IDS-002 Phase 2+ along with the other four non-BRD layers, none of which has a defined extraction boundary either.

See template `metadata.id_standard` for details.

## TDD Baseline

| Area | TDD |
|---------------------|----------|
| Position | L7 (after SPEC) |
| Test case shape | Section 4 test case definitions |
| Upstream | EARS + BDD + ADR + SPEC |
| Downstream | IPLAN, EVAL |
| Template model | Single unified template |
| Core assets | Template + index + README |

## Test Strategy (Section 2)

The Test Strategy section defines HOW tests are written, organized, and executed. It provides conventions that IPLANs follow when generating test files.

### Key Components

| Component | Purpose |
|-----------|---------|
| **test_types** | Defines unit, integration, e2e, and security test purposes and scopes |
| **mock_strategy** | Defines when to use mocks vs stubs vs real dependencies |
| **test_data** | Defines how test data is created, managed, and cleaned up |
| **execution_strategy** | Defines when and how tests run in development workflow |
| **distribution** | Target percentages for test pyramid (70/20/10) |

### IPLAN Integration

IPLANs reference TDD test strategy when generating test files:

1. **Test file paths** come from TDD `test_cases.*.test_file`
2. **Test function names** come from TDD `test_cases.*.test_function`
3. **Test logic** is derived from TDD `inputs` and `expected_output`
4. **Execution order** follows TDD `tdd_order` (tests first, then implementation)

### Verification Workflow

```
TDD defines tests → IPLAN generates files → Tests run → IPLAN status transitions
     ↓                    ↓                    ↓                    ↓
Section 2 (strategy)  file_manifest      tdd_order           Completed → Verified
Section 4 (cases)     tdd_ref links      Phase 1-5           (after validation)
```

## Template

| File | Purpose |
|------|---------|
| `TDD-TEMPLATE.yaml` | **Default** — full template with embedded authoring guidance. Self-documenting for AI agents. |
| `TDD-00_index.TEMPLATE.md` | TDD registry template — tracks planned and active TDDs per project |
