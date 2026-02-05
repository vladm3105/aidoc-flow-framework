# TASKS Validation Scripts

Tools for validating TASKS documents. Current scripts:

- [validate_tasks_quality_score.sh](./validate_tasks_quality_score.sh) — quality gates (see [../TASKS_MVP_QUALITY_GATE_VALIDATION.md](../TASKS_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_tasks.sh](./validate_tasks.sh) — current validator (run with `--help` for modes).

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../TASKS_VALIDATION_STRATEGY.md](../TASKS_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_tasks_quality_score.sh docs/11_TASKS/<folder>

# Inspect validator options
bash validate_tasks.sh --help
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Shell not executable | Ensure scripts use LF endings and `chmod +x` |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../TASKS_VALIDATION_STRATEGY.md](../TASKS_VALIDATION_STRATEGY.md)
- [../TASKS_VALIDATION_COMMANDS.md](../TASKS_VALIDATION_COMMANDS.md)
- [../TASKS_AI_VALIDATION_DECISION_GUIDE.md](../TASKS_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)