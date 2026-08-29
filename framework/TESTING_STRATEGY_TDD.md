# Testing Strategy: Test-Driven Development (SDD)
# Layer 7 — TDD Guide

## Overview

SDD integrates test-driven development as Layer 7, positioned after Technical Specifications (SPEC, Layer 6) and before Implementation Plans (IPLAN, Layer 8). Each TDD document defines test cases for a SPEC component by mapping BDD acceptance scenarios and SPEC interface contracts to concrete test implementations.

## TDD in the 8-Layer Workflow

```
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
                                    ↑       ↑
                            Specifies what     Defines tests against
                            to build           specification
```

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

## Test Paths Derive From the SPEC's `language:`

**The framework prescribes no test-file layout.** Test-file paths and
test-function names follow the conventions of the language and framework
declared upstream, in the SPEC's `language:` field — SPEC owns the toolchain
(`SPEC-TEMPLATE.yaml` **§2 Component Overview**, `component_overview.language`).

So `TDD-TEMPLATE.yaml` and `SPEC-TEMPLATE.yaml` carry **placeholders**, not
examples. They use different keys, because each names the path from its own side:

```yaml
# TDD-TEMPLATE.yaml §4 — the test case
test_file: "<unit test path, per the @spec language>"
test_function: "<unit test function name>"

# SPEC-TEMPLATE.yaml §7 tdd_contracts — the files the TDD will define
- path: "<unit test path, per the language: declared above>"
```

Replace them with concrete paths in the project's own toolchain, **including its
addressing convention** — the separator is part of what varies. A Python project
writes `tests/unit/test_auth.py` / `test_validate_token` (pytest addresses it as
`path::name`); a Go project writes `internal/auth/service_test.go` /
`TestValidateToken` (addressed as `go test -run TestValidateToken ./internal/auth`);
a TypeScript project writes `src/auth/__tests__/service.spec.ts`. All three are
conformant, and writing a Go path with pytest's `::` separator is the mistake this
section exists to prevent.

**Do not re-pin a language in TDD or IPLAN.** `IPLAN-TEMPLATE.yaml` states the
same rule twice for its own `file_manifest` and `execution_commands`, and the
reason is one-source-of-truth rather than style: a polyglot project (a Go
backend and a TypeScript frontend behind one SPEC set) has no single correct
test path, and a template that names one silently invalidates every other
toolchain. The per-tier distinction the templates *do* make — unit /
integration / e2e / security — is language-independent and is retained.

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
