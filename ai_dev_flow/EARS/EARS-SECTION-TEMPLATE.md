---
doc_id: EARS-{NNN}
section: {S}
title: "{Section Title}"
parent_doc: "EARS-{NNN}.0_index.md"
prev_section: "EARS-{NNN}.{S-1}_{prev_slug}.md"
next_section: "EARS-{NNN}.{S+1}_{next_slug}.md"
tags:
  - section-file
  - ears-section
  - layer-3-artifact
custom_fields:
  total_sections: {N}
  section_type: content
  artifact_type: EARS
  layer: 3
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
---

# EARS-{NNN}.{S}: {Section Title}

> **Navigation**: [Index](EARS-{NNN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
>
> **Parent Document**: EARS-{NNN}
> **Section**: {S} of {N}
> **Layer**: 3 - Formal Requirements

---

## Overview

{Brief description of what this section covers}

---

## {Main Content Heading}

{Section content goes here}

### Ubiquitous Requirements

**EARS-{NNN}-{ID}**: The {system} SHALL {requirement}.

### Event-Driven Requirements

**EARS-{NNN}-{ID}**: WHEN {trigger} THE {system} SHALL {requirement}.

### State-Driven Requirements

**EARS-{NNN}-{ID}**: WHILE {state} THE {system} SHALL {requirement}.

### Optional Feature Requirements

**EARS-{NNN}-{ID}**: WHERE {feature} THE {system} SHALL {requirement}.

### Unwanted Behavior Requirements

**EARS-{NNN}-{ID}**: IF {unwanted condition} THEN THE {system} SHALL {response} WITHIN {timeframe}.

---

## Requirements Table

| ID | Pattern | Statement | Priority | Source |
|----|---------|-----------|----------|--------|
| EARS-{NNN}-{ID} | {pattern} | {statement} | MUST/SHOULD/MAY | @ref: PRD-{NNN} |

---

## References

- **Parent Document**: @ref: EARS-{NNN}.0
- **Related Sections**: @ref: EARS-{NNN}.{related}
- **Upstream**: @ref: PRD-{NNN} (Product Requirements)
- **Downstream**: @ref: BDD-{NNN} (Behavior), @ref: ADR-{NNN} (Architecture)

---

> **Navigation**: [Index](EARS-{NNN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
