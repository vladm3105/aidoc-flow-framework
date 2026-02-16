---
title: "PRD Validation Strategy (Quick Reference)"
tags:
  - validation
  - prd
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: PRD
  priority: high
  version: "1.0"
  scope: prd-validation
---

# PRD Validation Strategy (Quick Reference)

**Purpose:** Quick reference for PRD validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [PRD_VALIDATION_COMMANDS.md](./PRD_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [PRD_AI_VALIDATION_DECISION_GUIDE.md](./PRD_AI_VALIDATION_DECISION_GUIDE.md) for PRD-specific decision patterns.

---

## PRD Validation Architecture

- Current scripts live in [scripts](./scripts).
- Present validators:
  - [scripts/validate_prd_quality_score.sh](scripts/validate_prd_quality_score.sh) — quality gates (see [PRD_MVP_QUALITY_GATE_VALIDATION.md](./PRD_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_prd.py](scripts/validate_prd.py) — main validator; run with `--help` to view supported modes.
- Planned alignment with the framework pattern (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)):
  - Add `validate_all.sh` orchestrator for file/directory flows.
  - Split checks into template, readiness, IDs, and cross-link validators following the REQ reference implementation.

---

## PRD Quality Gates and Rules

- Gate definitions: [PRD_MVP_QUALITY_GATE_VALIDATION.md](./PRD_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [PRD_MVP_VALIDATION_RULES.md](./PRD_MVP_VALIDATION_RULES.md)
- Creation rules: [PRD_MVP_CREATION_RULES.md](./PRD_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Quick Usage (current tooling)

- Quality gates (directory):
  - `bash scripts/validate_prd_quality_score.sh <directory>`
- Main validator (check `--help` for modes):
  - `python3 scripts/validate_prd.py --help`

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**PRD-Specific Docs:**
- [PRD_VALIDATION_COMMANDS.md](./PRD_VALIDATION_COMMANDS.md)
- [PRD_AI_VALIDATION_DECISION_GUIDE.md](./PRD_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)