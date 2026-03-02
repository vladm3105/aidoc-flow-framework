# ADR Validation Scripts

Tools for validating ADR documents. Current scripts:

- [adr_core_validator_hook.sh](./adr_core_validator_hook.sh) — canonical core-validator entrypoint for pre-commit/skills.
- [adr_quality_gate_hook.sh](./adr_quality_gate_hook.sh) — corpus quality-gate entrypoint for pre-commit/skills.
- [adr_sys_ready_score_hook.sh](./adr_sys_ready_score_hook.sh) — SYS-ready score gate wrapper (Template v1.1).
- [calculate_adr_sys_ready_score.py](./calculate_adr_sys_ready_score.py) — template-versioned ADR SYS-ready score formula script.
- [validate_adr_quality_score.sh](./validate_adr_quality_score.sh) — quality gates (see [../ADR_MVP_QUALITY_GATE_VALIDATION.md](../ADR_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_adr.py](./validate_adr.py) — main validator (run with `--help` for modes).

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../ADR_VALIDATION_STRATEGY.md](../ADR_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_adr_quality_score.sh docs/05_ADR/<folder>

# Hook wrapper entrypoints (skill-friendly)
bash adr_core_validator_hook.sh docs/05_ADR
bash adr_quality_gate_hook.sh docs/05_ADR
bash adr_sys_ready_score_hook.sh docs/05_ADR

# Pre-commit hook IDs (manual stage)
pre-commit run adr-core-validator --all-files --hook-stage manual
pre-commit run adr-quality-gate --all-files --hook-stage manual
pre-commit run adr-sys-ready-score --all-files --hook-stage manual

# Inspect validator options
python3 validate_adr.py --help
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../ADR_VALIDATION_STRATEGY.md](../ADR_VALIDATION_STRATEGY.md)
- [../ADR_VALIDATION_COMMANDS.md](../ADR_VALIDATION_COMMANDS.md)
- [../ADR_AI_VALIDATION_DECISION_GUIDE.md](../ADR_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)