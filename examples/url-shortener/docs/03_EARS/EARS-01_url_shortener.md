---
title: "EARS: URL Shortener"
doc_id: "EARS-01"
artifact_type: EARS
layer: 3
status: Approved
version: "1.0.0"
created: "2026-05-27"
last_updated: "2026-05-27"
custom_fields:
  document_type: ears-document
  artifact_type: EARS
  layer: 3
  upstream_artifacts: [BRD-01, PRD-01]
  downstream_artifacts: [BDD-01]
  readiness_score: 93
---

# EARS-01: URL Shortener

## Document Control

| Field | Value |
|-------|-------|
| Document ID | EARS-01 |
| Status | Approved |
| Version | 1.0.0 |
| Readiness score | 93 / 100 |
| Source | @prd: PRD.01.09.1dbc |

## 1. Purpose & Context

Formal, testable requirements for the URL shortener, refining `PRD-01` into
WHEN-THE-SHALL-WITHIN statements. Upstream tags @brd: BRD.01.04.0a13 and
@prd: PRD.01.09.1dbc are carried forward.

## 2. Requirements

### Event-driven

- **EARS.01.03.5e2a** — WHEN a user submits a long URL, THE service SHALL return
  a unique short code WITHIN 300 ms. Source @prd: PRD.01.09.1dbc
- **EARS.01.03.a1f7** — WHEN a request for a known short code arrives, THE
  service SHALL respond with a redirect to the original URL WITHIN 50 ms.
  Source @prd: PRD.01.09.4e21

### Unwanted

- **EARS.01.03.c3d9** — IF a request references an unknown short code, THE
  service SHALL respond with a 404 status WITHIN 50 ms. Source @prd: PRD.01.09.4e21

### Ubiquitous

- **EARS.01.03.b2e8** — THE service SHALL guarantee that issued short codes are
  unique for all created links. Source @brd: BRD.01.05.1f9d

## 3. Quality Attributes

| Attribute | Target |
|-----------|--------|
| Performance | redirect p95 under 50 ms |
| Reliability | unknown-code handling never 5xx |

Tracked as @threshold: EARS.01.perf.redirectP95Ms

## 4. Traceability

Upstream: @brd: BRD.01.04.0a13 | @prd: PRD.01.09.1dbc
Downstream `BDD-01` turns each statement into Given-When-Then scenarios.

## 5. Glossary

- **Issued code** — a short code that has been created and stored.
