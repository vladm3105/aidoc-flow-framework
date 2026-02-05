---
title: "TASKS Validation Strategy (Quick Reference)"
tags:
  - validation
  - tasks
  - quick-reference
custom_fields:
  document_type: quick-reference
  artifact_type: TASKS
  priority: high
  version: "1.0"
  scope: tasks-validation
---

# TASKS Validation Strategy (Quick Reference)

**Purpose:** Quick reference for TASKS validation architecture, gates, and patterns.

**Full Documentation:** See [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) for framework-wide architecture and patterns.

**CLI Reference:** See [TASKS_VALIDATION_COMMANDS.md](./TASKS_VALIDATION_COMMANDS.md) for command syntax.

**Decision Guide:** See [TASKS_AI_VALIDATION_DECISION_GUIDE.md](./TASKS_AI_VALIDATION_DECISION_GUIDE.md) for TASKS-specific decision patterns.

---

## TASKS Validation Architecture

- Current scripts live in [scripts](./scripts).
- Present validators:
  - [scripts/validate_tasks_quality_score.sh](scripts/validate_tasks_quality_score.sh) — quality gates (see [TASKS_MVP_QUALITY_GATE_VALIDATION.md](./TASKS_MVP_QUALITY_GATE_VALIDATION.md)).
  - [scripts/validate_tasks.sh](scripts/validate_tasks.sh) — current validator; run with `--help` to view supported modes.
- Planned alignment with the framework pattern (see [../VALIDATION_TEMPLATE_GUIDE.md](../VALIDATION_TEMPLATE_GUIDE.md)):
  - Add `validate_all.sh` orchestrator for file/directory flows.
  - Split checks into template, readiness, IDs, and cross-link validators following the REQ reference implementation.

---

## TASKS Quality Gates and Rules

- Gate definitions: [TASKS_MVP_QUALITY_GATE_VALIDATION.md](./TASKS_MVP_QUALITY_GATE_VALIDATION.md)
- Validation rules: [TASKS_MVP_VALIDATION_RULES.md](./TASKS_MVP_VALIDATION_RULES.md)
- Creation rules: [TASKS_MVP_CREATION_RULES.md](./TASKS_MVP_CREATION_RULES.md)
- Use the framework guidance in [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md) to organize gates and validators.

---

## Quick Usage (current tooling)

- Quality gates (directory):
  - `bash scripts/validate_tasks_quality_score.sh <directory>`
- Main validator (check `--help` for modes):
  - `bash scripts/validate_tasks.sh --help`

---

## More Information

**Framework-Level Docs:**
- [../VALIDATION_STRATEGY_GUIDE.md](../VALIDATION_STRATEGY_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [../AI_VALIDATION_DECISION_GUIDE.md](../AI_VALIDATION_DECISION_GUIDE.md)

**TASKS-Specific Docs:**
- [TASKS_VALIDATION_COMMANDS.md](./TASKS_VALIDATION_COMMANDS.md)
- [TASKS_AI_VALIDATION_DECISION_GUIDE.md](./TASKS_AI_VALIDATION_DECISION_GUIDE.md)
- [scripts/README.md](./scripts/README.md)