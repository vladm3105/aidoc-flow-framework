# SYS Validation Scripts

Tools for validating SYS documents. Current scripts:

- [validate_sys_quality_score.sh](./validate_sys_quality_score.sh) — quality gates (see [../SYS_MVP_QUALITY_GATE_VALIDATION.md](../SYS_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_sys.py](./validate_sys.py) — main validator (run with `--help` for modes).

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../SYS_VALIDATION_STRATEGY.md](../SYS_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_sys_quality_score.sh docs/06_SYS/<folder>

# Inspect validator options
python3 validate_sys.py --help
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../SYS_VALIDATION_STRATEGY.md](../SYS_VALIDATION_STRATEGY.md)
- [../SYS_VALIDATION_COMMANDS.md](../SYS_VALIDATION_COMMANDS.md)
- [../SYS_AI_VALIDATION_DECISION_GUIDE.md](../SYS_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)