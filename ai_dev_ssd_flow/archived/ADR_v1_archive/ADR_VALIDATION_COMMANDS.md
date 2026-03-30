---
title: "ADR Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - adr
custom_fields:
  document_type: reference-guide
  artifact_type: ADR
  priority: high
  version: "1.0"
  scope: adr-validation
---

# ADR Validation Commands

**Purpose:** Quick reference for ADR-specific validation commands.

**Framework CLI Reference:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for the universal command catalog.

**Strategy & Gates:** See [ADR_VALIDATION_STRATEGY.md](./ADR_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Current Validators

- Quality gates (directory):
  - `bash scripts/validate_adr_quality_score.sh <directory>`
- Main validator (check supported flags with `--help`):
  - `python3 scripts/validate_adr.py --help`

---

## Workflows (current state)

- **Quality sweep:**
  - `bash scripts/validate_adr_quality_score.sh docs/05_ADR/<folder>`
- **Inspect validator options:**
  - `python3 scripts/validate_adr.py --help`

> Planned: add `validate_all.sh` orchestrator once the ADR validators are split per the framework pattern.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths in CI environments |

---

## More Information

- [ADR_VALIDATION_STRATEGY.md](./ADR_VALIDATION_STRATEGY.md)
- [ADR_AI_VALIDATION_DECISION_GUIDE.md](./ADR_AI_VALIDATION_DECISION_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [scripts/README.md](./scripts/README.md)