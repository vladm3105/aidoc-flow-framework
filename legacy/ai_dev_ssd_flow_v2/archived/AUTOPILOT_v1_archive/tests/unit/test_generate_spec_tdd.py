"""
Unit Tests for generate_spec_tdd.py

Tests the test-aware SPEC generation functionality.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_spec_tdd import (
    TDDSpecGenerator,
    SpecContent,
)


@pytest.mark.unit
class TestTDDSpecGenerator:
    """Tests for TDDSpecGenerator class."""

    def test_init(self):
        """Test generator initialization."""
        generator = TDDSpecGenerator()
        assert generator is not None

    def test_init_with_verbose(self):
        """Test generator with verbose mode."""
        generator = TDDSpecGenerator(verbose=True)
        assert generator.verbose is True

    def test_load_test_requirements(self, sample_test_requirements: Path):
        """Test loading test requirements JSON."""
        generator = TDDSpecGenerator()

        data = generator._load_test_requirements(sample_test_requirements)

        assert "test_files" in data
        assert len(data["test_files"]) >= 1

    def test_generate_spec_from_test_file(self, sample_test_requirements: Path):
        """Test SPEC generation from test file info."""
        generator = TDDSpecGenerator()
        data = generator._load_test_requirements(sample_test_requirements)
        test_file = data["test_files"][0]

        spec = generator._generate_spec_from_test_file(test_file)

        assert isinstance(spec, SpecContent)
        assert spec.spec_id is not None
        assert "REQ-01" in spec.spec_id or "01" in spec.spec_id

    def test_generate_spec_includes_traceability(self, sample_test_requirements: Path):
        """Test SPEC includes traceability from tests."""
        generator = TDDSpecGenerator()
        data = generator._load_test_requirements(sample_test_requirements)
        test_file = data["test_files"][0]

        spec = generator._generate_spec_from_test_file(test_file)

        assert spec.traceability is not None
        assert "req" in spec.traceability

    def test_generate_spec_includes_methods(self, sample_test_requirements: Path):
        """Test SPEC includes required methods from tests."""
        generator = TDDSpecGenerator()
        data = generator._load_test_requirements(sample_test_requirements)
        test_file = data["test_files"][0]

        spec = generator._generate_spec_from_test_file(test_file)

        # Should have methods derived from test requirements
        assert spec.interfaces is not None or spec.methods is not None

    def test_generate_to_directory(self, sample_test_requirements: Path, temp_project_dir: Path):
        """Test generation to output directory."""
        generator = TDDSpecGenerator()
        output_dir = temp_project_dir / "generated_specs"

        result = generator.generate(sample_test_requirements, output_dir)

        assert result.files_generated >= 0
        if result.files_generated > 0:
            spec_files = list(output_dir.glob("*.yaml"))
            assert len(spec_files) > 0

    def test_generate_creates_output_dir(self, sample_test_requirements: Path, temp_project_dir: Path):
        """Test that generation creates output directory."""
        generator = TDDSpecGenerator()
        output_dir = temp_project_dir / "new_output_dir"

        assert not output_dir.exists()
        generator.generate(sample_test_requirements, output_dir)
        assert output_dir.exists()


@pytest.mark.unit
class TestSpecContent:
    """Tests for SpecContent dataclass."""

    def test_create_basic(self):
        """Test basic creation."""
        spec = SpecContent(
            spec_id="SPEC-01",
            title="Test Specification"
        )
        assert spec.spec_id == "SPEC-01"
        assert spec.title == "Test Specification"

    def test_create_with_traceability(self):
        """Test creation with traceability."""
        spec = SpecContent(
            spec_id="SPEC-01",
            title="Test Specification",
            traceability={"req": "REQ-01.01.01", "brd": "BRD.01.01.01"}
        )
        assert spec.traceability["req"] == "REQ-01.01.01"

    def test_to_yaml(self):
        """Test YAML output."""
        spec = SpecContent(
            spec_id="SPEC-01",
            title="Test Specification",
            version="1.0",
            status="draft"
        )
        yaml_str = spec.to_yaml()

        assert "SPEC-01" in yaml_str
        assert "Test Specification" in yaml_str
        assert "1.0" in yaml_str

    def test_to_dict(self):
        """Test dictionary output."""
        spec = SpecContent(
            spec_id="SPEC-01",
            title="Test Specification"
        )
        d = spec.to_dict()

        assert isinstance(d, dict)
        assert d["id"] == "SPEC-01"
        assert d["title"] == "Test Specification"


@pytest.mark.unit
class TestSpecValidation:
    """Tests for SPEC validation."""

    def test_validate_generated_spec(self, sample_test_requirements: Path, temp_project_dir: Path):
        """Test that generated SPEC is valid YAML."""
        import yaml

        generator = TDDSpecGenerator()
        output_dir = temp_project_dir / "specs"
        generator.generate(sample_test_requirements, output_dir)

        for spec_file in output_dir.glob("*.yaml"):
            content = spec_file.read_text()
            # Should parse without error
            data = yaml.safe_load(content)
            assert data is not None
            assert "id" in data or "spec_id" in data

    def test_spec_has_required_fields(self, sample_test_requirements: Path, temp_project_dir: Path):
        """Test that generated SPEC has required fields."""
        import yaml

        generator = TDDSpecGenerator()
        output_dir = temp_project_dir / "specs"
        generator.generate(sample_test_requirements, output_dir)

        for spec_file in output_dir.glob("*.yaml"):
            data = yaml.safe_load(spec_file.read_text())

            # Check required fields
            assert "title" in data, "SPEC missing title"
            assert "version" in data, "SPEC missing version"
