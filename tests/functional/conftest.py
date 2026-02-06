"""
Functional test fixtures and configuration.

These fixtures are specific to functional tests (FTEST) which:
- Test complete user workflows
- Validate end-to-end scenarios
- May be slower due to full system testing
- Verify business requirements are met

Reference: ai_dev_flow/10_TSPEC/FTEST/
"""

import pytest
from pathlib import Path
from typing import Any, Dict, Generator, List


# Apply ftest marker to all tests in this directory
def pytest_collection_modifyitems(items):
    """Add ftest marker to all tests in this directory."""
    for item in items:
        if "functional" in str(item.fspath):
            item.add_marker(pytest.mark.ftest)


@pytest.fixture
def user_workflow_steps() -> List[str]:
    """Common user workflow steps for testing."""
    return [
        "login",
        "navigate_to_artifacts",
        "create_artifact",
        "edit_artifact",
        "validate_artifact",
        "save_artifact",
        "logout",
    ]


@pytest.fixture
def complete_project_structure(tmp_path: Path) -> Generator[Path, None, None]:
    """Create complete project structure for functional testing."""
    import json
    import yaml

    project = tmp_path / "test_project"
    project.mkdir()

    # Create SDD layer structure
    layers = [
        ("01_BRD", "BRD"),
        ("02_PRD", "PRD"),
        ("07_REQ", "REQ"),
        ("10_SPEC", "SPEC"),
    ]

    for layer_dir, artifact_type in layers:
        layer_path = project / "docs" / layer_dir
        layer_path.mkdir(parents=True)

        # Create sample artifact
        artifact = {
            "artifact_id": f"{artifact_type}-001",
            "artifact_type": artifact_type,
            "title": f"Sample {artifact_type}",
            "status": "active",
        }
        (layer_path / f"{artifact_type}-001.yaml").write_text(yaml.dump(artifact))

    # Create src structure
    (project / "src").mkdir()
    (project / "src" / "__init__.py").write_text("")

    # Create tests structure
    (project / "tests").mkdir()
    (project / "tests" / "__init__.py").write_text("")

    yield project


@pytest.fixture
def workflow_context() -> Dict[str, Any]:
    """Context for workflow execution."""
    return {
        "user_id": "test-user-001",
        "session_id": "session-001",
        "permissions": ["read", "write", "validate"],
        "project_id": "test-project-001",
    }


@pytest.fixture
def expected_workflow_results() -> Dict[str, Any]:
    """Expected results for workflow completion."""
    return {
        "artifacts_created": 1,
        "validations_passed": True,
        "errors": [],
        "warnings": [],
    }
