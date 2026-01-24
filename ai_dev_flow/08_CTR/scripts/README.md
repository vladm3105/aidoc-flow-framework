# CTR Validation Scripts

Tools for validating CTR documents. Current scripts:

- [validate_ctr_quality_score.sh](./validate_ctr_quality_score.sh) — quality gates (see [../CTR_MVP_QUALITY_GATE_VALIDATION.md](../CTR_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_ctr.sh](./validate_ctr.sh) — current validator (run with `--help` for modes).

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../CTR_VALIDATION_STRATEGY.md](../CTR_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_ctr_quality_score.sh docs/08_CTR/<folder>

# Inspect validator options
bash validate_ctr.sh --help
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Shell not executable | Ensure scripts use LF endings and `chmod +x` |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../CTR_VALIDATION_STRATEGY.md](../CTR_VALIDATION_STRATEGY.md)
- [../CTR_VALIDATION_COMMANDS.md](../CTR_VALIDATION_COMMANDS.md)
- [../CTR_AI_VALIDATION_DECISION_GUIDE.md](../CTR_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)