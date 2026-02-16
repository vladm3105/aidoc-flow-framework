---
title: "SYS Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - sys
custom_fields:
  document_type: reference-guide
  artifact_type: SYS
  priority: high
  version: "1.0"
  scope: sys-validation
---

# SYS Validation Commands

**Purpose:** Quick reference for SYS-specific validation commands.

**Framework CLI Reference:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for the universal command catalog.

**Strategy & Gates:** See [SYS_VALIDATION_STRATEGY.md](./SYS_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Current Validators

- Quality gates (directory):
  - `bash scripts/validate_sys_quality_score.sh <directory>`
- Main validator (check supported flags with `--help`):
  - `python3 scripts/validate_sys.py --help`

---

## Workflows (current state)

- **Quality sweep:**
  - `bash scripts/validate_sys_quality_score.sh docs/06_SYS/<folder>`
- **Inspect validator options:**
  - `python3 scripts/validate_sys.py --help`

> Planned: add `validate_all.sh` orchestrator once the SYS validators are split per the framework pattern.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths in CI environments |

---

## More Information

- [SYS_VALIDATION_STRATEGY.md](./SYS_VALIDATION_STRATEGY.md)
- [SYS_AI_VALIDATION_DECISION_GUIDE.md](./SYS_AI_VALIDATION_DECISION_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [scripts/README.md](./scripts/README.md)