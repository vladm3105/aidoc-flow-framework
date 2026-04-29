# 07_SPEC — Technical Specification

## Purpose

Implementation-ready technical specification for a single software component. Defines interfaces, data models, and behavior contracts before code is written.

## Design Decisions

- **Unified template** — no CSPEC/DSPEC/UXSPEC/PROCSPEC/RISKSPEC subtypes
- **Subtype routing removed** — `deliverable_type` field eliminated; one SPEC template fits all
- **Test contract references** — links to TDD layer (Layer 6) for test file declarations
- **Unified v1.0 metadata model** — same structure as all other layers (no v2.0 divergence)

## What's Different from SPEC v2 (ai_dev_ssd_flow)

| SPEC v2 (14-layer) | SPEC v3 (7-layer) |
|--------------------|-------------------|
| schema_version 2.0, different metadata model | schema_version 1.0, unified model |
| Massive nested traceability tree | Flat upstream tags |
| 5 subtypes with separate templates | Single unified template |
| Upstream: REQ + CTR + SYS + ADR | Upstream: TDD + ADR |
| 30+ subsections | 8 clean sections |

## Template

See [SPEC-TEMPLATE.yaml](SPEC-TEMPLATE.yaml).
