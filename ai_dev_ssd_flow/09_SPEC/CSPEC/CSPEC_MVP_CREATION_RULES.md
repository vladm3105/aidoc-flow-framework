---
title: "CSPEC MVP Creation Rules"
tags:
  - creation-rules
  - layer-9-artifact
  - cspec-subtype
custom_fields:
  document_type: rules
  artifact_type: CSPEC
  layer: 9
  subtype_code: 50
---

# CSPEC MVP Creation Rules

## Purpose

Guidelines for creating Code Specification (CSPEC) documents - technical specifications for source code implementation.

## When to Create CSPEC

Create a CSPEC when:
- REQ document has `deliverable_type: code`
- Requirement results in source code output
- Implementation requires technical specification
- API/data contracts (CTR) exist for the interfaces

## Prerequisites

Before creating CSPEC:

1. **REQ Document**: Atomic requirement with `deliverable_type: code`
2. **CTR Document**: API/data contract for external interfaces (REQUIRED)
3. **ADR Document**: Architecture decisions for technology choices
4. **BDD Scenarios**: Test scenarios for verification

## File Naming

```
CSPEC-NN_component_name.yaml
```

- `NN`: Sequential number (01, 02, 03...)
- `component_name`: Snake_case, descriptive name

## Required Sections

| Section | Required | Description |
|---------|----------|-------------|
| metadata | Yes | Document control with `deliverable_type: code` |
| traceability | Yes | Must include REQ and CTR references |
| architecture | Yes | Component structure and dependencies |
| interfaces | Yes | APIs, classes, methods |
| behavior | Yes | State machines, processing logic |
| performance | Yes | Latency, throughput targets |
| security | Yes | Auth, authorization, validation |
| observability | Yes | Metrics, logging, health checks |
| verification | Yes | BDD scenarios, test references |
| implementation | Yes | Language, framework, paths |

## Element ID Format

```
CSPEC.{DOC}.{TYPE}.{SEQ}
```

| Code | Type | Example |
|------|------|---------|
| 50 | interface | CSPEC.01.50.01 |
| 51 | method | CSPEC.01.51.01 |
| 52 | model | CSPEC.01.52.01 |
| 53 | error | CSPEC.01.53.01 |
| 54 | config | CSPEC.01.54.01 |

## CTR Requirement

CSPEC **requires** CTR (Contract) reference:
- External APIs must have corresponding CTR document
- Reference CTR in traceability section
- Use CTR for request/response schemas

## Threshold References

Use `@threshold:` tags for all quantitative values:

```yaml
performance:
  latency_targets:
    p95_milliseconds: "@threshold: PRD.NN.perf.api.p95_latency"
```

## Quality Gate

**TASKS-Ready Score Target**: >= 90%

| Criterion | Weight |
|-----------|--------|
| Interface Completeness | 25% |
| Error Handling | 20% |
| Test Coverage Plan | 20% |
| Traceability | 20% |
| Implementation Guidance | 15% |

## Validation Checklist

- [ ] `deliverable_type: code` in metadata
- [ ] REQ reference in traceability
- [ ] CTR reference in traceability (required)
- [ ] All interfaces have method signatures
- [ ] Performance targets use @threshold references
- [ ] BDD scenarios referenced in verification
- [ ] Implementation language and paths specified

---

**Rules Version**: 1.0
**Last Updated**: 2026-03-01

---

## DEPRECATED: Template+Schema migration (2026-03-24)

This file is deprecated and retained for backward compatibility only.

Active references for MCP and framework tooling must use:
- `*-MVP-TEMPLATE.*`
- `*_MVP_SCHEMA.yaml`

Do not add new dependencies on this file.
