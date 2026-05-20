# Testing Strategy

**Project**: {PROJECT_NAME}

## SDD v3 Test Model

This project follows TDD + BDD test design with governance QA execution.

Canonical chain:
`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

Primary guide:
- `ucx_flow_v3/07_TDD/TDD-TEMPLATE.yaml`

## Quick Reference

| Test Type | Source | Environment |
|---|---|---|
| Unit, Integration | TDD test cases | CI |
| System, Functional | TDD + SPEC | Staging |
| Acceptance scenarios | BDD | Staging |
