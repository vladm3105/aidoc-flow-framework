---
title: "EARS-MVP-TEMPLATE: EARS Requirements (MVP)"
tags:
  - ears-template
  - mvp-template
  - layer-3-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  instance_document_type: ears-document
  deliverable_type: code  # Options: code, document, ux, risk, process - inherited from PRD
  artifact_type: EARS
  layer: 3
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.1"
  last_updated: "2026-02-26"
  total_sections: 6
---

> **Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `EARS-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `EARS_MVP_SCHEMA.yaml`
> - **Complete Explanation**: See [DUAL_MVP_TEMPLATES_ARCHITECTURE.md](../DUAL_MVP_TEMPLATES_ARCHITECTURE.md) for full comparison of formats, authority hierarchy, and when to use each.
> ---

<!--
AI_CONTEXT_START
Role: AI Logic Engineer
Objective: Create a streamlined MVP Engineering Requirements Document (EARS) with 6 sections.
Constraints:
- Use EARS syntax patterns: WHEN-THE-SHALL-WITHIN, WHILE-THE-SHALL-WITHIN, IF-THE-SHALL-WITHIN, THE-SHALL.
- Maintain 6-section structure (Purpose, Workflow, Requirements, Quality, Traceability, References).
- Include cumulative traceability tags (@brd, @prd) per Layer 3 requirements.
- Maintain single-file structure unless >20k tokens triggers nested folder rule.
AI_CONTEXT_END
-->

> **MVP Template** — Single-file, streamlined EARS for logic mapping.
> MVP Note: Single flat file; split only if too large for AI assistants; otherwise ignore `DOCUMENT_SPLITTING_RULES.md`.
> Use this template to translate PRD features into Atomic Logic for code generation.

> **Validation Note**: This is the standard EARS template (6 sections). Some legacy validators may report warnings - this is expected behavior.

> References: Schema `EARS_MVP_SCHEMA.yaml` | Rules `EARS-MVP-TEMPLATE.md`, `EARS_MVP_SCHEMA.yaml` | Matrix `EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md`

# EARS-NN: [Target Component/Feature]

## Document Control

| Item | Details |
|------|---------|
| **Version** | 0.1.0 |
| **Status** | Draft / Review / Approved |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Author Name] |
| **Priority** | Critical (P1) / High (P2) / Medium (P3) / Low (P4) |
| **Source Document** | @prd: PRD.NN.EE.SS |
| **BDD-Ready Score** | NN% (Target: >=90%) |

---

## 1. Purpose and Context

### 1.1 Document Purpose

[Purpose statement: Convert PRD features into formal EARS statements
using WHEN-THE-SHALL-WITHIN format for clarity and unambiguousness.
Provide precise timing and performance specifications for each requirement.]

### 1.2 Scope

[Scope description: Define the boundaries of these formal requirements.
Include which PRD features are mapped and which are out of scope.
Specify the system components and interfaces covered.]

### 1.3 Intended Audience

[Target audience: System architects, developers, QA engineers,
and business analysts who need precise requirements specifications.]

---

## 2. EARS in Development Workflow

### 2.1 Workflow Position

```
BRD -> PRD -> **EARS** -> BDD -> ADR -> SYS -> REQ -> SPEC -> TASKS
```

### 2.2 Role in Specification-Driven Development

EARS documents serve as the translation layer between product requirements (PRD)
and behavioral test specifications (BDD). Each EARS statement must be:

1. **Testable**: Can be translated directly to BDD Given-When-Then scenarios
2. **Measurable**: Contains quantifiable constraints with @threshold references
3. **Traceable**: Links to upstream PRD and downstream BDD artifacts
4. **Atomic**: Defines one testable concept per statement

---

## 3. Requirements

### 3.0 Element ID Mapping

| Section | ID Pattern | Element Type Code | Notes |
|---------|------------|-------------------|-------|
| 3.x Requirements | `EARS.NN.25.SS` | 25 | EARS statement IDs, sequential within document |
| 4.1 Performance QA | `EARS.NN.02.SS` | 02 | Performance quality attributes |
| 4.2 Security QA | `EARS.NN.03.SS` | 03 | Security quality attributes |
| 4.3 Reliability QA | `EARS.NN.04.SS` | 04 | Reliability quality attributes |

### 3.1 Event-Driven Requirements (WHEN-THE-SHALL-WITHIN)

**EARS.NN.25.01: [Requirement Name]**
```
WHEN [trigger condition],
THE [system component] SHALL [response action]
WITHIN [timing constraint] (@threshold: PRD.NN.category.key).
```
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS

### 3.2 State-Driven Requirements (WHILE-THE-SHALL-WITHIN)

**EARS.NN.25.02: [State Behavior]**
```
WHILE [state condition],
THE [system component] SHALL [continuous behavior]
WITHIN [operational context].
```
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS

### 3.3 Unwanted Behavior Requirements (IF-THE-SHALL-WITHIN)

**EARS.NN.25.03: [Error Scenario]**
```
IF [error condition],
THE [system component] SHALL [recovery action]
WITHIN [timing constraint].
```
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS

### 3.4 Ubiquitous Requirements (THE-SHALL)

**EARS.NN.25.04: [System-Wide Requirement]**
```
THE [system component] SHALL [universal behavior]
for [scope/context].
```
**Traceability**: @brd: BRD.NN.EE.SS | @prd: PRD.NN.EE.SS

---

## 4. Quality Attributes

### 4.1 Performance Requirements

| QA ID | Requirement Statement | Metric | Target | Priority | Measurement Method |
|-------|----------------------|--------|--------|----------|-------------------|
| EARS.NN.02.01 | THE [component] SHALL complete [operation] | Latency | p95 < NNms | High | Load test |
| EARS.NN.02.02 | THE [component] SHALL process [workload] | Throughput | NN/s | Medium | Performance test |

### 4.2 Security Requirements

| QA ID | Requirement Statement | Control | Compliance | Priority |
|-------|----------------------|---------|------------|----------|
| EARS.NN.03.01 | THE [component] SHALL authenticate using [method] | Authentication | [standard] | High |

### 4.3 Reliability Requirements

| QA ID | Requirement Statement | Metric | Target | Priority |
|-------|----------------------|--------|--------|----------|
| EARS.NN.04.01 | THE [component] SHALL maintain availability | Uptime | 99.9% | High |

---

## 5. Traceability

### 5.1 Upstream Sources

| Tag | Document | Section |
|-----|----------|---------|
| @brd | BRD.NN.EE.SS | [Section reference] |
| @prd | PRD.NN.EE.SS | [Section reference] |

### 5.2 Downstream Artifacts

| Artifact | Purpose | Status |
|----------|---------|--------|
| BDD | Behavioral test scenarios | Pending |
| ADR | Architecture decisions | Pending |
| SYS | System requirements | Pending |

### 5.3 Traceability Tags

**Required Tags** (Cumulative Tagging Hierarchy - Layer 3):
```markdown
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
```

### 5.4 Threshold References

| Threshold ID | Category | Value | Source |
|--------------|----------|-------|--------|
| @threshold: PRD.NN.timeout.category.key | Timing | NNms | PRD Section 20.1 |
| @threshold: PRD.NN.perf.category.key | Performance | NN/s | PRD Section 14 |

---

## 6. References

### 6.1 Internal Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| BRD-NN | `../01_BRD/BRD-NN_*.md` | Business requirements source |
| PRD-NN | `../02_PRD/PRD-NN_*.md` | Product requirements source |

### 6.2 External Standards

| Standard | Organization | Relevance |
|----------|--------------|-----------|
| EARS Syntax | Alistair Mavin et al. | Requirement specification format |

### 6.3 Framework References

| Reference | Type | Notes |
|-----------|------|-------|
| ID_NAMING_STANDARDS.md | Framework Guide | Element ID format |
| THRESHOLD_NAMING_RULES.md | Framework Guide | @threshold tag format |

---

**Document Version**: 0.1.0
**Template Version**: 1.1 (MVP - 6 sections)
**Last Updated**: 2026-02-26
**Maintained By**: [Requirements Engineer]

---

> **MVP Template Notes**:
> - This is the standard EARS template (6 sections)
> - Single file - no sectioning per user requirement
> - Maintains ai_dev_flow framework compliance
> - **Lifecycle**: MVP -> PROD -> NEW MVP (no separate "full EARS" template)

---

## Cross-Linking Tags (AI-Friendly)

Use machine-parseable tags to document relationships between EARS documents:
- `@depends: EARS-NN` — hard prerequisite EARS that must be satisfied first.
- `@discoverability: EARS-NN (short rationale); EARS-NN (short rationale)` — related EARS with brief reasons to aid AI search and ranking.

Prefer these tags over legacy "See also ..." strings.
