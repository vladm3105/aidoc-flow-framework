---
title: "AI Assistant Guide: ADR Validation Decision-Making"
tags:
  - ai-assistant-guide
  - validation-framework
  - decision-tree
  - best-practices
custom_fields:
  document_type: ai-guide
  artifact_type: ADR
  priority: high
  version: "0.1"
  scope: validation-and-quality
---

# AI Assistant Guide: ADR Validation Decision-Making

**ADR-Specific Guide:** ADR-focused patterns, validator nuances, and common fixes.

**Framework Guidance:**
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md) — framework-wide decision rules
- [../VALIDATION_DECISION_FRAMEWORK.md](../VALIDATION_DECISION_FRAMEWORK.md) — core universal rules

**Source of Gates:**
- [ADR_MVP_QUALITY_GATE_VALIDATION.md](./ADR_MVP_QUALITY_GATE_VALIDATION.md)
- [ADR_MVP_VALIDATION_RULES.md](./ADR_MVP_VALIDATION_RULES.md)

**Purpose:** Help AI assistants decide whether to fix the document, adjust validators, or accept warnings for ADR artifacts.

---

## How to Use This Guide

1. Start with the framework-wide guide above for universal rules.
2. Map errors to ADR gates using the gate references.
3. If a pattern is missing here, fall back to the framework rules and log the gap for follow-up.

---

## Current Coverage

This ADR guide is a starter scaffold. Populate with ADR-specific patterns as validators are aligned to the framework template (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)). Recommended sections to add next:

- Validation error analysis framework (ADR examples)
- Decision tree tailored to ADR gates
- Common ADR issues and resolutions
- Validator rules reference (per gate)
- Step-by-step resolution playbook

---

## Immediate Best Practices

- Confirm the document follows [ADR-MVP-TEMPLATE.md](./ADR-MVP-TEMPLATE.md) before changing validators.
- Prioritize fixes that improve clarity and traceability across decisions.
- Treat formatting-only warnings as validator candidates unless they block clarity or traceability.
- Record false positives with repro snippets to refine validators.

---

## References

- [ADR_VALIDATION_STRATEGY.md](./ADR_VALIDATION_STRATEGY.md)
- [ADR_VALIDATION_COMMANDS.md](./ADR_VALIDATION_COMMANDS.md)
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)