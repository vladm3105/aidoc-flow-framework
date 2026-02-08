---
title: "CTR Validation Commands (Quick Reference)"
tags:
  - validation
  - cli
  - ctr
custom_fields:
  document_type: reference-guide
  artifact_type: CTR
  priority: high
  version: "1.0"
  scope: ctr-validation
---

# CTR Validation Commands

**Purpose:** Quick reference for CTR-specific validation commands.

**Framework CLI Reference:** See [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md) for the universal command catalog.

**Strategy & Gates:** See [CTR_VALIDATION_STRATEGY.md](./CTR_VALIDATION_STRATEGY.md) for architecture and gate details.

---

## Current Validators

- Quality gates (directory):
  - `bash scripts/validate_ctr_quality_score.sh <directory>`
- Main validator (check supported flags with `--help`):
  - `bash scripts/validate_ctr.sh --help`

---

## Workflows (current state)

- **Quality sweep:**
  - `bash scripts/validate_ctr_quality_score.sh docs/08_CTR/<folder>`
- **Inspect validator options:**
  - `bash scripts/validate_ctr.sh --help`

> Planned: add `validate_all.sh` orchestrator once the CTR validators are split per the framework pattern.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x scripts/*.sh` |
| File not found | Use absolute paths in CI environments |
| Shell not executable | Ensure scripts use LF line endings and `chmod +x` |

---

## More Information

- [CTR_VALIDATION_STRATEGY.md](./CTR_VALIDATION_STRATEGY.md)
- [CTR_AI_VALIDATION_DECISION_GUIDE.md](./CTR_AI_VALIDATION_DECISION_GUIDE.md)
- [../VALIDATION_COMMANDS.md](../VALIDATION_COMMANDS.md)
- [scripts/README.md](./scripts/README.md)