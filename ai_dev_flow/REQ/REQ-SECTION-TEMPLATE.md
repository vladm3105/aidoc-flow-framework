---
doc_id: REQ-{NNN}
section: {S}
title: "{Section Title}"
parent_doc: "REQ-{NNN}.0_index.md"
prev_section: "REQ-{NNN}.{S-1}_{prev_slug}.md"
next_section: "REQ-{NNN}.{S+1}_{next_slug}.md"
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
---

# REQ-{NNN}.{S}: {Section Title}

> **Navigation**: [Index](REQ-{NNN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
>
> **Parent Document**: REQ-{NNN}
> **Section**: {S} of {N}
> **Layer**: 7 - Atomic Requirements

---

## Overview

{Brief description of what this section covers}

---

## Requirements

### REQ-{NNN}-{ID}: {Requirement Title}

| Field | Value |
|-------|-------|
| **ID** | REQ-{NNN}-{ID} |
| **Priority** | MUST / SHOULD / MAY |
| **Category** | Functional / Performance / Security |
| **Source** | @ref: SYS-{NNN}-{ID} |
| **Rationale** | {Why this requirement exists} |

**Statement**: {EARS-format requirement statement}

**Acceptance Criteria**:
1. {Criterion 1}
2. {Criterion 2}
3. {Criterion 3}

**Verification Method**: {Test / Analysis / Inspection / Demonstration}

**Traceability**:
- @ref: SYS-{NNN}-{ID} (upstream)
- @ref: SPEC-{NNN}-{ID} (downstream)

---

## References

- **Parent Document**: @ref: REQ-{NNN}.0
- **Related Sections**: @ref: REQ-{NNN}.{related}
- **Upstream**: @ref: SYS-{NNN} (System Requirements)
- **Downstream**: @ref: IMPL-{NNN} (Implementation), @ref: SPEC-{NNN} (Specifications)

---

> **Navigation**: [Index](REQ-{NNN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
