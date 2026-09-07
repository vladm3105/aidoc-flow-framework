# v3 Artifact to IPLAN Bridge

## Status

Active bridge for SDD v3.2 governance integration.

## Canonical Chain

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

## Bridge Purpose

This bridge defines how upstream v3 artifacts map into per-issue execution plans (`IPLAN`).

| Aspect | v3 Upstream Artifacts | IPLAN |
|---|---|---|
| Scope | Cross-issue design and constraints | Single issue execution |
| Format | YAML/structured docs | Markdown execution plan |
| Traceability | Artifact IDs and references | Issue + upstream references + verification |

## Required IPLAN Trace Tags

- `@brd`
- `@prd`
- `@ears` (if present)
- `@bdd` (if present)
- `@adr` (if present)
- `@spec`
- `@tdd`

## Deprecated

TASKS as a required governance bridge artifact is deprecated in v3 active workflows.
