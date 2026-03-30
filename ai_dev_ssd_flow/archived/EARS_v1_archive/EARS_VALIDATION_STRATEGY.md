---
title: "EARS Validation Strategy (Quick Reference)"
tags:
  - validation
  - ears
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: EARS
  priority: high
  version: "1.0"
  scope: ears-validation
---

# EARS Validation Strategy (Quick Reference)

**Purpose:** Quick reference for EARS validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [EARS_VALIDATION_COMMANDS.md](./EARS_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [EARS_AI_VALIDATION_DECISION_GUIDE.md](./EARS_AI_VALIDATION_DECISION_GUIDE.md) for EARS-specific decision patterns.

---

## EARS Validation Architecture

- Current scripts live in [scripts](./scripts).
- Present validators:
  - [scripts/validate_ears_quality_score.sh](scripts/validate_ears_quality_score.sh) — quality gates (see [EARS_MVP_QUALITY_GATE_VALIDATION.md](./EARS_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_ears_consistency.sh](scripts/validate_ears_consistency.sh) — consistency checks.
  - [scripts/validate_ears_duplicates.sh](scripts/validate_ears_duplicates.sh) — duplicate detection.
  - [scripts/validate_ears.py](scripts/validate_ears.py) — main validator; run with `--help` to view supported modes.
- Planned alignment with the framework pattern (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)):
  - Add `validate_all.sh` orchestrator for file/directory flows.
  - Split checks into template, readiness, IDs, and cross-link validators following the REQ reference implementation.

---

## EARS Quality Gates and Rules

- Gate definitions: [EARS_MVP_QUALITY_GATE_VALIDATION.md](./EARS_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [EARS_MVP_VALIDATION_RULES.md](./EARS_MVP_VALIDATION_RULES.md)
- Creation rules: [EARS_MVP_CREATION_RULES.md](./EARS_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Quick Usage (current tooling)

- Quality gates (directory):
  - `bash scripts/validate_ears_quality_score.sh <directory>`
- Consistency check:
  - `bash scripts/validate_ears_consistency.sh <directory>`
- Duplicate check:
  - `bash scripts/validate_ears_duplicates.sh <directory>`
- Main validator (check `--help` for modes):
  - `python3 scripts/validate_ears.py --help`

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**EARS-Specific Docs:**
- [EARS_VALIDATION_COMMANDS.md](./EARS_VALIDATION_COMMANDS.md)
- [EARS_AI_VALIDATION_DECISION_GUIDE.md](./EARS_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)