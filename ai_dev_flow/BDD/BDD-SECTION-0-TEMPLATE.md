---
doc_id: BDD-{NNN}
section: 0
title: "{Document Title} - Index"
total_sections: {N}
original_size_kb: {SIZE}
split_date: {YYYY-MM-DD}
tags:
  - section-index
  - bdd-section
  - layer-4-artifact
custom_fields:
  section_type: index
  artifact_type: BDD
  layer: 4
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  development_status: {active|reference|planned}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: true
---

# BDD-{NNN}.0: {Document Title} - Index

## Document Overview

| Field | Value |
|-------|-------|
| **Document ID** | BDD-{NNN} |
| **Document Type** | Behavior-Driven Development Scenarios |
| **Layer** | 4 - Behavior Specifications |
| **Title** | {Document Title} |
| **Total Sections** | {N} |
| **Original Size** | {SIZE} KB |
| **Split Date** | {YYYY-MM-DD} |
| **Status** | {status} |

---

## Purpose

{Brief description of BDD scenarios scope and why split into sections}

---

## Section Map

| Section | File | Title | Description |
|---------|------|-------|-------------|
| 0 | [BDD-{NNN}.0_index.md](BDD-{NNN}.0_index.md) | Index | This file - document overview and navigation |
| 1 | [BDD-{NNN}.1_{slug1}.md](BDD-{NNN}.1_{slug1}.md) | {Title 1} | {Description 1} |
| 2 | [BDD-{NNN}.2_{slug2}.md](BDD-{NNN}.2_{slug2}.md) | {Title 2} | {Description 2} |
| 3 | [BDD-{NNN}.3_{slug3}.md](BDD-{NNN}.3_{slug3}.md) | {Title 3} | {Description 3} |

---

## Scenario Summary

| Feature Area | Scenarios | Happy Path | Edge Cases | Error Cases |
|--------------|-----------|------------|------------|-------------|
| {Feature 1} | {N} | {N} | {N} | {N} |
| {Feature 2} | {N} | {N} | {N} | {N} |
| **Total** | {N} | {N} | {N} | {N} |

---

## Dependencies

### Upstream References
- @ref: EARS-{NNN} - Formal requirements these scenarios validate
- @ref: PRD-{NNN} - Product requirements driving scenarios

### Downstream References
- @ref: ADR-{NNN} - Architecture decisions informed by behaviors
- @ref: SYS-{NNN} - System requirements derived from scenarios

### Cross-Section Dependencies
- Section 2 depends on Section 1 (core scenarios)
- Section 3 references all prior sections

---

## Reading Order

**Recommended reading sequence:**
1. **Section 1**: {Title 1} - Start here for core user scenarios
2. **Section 2**: {Title 2} - Continue with edge case scenarios
3. **Section 3**: {Title 3} - Conclude with error handling scenarios

**Quick reference:**
- For happy path scenarios, see Section {N}
- For edge cases, see Section {M}
- For error scenarios, see Section {O}

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | {Author} | Initial split from monolithic document |

---

## Traceability

- **Original Document**: BDD-{NNN} (before split)
- **Element ID Range**: BDD.{NN}.{TT}.01 through BDD.{NN}.{TT}.{MAX}
- **Tag Format**: @ref: BDD-{NNN}.{S} (section reference)
- **Upstream Trace**: BRD -> PRD -> EARS
- **Downstream Trace**: ADR -> SYS -> REQ -> IMPL -> CTR -> SPEC
