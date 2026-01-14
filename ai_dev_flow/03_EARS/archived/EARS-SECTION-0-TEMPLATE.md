---
doc_id: EARS-{NN}
section: 0
title: "{Document Title} - Index"
total_sections: {N}
original_size_kb: {SIZE}
split_date: {YYYY-MM-DD}
tags:
  - section-index
  - ears-section
  - layer-3-artifact
custom_fields:
  section_type: index
  artifact_type: EARS
  layer: 3
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  development_status: {active|reference|planned}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: true
---

# EARS-{NN}.0: {Document Title} - Index

## Document Overview

| Field | Value |
|-------|-------|
| **Document ID** | EARS-{NN} |
| **Document Type** | EARS Engineering Requirements |
| **Layer** | 3 - Engineering Requirements |
| **Title** | {Document Title} |
| **Total Sections** | {N} |
| **Original Size** | {SIZE} KB |
| **Split Date** | {YYYY-MM-DD} |
| **Status** | {status} |

---

## Purpose

{Brief description of formal requirements scope and why split into sections}

---

## Section Map

| Section | File | Title | Description |
|---------|------|-------|-------------|
| 0 | [EARS-{NN}.0_index.md](EARS-{NN}.0_index.md) | Index | This file - document overview and navigation |
| 1 | [EARS-{NN}.1_{slug1}.md](EARS-{NN}.1_{slug1}.md) | {Title 1} | {Description 1} |
| 2 | [EARS-{NN}.2_{slug2}.md](EARS-{NN}.2_{slug2}.md) | {Title 2} | {Description 2} |
| 3 | [EARS-{NN}.3_{slug3}.md](EARS-{NN}.3_{slug3}.md) | {Title 3} | {Description 3} |

---

## Requirements Summary

| EARS Pattern | Count | Coverage |
|--------------|-------|----------|
| Ubiquitous | {N} | {%} |
| Event-Driven | {N} | {%} |
| State-Driven | {N} | {%} |
| Optional Feature | {N} | {%} |
| Unwanted Behavior | {N} | {%} |
| **Total** | {N} | 100% |

---

## Dependencies

### Upstream References
- @ref: PRD-{NN} - Product requirements these EARS formalize

### Downstream References
- @ref: BDD-{NN} - Behavior scenarios validating EARS
- @ref: ADR-{NN} - Architecture decisions based on EARS

### Cross-Section Dependencies
- Section 2 depends on Section 1 (core requirements)
- Section 3 references all prior sections

---

## Reading Order

**Recommended reading sequence:**
1. **Section 1**: {Title 1} - Start here for ubiquitous requirements
2. **Section 2**: {Title 2} - Continue with event-driven requirements
3. **Section 3**: {Title 3} - Conclude with state-driven requirements

**Quick reference:**
- For ubiquitous requirements, see Section {N}
- For event-driven requirements, see Section {M}
- For unwanted behaviors, see Section {O}

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | {Author} | Initial split from monolithic document |

---

## Traceability

- **Original Document**: EARS-{NN} (before split)
- **Element ID Range**: EARS.{NN}.{TT}.01 through EARS.{NN}.{TT}.{MAX}
- **Tag Format**: @ref: EARS-{NN}.{S} (section reference)
- **Upstream Trace**: BRD -> PRD
- **Downstream Trace**: BDD -> ADR -> SYS -> REQ -> IMPL -> CTR -> SPEC
