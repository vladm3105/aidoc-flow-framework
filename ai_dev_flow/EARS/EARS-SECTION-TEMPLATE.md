---
doc_id: EARS-{NN}
section: {S}
title: "{Section Title}"
parent_doc: "EARS-{NN}.0_index.md"
prev_section: "EARS-{NN}.{S-1}_{prev_slug}.md"
next_section: "EARS-{NN}.{S+1}_{next_slug}.md"
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
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: false
---

# EARS-{NN}.{S}: {Section Title}

> **Navigation**: [Index](EARS-{NN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
>
> **Parent Document**: EARS-{NN}
> **Section**: {S} of {N}
> **Layer**: 3 - Engineering Requirements

---

## Overview

{Brief description of what this section covers}

---

## {Main Content Heading}

{Section content goes here}

### Ubiquitous Requirements

**EARS-{NN}-{ID}**: The {system} SHALL {requirement}.

### Event-Driven Requirements

**EARS-{NN}-{ID}**: WHEN {trigger} THE {system} SHALL {requirement}.

### State-Driven Requirements

**EARS-{NN}-{ID}**: WHILE {state} THE {system} SHALL {requirement}.

### Optional Feature Requirements

**EARS-{NN}-{ID}**: WHERE {feature} THE {system} SHALL {requirement}.

### Unwanted Behavior Requirements

**EARS-{NN}-{ID}**: IF {unwanted condition} THEN THE {system} SHALL {response} WITHIN {timeframe}.

---

## Requirements Table

| ID | Pattern | Statement | Priority | Source |
|----|---------|-----------|----------|--------|
| EARS-{NN}-{ID} | {pattern} | {statement} | MUST/SHOULD/MAY | @ref: PRD-{NN} |

---

## References

- **Parent Document**: @ref: EARS-{NN}.0
- **Related Sections**: @ref: EARS-{NN}.{related}
- **Upstream**: @ref: PRD-{NN} (Product Requirements)
- **Downstream**: @ref: BDD-{NN} (Behavior), @ref: ADR-{NN} (Architecture)

---

> **Navigation**: [Index](EARS-{NN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
