---
title: "ADR Validation Strategy (Quick Reference)"
tags:
  - validation
  - adr
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: ADR
  priority: high
  version: "1.0"
  scope: adr-validation
---

# ADR Validation Strategy (Quick Reference)

**Purpose:** Quick reference for ADR validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [ADR_VALIDATION_COMMANDS.md](./ADR_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [ADR_AI_VALIDATION_DECISION_GUIDE.md](./ADR_AI_VALIDATION_DECISION_GUIDE.md) for ADR-specific decision patterns.

---

## ADR Validation Architecture

- Current scripts live in [scripts](./scripts).
- Present validators:
  - [scripts/validate_adr_quality_score.sh](scripts/validate_adr_quality_score.sh) — quality gates (see [ADR_MVP_QUALITY_GATE_VALIDATION.md](./ADR_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_adr.py](scripts/validate_adr.py) — main validator; run with `--help` to view supported modes.
- Planned alignment with the framework pattern (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)):
  - Add `validate_all.sh` orchestrator for file/directory flows.
  - Split checks into template, readiness, IDs, and cross-link validators following the REQ reference implementation.

---

## ADR Quality Gates and Rules

- Gate definitions: [ADR_MVP_QUALITY_GATE_VALIDATION.md](./ADR_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [ADR_MVP_VALIDATION_RULES.md](./ADR_MVP_VALIDATION_RULES.md)
- Creation rules: [ADR_MVP_CREATION_RULES.md](./ADR_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Quick Usage (current tooling)

- Quality gates (directory):
  - `bash scripts/validate_adr_quality_score.sh <directory>`
- Main validator (check `--help` for modes):
  - `python3 scripts/validate_adr.py --help`

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**ADR-Specific Docs:**
- [ADR_VALIDATION_COMMANDS.md](./ADR_VALIDATION_COMMANDS.md)
- [ADR_AI_VALIDATION_DECISION_GUIDE.md](./ADR_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)