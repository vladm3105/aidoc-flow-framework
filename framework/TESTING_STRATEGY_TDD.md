# Testing Strategy: Test-Driven Development (SDD)

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.53.0 |

# Layer 7 — TDD Guide

## Overview

SDD integrates test-driven development as Layer 7, positioned after Technical Specifications (SPEC, Layer 6) and before Implementation Plans (IPLAN, Layer 8). Each TDD document defines test cases for a SPEC component by mapping BDD acceptance scenarios and SPEC interface contracts to concrete test implementations.

## TDD in the 10-Layer Workflow

```
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
                                    ↑       ↑
                            Specifies what     Defines tests against
                            to build           specification
```

The 10-layer framework adds two additional layers:
- **CHG (L9)** — Change management overlay: gates, versioning, audit trail (governance overlay, outside layer numbering)
- **EVAL (L10)** — Evaluation & QA governance: test strategy, coverage matrices

## Language-Agnostic Test Path Philosophy

The TDD layer is intentionally **language-agnostic**. Test file paths, function
names, and directory structures are defined by the TDD document, not by the
target language's conventions. This means:

- A TDD may declare test paths like `tests/unit/auth_test.go` (Go) or
  `tests/unit/test_auth.py` (Python) — the IPLAN picks up whatever the TDD
  specifies.
- Test function naming follows whatever convention the TDD declares (e.g.
  `TestLoginSuccess` for Go, `test_login_success` for Python), not a
  framework-wide default.
- The same TDD document can drive test implementation across multiple
  languages in a polyglot project: the test mappings reference concrete file
  paths and function names per language.
- Validators check that TDD-declared paths and names exist in the actual
  test files (TDD-SYNC-001 through TDD-SYNC-004), regardless of language.

This philosophy ensures that the SDD framework works for Go, Python,
TypeScript, Rust, or any other language without imposing language-specific
conventions at the framework level.

## Test-First Enforcement

The TDD layer enforces test-first development through the `tdd_order` section:

1. **Write Tests** — Test files are generated from SPEC contracts and BDD scenario mappings
2. **Run Tests (Red)** — Tests fail (no implementation yet)
3. **Implement** — Code is written to make tests pass
4. **Verify (Green)** — All tests pass
5. **Refactor** — Clean up; tests remain green

The AI agent follows this order when generating code from the IPLAN document.

## Test Pyramid

| Level | Percentage | Purpose |
|-------|-----------|---------|
| Unit | 70% | Test individual functions/methods in isolation |
| Integration | 20% | Test component interactions and contracts |
| E2E | 10% | Test full user workflows (from BDD scenarios) |

## Quality Gate Thresholds

| Test Type | Coverage Target | Action on Failure |
|-----------|----------------|-------------------|
| Unit | >=90% | Block merge |
| Integration | >=85% | Block merge |
| E2E | >=75% of happy paths | Block deploy to staging |
| Security | All auth paths | Block deploy (if applicable) |

## Test Case Definitions

SDD embeds test case definitions directly in the TDD document (Section 4):
- **Unit tests**: Inputs, expected outputs, edge cases — derived from SPEC interfaces and data models
- **Integration tests**: Contract validation, state transitions, error paths — derived from SPEC behavior
- **E2E tests**: Workflow steps, timeouts, cleanup — derived from BDD scenarios

## One Document Per Component

SDD uses a single TDD document per SPEC component. The document:
- Maps BDD scenarios to test types (unit, integration, e2e)
- Defines concrete test cases with inputs, expected outputs, edge cases
- Sets quality thresholds per test type
- Declares TDD execution order

## BDD as Source of Truth

TDD does NOT create new test scenarios. It maps **existing BDD scenarios** (with their `spec_trace` links) to test implementation. If BDD has 10 scenarios for a feature, TDD maps those 10 scenarios to their corresponding test types, file paths, and concrete test cases.

**Every BDD scenario MUST be paired to a TDD test case (normative — GD-08).**
Pairing means a TDD **test case or §3 mapping entry** names the scenario — a
`bdd_scenario` mapping entry or an e2e-case `bdd_ref` field (in a rendered
Markdown TDD, the equivalent §3 mapping row or §4 e2e line carrying the
test-case id). A scenario listed only in the TDD §7 traceability block is
**not** paired. `ACC01` (`governance/LINT_RULES.md`) enforces this deterministically:
`warning` in `build`, `error` in `gate-code`. It is stricter than `COV02`, which
accepts a scenario realized by SPEC *or* TDD and so would pass a scenario that no
test covers.

## Bidirectional Status Sync (TDD ↔ IPLAN)

The TDD→IPLAN flow is one-way by design: TDD defines test cases, IPLAN picks them up via
`tdd_ref`, and the executor builds files. But the **return path** — status propagation from
executor back to TDD — was missing. This caused the "IPLAN says DONE, TDD says pending" bug.

### The Problem

1. IPLAN `file_manifest.files[].status: DONE` means "the file was created", not "every TDD
   test case inside it was implemented."
2. TDD `test_mapping.scenarios[].tests[].status: pending` has no lifecycle rules — nothing in
   the framework ever updates it.
3. No cross-layer validation checks that TDD function names exist in actual test files.
4. No lint rule verifies IPLAN test file paths match TDD `test_file` paths.

### The Fix: Four Lint Rules

| Rule | What it checks |
|------|---------------|
| `TDD-SYNC-001` | TDD `test_mapping` function names exist as `def test_*` / `function test_*` in declared `test_file` |
| `TDD-SYNC-002` | IPLAN `file_manifest` test file paths match TDD `test_file` paths |
| `TDD-SYNC-003` | IPLAN `status: DONE` + TDD `status: pending` = status not propagated |
| `TDD-SYNC-004` | TDD `test_file` paths exist on disk |

### Status Lifecycle for TDD test cases

TDD `test_mapping.scenarios[].tests[].status` transitions:
```
pending → implemented   (test function exists in file AND passes)
pending → missing       (test file does not exist on disk)
```

When an executor marks an IPLAN `file_manifest` entry as `DONE` with `verified: true`, it
MUST also update the corresponding TDD `test_mapping` status from `pending` to `implemented`
for each test case that the file implements.

### Execution Protocol

When implementing from an IPLAN:

1. Before writing test code: read TDD `test_mapping` for the function names and file paths.
2. Write the test file with functions matching the TDD-specified names.
3. After tests pass: update BOTH:
   - IPLAN `file_manifest` entry: `status: DONE`, `verified: true`
   - TDD `test_mapping` entries: `status: implemented`
4. If TDD-specified names don't fit the implementation, update the TDD FIRST (rename the
   function), then implement with the new name.

### Naming Discipline

Test function names in code MUST match the names declared in TDD `test_mapping`. If a
TDD-specified name is awkward or conflicts with an existing test, update the TDD document
before writing the code — never write a test with a different name and leave the TDD stale.
