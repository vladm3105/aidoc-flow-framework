# SPEC Validation Scripts

Tools for validating SPEC documents. Current scripts:

- [validate_spec_quality_score.sh](./validate_spec_quality_score.sh) — quality gates (see [../SPEC_MVP_QUALITY_GATE_VALIDATION.md](../SPEC_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_spec.py](./validate_spec.py) — main validator (run with `--help` for modes).

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../SPEC_VALIDATION_STRATEGY.md](../SPEC_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_spec_quality_score.sh docs/09_SPEC/<folder>

# Inspect validator options
python3 validate_spec.py --help
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../SPEC_VALIDATION_STRATEGY.md](../SPEC_VALIDATION_STRATEGY.md)
- [../SPEC_VALIDATION_COMMANDS.md](../SPEC_VALIDATION_COMMANDS.md)
- [../SPEC_AI_VALIDATION_DECISION_GUIDE.md](../SPEC_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)