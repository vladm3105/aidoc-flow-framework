# 07_TDD — Test-Driven Development Guide

## C4 Model Position

TDD is part of the **Implementation Bridge** (L7-L8, no C4 level). It defines test cases that validate SPEC (C4-L3 Component) contracts through test execution. C4-L4 (Code) ownership belongs to the source code layer, referenced by IPLAN.

## Purpose

Defines test cases that validate SPEC component contracts. Each TDD document maps BDD acceptance scenarios to concrete tests with inputs, outputs, edge cases, and quality thresholds. Positioned after SPEC (L6) and before IPLAN (L8).

## Design Decisions

- **L7 position** — Logical: SPEC defines what to build, TDD defines how to test it, IPLAN orchestrates the build.
- **Test case definitions embedded** — Section 4 of template provides concrete test inputs, expected outputs, and edge cases (fills the gap left by TSPEC removal).
- **Single template, no subtypes** — replaces the 42-file TSPEC v1 archive (6 subtypes × ~7 files each)
- **Test-first enforcement** — test files are generated BEFORE implementation files
- **BDD as source of truth** — no new behavior descriptions; maps existing BDD scenarios (with spec_trace links) to test types
- **One document per SPEC component** — same granularity as SPEC for minimal maintenance

## What's Different from TDD v3.0 / TSPEC v1

| TDD v3.0 / TSPEC v1 | TDD v3.2 |
|---------------------|----------|
| Position: L6 (before SPEC) | Position: L7 (after SPEC) |
| 80-line template, no test cases | Template with Section 4: test case definitions |
| Upstream: ADR + BDD only | Upstream: SPEC + ADR + BDD |
| Downstream: SPEC | Downstream: IPLAN |
| 6 subtypes (UTEST, ITEST, STEST, FTEST, PTEST, SECTEST) | Single unified template |
| 42 files total (TSPEC) | 1 template + 1 index + 1 README |

## Template

See [TDD-TEMPLATE.yaml](TDD-TEMPLATE.yaml).
