# SPEC Validation Scripts

Tools for validating SPEC documents.

## Available Scripts

### Core Validators

- [validate_spec_quality_score.sh](./validate_spec_quality_score.sh) — quality gates (see [../SPEC_MVP_QUALITY_GATE_VALIDATION.md](../SPEC_MVP_QUALITY_GATE_VALIDATION.md)).
- [validate_spec.py](./validate_spec.py) — standard SPEC validator (run with `--help` for usage).
- [validate_spec_implementation_readiness.py](./validate_spec_implementation_readiness.py) — **NEW**: Implementation-readiness scorer evaluates SPEC completeness for coding/development (≥90% target); checks for architecture, interfaces, behavior, performance, security, observability, verification, implementation details, REQ mapping, and concrete examples.

### Utility Scripts


### Orchestrator

- validate_all_spec.sh — runs quality gates, schema/template validator, and implementation-readiness scorer in one command (file or directory).

## Quick Start

```bash
# Make scripts executable

# All-in-one orchestrator
bash validate_all_spec.sh --file docs/09_SPEC/SPEC-01_iam.yaml
bash validate_all_spec.sh --directory docs/09_SPEC --min-score 90
chmod +x *.sh

# Implementation-Readiness validation (Python)
python validate_spec_implementation_readiness.py --spec-file docs/09_SPEC/SPEC-01_iam.yaml
python validate_spec_implementation_readiness.py --directory docs/09_SPEC/ --min-score 90

# Quality gates (Shell)
bash validate_spec_quality_score.sh <spec-directory>

# Standard validation
python3 validate_spec.py --help
```

## Implementation-Readiness Validator Details

The `validate_spec_implementation_readiness.py` script measures SPEC readiness for implementation based on 10 weighted criteria:

1. **Architecture** — Component structure, dependencies, patterns
2. **Interfaces** — External APIs, internal APIs, class definitions
3. **Behavior** — State machines, algorithms, workflows
4. **Performance** — Latency targets, throughput, resource limits
5. **Security** — Authentication, authorization, encryption, rate limiting
6. **Observability** — Logging, metrics, tracing, alerts
7. **Verification** — Unit, integration, contract, and performance tests
8. **Implementation** — Configuration, deployment, scaling, dependencies
9. **REQ Mapping** — req_implementations section linking REQs to code/behavior
10. **Concrete Examples** — Pseudocode, algorithms, API examples, data models

**Pass Threshold**: ≥90 points (9/10 checks passing).

**Output**: For each file, shows score, pass/fail status, and warnings for missing elements.

### Usage Examples

```bash
# Check single file readiness
python validate_spec_implementation_readiness.py --spec-file docs/09_SPEC/SPEC-01_iam.yaml

# Check directory with detailed report
python validate_spec_implementation_readiness.py --directory docs/09_SPEC/ --min-score 90

# Check with custom threshold
python validate_spec_implementation_readiness.py --directory docs/09_SPEC/ --min-score 80
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Permission denied | `chmod +x *.sh` |
| Python not found | Use `python3` explicitly |
| File not found | Use absolute paths when running from CI |

## Related Docs

- [../SPEC_VALIDATION_STRATEGY.md](../SPEC_VALIDATION_STRATEGY.md)
- [../SPEC_VALIDATION_COMMANDS.md](../SPEC_VALIDATION_COMMANDS.md)
- [../SPEC_AI_VALIDATION_DECISION_GUIDE.md](../SPEC_AI_VALIDATION_DECISION_GUIDE.md)
- [../../VALIDATION_STRATEGY_GUIDE.md](../../VALIDATION_STRATEGY_GUIDE.md)
- [../../VALIDATION_COMMANDS.md](../../VALIDATION_COMMANDS.md)
- [../../AI_VALIDATION_DECISION_GUIDE.md](../../AI_VALIDATION_DECISION_GUIDE.md)