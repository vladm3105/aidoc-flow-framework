---
title: "EARS Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - ears
custom_fields:
  document_type: reference-guide
  artifact_type: EARS
  priority: high
  version: "1.0"
  scope: ears-validation
---

# EARS Validation Commands

**Purpose:** Quick reference for EARS-specific validation commands.

**Framework CLI Reference:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for the universal command catalog.

**Strategy & Gates:** See [EARS_VALIDATION_STRATEGY.md](./EARS_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Current Validators

- Quality gates (directory):
  - `bash scripts/validate_ears_quality_score.sh <directory>`
- Consistency check:
  - `bash scripts/validate_ears_consistency.sh <directory>`
- Duplicate check:
  - `bash scripts/validate_ears_duplicates.sh <directory>`
- Main validator (check supported flags with `--help`):
  - `python3 scripts/validate_ears.py --help`

---

## Workflows (current state)

- **Quality sweep:**
  - `bash scripts/validate_ears_quality_score.sh docs/03_EARS/<folder>`
- **Consistency + duplicates:**
  - `bash scripts/validate_ears_consistency.sh docs/03_EARS/<folder>`
  - `bash scripts/validate_ears_duplicates.sh docs/03_EARS/<folder>`
- **Inspect validator options:**
  - `python3 scripts/validate_ears.py --help`

> Planned: add `validate_all.sh` orchestrator once the EARS validators are split per the framework pattern.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths in CI environments |

---

## More Information

- [EARS_VALIDATION_STRATEGY.md](./EARS_VALIDATION_STRATEGY.md)
- [EARS_AI_VALIDATION_DECISION_GUIDE.md](./EARS_AI_VALIDATION_DECISION_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [scripts/README.md](./scripts/README.md)