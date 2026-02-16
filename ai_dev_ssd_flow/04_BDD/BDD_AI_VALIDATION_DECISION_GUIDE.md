---
title: "AI Assistant Guide: BDD Validation Decision-Making"
tags:
  - ai-assistant-guide
  - validation-framework
  - decision-tree
  - best-practices
custom_fields:
  document_type: ai-guide
  artifact_type: BDD
  priority: high
  version: "0.1"
  scope: validation-and-quality
---

# AI Assistant Guide: BDD Validation Decision-Making

**BDD-Specific Guide:** BDD-focused patterns, validator nuances, and common fixes.

**Framework Guidance:**
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md) — framework-wide decision rules
- [../VALIDATION_DECISION_FRAMEWORK.md](../VALIDATION_DECISION_FRAMEWORK.md) — core universal rules

**Source of Gates:**
- [BDD_MVP_QUALITY_GATE_VALIDATION.md](./BDD_MVP_QUALITY_GATE_VALIDATION.md)
- [BDD_MVP_VALIDATION_RULES.md](./BDD_MVP_VALIDATION_RULES.md)

**Purpose:** Help AI assistants decide whether to fix the document, adjust validators, or accept warnings for BDD artifacts.

---

## How to Use This Guide

1. Start with the framework-wide guide above for universal rules.
2. Map errors to BDD gates using the gate references.
3. If a pattern is missing here, fall back to the framework rules and log the gap for follow-up.

---

## Current Coverage

This BDD guide is a starter scaffold. Populate with BDD-specific patterns as validators are aligned to the framework template (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)). Recommended sections to add next:

- Validation error analysis framework (BDD examples)
- Decision tree tailored to BDD gates
- Common BDD issues and resolutions
- Validator rules reference (per gate)
- Step-by-step resolution playbook

---

## Immediate Best Practices

- Confirm the document follows [BDD-MVP-TEMPLATE.feature](./BDD-MVP-TEMPLATE.feature) before changing validators.
- Prioritize fixes that improve readiness for downstream SPEC generation.
- Treat formatting-only warnings as validator candidates unless they block clarity or traceability.
- Record false positives with repro snippets to refine validators.

---

## References

- [BDD_VALIDATION_STRATEGY.md](./BDD_VALIDATION_STRATEGY.md)
- [BDD_VALIDATION_COMMANDS.md](./BDD_VALIDATION_COMMANDS.md)
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)