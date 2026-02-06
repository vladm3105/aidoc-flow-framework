"""
Sample unit tests demonstrating UTEST patterns.

These tests serve as examples and verify the testing infrastructure works.

Reference: ai_dev_flow/10_TSPEC/UTEST/
Test ID: UTEST-001
"""

import pytest
import json
import yaml
from pathlib import Path


class TestSampleUnit:
    """Sample unit test class demonstrating test patterns."""

    def test_yaml_parsing(self, sample_yaml_content: str):
        """Test YAML content can be parsed correctly."""
        data = yaml.safe_load(sample_yaml_content)

        assert data["artifact_id"] == "REQ-001"
        assert data["status"] == "active"
        assert "core" in data["tags"]

    def test_json_parsing(self, sample_json_content: str):
        """Test JSON content can be parsed correctly."""
        data = json.loads(sample_json_content)

        assert data["artifact_id"] == "REQ-001"
        assert data["title"] == "Sample Requirement"

    def test_artifact_structure(self, mock_artifact: dict):
        """Test artifact has required fields."""
        required_fields = ["artifact_id", "title", "status"]

        for field in required_fields:
            assert field in mock_artifact, f"Missing required field: {field}"

    def test_id_pattern_validation(self, mock_artifact: dict):
        """Test artifact ID follows naming convention."""
        import re

        pattern = r"^[A-Z]+-[0-9]{3}$"
        artifact_id = mock_artifact["artifact_id"]

        assert re.match(pattern, artifact_id), f"ID {artifact_id} does not match pattern"

    def test_project_structure_creation(self, temp_project_structure: Path):
        """Test temporary project structure is created correctly."""
        assert (temp_project_structure / "docs" / "REQ").exists()
        assert (temp_project_structure / "docs" / "SPEC").exists()
        assert (temp_project_structure / "src").exists()
        assert (temp_project_structure / "tests").exists()

    def test_sample_file_content(self, temp_project_structure: Path):
        """Test sample file has expected content."""
        req_file = temp_project_structure / "docs" / "REQ" / "REQ-001.md"
        content = req_file.read_text()

        assert "REQ-001" in content
        assert "Sample Requirement" in content


class TestValidation:
    """Tests for validation logic."""

    def test_required_fields_present(self, mock_artifact: dict, mock_validation_rules: dict):
        """Test all required fields are present in artifact."""
        required = mock_validation_rules["required_fields"]

        for field in required:
            assert field in mock_artifact

    def test_status_value_valid(self, mock_artifact: dict, mock_validation_rules: dict):
        """Test status has valid value."""
        valid_statuses = mock_validation_rules["status_values"]
        status = mock_artifact["status"]

        assert status in valid_statuses

    @pytest.mark.parametrize(
        "artifact_id,expected_valid",
        [
            ("REQ-001", True),
            ("SPEC-123", True),
            ("req-001", False),
            ("REQ001", False),
            ("REQ-1", False),
            ("REQ-1234", False),
        ],
    )
    def test_id_pattern_parametrized(
        self, artifact_id: str, expected_valid: bool, mock_validation_rules: dict
    ):
        """Test ID pattern validation with various inputs."""
        import re

        pattern = mock_validation_rules["id_pattern"]
        is_valid = bool(re.match(pattern, artifact_id))

        assert is_valid == expected_valid


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_yaml(self):
        """Test handling of empty YAML content."""
        data = yaml.safe_load("")
        assert data is None

    def test_malformed_json(self):
        """Test handling of malformed JSON."""
        with pytest.raises(json.JSONDecodeError):
            json.loads("{invalid json}")

    def test_missing_file(self, tmp_path: Path):
        """Test handling of missing file."""
        missing_file = tmp_path / "nonexistent.yaml"
        assert not missing_file.exists()

    def test_empty_artifact(self):
        """Test handling of empty artifact dict."""
        empty_artifact = {}
        assert len(empty_artifact) == 0
        assert "artifact_id" not in empty_artifact
