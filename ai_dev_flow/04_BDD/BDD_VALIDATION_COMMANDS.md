---
title: "BDD Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - bdd
custom_fields:
  document_type: reference-guide
  artifact_type: BDD
  priority: high
  version: "1.0"
  scope: bdd-validation
---

# BDD Validation Commands

**Purpose:** Quick reference for BDD-specific validation commands.

**Framework CLI Reference:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for the universal command catalog.

**Strategy & Gates:** See [BDD_VALIDATION_STRATEGY.md](./BDD_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Current Validators

- Quality gates (directory):
  - `bash scripts/validate_bdd_quality_score.sh <directory>`
- Suite validation:
  - `python3 scripts/validate_bdd_suite.py --help`
- Main validator (check supported flags with `--help`):
  - `python3 scripts/validate_bdd.py --help`
- Section migration helper:
  - `python3 scripts/migrate_bdd_to_sections.py --help`

---

## Workflows (current state)

- **Quality sweep:**
  - `bash scripts/validate_bdd_quality_score.sh docs/04_BDD/<folder>`
- **Suite validation:**
  - `python3 scripts/validate_bdd_suite.py --help`
- **Inspect validator options:**
  - `python3 scripts/validate_bdd.py --help`
- **Migrate sections:**
  - `python3 scripts/migrate_bdd_to_sections.py --help`

> Planned: add `validate_all.sh` orchestrator once the BDD validators are split per the framework pattern.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths in CI environments |

---

## More Information

- [BDD_VALIDATION_STRATEGY.md](./BDD_VALIDATION_STRATEGY.md)
- [BDD_AI_VALIDATION_DECISION_GUIDE.md](./BDD_AI_VALIDATION_DECISION_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [scripts/README.md](./scripts/README.md)