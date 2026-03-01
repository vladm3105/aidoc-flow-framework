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

- Canonical wrapper (core + advisory):
  - `bash scripts/validate_prd_wrapper.sh docs/02_PRD`
- Canonical wrapper (core only; automation mode):
  - `bash scripts/validate_prd_wrapper.sh docs/02_PRD --skip-advisory`
- Component validator options (secondary diagnostics):
  - `python3 scripts/validate_prd.py --help`

---

## Workflows (current state)

- **Local pre-commit parity (core blocking):**
  - `bash scripts/validate_prd_wrapper.sh docs/02_PRD --skip-advisory`
- **Manual full sweep (includes advisory tier):**
  - `bash scripts/validate_prd_wrapper.sh docs/02_PRD`
- **Inspect component validator options:**
  - `python3 scripts/validate_prd.py --help`

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