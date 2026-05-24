# Testing Strategy: Test-Driven Development (SDD v3.2)

# Layer 7 — TDD Guide

## Overview

SDD v3.2 integrates test-driven development as Layer 7, positioned after Technical Specifications (SPEC, Layer 6) and before Implementation Plans (IPLAN, Layer 8). Each TDD document defines test cases for a SPEC component by mapping BDD acceptance scenarios and SPEC interface contracts to concrete test implementations.

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

SDD v3.2 embeds test case definitions directly in the TDD document (Section 4):

- **Unit tests**: Inputs, expected outputs, edge cases — derived from SPEC interfaces and data models
- **Integration tests**: Contract validation, state transitions, error paths — derived from SPEC behavior
- **E2E tests**: Workflow steps, timeouts, cleanup — derived from BDD scenarios

## One Document Per Component

SDD v3.2 uses a single TDD document per SPEC component. The document:

- Maps BDD scenarios to test types (unit, integration, e2e)
- Defines concrete test cases with inputs, expected outputs, edge cases
- Sets quality thresholds per test type
- Declares TDD execution order

## BDD as Source of Truth

TDD does NOT create new test scenarios. It maps **existing BDD scenarios** (with their `spec_trace` links) to test implementation. If BDD has 10 scenarios for a feature, TDD maps those 10 scenarios to their corresponding test types, file paths, and concrete test cases.

## v3.2 Changes from v3.0

| Change | Rationale |
|--------|-----------|
| TDD moved to L7 | Logical: SPEC defines what to build first, then TDD defines tests against SPEC |
| Section 4: Test Case Definitions added | Concrete test inputs, outputs, edge cases are explicit in TDD |
| Upstream: SPEC (not just ADR) | Test cases derive directly from SPEC interfaces, data models, and behavior |
| Downstream: IPLAN | TDD test-first order enforced by IPLAN execution |
