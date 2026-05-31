---
title: "IPLAN: Shorten Service"
doc_id: "IPLAN-01"
artifact_type: IPLAN
layer: 8
status: Completed
version: "1.0.0"
created: "2026-05-27"
last_updated: "2026-05-27"
custom_fields:
  document_type: iplan-document
  artifact_type: IPLAN
  layer: 8
  upstream_artifacts: [BRD-01, PRD-01, EARS-01, BDD-01, ADR-01, SPEC-01, TDD-01]
  downstream_artifacts: [Code]
  readiness_score: 91
---

# IPLAN-01: Shorten Service

## Document Control

| Field | Value |
|-------|-------|
| Document ID | IPLAN-01 |
| Status | Completed |
| Version | 1.0.0 |
| Readiness score | 91 / 100 |
| Self | @iplan: IPLAN-01 |

## 1. Overview

The execution bridge from `SPEC-01` + `TDD-01` to code: file manifest, commands,
and the audit trail for implementing the ShortenService component.
Source @spec: SPEC-01 and @tdd: TDD.01.04.a3c1

## 2. File Manifest

| File | Purpose |
|------|---------|
| `src/shorten_service.py` | `create` / `resolve` per @spec: SPEC.01.03.a1b2 |
| `src/store_port.py` | key-value store port |
| `tests/test_shorten_service.py` | tests per @tdd: TDD.01.04.a3c1 |

## 3. Commands

```bash
python -m pytest tests/test_shorten_service.py
ruff check src tests
```

## 4. Implementation Steps

1. Implement `StorePort` (get / put-if-absent).
2. Implement `ShortenService.create` with base62 codes + bounded collision retry
   per @adr: ADR-01
3. Implement `ShortenService.resolve` returning the URL or not-found.
4. Write the tests from `TDD-01`; make them pass.

## 5. Session Handoff

State after each step in the PR description; the suite under section 3 is the
gate before merge.

## 6. Audit Trail

| Step | Verifies |
|------|----------|
| 1-2 | @bdd: BDD.01.03.8f4c |
| 3 | @bdd: BDD.01.03.9a1d |
| 4 | @tdd: TDD.01.04.a3c1 |

## 7. Traceability

Upstream: @brd: BRD.01.04.0a13 | @prd: PRD.01.09.1dbc | @ears: EARS.01.03.5e2a | @bdd: BDD.01.03.8f4c | @adr: ADR-01 | @spec: SPEC-01 | @tdd: TDD.01.04.a3c1
Downstream the implementation (Code).
