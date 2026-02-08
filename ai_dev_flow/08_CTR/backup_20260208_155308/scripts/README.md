# CTR Validation Scripts

Tools for validating CTR documents.

## Available Scripts

### Core Validators

- [validate_ctr_quality_score.sh](./validate_ctr_quality_score.sh) — quality gates (see [../CTR_MVP_QUALITY_GATE_VALIDATION.md](../CTR_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_ctr.sh](./validate_ctr.sh) — standard CTR validator (run with `--help` for usage).
- [validate_ctr_spec_readiness.py](./validate_ctr_spec_readiness.py) — **NEW**: SPEC-readiness scorer evaluates CTR completeness for SPEC generation (≥90% target); checks for Pydantic models, type annotations, concrete examples, error recovery strategies, versioning, testing strategy.
- [validate_ctr_ids.py](./validate_ctr_ids.py) — CTR ID and filename validation.

### Utility Scripts

- [validate_ctr_all.sh](./validate_ctr_all.sh) — orchestrator for running all validators on a directory.

## Quick Start

```bash
# Make scripts executable
chmod +x *.sh

# SPEC-Readiness validation (Python)
python validate_ctr_spec_readiness.py --directory <ctr-directory> --min-score 90
python validate_ctr_spec_readiness.py --ctr-file <path-to-ctr-file>

# Quality gates (Shell)
bash validate_ctr_quality_score.sh docs/08_CTR/<folder>

# Standard validation
bash validate_ctr.sh --help
```

## SPEC-Readiness Validator Details

The `validate_ctr_spec_readiness.py` script measures CTR readiness for SPEC generation based on 10 weighted criteria:

1. **API Specification** — Section 2-5 with endpoints/methods documented
2. **Data Models** — Pydantic BaseModel OR JSON Schema
3. **Error Handling** — Exception catalog with HTTP codes, retry, recovery
4. **Versioning** — Version policy and breaking changes documented
5. **Testing** — Contract test strategy defined
6. **Endpoints** — GET/POST/PUT/DELETE or equivalent methods listed
7. **OpenAPI/Schema** — OpenAPI/JSON Schema reference or inline
8. **Type Annotations** — 3+ functions with `param: Type -> ReturnType` patterns
9. **Error Recovery** — 2+ recovery keywords (retry, backoff, fallback, circuit breaker, timeout)
10. **Concrete Examples** — 10+ real domain instances (IDs, symbols, dates, amounts)

**Pass Threshold**: ≥90 points (9/10 checks passing).

**Output**: For each file, shows score, pass/fail status, and warnings for missing elements.

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