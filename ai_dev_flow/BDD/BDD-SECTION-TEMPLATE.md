---
doc_id: BDD-{NN}
section: {S}
title: "{Section Title}"
parent_doc: "BDD-{NN}.0_index.md"
prev_section: "BDD-{NN}.{S-1}_{prev_slug}.md"
next_section: "BDD-{NN}.{S+1}_{next_slug}.md"
tags:
  - section-file
  - bdd-section
  - layer-4-artifact
custom_fields:
  total_sections: {N}
  section_type: content
  artifact_type: BDD
  layer: 4
  architecture_approach: {approach-name}
  priority: {primary|fallback|shared}
  split_type: section
  reading_order: sequential
  traceability_scope: inherited
  index_role: false
---

# BDD-{NN}.{S}: {Section Title}

> **Navigation**: [Index](BDD-{NN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
>
> **Parent Document**: BDD-{NN}
> **Section**: {S} of {N}
> **Layer**: 4 - Behavior Specifications

---

## Overview

{Brief description of what this section covers}

---

## Feature: {Feature Name}

{Feature description}

### Scenario: {Scenario Name}

**Given** {precondition}
**When** {action}
**Then** {expected result}

### Scenario Outline: {Scenario Outline Name}

**Given** {precondition with <parameter>}
**When** {action with <parameter>}
**Then** {expected result with <parameter>}

| parameter1 | parameter2 | expected |
|------------|------------|----------|
| {value1} | {value2} | {expected1} |
| {value3} | {value4} | {expected2} |

---

## Edge Cases

### Scenario: {Edge Case Name}

**Given** {edge case precondition}
**When** {action}
**Then** {expected behavior}

---

## Error Scenarios

### Scenario: {Error Case Name}

**Given** {error condition}
**When** {action that triggers error}
**Then** {expected error handling}

---

## References

- **Parent Document**: @ref: BDD-{NN}.0
- **Related Sections**: @ref: BDD-{NN}.{related}
- **Upstream**: @ref: EARS-{NN} (Requirements), @ref: PRD-{NN} (Product)
- **Downstream**: @ref: ADR-{NN} (Architecture)

---

> **Navigation**: [Index](BDD-{NN}.0_index.md) | [Previous]({prev_section}) | [Next]({next_section})
