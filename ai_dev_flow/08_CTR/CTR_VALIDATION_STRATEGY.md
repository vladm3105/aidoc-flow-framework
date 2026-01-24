---
title: "CTR Validation Strategy (Quick Reference)"
tags:
  - validation
  - ctr
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: CTR
  priority: high
  version: "1.0"
  scope: ctr-validation
---

# CTR Validation Strategy (Quick Reference)

**Purpose:** Quick reference for CTR validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [CTR_VALIDATION_COMMANDS.md](./CTR_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [CTR_AI_VALIDATION_DECISION_GUIDE.md](./CTR_AI_VALIDATION_DECISION_GUIDE.md) for CTR-specific decision patterns.

---

## CTR Validation Architecture

- Current scripts live in [scripts](./scripts).
- Present validators:
  - [scripts/validate_ctr_quality_score.sh](scripts/validate_ctr_quality_score.sh) — quality gates (see [CTR_MVP_QUALITY_GATE_VALIDATION.md](./CTR_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_ctr.sh](scripts/validate_ctr.sh) — current validator; run with `--help` to view supported modes.
- Planned alignment with the framework pattern (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)):
  - Add `validate_all.sh` orchestrator for file/directory flows.
  - Split checks into template, readiness, IDs, and cross-link validators following the REQ reference implementation.

---

## CTR Quality Gates and Rules

- Gate definitions: [CTR_MVP_QUALITY_GATE_VALIDATION.md](./CTR_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [CTR_MVP_VALIDATION_RULES.md](./CTR_MVP_VALIDATION_RULES.md)
- Creation rules: [CTR_MVP_CREATION_RULES.md](./CTR_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Quick Usage (current tooling)

- Quality gates (directory):
  - `bash scripts/validate_ctr_quality_score.sh <directory>`
- Main validator (check `--help` for modes):
  - `bash scripts/validate_ctr.sh --help`

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**CTR-Specific Docs:**
- [CTR_VALIDATION_COMMANDS.md](./CTR_VALIDATION_COMMANDS.md)
- [CTR_AI_VALIDATION_DECISION_GUIDE.md](./CTR_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)