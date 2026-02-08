---
title: "AI Assistant Guide: BRD Validation Decision-Making"
tags:
  - ai-assistant-guide
  - validation-framework
  - decision-tree
  - best-practices
custom_fields:
  document_type: ai-guide
  artifact_type: BRD
  priority: high
  version: "0.1"
  scope: validation-and-quality
---

# AI Assistant Guide: BRD Validation Decision-Making

**BRD-Specific Guide:** BRD-focused patterns, validator nuances, and common fixes.

**Framework Guidance:**
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md) — framework-wide decision rules
- [../VALIDATION_DECISION_FRAMEWORK.md](../VALIDATION_DECISION_FRAMEWORK.md) — core universal rules

**Source of Gates:**
- [BRD_MVP_QUALITY_GATE_VALIDATION.md](./BRD_MVP_QUALITY_GATE_VALIDATION.md)
- [BRD_MVP_VALIDATION_RULES.md](./BRD_MVP_VALIDATION_RULES.md)

**Purpose:** Help AI assistants decide whether to fix the document, adjust validators, or accept warnings for BRD artifacts.

---

## How to Use This Guide

1. Start with the framework-wide guide above for universal rules.
2. Map errors to BRD gates using the gate references.
3. If a pattern is missing here, fall back to the framework rules and log the gap for follow-up.

---

## Current Coverage

This BRD guide is a starter scaffold. Populate with BRD-specific patterns as validators are aligned to the framework template (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)). Recommended sections to add next:

- Validation error analysis framework (BRD examples)
- Decision tree tailored to BRD gates
- Common BRD issues and resolutions
- Validator rules reference (per gate)
- Step-by-step resolution playbook

---

## Immediate Best Practices

- Confirm the document follows [BRD-MVP-TEMPLATE.md](./BRD-MVP-TEMPLATE.md) before changing validators.
- Prioritize fixes that improve readiness for downstream PRD/EARS/SPEC generation.
- Treat formatting-only warnings as validator candidates unless they block clarity or traceability.
- Record false positives with repro snippets to refine validators.

---

## References

- [BRD_VALIDATION_STRATEGY.md](./BRD_VALIDATION_STRATEGY.md)
- [BRD_VALIDATION_COMMANDS.md](./BRD_VALIDATION_COMMANDS.md)
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)