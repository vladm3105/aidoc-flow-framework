# TDD and BDD to QA Bridge

## Overview

This document maps SDD v3 `TDD` and `BDD` artifacts to governance QA execution.

## Canonical Chain

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

## Test Mapping

| Test Type | Source Artifact | Execution Surface | Environment |
|---|---|---|---|
| Unit | TDD test cases | CI | PR checks |
| Integration | TDD test cases | CI | PR checks |
| System | TDD + SPEC | QA workflow | Staging |
| Functional | BDD scenarios + TDD | QA workflow | Staging |

## Registry Guidance

Preferred registry path:
- `docs/07_TDD/test_registry.yaml`

Optional BDD scenario catalog:
- `tests/bdd/features/*.feature`

## QA Script Integration

`governance/scripts/workflows/execute_qa_tests.py` maps pytest results to TDD registry IDs and generates traceability output.

## References

- `ucx_flow_v3/07_TDD/TDD-TEMPLATE.yaml`
- `ucx_flow_v3/04_BDD/BDD-TEMPLATE.yaml`
- `governance/templates/qa/01-testing-strategy.md`
