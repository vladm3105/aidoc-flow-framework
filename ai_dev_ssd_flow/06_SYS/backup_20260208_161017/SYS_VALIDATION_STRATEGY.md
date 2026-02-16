---
title: "SYS Validation Strategy (Quick Reference)"
tags:
  - validation
  - sys
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: SYS
  priority: high
  version: "1.0"
  scope: sys-validation
---

# SYS Validation Strategy (Quick Reference)

**Purpose:** Quick reference for SYS validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [SYS_VALIDATION_COMMANDS.md](./SYS_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [SYS_AI_VALIDATION_DECISION_GUIDE.md](./SYS_AI_VALIDATION_DECISION_GUIDE.md) for SYS-specific decision patterns.

---

## SYS Validation Architecture

- Current scripts live in [scripts](./scripts).
- Present validators:
  - [scripts/validate_sys_quality_score.sh](scripts/validate_sys_quality_score.sh) — quality gates (see [SYS_MVP_QUALITY_GATE_VALIDATION.md](./SYS_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_sys.py](scripts/validate_sys.py) — main validator; run with `--help` to view supported modes.
- Planned alignment with the framework pattern (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)):
  - Add `validate_all.sh` orchestrator for file/directory flows.
  - Split checks into template, readiness, IDs, and cross-link validators following the REQ reference implementation.

---

## SYS Quality Gates and Rules

- Gate definitions: [SYS_MVP_QUALITY_GATE_VALIDATION.md](./SYS_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [SYS_MVP_VALIDATION_RULES.md](./SYS_MVP_VALIDATION_RULES.md)
- Creation rules: [SYS_MVP_CREATION_RULES.md](./SYS_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Quick Usage (current tooling)

- Quality gates (directory):
  - `bash scripts/validate_sys_quality_score.sh <directory>`
- Main validator (check `--help` for modes):
  - `python3 scripts/validate_sys.py --help`

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**SYS-Specific Docs:**
- [SYS_VALIDATION_COMMANDS.md](./SYS_VALIDATION_COMMANDS.md)
- [SYS_AI_VALIDATION_DECISION_GUIDE.md](./SYS_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)