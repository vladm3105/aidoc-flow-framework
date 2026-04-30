# PRD Validation Scripts

Tools for validating PRD documents. Current scripts:

- [prd_standardized_element_codes_hook.sh](./prd_standardized_element_codes_hook.sh) — strict PRD standardized element type code checks.
- [prd_legacy_pattern_hook.sh](./prd_legacy_pattern_hook.sh) — legacy PRD element ID pattern detection.
- [prd_core_wrapper_hook.sh](./prd_core_wrapper_hook.sh) — pre-commit/automation canonical core wrapper entrypoint.
- [prd_quality_gate_hook.sh](./prd_quality_gate_hook.sh) — manual/deprecated alias to core wrapper path.
- [validate_prd_wrapper.sh](./validate_prd_wrapper.sh) — single entrypoint with tiered checks (core blocking, advisory non-blocking).
- [validate_prd_quality_score.sh](./validate_prd_quality_score.sh) — quality gates (see [../PRD_MVP_QUALITY_GATE_VALIDATION.md](../PRD_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_prd.py](./validate_prd.py) — main validator (run with `--help` for modes).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Quality gates (directory)
bash validate_prd_quality_score.sh docs/02_PRD/<folder>

# Canonical wrapper (core + advisory)
bash validate_prd_wrapper.sh docs/02_PRD

# Automation core mode (pre-commit/CI parity)
bash prd_core_wrapper_hook.sh ai_dev_ssd_flow/02_PRD

# Direct strict ID checks (optional diagnostics)
bash prd_standardized_element_codes_hook.sh ai_dev_ssd_flow/02_PRD
bash prd_legacy_pattern_hook.sh ai_dev_ssd_flow/02_PRD

# Inspect validator options
python3 validate_prd.py --help
```

## Troubleshooting

| Issue | Fix |
| ----- | --- |
| Permission denied | `chmod +x *.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths when running from CI |
| False positives from audit/review reports | Companion files (`*.A_*.md`, `*.R_*.md`, `*.F_*.md`) are auto-excluded in v1.1+ |
| GATE-03 count mismatch errors | Script handles edge cases with `|| true` for grep pipelines |
| GATE-08 duplicate ID errors in same file | Only cross-file duplicates are flagged (v1.1+) |

## Related Docs

- [../PRD_VALIDATION_STRATEGY.md](../PRD_VALIDATION_STRATEGY.md)
- [../PRD_VALIDATION_COMMANDS.md](../PRD_VALIDATION_COMMANDS.md)
- [../PRD_AI_VALIDATION_DECISION_GUIDE.md](../PRD_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)
