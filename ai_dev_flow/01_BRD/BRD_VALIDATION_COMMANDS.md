---
title: "BRD Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - brd
custom_fields:
  document_type: reference-guide
  artifact_type: BRD
  priority: high
  version: "1.0"
  scope: brd-validation
---

# BRD Validation Commands

**Purpose:** Quick reference for BRD-specific validation commands.

**Framework CLI Reference:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for the universal command catalog.

**Strategy & Gates:** See [BRD_VALIDATION_STRATEGY.md](./BRD_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Current Validators

- Quality gates (directory):
  - `bash scripts/validate_brd_quality_score.sh <directory>`
- Main validator (check supported flags with `--help`):
  - `python3 scripts/validate_brd.py --help`

---

## Workflows (current state)

- **Single folder quality sweep:**
  - `bash scripts/validate_brd_quality_score.sh docs/01_BRD/<folder>`
- **Inspect validator options:**
  - `python3 scripts/validate_brd.py --help`

> Planned: add `validate_all.sh` orchestrator once the BRD validators are split per the framework pattern.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths in CI environments |

---

## More Information

- [BRD_VALIDATION_STRATEGY.md](./BRD_VALIDATION_STRATEGY.md)
- [BRD_AI_VALIDATION_DECISION_GUIDE.md](./BRD_AI_VALIDATION_DECISION_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [scripts/README.md](./scripts/README.md)