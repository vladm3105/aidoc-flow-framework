# Test Standards

**Project**: {PROJECT_NAME}
**Version**: 1.0
**Last Updated**: {DATE}

---

## Naming Conventions

### Test Files

```
test_{module_name}.py
```

Examples:
- `test_models.py` — Tests for `models.py`
- `test_firestore.py` — Tests for `firestore.py`
- `test_budget_remediation.py` — Tests for `budget_remediation.py`

### Test Functions

```
test_{function_name}_{scenario}_{expected_outcome}
```

Examples:
- `test_validate_budget_valid_input_returns_true`
- `test_validate_budget_negative_amount_raises_error`
- `test_get_costs_empty_project_returns_empty_list`

### Test Classes (optional grouping)

```
class Test{ClassName}:
    def test_{method}_{scenario}_{expected}(self):
```

Example:
```python
class TestBudgetConfig:
    def test_from_dict_valid_data_creates_instance(self):
        ...

    def test_from_dict_missing_field_raises_validation_error(self):
        ...
```

---

## Directory Structure

```
{component}/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Unit-specific fixtures
│   │   ├── test_models.py
│   │   ├── test_utils.py
│   │   └── test_validators.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Integration-specific fixtures
│   │   ├── test_firestore_client.py
│   │   └── test_pubsub_handler.py
│   └── e2e/
│       ├── __init__.py
│       ├── conftest.py          # E2E-specific fixtures
│       └── test_budget_workflow.py
```

---

## Fixture Guidelines

### Fixture Scope

| Scope | Use Case | Example |
|:------|:---------|:--------|
| `function` (default) | Isolated test data | `budget_config` |
| `class` | Shared across class methods | `database_connection` |
| `module` | Expensive setup, read-only | `loaded_test_data` |
| `session` | One-time setup | `docker_container` |

### Fixture Location

| Fixture Type | Location |
|:-------------|:---------|
| Used across all tests | `tests/conftest.py` |
| Used in unit tests only | `tests/unit/conftest.py` |
| Used in one test file | Same file as test |

### Fixture Naming

```python
@pytest.fixture
def budget_config():
    """A valid BudgetConfig instance for testing."""
    return BudgetConfig(
        project_id="test-project",
        budget_amount=1000.0,
        threshold_percent=80,
    )

@pytest.fixture
def invalid_budget_config():
    """A BudgetConfig with invalid values for error testing."""
    return {"project_id": "", "budget_amount": -100}
```

---

## Assertion Guidelines

### Use pytest Assertions

```python
# Good - pytest assertion with automatic diff
assert result == expected

# Good - assertion with message
assert len(items) == 3, f"Expected 3 items, got {len(items)}"

# Bad - unittest style
self.assertEqual(result, expected)
```

### Common Assertion Patterns

```python
# Equality
assert actual == expected

# Truthiness
assert result is True
assert result is not None

# Collections
assert item in collection
assert len(collection) == expected_length
assert set(actual) == set(expected)  # Order-independent

# Exceptions
with pytest.raises(ValueError, match="invalid budget"):
    validate_budget(-100)

# Approximate equality (floats)
assert actual == pytest.approx(expected, rel=1e-3)
```

---

## Test Independence

Each test must be fully isolated:

1. **No shared mutable state** — Each test creates its own data
2. **No test ordering dependency** — Tests can run in any order
3. **Clean up after yourself** — Use fixtures with teardown
4. **No hardcoded paths** — Use `tmp_path` fixture for temp files

### Example: Isolated Test

```python
@pytest.fixture
def sample_budget(tmp_path):
    """Create a fresh budget config for each test."""
    config = BudgetConfig(project_id="test", amount=1000)
    yield config
    # Cleanup happens automatically when fixture goes out of scope

def test_budget_save(sample_budget, tmp_path):
    # Uses fresh fixtures, isolated path
    file_path = tmp_path / "budget.json"
    sample_budget.save(file_path)
    assert file_path.exists()
```

---

## Async Testing

Use `pytest-asyncio` for async code:

```python
import pytest

@pytest.mark.asyncio
async def test_async_get_costs():
    client = CostClient()
    result = await client.get_costs("project-id")
    assert result is not None
```

### Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

---

## Parameterized Tests

Use `@pytest.mark.parametrize` for testing multiple inputs:

```python
@pytest.mark.parametrize("input_value,expected", [
    (100, True),
    (0, True),
    (-1, False),
    (None, False),
])
def test_validate_amount(input_value, expected):
    assert validate_amount(input_value) == expected
```

### Parameterize with IDs

```python
@pytest.mark.parametrize("threshold,expected", [
    pytest.param(50, "warning", id="50%-threshold-warning"),
    pytest.param(80, "critical", id="80%-threshold-critical"),
    pytest.param(100, "exceeded", id="100%-threshold-exceeded"),
])
def test_threshold_status(threshold, expected):
    assert get_status(threshold) == expected
```

---

## Mocking Best Practices

### Mock External Dependencies

```python
from unittest.mock import patch, MagicMock

def test_get_gcp_costs(mocker):
    # Mock the GCP client
    mock_client = mocker.patch("cost_guard.utils.gcp.BillingClient")
    mock_client.return_value.get_costs.return_value = [
        {"amount": 100, "service": "compute"}
    ]

    result = get_costs("project-id")

    assert len(result) == 1
    mock_client.return_value.get_costs.assert_called_once_with("project-id")
```

### Mock at the Right Level

```python
# Good - mock at boundary
mocker.patch("cost_guard.handlers.firestore_client.get")

# Bad - mock internal implementation
mocker.patch("cost_guard.handlers._parse_response")
```

---

## Test Documentation

### Docstrings for Complex Tests

```python
def test_budget_remediation_scales_down_on_breach():
    """
    Given a budget breach event for a Cloud Run service,
    When the remediation handler processes the event,
    Then the service should be scaled to zero instances.

    Regression test for issue #45.
    """
    ...
```

### Mark Known Issues

```python
@pytest.mark.xfail(reason="Issue #123: Firestore emulator race condition")
def test_concurrent_updates():
    ...
```

---

## Performance Guidelines

| Test Type | Max Duration | Action if Exceeded |
|:----------|:-------------|:-------------------|
| Unit | 100ms | Investigate, optimize |
| Integration | 10s | Add `@pytest.mark.slow` |
| E2E | 60s | Review scope, split if needed |

### Timeout Enforcement

```python
@pytest.mark.timeout(5)
def test_api_response_time():
    """API must respond within 5 seconds."""
    response = client.get("/health")
    assert response.status_code == 200
```

---

## References

- [01-testing-strategy.md](01-testing-strategy.md) — Testing pyramid and coverage targets
- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
