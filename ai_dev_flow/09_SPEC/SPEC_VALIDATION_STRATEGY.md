---
title: "SPEC Validation Strategy (Quick Reference)"
tags:
  - validation
  - spec
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: SPEC
  priority: high
  version: "1.0"
  scope: spec-validation
---

# SPEC Validation Strategy (Quick Reference)

**Purpose:** Quick reference for SPEC validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [SPEC_VALIDATION_COMMANDS.md](./SPEC_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [SPEC_AI_VALIDATION_DECISION_GUIDE.md](./SPEC_AI_VALIDATION_DECISION_GUIDE.md) for SPEC-specific decision patterns.

---

## SPEC Validation Architecture

- Current scripts live in [scripts](./scripts).
- Present validators:
  - [scripts/validate_spec_quality_score.sh](scripts/validate_spec_quality_score.sh) — quality gates (see [SPEC_MVP_QUALITY_GATE_VALIDATION.md](./SPEC_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_spec.py](scripts/validate_spec.py) — main validator; run with `--help` to view supported modes.
- Planned alignment with the framework pattern (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)):
  - Add `validate_all.sh` orchestrator for file/directory flows.
  - Split checks into template, readiness, IDs, and cross-link validators following the REQ reference implementation.

---

## SPEC Quality Gates and Rules

- Gate definitions: [SPEC_MVP_QUALITY_GATE_VALIDATION.md](./SPEC_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [SPEC_MVP_VALIDATION_RULES.md](./SPEC_MVP_VALIDATION_RULES.md)
- Creation rules: [SPEC_MVP_CREATION_RULES.md](./SPEC_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Quick Usage (current tooling)

- Quality gates (directory):
  - `bash scripts/validate_spec_quality_score.sh <directory>`
- Main validator (check `--help` for modes):
  - `python3 scripts/validate_spec.py --help`

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**SPEC-Specific Docs:**
- [SPEC_VALIDATION_COMMANDS.md](./SPEC_VALIDATION_COMMANDS.md)
- [SPEC_AI_VALIDATION_DECISION_GUIDE.md](./SPEC_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)