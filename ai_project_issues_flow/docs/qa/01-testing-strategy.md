# Testing Strategy

**Project**: AI Cloud Cost Monitoring
**Version**: 1.0
**Last Updated**: {DATE}

---

## Testing Pyramid

The project follows the standard testing pyramid with emphasis on fast, isolated unit tests at the base.

```
        /\
       /  \     E2E Tests (10%)
      /    \    - Critical user journeys
     /------\   - Run on staging only
    /        \
   /          \ Integration Tests (20%)
  /            \ - Service boundaries
 /--------------\ - External dependencies
/                \
/                  \ Unit Tests (70%)
/                    \ - Fast, isolated
/______________________\ - No external dependencies
```

### Distribution by Component

| Component | Unit | Integration | E2E |
|:----------|:-----|:------------|:----|
| `{SERVICE_NAME}` | 80% | 15% | 5% |
| `mcp-servers` | 70% | 25% | 5% |
| `agents` | 60% | 30% | 10% |
| `frontend` | 70% | 20% | 10% |

---

## Coverage Targets

| Test Type | Target | Enforcement | Rationale |
|:----------|:-------|:------------|:----------|
| Unit | 80% | CI gate (fail) | Core business logic must be tested |
| Integration | 60% | CI gate (warn) | Service boundaries need validation |
| E2E | Critical paths | Manual | High maintenance cost, focus on value |

### Coverage Exceptions

Lines excluded from coverage calculation:
- Type checking blocks (`if TYPE_CHECKING:`)
- Abstract method stubs (`raise NotImplementedError`)
- Debug/development code marked with `# pragma: no cover`

---

## Test Environments

| Environment | Purpose | Data Source | External Services |
|:------------|:--------|:------------|:------------------|
| Local | Developer testing | Fixtures, mocks | All mocked |
| CI | Automated validation | Fixtures, test containers | Mocked or emulated |
| Staging | Pre-prod validation | Anonymized prod data | Real services (non-prod) |

### Environment Parity

Staging mirrors production configuration except:
- Reduced instance counts (min: 1 vs 2)
- Reduced resource allocation (1 CPU vs 2)
- Separate GCP project with isolated billing
- Test data, not production data

---

## Test Data Strategy

### Unit Tests
- Use hardcoded fixtures in `conftest.py`
- Use `factory-boy` for complex object creation
- Use `faker` for realistic but fake data

### Integration Tests
- Use `testcontainers` for databases (Firestore emulator, PostgreSQL)
- Use `respx` for HTTP service mocking
- Seed data via setup fixtures, clean up via teardown

### E2E Tests
- Dedicated test tenant in staging environment
- Data reset before each test suite run
- No shared state between test runs

---

## Mocking Strategy

### When to Mock

| Scenario | Mock? | Rationale |
|:---------|:------|:----------|
| External HTTP APIs | Yes | Network unreliability, rate limits |
| GCP services in unit tests | Yes | Speed, isolation |
| Database in unit tests | Yes | Speed, isolation |
| Database in integration tests | No | Test real behavior |
| Time-dependent logic | Yes | Reproducibility |
| Random/UUID generation | Yes | Reproducibility |

### Mock Libraries

| Use Case | Library |
|:---------|:--------|
| Function/method mocking | `pytest-mock` (unittest.mock wrapper) |
| HTTP request mocking | `respx` (for httpx) or `responses` (for requests) |
| GCP service emulation | Firestore emulator, Pub/Sub emulator |
| Time manipulation | `freezegun` |

### Mock Best Practices

1. **Mock at boundaries, not internals** — Mock external services, not internal functions
2. **Verify mock calls** — Assert that mocks were called with expected arguments
3. **Use realistic responses** — Mock responses should match actual API schemas
4. **Document mock behavior** — Comment non-obvious mock configurations

---

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

- Test a single function or class in isolation
- No I/O operations (network, disk, database)
- Execute in <100ms per test
- No setup beyond object instantiation

### Integration Tests (`@pytest.mark.integration`)

- Test interaction between components
- May use test containers or emulators
- Execute in <10s per test
- Require setup/teardown for external resources

### E2E Tests (`@pytest.mark.e2e`)

- Test complete user workflows
- Run against staging environment
- Execute in <60s per test
- Require authenticated session, test data

### Slow Tests (`@pytest.mark.slow`)

- Any test taking >1s
- Run separately in CI (not blocking PR merge)
- Scheduled nightly or on-demand

---

## Test Execution Order

1. **Pre-commit** (local): Lint + unit tests for changed files
2. **PR Creation**: Full lint + all unit tests
3. **PR Update**: Incremental unit tests + affected integration tests
4. **Merge to main**: Full suite (unit + integration)
5. **Deploy to staging**: E2E tests
6. **Deploy to prod**: Smoke tests only

---

## Failure Handling

| Failure Type | Action |
|:-------------|:-------|
| Unit test failure | Block PR merge |
| Integration test failure | Block PR merge |
| E2E test failure | Block staging→prod promotion |
| Flaky test (3+ failures in 7 days) | Disable test, create ticket |
| Coverage below threshold | Block PR merge |

---

## References

- [02-test-standards.md](02-test-standards.md) — How to write tests
- [03-ci-pipeline-spec.md](03-ci-pipeline-spec.md) — CI workflow details
- [06-security-testing.md](06-security-testing.md) — Security test requirements
