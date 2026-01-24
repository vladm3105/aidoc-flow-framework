---
title: "AI Assistant Guide: TASKS Validation Decision-Making"
tags:
  - ai-assistant-guide
  - validation-framework
  - decision-tree
  - best-practices
custom_fields:
  document_type: ai-guide
  artifact_type: TASKS
  priority: high
  version: "0.1"
  scope: validation-and-quality
---

# AI Assistant Guide: TASKS Validation Decision-Making

**TASKS-Specific Guide:** TASKS-focused patterns, validator nuances, and common fixes.

**Framework Guidance:**
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md) — framework-wide decision rules
- [../VALIDATION_DECISION_FRAMEWORK.md](../VALIDATION_DECISION_FRAMEWORK.md) — core universal rules

**Source of Gates:**
- [TASKS_MVP_QUALITY_GATE_VALIDATION.md](./TASKS_MVP_QUALITY_GATE_VALIDATION.md)
- [TASKS_MVP_VALIDATION_RULES.md](./TASKS_MVP_VALIDATION_RULES.md)

**Purpose:** Help AI assistants decide whether to fix the document, adjust validators, or accept warnings for TASKS artifacts.

---

## How to Use This Guide

1. Start with the framework-wide guide above for universal rules.
2. Map errors to TASKS gates using the gate references.
3. If a pattern is missing here, fall back to the framework rules and log the gap for follow-up.

---

## Current Coverage

This TASKS guide is a starter scaffold. Populate with TASKS-specific patterns as validators are aligned to the framework template (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)). Recommended sections to add next:

- Validation error analysis framework (TASKS examples)
- Decision tree tailored to TASKS gates
- Common TASKS issues and resolutions
- Validator rules reference (per gate)
- Step-by-step resolution playbook

---

## Immediate Best Practices

- Confirm the document follows [TASKS-MVP-TEMPLATE.md](./TASKS-MVP-TEMPLATE.md) before changing validators.
- Prioritize fixes that improve readiness for downstream implementation planning.
- Treat formatting-only warnings as validator candidates unless they block clarity or traceability.
- Record false positives with repro snippets to refine validators.

---

## References

- [TASKS_VALIDATION_STRATEGY.md](./TASKS_VALIDATION_STRATEGY.md)
- [TASKS_VALIDATION_COMMANDS.md](./TASKS_VALIDATION_COMMANDS.md)
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)