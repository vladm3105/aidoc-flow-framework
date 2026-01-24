---
title: "BDD Validation Strategy (Quick Reference)"
tags:
  - validation
  - bdd
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: BDD
  priority: high
  version: "1.0"
  scope: bdd-validation
---

# BDD Validation Strategy (Quick Reference)

**Purpose:** Quick reference for BDD validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [BDD_VALIDATION_COMMANDS.md](./BDD_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [BDD_AI_VALIDATION_DECISION_GUIDE.md](./BDD_AI_VALIDATION_DECISION_GUIDE.md) for BDD-specific decision patterns.

---

## BDD Validation Architecture

- Current scripts live in [scripts](./scripts).
- Present validators:
  - [scripts/validate_bdd_quality_score.sh](scripts/validate_bdd_quality_score.sh) — quality gates (see [BDD_MVP_QUALITY_GATE_VALIDATION.md](./BDD_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_bdd.py](scripts/validate_bdd.py) — main validator; run with `--help` to view supported modes.
  - [scripts/validate_bdd_suite.py](scripts/validate_bdd_suite.py) — suite-level validation.
  - [scripts/migrate_bdd_to_sections.py](scripts/migrate_bdd_to_sections.py) — helper for section migration.
- Planned alignment with the framework pattern (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)):
  - Add `validate_all.sh` orchestrator for file/directory flows.
  - Split checks into template, readiness, IDs, and cross-link validators following the REQ reference implementation.

---

## BDD Quality Gates and Rules

- Gate definitions: [BDD_MVP_QUALITY_GATE_VALIDATION.md](./BDD_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [BDD_MVP_VALIDATION_RULES.md](./BDD_MVP_VALIDATION_RULES.md)
- Creation rules: [BDD_MVP_CREATION_RULES.md](./BDD_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Quick Usage (current tooling)

- Quality gates (directory):
  - `bash scripts/validate_bdd_quality_score.sh <directory>`
- Suite validation:
  - `bash scripts/validate_bdd_suite.py --help`
- Main validator (check `--help` for modes):
  - `python3 scripts/validate_bdd.py --help`
- Section migration helper:
  - `python3 scripts/migrate_bdd_to_sections.py --help`

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**BDD-Specific Docs:**
- [BDD_VALIDATION_COMMANDS.md](./BDD_VALIDATION_COMMANDS.md)
- [BDD_AI_VALIDATION_DECISION_GUIDE.md](./BDD_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)