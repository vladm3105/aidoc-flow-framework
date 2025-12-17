---
doc_id: ADR-{NNN}
section: {S}
title: "{Section Title}"
parent_doc: "ADR-{NNN}.0_index.md"
prev_section: "ADR-{NNN}.{S-1}_{prev_slug}.md"
next_section: "ADR-{NNN}.{S+1}_{next_slug}.md"
tags:
  - section-file
  - adr-section
  - layer-5-artifact
custom_fields:
  total_sections: {N}
  section_type: content
  artifact_type: ADR
  layer: 5
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
---

# ADR-{NNN}.{S}: {Section Title}

> **Navigation**: [Index](ADR-{NNN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
>
> **Parent Document**: ADR-{NNN}
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

- **Parent Document**: @ref: ADR-{NNN}.0
- **Related Sections**: @ref: ADR-{NNN}.{related}
- **Upstream**: @ref: BDD-{NNN} (Behavior), @ref: EARS-{NNN} (Requirements)
- **Downstream**: @ref: SYS-{NNN} (System), @ref: SPEC-{NNN} (Specifications)

---

> **Navigation**: [Index](ADR-{NNN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
