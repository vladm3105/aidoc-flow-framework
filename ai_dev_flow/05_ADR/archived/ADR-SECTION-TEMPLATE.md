---
doc_id: ADR-{NN}
section: {S}
title: "{Section Title}"
parent_doc: "ADR-{NN}.0_index.md"
prev_section: "ADR-{NN}.{S-1}_{prev_slug}.md"
next_section: "ADR-{NN}.{S+1}_{next_slug}.md"
tags:
  - section-file
  - adr-section
  - layer-5-artifact
custom_fields:
  total_sections: {N}
  section_type: content
  artifact_type: ADR
  layer: 5
  folder_structure: nested
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: false
---

# ADR-{NN}.{S}: {Section Title}

> **Navigation**: [Index](ADR-{NN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
>
> **Parent Document**: ADR-{NN}
> **Section**: {S} of {N}
> **Layer**: 5 - Architecture Decisions

---

## Overview

{Brief description of what this section covers}

---

## {Main Content Heading}

{Section content goes here}

### Context

{Business and technical context driving this decision}

### Decision

{The architectural decision made}

### Alternatives Considered

| Alternative | Pros | Cons | Evaluation |
|-------------|------|------|------------|
| {Option 1} | {Pros} | {Cons} | {Rejected/Accepted} |
| {Option 2} | {Pros} | {Cons} | {Rejected/Accepted} |

### Consequences

**Positive:**
- {Positive consequence 1}
- {Positive consequence 2}

**Negative:**
- {Negative consequence 1}
- {Trade-off accepted}

**Neutral:**
- {Neutral impact}

---

## References

- **Parent Document**: @ref: ADR-{NN}.0
- **Related Sections**: @ref: ADR-{NN}.{related}
- **Upstream**: @ref: BDD-{NN} (Behavior), @ref: EARS-{NN} (Requirements)
- **Downstream**: @ref: SYS-{NN} (System), @ref: SPEC-{NN} (Specifications)

---

> **Navigation**: [Index](ADR-{NN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
