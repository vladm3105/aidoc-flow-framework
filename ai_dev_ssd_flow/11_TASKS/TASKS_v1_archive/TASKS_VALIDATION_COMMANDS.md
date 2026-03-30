---
title: "TASKS Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - tasks
custom_fields:
  document_type: reference-guide
  artifact_type: TASKS
  priority: high
  version: "1.0"
  scope: tasks-validation
---

# TASKS Validation Commands

**Purpose:** Quick reference for TASKS-specific validation commands.

**Framework CLI Reference:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for the universal command catalog.

**Strategy & Gates:** See [TASKS_VALIDATION_STRATEGY.md](./TASKS_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Current Validators

- Quality gates (directory):
  - `bash scripts/validate_tasks_quality_score.sh <directory>`
- Main validator (check supported flags with `--help`):
  - `bash scripts/validate_tasks.sh --help`

---

## Workflows (current state)

- **Quality sweep:**
  - `bash scripts/validate_tasks_quality_score.sh docs/11_TASKS/<folder>`
- **Inspect validator options:**
  - `bash scripts/validate_tasks.sh --help`

> Planned: add `validate_all.sh` orchestrator once the TASKS validators are split per the framework pattern.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh` |
| File not found | Use absolute paths in CI environments |
| Shell not executable | Ensure scripts use LF line endings and `chmod +x` |

---

## More Information

- [TASKS_VALIDATION_STRATEGY.md](./TASKS_VALIDATION_STRATEGY.md)
- [TASKS_AI_VALIDATION_DECISION_GUIDE.md](./TASKS_AI_VALIDATION_DECISION_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [scripts/README.md](./scripts/README.md)