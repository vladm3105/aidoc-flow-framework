---
title: "TDD: Shorten Service"
doc_id: "TDD-01"
artifact_type: TDD
layer: 7
status: Approved
version: "1.0.0"
created: "2026-05-27"
last_updated: "2026-05-27"
custom_fields:
  document_type: tdd-document
  artifact_type: TDD
  layer: 7
  upstream_artifacts: [BRD-01, PRD-01, EARS-01, BDD-01, ADR-01, SPEC-01]
  downstream_artifacts: [IPLAN-01]
  readiness_score: 92
---

# TDD-01: Shorten Service

## Document Control

| Field | Value |
|-------|-------|
| Document ID | TDD-01 |
| Status | Approved |
| Version | 1.0.0 |
| Readiness score | 92 / 100 |
| Spec source | @spec: SPEC-01 |

## 1. Overview

Test-case definitions for `SPEC-01`, mapping each BDD scenario to verifiable
tests. Source @spec: SPEC-01

## 2. Test Cases

- **TDD.01.04.a3c1** — type: unit. `create` returns a unique 7-char code and the
  mapping resolves back to the input URL. Covers @bdd: BDD.01.03.8f4c and
  @spec: SPEC-01
- **TDD.01.04.f0e2** — type: integration. A created code, when resolved, yields a
  redirect to the original URL. Covers @bdd: BDD.01.03.2c6b
- **TDD.01.04.7b9c** — type: unit. `resolve` of an unissued code returns
  not-found (maps to a 404). Covers @bdd: BDD.01.03.9a1d

## 3. Scenario-to-test mapping

| Test | Scenario | Type |
|------|----------|------|
| TDD.01.04.a3c1 | create short link | unit |
| TDD.01.04.f0e2 | redirect | integration |
| TDD.01.04.7b9c | unknown code 404 | unit |

## 4. Quality Thresholds

Line coverage target 80 percent for the service module.
Tracked as @threshold: TDD.01.quality.coverageTarget

## 5. Execution Order

1. Unit tests (create, resolve).
2. Integration test (end-to-end redirect).

## 6. Traceability

Upstream: @brd: BRD.01.04.0a13 | @prd: PRD.01.09.1dbc | @ears: EARS.01.03.5e2a | @bdd: BDD.01.03.8f4c | @adr: ADR-01 | @spec: SPEC-01
Downstream `IPLAN-01` sequences the implementation.
