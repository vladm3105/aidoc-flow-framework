# BRD Validation Scripts

Tools for validating BRD documents. Current scripts:

- [validate_brd_wrapper.sh](./validate_brd_wrapper.sh) — single entrypoint with tiered checks (core blocking, advisory non-blocking).
- [validate_brd_quality_score.sh](./validate_brd_quality_score.sh) — quality gates (see [../BRD_MVP_QUALITY_GATE_VALIDATION.md](../BRD_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_brd.py](./validate_brd.py) — main validator (run with `--help` for modes).

Current BRD validation behavior:
- `validate_brd_wrapper.sh` auto-detects section-based BRD roots and skips monolithic structural validation in that mode.
- `validate_brd_quality_score.sh` excludes companion report artifacts (`*.A_audit_report*`, `*.R_review_report*`, `*.F_fix_report*`, `*.V_validation_report*`) from quality-gate corpus checks.
- Diagram contract checks are skipped in quality gate mode when section-based BRD layout is detected.

Planned: add `validate_all.sh` orchestrator plus template/readiness/ID validators per the framework pattern described in [../BRD_VALIDATION_STRATEGY.md](../BRD_VALIDATION_STRATEGY.md) and [../../VALIDATION_TEMPLATE_GUIDE.md](../../VALIDATION_TEMPLATE_GUIDE.md).

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# Recommended: run tiered wrapper
bash validate_brd_wrapper.sh docs/01_BRD

# Quality gates (directory)
bash validate_brd_quality_score.sh docs/01_BRD/<folder>

# Inspect validator options
python3 validate_brd.py --help
```

## Troubleshooting

| Issue | Fix |
| ----- | --- |
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
