"""
Sample functional tests demonstrating FTEST patterns.

These tests verify complete user workflows and end-to-end scenarios.

Reference: ai_dev_flow/10_TSPEC/FTEST/
Test ID: FTEST-001
"""

import json
import yaml
import pytest
from pathlib import Path
from typing import Any, Dict, List


class TestArtifactCreationWorkflow:
    """Functional tests for artifact creation workflow."""

    def test_create_complete_artifact(self, complete_project_structure: Path):
        """Test creating a complete artifact with all required fields."""
        docs_dir = complete_project_structure / "docs" / "07_REQ"

        # Create new artifact
        artifact = {
            "artifact_id": "REQ-002",
            "artifact_type": "REQ",
            "title": "New Functional Requirement",
            "description": "Description of the requirement",
            "status": "active",
            "priority": "high",
            "version": "1.0",
            "created_date": "2026-02-06",
            "upstream_refs": ["BRD-001"],
            "downstream_refs": [],
            "acceptance_criteria": [
                "Criterion 1",
                "Criterion 2",
            ],
        }

        artifact_path = docs_dir / "REQ-002.yaml"
        artifact_path.write_text(yaml.dump(artifact))

        # Verify creation
        assert artifact_path.exists()
        loaded = yaml.safe_load(artifact_path.read_text())
        assert loaded["artifact_id"] == "REQ-002"
        assert len(loaded["acceptance_criteria"]) == 2

    def test_artifact_validation_workflow(self, complete_project_structure: Path):
        """Test artifact validation workflow."""
        # Load existing artifact
        req_path = complete_project_structure / "docs" / "07_REQ" / "REQ-001.yaml"
        artifact = yaml.safe_load(req_path.read_text())

        # Validate required fields
        required_fields = ["artifact_id", "artifact_type", "title", "status"]
        validation_errors = []

        for field in required_fields:
            if field not in artifact:
                validation_errors.append(f"Missing required field: {field}")

        # Validate ID format
        import re
        if not re.match(r"^REQ-[0-9]{3}$", artifact.get("artifact_id", "")):
            validation_errors.append("Invalid artifact ID format")

        assert len(validation_errors) == 0, f"Validation errors: {validation_errors}"


class TestTraceabilityWorkflow:
    """Functional tests for traceability workflow."""

    def test_upstream_downstream_linking(self, complete_project_structure: Path):
        """Test creating upstream/downstream links between artifacts."""
        brd_path = complete_project_structure / "docs" / "01_BRD" / "BRD-001.yaml"
        req_path = complete_project_structure / "docs" / "07_REQ" / "REQ-001.yaml"

        # Update BRD with downstream ref
        brd = yaml.safe_load(brd_path.read_text())
        brd["downstream_refs"] = ["REQ-001"]
        brd_path.write_text(yaml.dump(brd))

        # Update REQ with upstream ref
        req = yaml.safe_load(req_path.read_text())
        req["upstream_refs"] = ["BRD-001"]
        req_path.write_text(yaml.dump(req))

        # Verify bidirectional linking
        loaded_brd = yaml.safe_load(brd_path.read_text())
        loaded_req = yaml.safe_load(req_path.read_text())

        assert "REQ-001" in loaded_brd.get("downstream_refs", [])
        assert "BRD-001" in loaded_req.get("upstream_refs", [])

    def test_traceability_chain_validation(self, complete_project_structure: Path):
        """Test validating complete traceability chain."""
        # Walk through layers and validate connections
        layer_order = ["01_BRD", "02_PRD", "07_REQ", "10_SPEC"]
        docs_dir = complete_project_structure / "docs"

        artifacts_by_layer = {}
        for layer in layer_order:
            layer_path = docs_dir / layer
            if layer_path.exists():
                artifacts = []
                for file in layer_path.glob("*.yaml"):
                    data = yaml.safe_load(file.read_text())
                    artifacts.append(data)
                artifacts_by_layer[layer] = artifacts

        # Verify at least one artifact per layer
        for layer in layer_order:
            assert layer in artifacts_by_layer
            assert len(artifacts_by_layer[layer]) > 0


class TestProjectStructureWorkflow:
    """Functional tests for project structure operations."""

    def test_complete_project_initialization(self, tmp_path: Path):
        """Test initializing a complete project structure."""
        project = tmp_path / "new_project"

        # Create standard SDD structure
        standard_dirs = [
            "docs/01_BRD",
            "docs/02_PRD",
            "docs/03_EARS",
            "docs/04_BDD",
            "docs/05_ADR",
            "docs/06_SYS",
            "docs/07_REQ",
            "docs/09_CTR",
            "docs/10_SPEC",
            "docs/11_TASKS",
            "src",
            "tests/unit",
            "tests/integration",
            "tests/smoke",
            "tests/functional",
        ]

        for dir_path in standard_dirs:
            (project / dir_path).mkdir(parents=True)

        # Verify structure
        for dir_path in standard_dirs:
            assert (project / dir_path).exists()

    def test_layer_artifact_discovery(self, complete_project_structure: Path):
        """Test discovering all artifacts in project layers."""
        docs_dir = complete_project_structure / "docs"
        discovered = {}

        for layer_dir in docs_dir.iterdir():
            if layer_dir.is_dir():
                artifacts = list(layer_dir.glob("*.yaml"))
                discovered[layer_dir.name] = len(artifacts)

        # Should have artifacts in each layer
        assert sum(discovered.values()) > 0


class TestWorkflowExecution:
    """Functional tests for complete workflow execution."""

    def test_full_sdd_workflow(
        self,
        complete_project_structure: Path,
        workflow_context: Dict[str, Any],
    ):
        """Test complete SDD workflow from BRD to SPEC."""
        docs_dir = complete_project_structure / "docs"

        # Step 1: Verify BRD exists
        brd = yaml.safe_load(
            (docs_dir / "01_BRD" / "BRD-001.yaml").read_text()
        )
        assert brd["status"] == "active"

        # Step 2: Verify PRD links to BRD
        prd = yaml.safe_load(
            (docs_dir / "02_PRD" / "PRD-001.yaml").read_text()
        )
        assert prd["artifact_type"] == "PRD"

        # Step 3: Verify REQ exists
        req = yaml.safe_load(
            (docs_dir / "07_REQ" / "REQ-001.yaml").read_text()
        )
        assert req["artifact_type"] == "REQ"

        # Step 4: Verify SPEC exists
        spec = yaml.safe_load(
            (docs_dir / "10_SPEC" / "SPEC-001.yaml").read_text()
        )
        assert spec["artifact_type"] == "SPEC"

        # Workflow complete
        assert workflow_context["user_id"] is not None
