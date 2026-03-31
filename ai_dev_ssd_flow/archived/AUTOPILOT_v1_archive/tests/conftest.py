"""
Pytest Configuration for Autopilot TDD Scripts

Provides shared fixtures, markers, and configuration for testing
the TDD workflow automation scripts.

Usage:
    pytest ai_dev_flow/AUTOPILOT/tests/ -v
    pytest ai_dev_flow/AUTOPILOT/tests/ -m smoke
    pytest ai_dev_flow/AUTOPILOT/tests/ -m "not slow"
"""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest


# =============================================================================
# Path Configuration
# =============================================================================

AUTOPILOT_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = AUTOPILOT_DIR / "scripts"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "smoke: Quick smoke tests for basic functionality")
    config.addinivalue_line("markers", "unit: Unit tests for individual functions")
    config.addinivalue_line("markers", "regression: Regression tests with baseline comparison")
    config.addinivalue_line("markers", "integration: Integration tests for workflow stages")
    config.addinivalue_line("markers", "bdd: BDD acceptance tests")
    config.addinivalue_line("markers", "slow: Tests that take more than 5 seconds")


# =============================================================================
# Directory Fixtures
# =============================================================================

@pytest.fixture
def scripts_dir() -> Path:
    """Return path to Autopilot scripts directory."""
    return SCRIPTS_DIR


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create a temporary project directory with SDD structure."""
    temp_dir = Path(tempfile.mkdtemp(prefix="autopilot_test_"))

    # Create SDD directory structure
    dirs = [
        "ai_dev_flow/01_BRD",
        "ai_dev_flow/02_PRD",
        "ai_dev_flow/03_EARS",
        "ai_dev_flow/04_BDD",
        "ai_dev_flow/05_ADR",
        "ai_dev_flow/06_SYS",
        "ai_dev_flow/07_REQ",
        "ai_dev_flow/08_CTR",
        "ai_dev_flow/09_SPEC",
        "ai_dev_flow/10_TSPEC",
        "ai_dev_flow/11_TASKS",
        "tests/unit",
        "tests/integration",
        "tests/smoke",
        "tests/bdd",
        "src/services",
        "tmp",
    ]

    for d in dirs:
        (temp_dir / d).mkdir(parents=True, exist_ok=True)

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_test_dir(temp_project_dir: Path) -> Path:
    """Return path to temp unit test directory."""
    return temp_project_dir / "tests" / "unit"


@pytest.fixture
def temp_spec_dir(temp_project_dir: Path) -> Path:
    """Return path to temp SPEC directory."""
    return temp_project_dir / "ai_dev_flow" / "09_SPEC"


@pytest.fixture
def temp_req_dir(temp_project_dir: Path) -> Path:
    """Return path to temp REQ directory."""
    return temp_project_dir / "ai_dev_flow" / "07_REQ"


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_test_file(temp_test_dir: Path) -> Path:
    """Create a sample unit test file with traceability tags."""
    test_file = temp_test_dir / "test_sample_req_01.py"
    test_file.write_text('''"""
Unit tests for REQ-01

@brd: BRD.01.01.01
@prd: PRD.01.02.01
@req: REQ-01.01.01
@spec: PENDING
@code: PENDING
"""

import pytest


class TestSampleRequirement:
    """Tests for sample requirement."""

    def test_validate_input(self):
        """Test input validation."""
        # Arrange
        data = {"name": "test", "value": 42}

        # Act
        result = validate_input(data)

        # Assert
        assert result is True

    def test_process_request(self):
        """Test request processing."""
        # Arrange
        request = {"action": "process", "data": [1, 2, 3]}

        # Act
        response = process_request(request)

        # Assert
        assert response["status"] == "success"

    def test_error_handling(self):
        """Test error handling for invalid input."""
        # Arrange
        invalid_data = None

        # Act & Assert
        with pytest.raises(ValueError):
            validate_input(invalid_data)
''')
    return test_file


@pytest.fixture
def sample_req_file(temp_req_dir: Path) -> Path:
    """Create a sample REQ file."""
    req_file = temp_req_dir / "REQ-01_sample_requirement.md"
    req_file.write_text('''---
title: "REQ-01: Sample Requirement"
tags:
  - requirement
  - layer-7-artifact
custom_fields:
  artifact_type: REQ
  layer: 7
  priority: P1
---

# REQ-01: Sample Requirement

## Document Control

| Field | Value |
|-------|-------|
| **REQ ID** | REQ-01 |
| **Status** | Draft |
| **Priority** | P1 |

## Description

The system shall validate input data before processing.

## Acceptance Criteria

- AC-01: Input validation returns True for valid data
- AC-02: Input validation raises ValueError for None input
- AC-03: Request processing returns success status

## Traceability

@brd: BRD.01.01.01
@prd: PRD.01.02.01
''')
    return req_file


@pytest.fixture
def sample_spec_file(temp_spec_dir: Path) -> Path:
    """Create a sample SPEC file."""
    spec_file = temp_spec_dir / "SPEC-01_sample_spec.yaml"
    spec_file.write_text('''id: SPEC-01
title: Sample Specification
version: "1.0"
status: draft

traceability:
  brd: BRD.01.01.01
  prd: PRD.01.02.01
  req: REQ-01.01.01

interfaces:
  internal_apis:
    - interface: ValidationService
      purpose: Input validation
      methods:
        - name: validate_input
          parameters:
            - name: data
              type: dict
          returns: bool
        - name: process_request
          parameters:
            - name: request
              type: dict
          returns: dict

  external_dependencies: []

implementation:
  module: src/services/validation_service.py
  class: ValidationService
''')
    return spec_file


@pytest.fixture
def sample_bdd_file(temp_project_dir: Path) -> Path:
    """Create a sample BDD feature file."""
    bdd_dir = temp_project_dir / "ai_dev_flow" / "04_BDD"
    bdd_file = bdd_dir / "sample_feature.feature"
    bdd_file.write_text('''@smoke @critical
Feature: Input Validation

  As a user
  I want input to be validated
  So that invalid data is rejected

  @smoke
  Scenario: Valid input is accepted
    Given I have valid input data
    When I submit the data for validation
    Then the validation should pass

  @critical
  Scenario: Invalid input is rejected
    Given I have invalid input data
    When I submit the data for validation
    Then the validation should fail
    And an error message should be returned
''')
    return bdd_file


@pytest.fixture
def sample_ears_file(temp_project_dir: Path) -> Path:
    """Create a sample EARS file."""
    ears_dir = temp_project_dir / "ai_dev_flow" / "03_EARS"
    ears_file = ears_dir / "EARS-01_sample.md"
    ears_file.write_text('''---
title: "EARS-01: Sample EARS Requirements"
---

# EARS-01: Sample EARS Requirements

## Requirements

### EARS-01.01 Input Validation

WHEN the user submits data THE system SHALL validate the input WITHIN 100ms.

### EARS-01.02 Error Response

WHEN the validation fails THE system SHALL return an error message WITHIN 50ms.
''')
    return ears_file


@pytest.fixture
def sample_ctr_file(temp_project_dir: Path) -> Path:
    """Create a sample CTR file."""
    ctr_dir = temp_project_dir / "ai_dev_flow" / "08_CTR"
    ctr_file = ctr_dir / "CTR-01_sample.yaml"
    ctr_file.write_text('''id: CTR-01
title: Sample Contract
version: "1.0"

endpoints:
  - path: /api/v1/validate
    method: POST
    description: Validate input data
    request:
      content_type: application/json
      schema:
        type: object
        properties:
          data:
            type: object
    response:
      content_type: application/json
      schema:
        type: object
        properties:
          valid:
            type: boolean
          errors:
            type: array

interfaces:
  ValidationInterface:
    methods:
      - validate
      - process
''')
    return ctr_file


# =============================================================================
# Test Requirements Fixtures
# =============================================================================

@pytest.fixture
def sample_test_requirements(temp_project_dir: Path) -> Path:
    """Create a sample test requirements JSON file."""
    output_file = temp_project_dir / "tmp" / "test_requirements.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "generated_at": "2026-02-06T12:00:00",
        "test_directory": "tests/unit",
        "test_files": [
            {
                "file_path": "tests/unit/test_sample_req_01.py",
                "req_id": "REQ-01",
                "traceability": {
                    "brd": "BRD.01.01.01",
                    "prd": "PRD.01.02.01",
                    "req": "REQ-01.01.01",
                    "spec": "PENDING",
                    "code": "PENDING"
                },
                "test_classes": [
                    {
                        "name": "TestSampleRequirement",
                        "methods": [
                            {"name": "test_validate_input", "docstring": "Test input validation."},
                            {"name": "test_process_request", "docstring": "Test request processing."},
                            {"name": "test_error_handling", "docstring": "Test error handling for invalid input."}
                        ]
                    }
                ],
                "required_functions": ["validate_input", "process_request"]
            }
        ],
        "summary": {
            "total_files": 1,
            "total_classes": 1,
            "total_methods": 3,
            "pending_specs": 1,
            "pending_code": 1
        }
    }

    output_file.write_text(json.dumps(data, indent=2))
    return output_file


# =============================================================================
# Code Fixtures
# =============================================================================

@pytest.fixture
def sample_code_file(temp_project_dir: Path) -> Path:
    """Create a sample implementation file."""
    code_dir = temp_project_dir / "src" / "services"
    code_file = code_dir / "validation_service.py"
    code_file.write_text('''"""
Validation Service Implementation

@spec: SPEC-01_sample_spec.yaml
@req: REQ-01.01.01
"""

from typing import Any, Dict


def validate_input(data: Dict[str, Any]) -> bool:
    """
    Validate input data.

    Args:
        data: Input data dictionary

    Returns:
        True if valid, raises ValueError if invalid

    Raises:
        ValueError: If data is None or invalid
    """
    if data is None:
        raise ValueError("Data cannot be None")

    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")

    return True


def process_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process incoming request.

    Args:
        request: Request dictionary with action and data

    Returns:
        Response dictionary with status
    """
    if not validate_input(request):
        return {"status": "error", "message": "Invalid request"}

    return {
        "status": "success",
        "data": request.get("data", [])
    }
''')
    return code_file


# =============================================================================
# Helper Functions
# =============================================================================

@pytest.fixture
def run_script(scripts_dir: Path):
    """Factory fixture for running Autopilot scripts."""
    import subprocess
    import sys

    def _run_script(script_name: str, *args, timeout: int = 60) -> subprocess.CompletedProcess:
        script_path = scripts_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        cmd = [sys.executable, str(script_path)] + list(args)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    return _run_script


@pytest.fixture
def assert_file_contains():
    """Factory fixture for asserting file contents."""
    def _assert_file_contains(file_path: Path, *patterns: str):
        content = file_path.read_text()
        for pattern in patterns:
            assert pattern in content, f"Pattern '{pattern}' not found in {file_path}"

    return _assert_file_contains


@pytest.fixture
def assert_valid_json():
    """Factory fixture for asserting valid JSON."""
    def _assert_valid_json(file_path: Path) -> dict:
        content = file_path.read_text()
        return json.loads(content)

    return _assert_valid_json
