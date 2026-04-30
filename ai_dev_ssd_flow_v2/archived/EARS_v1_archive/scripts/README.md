# EARS Validation Scripts

Tools for validating EARS documents. Current scripts:

- [ears_core_validator_hook.sh](./ears_core_validator_hook.sh) — canonical core-validator entrypoint for pre-commit/skills.
- [ears_quality_gate_hook.sh](./ears_quality_gate_hook.sh) — corpus quality-gate entrypoint for pre-commit/skills.
- [ears_ready_score_hook.sh](./ears_ready_score_hook.sh) — readiness-score gate wrapper (Template v2.0).
- [calculate_ears_ready_score.py](./calculate_ears_ready_score.py) — template-versioned EARS BDD-ready score formula script.
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

# Hook wrapper entrypoints (skill-friendly)
bash ears_core_validator_hook.sh docs/03_EARS
bash ears_quality_gate_hook.sh docs/03_EARS
bash ears_ready_score_hook.sh docs/03_EARS

# Pre-commit hook IDs (manual stage)
pre-commit run ears-core-validator --all-files --hook-stage manual
pre-commit run ears-quality-gate --all-files --hook-stage manual
pre-commit run ears-ready-score --all-files --hook-stage manual

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