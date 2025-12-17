---
doc_id: ADR-{NNN}
section: 0
title: "{Document Title} - Index"
total_sections: {N}
original_size_kb: {SIZE}
split_date: {YYYY-MM-DD}
tags:
  - section-index
  - adr-section
  - layer-5-artifact
custom_fields:
  section_type: index
  artifact_type: ADR
  layer: 5
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  development_status: {active|reference|planned}
---

# ADR-{NNN}.0: {Document Title} - Index

## Document Overview

| Field | Value |
|-------|-------|
| **Document ID** | ADR-{NNN} |
| **Document Type** | Architecture Decision Record |
| **Layer** | 5 - Architecture Decisions |
| **Title** | {Document Title} |
| **Total Sections** | {N} |
| **Original Size** | {SIZE} KB |
| **Split Date** | {YYYY-MM-DD} |
| **Status** | {Proposed|Accepted|Deprecated|Superseded} |

---

## Purpose

{Brief description of architecture decision scope and why split into sections}

---

## Section Map

| Section | File | Title | Description |
|---------|------|-------|-------------|
| 0 | [ADR-{NNN}.0_index.md](ADR-{NNN}.0_index.md) | Index | This file - document overview and navigation |
| 1 | [ADR-{NNN}.1_{slug1}.md](ADR-{NNN}.1_{slug1}.md) | {Title 1} | {Description 1} |
| 2 | [ADR-{NNN}.2_{slug2}.md](ADR-{NNN}.2_{slug2}.md) | {Title 2} | {Description 2} |
| 3 | [ADR-{NNN}.3_{slug3}.md](ADR-{NNN}.3_{slug3}.md) | {Title 3} | {Description 3} |

---

## Decision Summary

| Aspect | Description |
|--------|-------------|
| **Decision** | {Brief statement of the architectural decision} |
| **Context** | {Why this decision is needed} |
| **Consequences** | {Impact of the decision} |
| **Alternatives Considered** | {Number} options evaluated |

---

## Dependencies

### Upstream References
- @ref: BDD-{NNN} - Behavior scenarios informing architecture
- @ref: EARS-{NNN} - Formal requirements driving decisions

### Downstream References
- @ref: SYS-{NNN} - System requirements implementing this ADR
- @ref: REQ-{NNN} - Atomic requirements derived from decisions
- @ref: SPEC-{NNN} - Technical specifications guided by ADR

### Cross-Section Dependencies
- Section 2 depends on Section 1 (context)
- Section 3 references all prior sections

---

## Reading Order

**Recommended reading sequence:**
1. **Section 1**: {Title 1} - Start here for context and problem
2. **Section 2**: {Title 2} - Continue with decision and alternatives
3. **Section 3**: {Title 3} - Conclude with consequences and implementation

**Quick reference:**
- For decision context, see Section {N}
- For alternatives analysis, see Section {M}
- For implementation guidance, see Section {O}

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | {Author} | Initial split from monolithic document |

---

## Traceability

- **Original Document**: ADR-{NNN} (before split)
- **Element ID Range**: ADR.{NN}.{TT}.01 through ADR.{NN}.{TT}.{MAX}
- **Tag Format**: @ref: ADR-{NNN}.{S} (section reference)
- **Upstream Trace**: BRD -> PRD -> EARS -> BDD
- **Downstream Trace**: SYS -> REQ -> IMPL -> CTR -> SPEC -> TASKS -> IPLAN
