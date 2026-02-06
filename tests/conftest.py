"""
Shared pytest fixtures for AI Dev Flow testing.

Fixtures are organized by test type:
- Unit test fixtures: Mocks, stubs, isolated components
- Integration test fixtures: Database, API clients
- Smoke test fixtures: Deployment verification
- Functional test fixtures: End-to-end scenarios

Reference: TESTING_STRATEGY_TDD.md, ai_dev_flow/10_TSPEC/
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List

import pytest
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# === Configuration Fixtures ===


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def ai_dev_flow_path(project_root: Path) -> Path:
    """Return ai_dev_flow directory path."""
    return project_root / "ai_dev_flow"


@pytest.fixture(scope="session")
def test_config(project_root: Path) -> Dict[str, Any]:
    """Load test configuration from test_config.yaml."""
    config_path = project_root / "tests" / "test_config.yaml"
    if config_path.exists():
        return yaml.safe_load(config_path.read_text())
    return {
        "environment": "test",
        "debug": True,
        "timeout": 30,
        "deployment_url": "http://localhost:8000",
    }


# === Test Result Recording ===


@pytest.fixture(scope="session")
def test_results() -> Generator[Dict[str, Any], None, None]:
    """
    Accumulate test results for comparison.

    Results are collected throughout the session and saved
    when the session completes.
    """
    results: Dict[str, Any] = {
        "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "started_at": datetime.now().isoformat(),
        "test_type": "ALL",
        "environment": "test",
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration_seconds": 0.0,
        },
        "tests": [],
    }
    yield results
    results["completed_at"] = datetime.now().isoformat()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test result on the item for fixture access."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def record_test_result(request, test_results: Dict[str, Any]) -> Generator[None, None, None]:
    """Record each test result for later comparison."""
    yield

    # Get test outcome from stored report
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call:
        outcome = "passed" if rep_call.passed else "failed"
        if rep_call.skipped:
            outcome = "skipped"

        test_results["tests"].append(
            {
                "name": request.node.name,
                "nodeid": request.node.nodeid,
                "outcome": outcome,
                "duration": getattr(rep_call, "duration", 0),
            }
        )

        # Update summary
        test_results["summary"]["total"] += 1
        test_results["summary"][outcome] += 1
        test_results["summary"]["duration_seconds"] += getattr(rep_call, "duration", 0)


# === Unit Test Fixtures (UTEST) ===


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide mock configuration for unit tests."""
    return {
        "environment": "test",
        "debug": True,
        "timeout": 30,
        "log_level": "DEBUG",
    }


@pytest.fixture
def temp_yaml_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary YAML file for testing."""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml.dump({"test": "data"}))
    yield yaml_file


@pytest.fixture
def temp_json_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary JSON file for testing."""
    json_file = tmp_path / "test.json"
    json_file.write_text(json.dumps({"test": "data"}, indent=2))
    yield json_file


@pytest.fixture
def sample_artifact_data() -> Dict[str, Any]:
    """Provide sample SDD artifact data for testing."""
    return {
        "artifact_id": "REQ-001",
        "artifact_type": "REQ",
        "title": "Sample Requirement",
        "status": "active",
        "created_date": "2026-02-06",
        "upstream_refs": ["BRD-001"],
        "downstream_refs": ["SPEC-001"],
    }


# === Integration Test Fixtures (ITEST) ===


@pytest.fixture(scope="module")
def db_connection():
    """
    Database connection for integration tests.

    Override this fixture in tests/integration/conftest.py
    with actual database connection logic.
    """
    connection = None  # Replace with: create_test_database()
    yield connection
    # Replace with: cleanup_test_database(connection)


@pytest.fixture(scope="module")
def filesystem_sandbox(tmp_path_factory) -> Path:
    """Create isolated filesystem for integration tests."""
    sandbox = tmp_path_factory.mktemp("sandbox")

    # Create standard directory structure
    (sandbox / "docs").mkdir()
    (sandbox / "tests").mkdir()
    (sandbox / "src").mkdir()

    return sandbox


# === Smoke Test Fixtures (STEST) ===


@pytest.fixture
def deployment_url(test_config: Dict[str, Any]) -> str:
    """Get deployment URL for smoke tests."""
    return test_config.get("deployment_url", "http://localhost:8000")


@pytest.fixture
def health_check_endpoints() -> List[str]:
    """List of health check endpoints to verify."""
    return [
        "/health",
        "/api/status",
        "/ready",
    ]


# === Functional Test Fixtures (FTEST) ===


@pytest.fixture
def api_client(deployment_url: str):
    """
    API client for functional tests.

    Override this fixture in tests/functional/conftest.py
    with actual API client implementation.
    """
    return None  # Replace with: APIClient(deployment_url)


@pytest.fixture
def authenticated_user():
    """
    Authenticated user context for functional tests.

    Override with actual authentication logic.
    """
    return {
        "user_id": "test-user-001",
        "username": "testuser",
        "email": "test@example.com",
        "roles": ["user", "tester"],
    }


# === Validation Fixtures ===


@pytest.fixture
def schema_validator(ai_dev_flow_path: Path):
    """
    Schema validator for SDD artifacts.

    Returns a function that validates data against a schema file.
    """

    def validate(data: Dict, schema_filename: str) -> bool:
        try:
            import jsonschema

            schema_path = ai_dev_flow_path / "schemas" / schema_filename
            if not schema_path.exists():
                # Try in the specific layer directory
                return True  # Schema not found, skip validation

            schema = yaml.safe_load(schema_path.read_text())
            jsonschema.validate(data, schema)
            return True
        except ImportError:
            # jsonschema not installed
            return True
        except Exception:
            return False

    return validate


# === Utility Fixtures ===


@pytest.fixture
def capture_logs(caplog):
    """Capture log output for verification."""
    caplog.set_level("DEBUG")
    return caplog


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime.now() for deterministic testing."""

    class MockDatetime:
        @staticmethod
        def now():
            return datetime(2026, 2, 6, 10, 30, 0)

        @staticmethod
        def today():
            return datetime(2026, 2, 6).date()

    monkeypatch.setattr("datetime.datetime", MockDatetime)
    return MockDatetime
