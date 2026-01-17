---
doc_id: PRD-{NN}
section: 0
title: "{Document Title} - Index"
total_sections: {N}
original_size_kb: {SIZE}
split_date: {YYYY-MM-DD}
tags:
  - section-index
  - prd-section
  - layer-2-artifact
custom_fields:
  section_type: index
  artifact_type: PRD
  layer: 2
  folder_structure: nested
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  development_status: {active|reference|planned}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: true
---

# PRD-{NN}.0: {Document Title} - Index

## Document Overview

| Field | Value |
|-------|-------|
| **Document ID** | PRD-{NN} |
| **Document Type** | Product Requirements Document |
| **Layer** | 2 - Product Requirements |
| **Title** | {Document Title} |
| **Total Sections** | {N} |
| **Original Size** | {SIZE} KB |
| **Split Date** | {YYYY-MM-DD} |
| **Status** | {status} |

---

## Purpose

{Brief description of product requirements scope and why split into sections}

---

## Section Map

| Section | File | Title | Description |
|---------|------|-------|-------------|
| 0 | [PRD-{NN}.0_index.md](PRD-{NN}.0_index.md) | Index | This file - document overview and navigation |
| 1 | [PRD-{NN}.1_{slug1}.md](PRD-{NN}.1_{slug1}.md) | {Title 1} | {Description 1} |
| 2 | [PRD-{NN}.2_{slug2}.md](PRD-{NN}.2_{slug2}.md) | {Title 2} | {Description 2} |
| 3 | [PRD-{NN}.3_{slug3}.md](PRD-{NN}.3_{slug3}.md) | {Title 3} | {Description 3} |

---

## Dependencies

### Upstream References
- @ref: BRD-{NN} - Business Requirements this PRD implements

### Downstream References
- @ref: EARS-{NN} - Formal requirements derived from this PRD
- @ref: BDD-{NN} - Behavior scenarios based on PRD features

### Cross-Section Dependencies
- Section 2 depends on Section 1 (product vision)
- Section 3 references all prior sections

---

## Reading Order

**Recommended reading sequence:**
1. **Section 1**: {Title 1} - Start here for product vision
2. **Section 2**: {Title 2} - Continue with feature specifications
3. **Section 3**: {Title 3} - Conclude with release criteria

**Quick reference:**
- For user stories, see Section {N}
- For feature requirements, see Section {M}
- For acceptance criteria, see Section {O}

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | {Author} | Initial split from monolithic document |

---

## Traceability

- **Original Document**: PRD-{NN} (before split)
- **Element ID Range**: PRD.{NN}.{TT}.01 through PRD.{NN}.{TT}.{MAX}
- **Tag Format**: @ref: PRD-{NN}.{S} (section reference)
- **Upstream Trace**: BRD
- **Downstream Trace**: EARS -> BDD -> ADR -> SYS -> REQ -> IMPL -> CTR -> SPEC
