# BRD Validation Scripts

Tools for validating BRD documents. Current scripts:

- [validate_brd_quality_score.sh](./validate_brd_quality_score.sh) — quality gates (see [../BRD_MVP_QUALITY_GATE_VALIDATION.md](../BRD_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_brd.py](./validate_brd.py) — main validator (run with `--help` for modes).

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../BRD_VALIDATION_STRATEGY.md](../BRD_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_brd_quality_score.sh docs/01_BRD/<folder>

# Inspect validator options
python3 validate_brd.py --help
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../BRD_VALIDATION_STRATEGY.md](../BRD_VALIDATION_STRATEGY.md)
- [../BRD_VALIDATION_COMMANDS.md](../BRD_VALIDATION_COMMANDS.md)
- [../BRD_AI_VALIDATION_DECISION_GUIDE.md](../BRD_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)