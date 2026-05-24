# End-to-End Testing Guide

**Project**: {PROJECT_NAME}
**Version**: 1.0
**Last Updated**: {DATE}

---

## Overview

E2E tests validate complete user workflows against the staging environment. They are the final gate before production deployment.

### E2E Testing Principles

1. **Test critical paths only** — E2E tests are expensive to maintain
2. **Run against staging** — Never against production
3. **Isolated test data** — Dedicated test tenant, reset between runs
4. **Deterministic** — No flaky tests in the suite
5. **Fast feedback** — Target <10 minutes for full suite

---

## Test Framework

### API Testing: pytest + httpx

```python
import httpx
import pytest

@pytest.fixture
def staging_client():
    """HTTP client configured for staging environment."""
    return httpx.AsyncClient(
        base_url=os.environ["STAGING_URL"],
        headers={"Authorization": f"Bearer {os.environ['TEST_TOKEN']}"},
        timeout=30.0,
    )

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_budget_status(staging_client):
    response = await staging_client.get("/api/v1/budgets/test-project")
    assert response.status_code == 200
    data = response.json()
    assert "budget_amount" in data
    assert "current_spend" in data
```

### UI Testing: Playwright (Future)

For frontend E2E tests when `components/frontend` is implemented:

```python
from playwright.sync_api import Page

def test_login_flow(page: Page):
    page.goto(f"{STAGING_URL}/login")
    page.fill("#email", "test@example.com")
    page.fill("#password", "test-password")
    page.click("button[type='submit']")
    page.wait_for_url("**/dashboard")
    assert page.title() == "Dashboard - AI Cost Monitor"
```

---

## Test Scenarios

### Critical User Journeys

| Journey | Priority | Frequency |
|:--------|:---------|:----------|
| View budget status | P1 | Every deploy |
| Receive budget alert | P1 | Every deploy |
| Trigger remediation | P1 | Every deploy |
| Query cost history | P2 | Daily |
| Configure budget threshold | P2 | Daily |
| Export cost report | P3 | Weekly |

### Scenario: Budget Alert Flow

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_budget_alert_flow(staging_client, test_project):
    """
    Given a project with 80% budget threshold
    When spend exceeds the threshold
    Then an alert should be generated
    And the alert should appear in the alerts API
    """
    # Setup: Ensure test project has budget configured
    setup_response = await staging_client.put(
        f"/api/v1/budgets/{test_project}",
        json={"budget_amount": 100.0, "threshold_percent": 80}
    )
    assert setup_response.status_code in (200, 201)

    # Trigger: Simulate spend exceeding threshold
    trigger_response = await staging_client.post(
        f"/api/v1/test/simulate-spend",
        json={"project_id": test_project, "amount": 85.0}
    )
    assert trigger_response.status_code == 200

    # Wait for async processing
    await asyncio.sleep(5)

    # Verify: Check alert was created
    alerts_response = await staging_client.get(
        f"/api/v1/alerts?project_id={test_project}"
    )
    assert alerts_response.status_code == 200
    alerts = alerts_response.json()
    assert len(alerts) > 0
    assert alerts[0]["type"] == "budget_threshold"
    assert alerts[0]["threshold_percent"] == 80
```

---

## Test Environment

### Staging Configuration

| Setting | Value |
|:--------|:------|
| Base URL | `https://staging.{PROJECT_PREFIX}.example.com` |
| Auth method | Service account token |
| Test tenant | `test-tenant-e2e` |
| Data isolation | Dedicated project ID |

### Environment Variables

```bash
# Required for E2E tests
STAGING_URL=https://staging.{PROJECT_PREFIX}.example.com
TEST_TOKEN=<service-account-token>
TEST_PROJECT_ID=test-project-e2e
TEST_TENANT_ID=test-tenant-e2e
```

### Test Data Management

```python
@pytest.fixture(scope="session", autouse=True)
async def setup_test_data(staging_client):
    """Setup test data before suite, cleanup after."""
    # Setup
    await staging_client.post("/api/v1/test/setup", json={
        "tenant_id": os.environ["TEST_TENANT_ID"],
        "projects": ["test-project-1", "test-project-2"],
    })

    yield

    # Cleanup
    await staging_client.post("/api/v1/test/cleanup", json={
        "tenant_id": os.environ["TEST_TENANT_ID"],
    })
```

---

## Running E2E Tests

### Local Execution

```bash
# Set environment variables
export STAGING_URL=https://staging.{PROJECT_PREFIX}.example.com
export TEST_TOKEN=$(gcloud auth print-identity-token)

# Run E2E tests
pytest tests/e2e/ -v -m e2e --timeout=60
```

### CI Execution

```yaml
jobs:
  e2e:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - run: |
          git clone ... .

      - name: Authenticate
        run: |
          # WIF authentication
          gcloud auth login --cred-file=${GOOGLE_APPLICATION_CREDENTIALS}
          export TEST_TOKEN=$(gcloud auth print-identity-token)

      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v -m e2e \
            --timeout=60 \
            --junitxml=e2e-results.xml
        env:
          STAGING_URL: ${{ secrets.STAGING_URL }}
```

---

## Flaky Test Policy

### Definition

A test is **flaky** if it:

- Passes and fails on the same code without changes
- Depends on timing, network conditions, or external state
- Has failed 3+ times in the last 7 days without code changes

### Handling Flaky Tests

```
Flaky detected → Quarantine → Investigate → Fix or Remove

      Track in issue
```

### Quarantine Process

1. Add `@pytest.mark.skip(reason="Flaky: tracking in #123")` temporarily
2. Create tracking issue with:
   - Failure frequency
   - Error messages
   - Suspected cause
3. Investigate within 7 days
4. Either fix the root cause or remove the test

### Retry Strategy

For tests with known transient failures:

```python
@pytest.mark.flaky(reruns=2, reruns_delay=5)
def test_external_api_integration():
    """This test may fail due to network issues."""
    ...
```

---

## Test Maintenance

### Monthly Review

- [ ] Review test execution times
- [ ] Identify tests >30s and optimize
- [ ] Remove obsolete tests for removed features
- [ ] Update test data for schema changes
- [ ] Check for flaky test backlog

### Test Coverage Audit

| Journey | Covered | Last Updated |
|:--------|:--------|:-------------|
| Budget status | Yes | {DATE} |
| Budget alerts | Yes | {DATE} |
| Remediation | Partial | {DATE} |
| Cost queries | No | - |
| User auth | No | - |

---

## Debugging Failed Tests

### Local Reproduction

```bash
# Run specific failing test with verbose output
pytest tests/e2e/test_budget_flow.py::test_budget_alert_flow -vvs

# Run with debug logging
pytest tests/e2e/ -v --log-cli-level=DEBUG
```

### CI Artifact Collection

```yaml
- name: Upload test artifacts on failure
  if: failure()
  run: |
    mkdir -p artifacts
    cp e2e-results.xml artifacts/
    cp -r tests/e2e/screenshots artifacts/ 2>/dev/null || true
    # Upload artifacts...
```

### Common Failure Causes

| Symptom | Likely Cause | Resolution |
|:--------|:-------------|:-----------|
| Timeout | Slow staging | Increase timeout, check staging health |
| Auth error | Token expired | Refresh authentication |
| 404 errors | API path changed | Update test endpoints |
| Data mismatch | Schema changed | Update test assertions |
| Flaky pass/fail | Race condition | Add explicit waits |

---

## References

- [01-testing-strategy.md](01-testing-strategy.md) — Testing pyramid
- [04-deployment-strategy.md](04-deployment-strategy.md) — Deployment gates
- [05-environment-spec.md](05-environment-spec.md) — Staging configuration
