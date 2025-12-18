---
doc_id: SYS-{NNN}
section: 0
title: "{Document Title} - Index"
total_sections: {N}
original_size_kb: {SIZE}
split_date: {YYYY-MM-DD}
tags:
  - section-index
  - sys-section
  - layer-6-artifact
custom_fields:
  section_type: index
  artifact_type: SYS
  layer: 6
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  development_status: {active|reference|planned}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: true
---

# SYS-{NNN}.0: {Document Title} - Index

## Document Overview

| Field | Value |
|-------|-------|
| **Document ID** | SYS-{NNN} |
| **Document Type** | System Requirements |
| **Layer** | 6 - System Requirements |
| **Title** | {Document Title} |
| **Total Sections** | {N} |
| **Original Size** | {SIZE} KB |
| **Split Date** | {YYYY-MM-DD} |
| **Status** | {status} |

---

## Purpose

{Brief description of system requirements scope and why split into sections}

---

## Section Map

| Section | File | Title | Description |
|---------|------|-------|-------------|
| 0 | [SYS-{NNN}.0_index.md](SYS-{NNN}.0_index.md) | Index | This file - document overview and navigation |
| 1 | [SYS-{NNN}.1_{slug1}.md](SYS-{NNN}.1_{slug1}.md) | {Title 1} | {Description 1} |
| 2 | [SYS-{NNN}.2_{slug2}.md](SYS-{NNN}.2_{slug2}.md) | {Title 2} | {Description 2} |
| 3 | [SYS-{NNN}.3_{slug3}.md](SYS-{NNN}.3_{slug3}.md) | {Title 3} | {Description 3} |

---

## System Requirements Summary

| Category | Count | Coverage |
|----------|-------|----------|
| Functional Requirements | {N} | {%} |
| Quality Attributes | {N} | {%} |
| Interface Requirements | {N} | {%} |
| Constraints | {N} | {%} |
| **Total** | {N} | 100% |

---

## Dependencies

### Upstream References
- @ref: ADR-{NNN} - Architecture decisions guiding system design
- @ref: BDD-{NNN} - Behavior scenarios informing requirements

### Downstream References
- @ref: REQ-{NNN} - Atomic requirements derived from this SYS
- @ref: SPEC-{NNN} - Technical specifications

### Cross-Section Dependencies
- Section 2 depends on Section 1 (functional requirements)
- Section 3 references all prior sections

---

## Reading Order

**Recommended reading sequence:**
1. **Section 1**: {Title 1} - Start here for functional requirements
2. **Section 2**: {Title 2} - Continue with quality attributes
3. **Section 3**: {Title 3} - Conclude with interface requirements

**Quick reference:**
- For functional requirements, see Section {N}
- For quality attributes, see Section {M}
- For interface requirements, see Section {O}

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | {Author} | Initial split from monolithic document |

---

## Traceability

- **Original Document**: SYS-{NNN} (before split)
- **Element ID Range**: SYS.{NN}.{TT}.01 through SYS.{NN}.{TT}.{MAX}
- **Tag Format**: @ref: SYS-{NNN}.{S} (section reference)
- **Upstream Trace**: BRD -> PRD -> EARS -> BDD -> ADR
- **Downstream Trace**: REQ -> IMPL -> CTR -> SPEC -> TASKS -> IPLAN
