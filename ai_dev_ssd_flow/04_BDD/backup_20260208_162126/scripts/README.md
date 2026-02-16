# BDD Validation Scripts

Tools for validating BDD artifacts. Current scripts:

- [validate_bdd_quality_score.sh](./validate_bdd_quality_score.sh) — quality gates (see [../BDD_MVP_QUALITY_GATE_VALIDATION.md](../BDD_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_bdd.py](./validate_bdd.py) — main validator (run with `--help` for modes).
- [validate_bdd_suite.py](./validate_bdd_suite.py) — suite-level validation helper.
- [migrate_bdd_to_sections.py](./migrate_bdd_to_sections.py) — section migration helper.

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../BDD_VALIDATION_STRATEGY.md](../BDD_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_bdd_quality_score.sh docs/04_BDD/<folder>

# Suite validation
python3 validate_bdd_suite.py --help

# Inspect validator options
python3 validate_bdd.py --help

# Migrate sections
python3 migrate_bdd_to_sections.py --help
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../BDD_VALIDATION_STRATEGY.md](../BDD_VALIDATION_STRATEGY.md)
- [../BDD_VALIDATION_COMMANDS.md](../BDD_VALIDATION_COMMANDS.md)
- [../BDD_AI_VALIDATION_DECISION_GUIDE.md](../BDD_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)