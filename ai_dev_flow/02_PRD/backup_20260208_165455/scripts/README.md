# PRD Validation Scripts

Tools for validating PRD documents. Current scripts:

- [validate_prd_quality_score.sh](./validate_prd_quality_score.sh) — quality gates (see [../PRD_MVP_QUALITY_GATE_VALIDATION.md](../PRD_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_prd.py](./validate_prd.py) — main validator (run with `--help` for modes).

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../PRD_VALIDATION_STRATEGY.md](../PRD_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_prd_quality_score.sh docs/02_PRD/<folder>

# Inspect validator options
python3 validate_prd.py --help
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../PRD_VALIDATION_STRATEGY.md](../PRD_VALIDATION_STRATEGY.md)
- [../PRD_VALIDATION_COMMANDS.md](../PRD_VALIDATION_COMMANDS.md)
- [../PRD_AI_VALIDATION_DECISION_GUIDE.md](../PRD_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)