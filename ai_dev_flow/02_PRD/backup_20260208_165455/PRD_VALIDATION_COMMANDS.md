---
title: "PRD Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - prd
custom_fields:
  document_type: reference-guide
  artifact_type: PRD
  priority: high
  version: "1.0"
  scope: prd-validation
---

# PRD Validation Commands

**Purpose:** Quick reference for PRD-specific validation commands.

**Framework CLI Reference:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for the universal command catalog.

**Strategy & Gates:** See [PRD_VALIDATION_STRATEGY.md](./PRD_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Current Validators

- Quality gates (directory):
  - `bash scripts/validate_prd_quality_score.sh <directory>`
- Main validator (check supported flags with `--help`):
  - `python3 scripts/validate_prd.py --help`

---

## Workflows (current state)

- **Single folder quality sweep:**
  - `bash scripts/validate_prd_quality_score.sh docs/02_PRD/<folder>`
- **Inspect validator options:**
  - `python3 scripts/validate_prd.py --help`

> Planned: add `validate_all.sh` orchestrator once the PRD validators are split per the framework pattern.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths in CI environments |

---

## More Information

- [PRD_VALIDATION_STRATEGY.md](./PRD_VALIDATION_STRATEGY.md)
- [PRD_AI_VALIDATION_DECISION_GUIDE.md](./PRD_AI_VALIDATION_DECISION_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [scripts/README.md](./scripts/README.md)