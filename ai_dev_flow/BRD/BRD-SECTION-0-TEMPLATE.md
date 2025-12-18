---
doc_id: BRD-{NNN}
section: 0
title: "{Document Title} - Index"
total_sections: {N}
original_size_kb: {SIZE}
split_date: {YYYY-MM-DD}
tags:
  - section-index
  - brd-section
  - layer-1-artifact
custom_fields:
  section_type: index
  artifact_type: BRD
  layer: 1
  folder_structure: nested
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  development_status: {active|reference|planned}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: true
---

# BRD-{NNN}.0: {Document Title} - Index

## Document Overview

| Field | Value |
|-------|-------|
| **Document ID** | BRD-{NNN} |
| **Document Type** | Business Requirements Document |
| **Layer** | 1 - Business Requirements |
| **Title** | {Document Title} |
| **Total Sections** | {N} |
| **Original Size** | {SIZE} KB |
| **Split Date** | {YYYY-MM-DD} |
| **Status** | {status} |

---

## Purpose

{Brief description of business requirements scope and why split into sections}

---

## Section Map

| Section | File | Title | Description |
|---------|------|-------|-------------|
| 0 | [BRD-{NNN}.0_index.md](BRD-{NNN}.0_index.md) | Index | This file - document overview and navigation |
| 1 | [BRD-{NNN}.1_{slug1}.md](BRD-{NNN}.1_{slug1}.md) | {Title 1} | {Description 1} |
| 2 | [BRD-{NNN}.2_{slug2}.md](BRD-{NNN}.2_{slug2}.md) | {Title 2} | {Description 2} |
| 3 | [BRD-{NNN}.3_{slug3}.md](BRD-{NNN}.3_{slug3}.md) | {Title 3} | {Description 3} |

---

## Dependencies

### Upstream References
- None (BRD is Layer 1 - origin layer)

### Downstream References
- @ref: PRD-{NNN} - Product Requirements derived from this BRD
- @ref: EARS-{NNN} - Formal requirements derived from PRD

### Cross-Section Dependencies
- Section 2 depends on Section 1 (business context)
- Section 3 references all prior sections

---

## Reading Order

**Recommended reading sequence:**
1. **Section 1**: {Title 1} - Start here for business context
2. **Section 2**: {Title 2} - Continue with stakeholder requirements
3. **Section 3**: {Title 3} - Conclude with success criteria

**Quick reference:**
- For business objectives, see Section {N}
- For stakeholder analysis, see Section {M}
- For constraints and assumptions, see Section {O}

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | {Author} | Initial split from monolithic document |

---

## Traceability

- **Original Document**: BRD-{NNN} (before split)
- **Element ID Range**: BRD.{NN}.{TT}.01 through BRD.{NN}.{TT}.{MAX}
- **Tag Format**: @ref: BRD-{NNN}.{S} (section reference)
- **Downstream Trace**: PRD -> EARS -> BDD -> ADR -> SYS -> REQ -> IMPL -> CTR -> SPEC
