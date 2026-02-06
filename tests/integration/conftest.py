"""
Integration test fixtures and configuration.

These fixtures are specific to integration tests (ITEST) which:
- Test interaction between components
- May require external services (databases, APIs)
- Are slower than unit tests
- Test real integration points

Reference: ai_dev_flow/10_TSPEC/ITEST/
"""

import os
import pytest
from pathlib import Path
from typing import Any, Dict, Generator, Optional


# Apply itest marker to all tests in this directory
def pytest_collection_modifyitems(items):
    """Add itest marker to all tests in this directory."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.itest)


@pytest.fixture(scope="module")
def integration_config() -> Dict[str, Any]:
    """Configuration for integration tests from environment."""
    return {
        "db_host": os.environ.get("TEST_DB_HOST", "localhost"),
        "db_port": int(os.environ.get("TEST_DB_PORT", "5432")),
        "db_user": os.environ.get("TEST_DB_USER", "test_user"),
        "db_password": os.environ.get("TEST_DB_PASSWORD", "test_password"),
        "db_name": os.environ.get("TEST_DB_NAME", "test_db"),
        "api_url": os.environ.get("TEST_API_URL", "http://localhost:8000"),
    }


@pytest.fixture(scope="module")
def test_data_dir(project_root: Path) -> Path:
    """Return test data directory."""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture(scope="module")
def sample_artifacts(test_data_dir: Path) -> Generator[Path, None, None]:
    """Create sample artifacts for integration testing."""
    import json
    import yaml

    # Create sample REQ file
    req_file = test_data_dir / "REQ-001.yaml"
    req_data = {
        "artifact_id": "REQ-001",
        "artifact_type": "REQ",
        "title": "Integration Test Requirement",
        "status": "active",
        "version": "1.0",
    }
    req_file.write_text(yaml.dump(req_data))

    # Create sample SPEC file
    spec_file = test_data_dir / "SPEC-001.json"
    spec_data = {
        "artifact_id": "SPEC-001",
        "artifact_type": "SPEC",
        "title": "Integration Test Specification",
        "upstream_refs": ["REQ-001"],
        "status": "active",
    }
    spec_file.write_text(json.dumps(spec_data, indent=2))

    yield test_data_dir

    # Cleanup
    if req_file.exists():
        req_file.unlink()
    if spec_file.exists():
        spec_file.unlink()


@pytest.fixture(scope="function")
def isolated_workspace(tmp_path: Path) -> Path:
    """Create isolated workspace for each test."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create standard structure
    (workspace / "docs").mkdir()
    (workspace / "src").mkdir()
    (workspace / "tests").mkdir()

    return workspace


@pytest.fixture
def mock_api_response() -> Dict[str, Any]:
    """Mock API response for testing without real API."""
    return {
        "status": "success",
        "data": {
            "artifacts": [
                {"id": "REQ-001", "type": "REQ", "status": "active"},
                {"id": "SPEC-001", "type": "SPEC", "status": "active"},
            ],
            "total": 2,
        },
        "metadata": {
            "timestamp": "2026-02-06T10:00:00Z",
            "version": "1.0",
        },
    }
