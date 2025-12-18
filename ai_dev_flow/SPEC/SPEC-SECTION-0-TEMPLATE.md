---
doc_id: SPEC-{NNN}
section: 0
title: "{Document Title} - Index"
total_sections: {N}
original_size_kb: {SIZE}
split_date: {YYYY-MM-DD}
tags:
  - section-index
  - spec-section
  - layer-10-artifact
custom_fields:
  section_type: index
  artifact_type: SPEC
  layer: 10
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  development_status: {active|reference|planned}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: true
---

# SPEC-{NNN}.0: {Document Title} - Index

## Document Overview

| Field | Value |
|-------|-------|
| **Document ID** | SPEC-{NNN} |
| **Document Type** | Technical Specification |
| **Layer** | 10 - Technical Specifications |
| **Title** | {Document Title} |
| **Total Sections** | {N} |
| **Original Size** | {SIZE} KB |
| **Split Date** | {YYYY-MM-DD} |
| **Status** | {status} |

---

## Purpose

{Brief description of technical specification scope and why split into sections}

---

## Section Map

| Section | File | Title | Description |
|---------|------|-------|-------------|
| 0 | [SPEC-{NNN}.0_index.md](SPEC-{NNN}.0_index.md) | Index | This file - document overview and navigation |
| 1 | [SPEC-{NNN}.1_{slug1}.md](SPEC-{NNN}.1_{slug1}.md) | {Title 1} | {Description 1} |
| 2 | [SPEC-{NNN}.2_{slug2}.md](SPEC-{NNN}.2_{slug2}.md) | {Title 2} | {Description 2} |
| 3 | [SPEC-{NNN}.3_{slug3}.md](SPEC-{NNN}.3_{slug3}.md) | {Title 3} | {Description 3} |

---

## Dependencies

### Upstream References
- @ref: CTR-{NNN} - Contracts this SPEC implements
- @ref: REQ-{NNN} - Requirements this SPEC fulfills
- @ref: ADR-{NNN} - Architecture decisions guiding this SPEC

### Downstream References
- @ref: TASKS-{NNN} - Task breakdown for implementation
- @ref: IPLAN-{NNN} - Implementation plans

### Cross-Section Dependencies
- Section 2 depends on Section 1 (data models)
- Section 3 references all prior sections

---

## Reading Order

**Recommended reading sequence:**
1. **Section 1**: {Title 1} - Start here for technical architecture
2. **Section 2**: {Title 2} - Continue with API specifications
3. **Section 3**: {Title 3} - Conclude with implementation details

**Quick reference:**
- For data models, see Section {N}
- For API specifications, see Section {M}
- For error handling, see Section {O}

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | {Author} | Initial split from monolithic document |

---

## Traceability

- **Original Document**: SPEC-{NNN} (before split)
- **Element ID Range**: SPEC.{NN}.{TT}.01 through SPEC.{NN}.{TT}.{MAX}
- **Tag Format**: @ref: SPEC-{NNN}.{S} (section reference)
- **Upstream Trace**: BRD -> PRD -> EARS -> BDD -> ADR -> SYS -> REQ -> IMPL -> CTR
- **Downstream Trace**: TASKS -> IPLAN -> Code
