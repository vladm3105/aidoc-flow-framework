---
title: "BRD Validation Strategy (Quick Reference)"
tags:
  - validation
  - brd
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: BRD
  priority: high
  version: "1.0"
  scope: brd-validation
---

# BRD Validation Strategy (Quick Reference)

**Purpose:** Quick reference for BRD validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [BRD_VALIDATION_COMMANDS.md](./BRD_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [BRD_AI_VALIDATION_DECISION_GUIDE.md](./BRD_AI_VALIDATION_DECISION_GUIDE.md) for BRD-specific decision patterns.

---

## BRD Validation Architecture

- Current scripts live in [scripts](./scripts).
- Present validators:
  - [scripts/validate_brd_quality_score.sh](scripts/validate_brd_quality_score.sh) — quality gates (see [BRD_MVP_QUALITY_GATE_VALIDATION.md](./BRD_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_brd.py](scripts/validate_brd.py) — main validator; run with `--help` to view supported modes.
- Planned alignment with the framework pattern (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)):
  - Add `validate_all.sh` orchestrator for file/directory flows.
  - Split checks into template, readiness, IDs, and cross-link validators following the REQ reference implementation.

---

## BRD Quality Gates and Rules

- Gate definitions: [BRD_MVP_QUALITY_GATE_VALIDATION.md](./BRD_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [BRD_MVP_VALIDATION_RULES.md](./BRD_MVP_VALIDATION_RULES.md)
- Creation rules: [BRD_MVP_CREATION_RULES.md](./BRD_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Quick Usage (current tooling)

- Quality gates (directory):
  - `bash scripts/validate_brd_quality_score.sh <directory>`
- Main validator (check `--help` for modes):
  - `python3 scripts/validate_brd.py --help`

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**BRD-Specific Docs:**
- [BRD_VALIDATION_COMMANDS.md](./BRD_VALIDATION_COMMANDS.md)
- [BRD_AI_VALIDATION_DECISION_GUIDE.md](./BRD_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)