# AI Dev Flow Test Suite

Testing infrastructure for the AI Dev Flow framework aligned with TSPEC (Layer 10).

## Directory Structure

```
tests/
├── conftest.py              # Shared fixtures for all test types
├── test_config.yaml         # Test environment configuration
├── README.md                # This file
│
├── unit/                    # UTEST - Unit Tests (Code 40)
│   ├── conftest.py          # Unit-specific fixtures
│   └── test_*.py            # Unit test files
│
├── integration/             # ITEST - Integration Tests (Code 41)
│   ├── conftest.py          # Integration-specific fixtures
│   └── test_*.py            # Integration test files
│
├── smoke/                   # STEST - Smoke Tests (Code 42)
│   ├── conftest.py          # Smoke-specific fixtures
│   └── test_*.py            # Smoke test files
│
├── functional/              # FTEST - Functional Tests (Code 43)
│   ├── conftest.py          # Functional-specific fixtures
│   └── test_*.py            # Functional test files
│
└── results/                 # Test result archives
    └── .gitkeep
```

## Test Types

| Type | Marker | Characteristics | Typical Duration |
|------|--------|-----------------|------------------|
| UTEST | `@pytest.mark.utest` | Fast, isolated, no external dependencies | <1 second |
| ITEST | `@pytest.mark.itest` | Component interaction, may require services | <60 seconds |
| STEST | `@pytest.mark.stest` | Post-deployment health checks | <30 seconds |
| FTEST | `@pytest.mark.ftest` | End-to-end user workflows | <120 seconds |

## Running Tests

### Using the Unified Runner

```bash
# Run all tests
python scripts/run_tests.py --type all

# Run specific test type
python scripts/run_tests.py --type utest
python scripts/run_tests.py --type itest
python scripts/run_tests.py --type stest
python scripts/run_tests.py --type ftest

# Run and save results for comparison
python scripts/run_tests.py --type utest --save

# Run with coverage
python scripts/run_tests.py --type all --coverage
```

### Using pytest Directly

```bash
# Run all tests
pytest tests/

# Run by directory
pytest tests/unit/
pytest tests/integration/

# Run by marker
pytest -m utest
pytest -m itest
pytest -m "utest or stest"

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Fixtures

### Shared Fixtures (conftest.py)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `project_root` | session | Project root directory path |
| `ai_dev_flow_path` | session | ai_dev_flow directory path |
| `test_config` | session | Test configuration from test_config.yaml |
| `test_results` | session | Accumulate results for comparison |
| `mock_config` | function | Mock configuration for unit tests |
| `temp_yaml_file` | function | Temporary YAML file |
| `temp_json_file` | function | Temporary JSON file |

### Unit Test Fixtures (unit/conftest.py)

| Fixture | Purpose |
|---------|---------|
| `sample_yaml_content` | Sample YAML content for parsing tests |
| `sample_json_content` | Sample JSON content for parsing tests |
| `mock_artifact` | Mock SDD artifact for unit testing |
| `mock_validation_rules` | Mock validation rules |
| `temp_project_structure` | Temporary project directory structure |

### Integration Test Fixtures (integration/conftest.py)

| Fixture | Purpose |
|---------|---------|
| `integration_config` | Configuration from environment variables |
| `test_data_dir` | Test data directory |
| `sample_artifacts` | Sample artifact files |
| `filesystem_sandbox` | Isolated filesystem for testing |
| `mock_api_response` | Mock API response data |

### Smoke Test Fixtures (smoke/conftest.py)

| Fixture | Purpose |
|---------|---------|
| `critical_paths` | Critical paths to verify |
| `expected_services` | Services that should be running |
| `health_thresholds` | Health check thresholds |
| `smoke_test_config` | Smoke test configuration |

### Functional Test Fixtures (functional/conftest.py)

| Fixture | Purpose |
|---------|---------|
| `user_workflow_steps` | Common workflow steps |
| `complete_project_structure` | Complete project for testing |
| `workflow_context` | Workflow execution context |
| `expected_workflow_results` | Expected workflow outcomes |

## Configuration

### pytest.ini

Located at project root, configures:
- Test discovery paths
- Markers for test types
- Timeout settings
- Output formatting
- Coverage options

### test_config.yaml

Environment-specific settings:
- Timeouts by test type
- Deployment URLs
- Database settings
- API configuration
- Coverage thresholds

### pyproject.toml

Tool configuration:
- Coverage source and exclusions
- Coverage thresholds (80% default)
- Report formats (HTML, JSON, XML)

## Test Result Management

### Saving Results

```bash
# Run and save results
python scripts/run_tests.py --type utest --save
# Creates: tests/results/results_utest_{timestamp}.json
# Updates: tests/results/latest_utest.json
```

### Comparing Results

```bash
# Compare two result files
python scripts/compare_test_results.py baseline.json current.json

# Compare latest results
python scripts/compare_test_results.py --latest tests/results/

# Save comparison report
python scripts/compare_test_results.py --output report.md baseline.json current.json
```

### Archiving Results

```bash
# Archive results with metadata
python scripts/archive_test_results.py --save tests/results/latest_utest.json

# Set baseline for comparison
python scripts/archive_test_results.py --set-baseline tests/results/latest_utest.json

# Prune old archives (keep last 10)
python scripts/archive_test_results.py --prune --keep 10

# View trend report
python scripts/archive_test_results.py --trend
```

## Coverage Reports

### Generating Reports

```bash
# Generate coverage report
python scripts/generate_coverage_report.py --type all

# Generate HTML report
python scripts/generate_coverage_report.py --type all --html

# Check threshold
python scripts/generate_coverage_report.py --check --threshold 80
```

### Coverage Thresholds

| Metric | Default Threshold |
|--------|-------------------|
| Overall coverage | 80% |
| Branch coverage | Enabled |
| Fail under threshold | Configurable |

## Test Registry

Tests are cataloged in the TSPEC layer registry:

```bash
# List registered tests
python ai_dev_flow/10_TSPEC/scripts/manage_test_registry.py --list

# Register new test
python ai_dev_flow/10_TSPEC/scripts/manage_test_registry.py --add \
  UTEST-001 UTEST "Test description" "tests/unit/test_file.py::test_func"

# Sync from filesystem
python ai_dev_flow/10_TSPEC/scripts/manage_test_registry.py --sync
```

## CI/CD Integration

GitHub Actions workflow (`.github/workflows/test-pipeline.yml`) runs:

1. **Unit Tests**: On every push/PR
2. **Integration Tests**: After unit tests pass
3. **Smoke Tests**: On main branch deployments
4. **Coverage Report**: After all tests complete
5. **Regression Check**: On pull requests

## Writing Tests

### Unit Test Example

```python
"""
Test module for authentication.

Test ID: UTEST-001
Reference: ai_dev_flow/10_TSPEC/UTEST/
"""

import pytest

class TestAuthentication:
    """Unit tests for authentication module."""

    @pytest.mark.utest
    def test_token_generation(self, mock_config):
        """Test that tokens are generated correctly."""
        # Arrange
        # Act
        # Assert
        pass
```

### Integration Test Example

```python
"""
Integration tests for database operations.

Test ID: ITEST-001
Reference: ai_dev_flow/10_TSPEC/ITEST/
"""

import pytest

class TestDatabaseIntegration:
    """Integration tests for database layer."""

    @pytest.mark.itest
    @pytest.mark.requires_db
    def test_connection(self, db_connection):
        """Test database connection."""
        # Arrange
        # Act
        # Assert
        pass
```

## Dependencies

Required packages (in requirements-test.txt):

```
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-timeout>=2.2.0
pytest-json-report>=1.5.0
pyyaml>=6.0.1
jsonschema>=4.21.0
```

Optional packages:

```
pytest-xdist>=3.5.0      # Parallel execution
pytest-html>=4.1.0       # HTML reports
pytest-bdd>=7.0.0        # BDD integration
```

## References

- [ai_dev_flow/10_TSPEC/README.md](../ai_dev_flow/10_TSPEC/README.md) - TSPEC layer documentation
- [ai_dev_flow/TESTING_STRATEGY_TDD.md](../ai_dev_flow/TESTING_STRATEGY_TDD.md) - TDD workflow
- [pytest.ini](../pytest.ini) - Pytest configuration
- [pyproject.toml](../pyproject.toml) - Tool configuration
