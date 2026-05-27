---
title: "BDD: URL Shortener"
doc_id: "BDD-01"
artifact_type: BDD
layer: 4
status: Approved
version: "1.0.0"
created: "2026-05-27"
last_updated: "2026-05-27"
custom_fields:
  document_type: bdd-document
  artifact_type: BDD
  layer: 4
  upstream_artifacts: [BRD-01, PRD-01, EARS-01]
  downstream_artifacts: [ADR-01]
  readiness_score: 92
---

# BDD-01: URL Shortener

## Document Control

| Field | Value |
|-------|-------|
| Document ID | BDD-01 |
| Status | Approved |
| Version | 1.0.0 |
| Readiness score | 92 / 100 |
| Source | @ears: EARS.01.03.5e2a |

## 1. Purpose & Context

Executable acceptance scenarios for the URL shortener, derived from `EARS-01`.
Upstream: @brd: BRD.01.04.0a13 | @prd: PRD.01.09.1dbc | @ears: EARS.01.03.5e2a

## 2. Scenarios

### BDD.01.03.8f4c — Create a short link

Source @ears: EARS.01.03.5e2a

```gherkin
Feature: Create short link
  Scenario: A long URL is shortened
    Given a valid long URL
    When the user submits it
    Then the service returns a unique short code
    And the code resolves back to the submitted URL
```

### BDD.01.03.2c6b — Redirect a known code

Source @ears: EARS.01.03.a1f7

```gherkin
Feature: Redirect
  Scenario: A known short code redirects
    Given a previously created short code
    When a visitor requests that code
    Then the service responds with a redirect to the original URL
```

### BDD.01.03.9a1d — Unknown code returns 404

Source @ears: EARS.01.03.c3d9

```gherkin
Feature: Unknown code
  Scenario: An unknown short code is rejected
    Given a short code that was never issued
    When a visitor requests that code
    Then the service responds with a 404 status
```

## 3. Traceability

Upstream: @brd: BRD.01.04.0a13 | @prd: PRD.01.09.4e21 | @ears: EARS.01.03.a1f7
Downstream `ADR-01` records the architecture decision these scenarios constrain.
