"""
Sample integration tests demonstrating ITEST patterns.

These tests verify component interactions and integrations.

Reference: ai_dev_flow/10_TSPEC/ITEST/
Test ID: ITEST-001
"""

import json
import yaml
import pytest
from pathlib import Path
from typing import Dict, Any


class TestFileSystemIntegration:
    """Tests for filesystem integration operations."""

    def test_create_and_read_artifact(self, isolated_workspace: Path):
        """Test creating and reading back an artifact file."""
        # Create artifact
        artifact = {
            "artifact_id": "REQ-001",
            "title": "Test Requirement",
            "status": "active",
        }

        artifact_path = isolated_workspace / "docs" / "REQ-001.yaml"
        artifact_path.parent.mkdir(exist_ok=True)
        artifact_path.write_text(yaml.dump(artifact))

        # Read back and verify
        loaded = yaml.safe_load(artifact_path.read_text())
        assert loaded["artifact_id"] == artifact["artifact_id"]
        assert loaded["status"] == "active"

    def test_artifact_update_flow(self, isolated_workspace: Path):
        """Test updating an existing artifact."""
        artifact_path = isolated_workspace / "docs" / "REQ-001.yaml"
        artifact_path.parent.mkdir(exist_ok=True)

        # Create initial artifact
        initial = {"artifact_id": "REQ-001", "status": "draft", "version": "1.0"}
        artifact_path.write_text(yaml.dump(initial))

        # Update artifact
        loaded = yaml.safe_load(artifact_path.read_text())
        loaded["status"] = "active"
        loaded["version"] = "1.1"
        artifact_path.write_text(yaml.dump(loaded))

        # Verify update
        final = yaml.safe_load(artifact_path.read_text())
        assert final["status"] == "active"
        assert final["version"] == "1.1"

    def test_multi_artifact_relationship(self, isolated_workspace: Path):
        """Test creating related artifacts with references."""
        docs_dir = isolated_workspace / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Create REQ
        req = {
            "artifact_id": "REQ-001",
            "title": "Parent Requirement",
            "downstream_refs": ["SPEC-001"],
        }
        (docs_dir / "REQ-001.yaml").write_text(yaml.dump(req))

        # Create SPEC referencing REQ
        spec = {
            "artifact_id": "SPEC-001",
            "title": "Child Specification",
            "upstream_refs": ["REQ-001"],
        }
        (docs_dir / "SPEC-001.yaml").write_text(yaml.dump(spec))

        # Verify references
        loaded_req = yaml.safe_load((docs_dir / "REQ-001.yaml").read_text())
        loaded_spec = yaml.safe_load((docs_dir / "SPEC-001.yaml").read_text())

        assert "SPEC-001" in loaded_req["downstream_refs"]
        assert "REQ-001" in loaded_spec["upstream_refs"]


class TestDataFormatIntegration:
    """Tests for data format conversion and handling."""

    def test_yaml_to_json_conversion(self, sample_artifacts: Path):
        """Test converting YAML artifact to JSON format."""
        yaml_file = sample_artifacts / "REQ-001.yaml"
        yaml_data = yaml.safe_load(yaml_file.read_text())

        # Convert to JSON
        json_str = json.dumps(yaml_data, indent=2)
        json_data = json.loads(json_str)

        assert json_data["artifact_id"] == yaml_data["artifact_id"]
        assert json_data["status"] == yaml_data["status"]

    def test_json_to_yaml_conversion(self, sample_artifacts: Path):
        """Test converting JSON artifact to YAML format."""
        json_file = sample_artifacts / "SPEC-001.json"
        json_data = json.loads(json_file.read_text())

        # Convert to YAML
        yaml_str = yaml.dump(json_data)
        yaml_data = yaml.safe_load(yaml_str)

        assert yaml_data["artifact_id"] == json_data["artifact_id"]
        assert yaml_data["upstream_refs"] == json_data["upstream_refs"]


class TestConfigurationIntegration:
    """Tests for configuration loading and management."""

    def test_load_integration_config(self, integration_config: Dict[str, Any]):
        """Test integration configuration is loaded correctly."""
        assert "db_host" in integration_config
        assert "api_url" in integration_config
        assert isinstance(integration_config["db_port"], int)

    def test_config_defaults(self, integration_config: Dict[str, Any]):
        """Test configuration defaults are applied."""
        # These should match defaults in conftest
        assert integration_config["db_host"] in ["localhost", os.environ.get("TEST_DB_HOST", "localhost")]
        assert integration_config["db_port"] >= 0

    @pytest.mark.requires_db
    def test_database_connection_placeholder(self, integration_config: Dict[str, Any]):
        """Placeholder for database connection test."""
        # This test would connect to actual database when available
        pytest.skip("Database not configured for this test run")


# Import for type checking
import os
