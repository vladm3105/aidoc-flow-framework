# EARS Validation Scripts

Tools for validating EARS documents. Current scripts:

- [validate_ears_quality_score.sh](./validate_ears_quality_score.sh) — quality gates (see [../EARS_MVP_QUALITY_GATE_VALIDATION.md](../EARS_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_ears_consistency.sh](./validate_ears_consistency.sh) — consistency checks.
- [validate_ears_duplicates.sh](./validate_ears_duplicates.sh) — duplicate detection.
- [validate_ears.py](./validate_ears.py) — main validator (run with `--help` for modes).

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../EARS_VALIDATION_STRATEGY.md](../EARS_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_ears_quality_score.sh docs/03_EARS/<folder>

# Consistency and duplicates
bash validate_ears_consistency.sh docs/03_EARS/<folder>
bash validate_ears_duplicates.sh docs/03_EARS/<folder>

# Inspect validator options
python3 validate_ears.py --help
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../EARS_VALIDATION_STRATEGY.md](../EARS_VALIDATION_STRATEGY.md)
- [../EARS_VALIDATION_COMMANDS.md](../EARS_VALIDATION_COMMANDS.md)
- [../EARS_AI_VALIDATION_DECISION_GUIDE.md](../EARS_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)