---
title: "SPEC Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - spec
custom_fields:
  document_type: reference-guide
  artifact_type: SPEC
  priority: high
  version: "1.0"
  scope: spec-validation
---

# SPEC Validation Commands

**Purpose:** Quick reference for SPEC-specific validation commands.

**Framework CLI Reference:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for the universal command catalog.

**Strategy & Gates:** See [SPEC_VALIDATION_STRATEGY.md](./SPEC_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Current Validators

- Quality gates (directory):
  - `bash scripts/validate_spec_quality_score.sh <directory>`
- Main validator (check supported flags with `--help`):
  - `python3 scripts/validate_spec.py --help`

---

## Workflows (current state)

- **Quality sweep:**
  - `bash scripts/validate_spec_quality_score.sh docs/09_SPEC/<folder>`
- **Inspect validator options:**
  - `python3 scripts/validate_spec.py --help`

> Planned: add `validate_all.sh` orchestrator once the SPEC validators are split per the framework pattern.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths in CI environments |

---

## More Information

- [SPEC_VALIDATION_STRATEGY.md](./SPEC_VALIDATION_STRATEGY.md)
- [SPEC_AI_VALIDATION_DECISION_GUIDE.md](./SPEC_AI_VALIDATION_DECISION_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [scripts/README.md](./scripts/README.md)