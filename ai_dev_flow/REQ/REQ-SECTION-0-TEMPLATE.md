---
doc_id: REQ-{NNN}
section: 0
title: "{Document Title} - Index"
total_sections: {N}
original_size_kb: {SIZE}
split_date: {YYYY-MM-DD}
tags:
  - section-index
  - req-section
  - layer-7-artifact
custom_fields:
  section_type: index
  artifact_type: REQ
  layer: 7
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  development_status: {active|reference|planned}
---

# REQ-{NNN}.0: {Document Title} - Index

## Document Overview

| Field | Value |
|-------|-------|
| **Document ID** | REQ-{NNN} |
| **Document Type** | Atomic Requirements |
| **Layer** | 7 - Atomic Requirements |
| **Title** | {Document Title} |
| **Total Sections** | {N} |
| **Original Size** | {SIZE} KB |
| **Split Date** | {YYYY-MM-DD} |
| **Status** | {status} |

---

## Purpose

{Brief description of atomic requirements scope and why split into sections}

---

## Section Map

| Section | File | Title | Description |
|---------|------|-------|-------------|
| 0 | [REQ-{NNN}.0_index.md](REQ-{NNN}.0_index.md) | Index | This file - document overview and navigation |
| 1 | [REQ-{NNN}.1_{slug1}.md](REQ-{NNN}.1_{slug1}.md) | {Title 1} | {Description 1} |
| 2 | [REQ-{NNN}.2_{slug2}.md](REQ-{NNN}.2_{slug2}.md) | {Title 2} | {Description 2} |
| 3 | [REQ-{NNN}.3_{slug3}.md](REQ-{NNN}.3_{slug3}.md) | {Title 3} | {Description 3} |

---

## Requirements Summary

| Category | MUST | SHOULD | MAY | Total |
|----------|------|--------|-----|-------|
| Functional | {N} | {N} | {N} | {N} |
| Performance | {N} | {N} | {N} | {N} |
| Security | {N} | {N} | {N} | {N} |
| **Total** | {N} | {N} | {N} | {N} |

---

## Dependencies

### Upstream References
- @ref: SYS-{NNN} - System Requirements this REQ derives from
- @ref: ADR-{NNN} - Architecture decisions guiding requirements

### Downstream References
- @ref: IMPL-{NNN} - Implementation approach for these requirements
- @ref: SPEC-{NNN} - Technical specifications implementing requirements

### Cross-Section Dependencies
- Section 2 depends on Section 1 (core requirements)
- Section 3 references all prior sections

---

## Reading Order

**Recommended reading sequence:**
1. **Section 1**: {Title 1} - Start here for functional requirements
2. **Section 2**: {Title 2} - Continue with non-functional requirements
3. **Section 3**: {Title 3} - Conclude with verification requirements

**Quick reference:**
- For functional requirements, see Section {N}
- For performance requirements, see Section {M}
- For security requirements, see Section {O}

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | {Author} | Initial split from monolithic document |

---

## Traceability

- **Original Document**: REQ-{NNN} (before split)
- **Element ID Range**: REQ.{NN}.{TT}.01 through REQ.{NN}.{TT}.{MAX}
- **Tag Format**: @ref: REQ-{NNN}.{S} (section reference)
- **Upstream Trace**: BRD -> PRD -> EARS -> BDD -> ADR -> SYS
- **Downstream Trace**: IMPL -> CTR -> SPEC -> TASKS -> IPLAN
