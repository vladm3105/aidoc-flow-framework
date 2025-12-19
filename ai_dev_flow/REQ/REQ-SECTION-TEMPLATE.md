---
doc_id: REQ-{NN}
section: {S}
title: "{Section Title}"
parent_doc: "REQ-{NN}.0_index.md"
prev_section: "REQ-{NN}.{S-1}_{prev_slug}.md"
next_section: "REQ-{NN}.{S+1}_{next_slug}.md"
tags:
  - section-file
  - req-section
  - layer-7-artifact
custom_fields:
  total_sections: {N}
  section_type: content
  artifact_type: REQ
  layer: 7
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: false
---

# REQ-{NN}.{S}: {Section Title}

> **Navigation**: [Index](REQ-{NN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
>
> **Parent Document**: REQ-{NN}
> **Section**: {S} of {N}
> **Layer**: 7 - Atomic Requirements

---

## Overview

{Brief description of what this section covers}

---

## Requirements

### REQ-{NN}-{ID}: {Requirement Title}

| Field | Value |
|-------|-------|
| **ID** | REQ-{NN}-{ID} |
| **Priority** | MUST / SHOULD / MAY |
| **Category** | Functional / Performance / Security |
| **Source** | @ref: SYS-{NN}-{ID} |
| **Rationale** | {Why this requirement exists} |

**Statement**: {EARS-format requirement statement}

**Acceptance Criteria**:
1. {Criterion 1}
2. {Criterion 2}
3. {Criterion 3}

**Verification Method**: {Test / Analysis / Inspection / Demonstration}

**Traceability**:
- @ref: SYS-{NN}-{ID} (upstream)
- @ref: SPEC-{NN}-{ID} (downstream)

---

## References

- **Parent Document**: @ref: REQ-{NN}.0
- **Related Sections**: @ref: REQ-{NN}.{related}
- **Upstream**: @ref: SYS-{NN} (System Requirements)
- **Downstream**: @ref: IMPL-{NN} (Implementation), @ref: SPEC-{NN} (Specifications)

---

> **Navigation**: [Index](REQ-{NN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
