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
- **One document per SPEC component** — same granularity as SPEC for minimal maintenance

## TDD Baseline

| Area | TDD |
|---------------------|----------|
| Position | L7 (after SPEC) |
| Test case shape | Section 4 test case definitions |
| Upstream | SPEC + ADR + BDD |
| Downstream | IPLAN |
| Template model | Single unified template |
| Core assets | Template + index + README |

## Template

See [TDD-TEMPLATE.yaml](TDD-TEMPLATE.yaml).
