# EARS-01: Login Requirements

## Document Control

- Status: In Review
- Traceability: @brd: BRD.01.07.a7f3 | @prd: PRD.01.09.1dbc

## Purpose and Context

Capture login event/state/optional/unwanted requirements traced to upstream BRD/PRD.

## Requirements

EARS.01.03.c4d8 — Event-driven:
WHEN a user submits valid credentials,
THE system SHALL establish a session WITHIN 200ms.
@brd: BRD.01.07.a7f3 | @prd: PRD.01.09.1dbc

EARS.01.03.b2e1 — Optional / feature-gated:
WHERE multi-factor authentication is enabled,
THE system SHALL require a second factor.
@brd: BRD.01.07.a7f3 | @prd: PRD.01.09.1dbc
@threshold: PRD.01.auth.attempts.max

EARS.01.03.f0a9 — Unwanted:
IF the credentials are invalid,
THE system SHALL reject the attempt WITHIN 100ms.
@brd: BRD.01.07.a7f3 | @prd: PRD.01.09.1dbc

## Quality Attributes

Latency budget recorded above via @threshold: PRD.01.auth.attempts.max

## Traceability

Upstream references: @brd: BRD.01.07.a7f3 | @prd: PRD.01.09.1dbc

## Glossary

- MFA — multi-factor authentication.
