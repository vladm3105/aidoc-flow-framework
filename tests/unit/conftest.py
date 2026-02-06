"""
Unit test fixtures and configuration.

These fixtures are specific to unit tests (UTEST) which are:
- Fast (< 1 second per test)
- Isolated (no external dependencies)
- Deterministic (same result every time)

Reference: ai_dev_flow/10_TSPEC/UTEST/
"""

import pytest
from pathlib import Path
from typing import Any, Dict


# Apply utest marker to all tests in this directory
def pytest_collection_modifyitems(items):
    """Add utest marker to all tests in this directory."""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.utest)


@pytest.fixture
def sample_yaml_content() -> str:
    """Sample YAML content for parsing tests."""
    return """
artifact_id: REQ-001
title: Sample Requirement
status: active
version: "1.0"
tags:
  - core
  - authentication
"""


@pytest.fixture
def sample_json_content() -> str:
    """Sample JSON content for parsing tests."""
    return '{"artifact_id": "REQ-001", "title": "Sample Requirement", "status": "active"}'


@pytest.fixture
def mock_artifact() -> Dict[str, Any]:
    """Mock SDD artifact for unit testing."""
    return {
        "artifact_id": "REQ-001",
        "artifact_type": "REQ",
        "title": "Test Requirement",
        "description": "A test requirement for unit testing",
        "status": "active",
        "priority": "high",
        "version": "1.0",
        "created_date": "2026-02-06",
        "modified_date": "2026-02-06",
        "upstream_refs": ["BRD-001"],
        "downstream_refs": ["SPEC-001"],
        "tags": ["test", "unit"],
    }


@pytest.fixture
def mock_validation_rules() -> Dict[str, Any]:
    """Mock validation rules for testing validators."""
    return {
        "required_fields": ["artifact_id", "title", "status"],
        "optional_fields": ["description", "tags", "priority"],
        "status_values": ["active", "deprecated", "draft"],
        "id_pattern": r"^[A-Z]+-[0-9]{3}$",
    }


@pytest.fixture
def temp_project_structure(tmp_path: Path) -> Path:
    """Create temporary project structure for testing."""
    # Create directory structure
    (tmp_path / "docs" / "REQ").mkdir(parents=True)
    (tmp_path / "docs" / "SPEC").mkdir(parents=True)
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "tests").mkdir(parents=True)

    # Create sample files
    (tmp_path / "docs" / "REQ" / "REQ-001.md").write_text(
        "# REQ-001: Sample Requirement\n\nDescription here."
    )

    return tmp_path
