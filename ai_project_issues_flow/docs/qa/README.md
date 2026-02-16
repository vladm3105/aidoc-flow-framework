# Quality Assurance Documentation

This directory contains QA strategy, testing standards, and deployment specifications for the AI Cloud Cost Monitoring platform.

## Document Index

| Document | Purpose |
|:---------|:--------|
| [01-testing-strategy.md](01-testing-strategy.md) | Testing pyramid, coverage targets, test types |
| [02-test-standards.md](02-test-standards.md) | How to write tests, naming conventions, structure |
| [03-ci-pipeline-spec.md](03-ci-pipeline-spec.md) | CI workflow specification |
| [04-deployment-strategy.md](04-deployment-strategy.md) | Environment promotion, rollback procedures |
| [05-environment-spec.md](05-environment-spec.md) | Dev/staging/prod configuration |
| [06-security-testing.md](06-security-testing.md) | SAST, dependency scanning, container scanning |
| [07-e2e-testing-guide.md](07-e2e-testing-guide.md) | E2E test framework, scenarios, maintenance |

## Quick Reference

### Coverage Targets

| Test Type | Target | Enforcement |
|:----------|:-------|:------------|
| Unit | 80% | CI gate (fail build) |
| Integration | 60% | CI gate (warning) |
| E2E | Critical paths | Manual review |

### Environment Flow

```
Development → Staging → Production
(auto)        (auto)    (manual approval)
```

### Test Command Quick Reference

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/ -m unit

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests
pytest tests/integration/ -m integration

# Run specific test file
pytest tests/unit/test_models.py -v
```

## Related Documents

- [GOVERNANCE_RULES.md §8](../../governance/GOVERNANCE_RULES.md) — QA & Deployment rules
- [DEFINITION_OF_DONE.md](../../governance/DEFINITION_OF_DONE.md) — Testing checklist items
- [GITHUB_WORKFLOWS.md](../../governance/GITHUB_WORKFLOWS.md) — CI/CD workflow documentation
- [IPLAN-009](../../governance/plans/IPLAN-009_qa-deployment-pipelines.md) — Implementation plan
