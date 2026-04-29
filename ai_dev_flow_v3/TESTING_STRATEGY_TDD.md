# Testing Strategy: Test-Driven Development (SDD v3)
# Layer 6 — TDD Guide

## Overview

SDD v3 integrates test-driven development as Layer 6, positioned between Architecture Decision Records (ADR, Layer 5) and Technical Specifications (SPEC, Layer 7). Each TDD document defines the test strategy for a SPEC component by mapping BDD acceptance scenarios to test implementation ordering.

## TDD in the 7-Layer Workflow

```
BRD → PRD → EARS → BDD → ADR → TDD → SPEC → Code
                                   ↑
                            Tests defined here,
                            generated BEFORE code
```

## Test-First Enforcement

The TDD layer enforces test-first development through the `tdd_order` section:

1. **Write Tests** — Test files are generated from BDD scenario mappings
2. **Run Tests (Red)** — Tests fail (no implementation yet)
3. **Implement** — Code is written to make tests pass
4. **Verify (Green)** — All tests pass
5. **Refactor** — Clean up; tests remain green

The AI agent/coder follows this order when generating code from the SPEC document.

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

## One Document Per Component

Unlike the 42-file TSPEC v1 archive (6 subtypes × ~7 files each), SDD v3 uses a single TDD document per SPEC component. The document:

- Maps BDD scenarios to test types (unit, integration, e2e)
- Declares test file paths and function names
- Sets quality thresholds per test type
- Declares TDD execution order

## BDD as Source of Truth

TDD does NOT create new test scenarios. It maps **existing BDD scenarios** to test implementation. If BDD has 10 scenarios for a feature, TDD maps those 10 scenarios to their corresponding test types and file paths.
