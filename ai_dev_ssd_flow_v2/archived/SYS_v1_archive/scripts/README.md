# SYS Validation Scripts

Tools for validating SYS documents. Current scripts:

- [sys_core_validator_hook.sh](./sys_core_validator_hook.sh) — canonical core-validator entrypoint for pre-commit/skills.
- [sys_quality_gate_hook.sh](./sys_quality_gate_hook.sh) — corpus quality-gate entrypoint for pre-commit/skills.
- [sys_req_ready_score_hook.sh](./sys_req_ready_score_hook.sh) — REQ-ready score gate wrapper (Template v2.1).
- [calculate_sys_req_ready_score.py](./calculate_sys_req_ready_score.py) — template-versioned SYS REQ-ready score formula script.
- [validate_sys_quality_score.sh](./validate_sys_quality_score.sh) — quality gates (see [../SYS_MVP_QUALITY_GATE_VALIDATION.md](../SYS_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_sys.py](./validate_sys.py) — main validator (run with `--help` for modes).

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../SYS_VALIDATION_STRATEGY.md](../SYS_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_sys_quality_score.sh docs/06_SYS/<folder>

# Hook wrapper entrypoints (skill-friendly)
bash sys_core_validator_hook.sh docs/06_SYS
bash sys_quality_gate_hook.sh docs/06_SYS
bash sys_req_ready_score_hook.sh docs/06_SYS

# Pre-commit hook IDs (manual stage)
pre-commit run sys-core-validator --all-files --hook-stage manual
pre-commit run sys-quality-gate --all-files --hook-stage manual
pre-commit run sys-req-ready-score --all-files --hook-stage manual

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