"""
Unit Tests for analyze_test_requirements.py

Tests the test requirement analyzer functionality.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from analyze_test_requirements import (
    TestRequirementAnalyzer,
    TestFileInfo,
    TestClassInfo,
    TestMethodInfo,
)


@pytest.mark.unit
class TestTestRequirementAnalyzer:
    """Tests for TestRequirementAnalyzer class."""

    def test_init(self):
        """Test analyzer initialization."""
        analyzer = TestRequirementAnalyzer()
        assert analyzer is not None

    def test_init_with_verbose(self):
        """Test analyzer with verbose mode."""
        analyzer = TestRequirementAnalyzer(verbose=True)
        assert analyzer.verbose is True

    def test_extract_traceability_tags(self, sample_test_file: Path):
        """Test extraction of traceability tags from test file."""
        analyzer = TestRequirementAnalyzer()
        content = sample_test_file.read_text()

        tags = analyzer._extract_traceability_tags(content)

        assert "brd" in tags
        assert tags["brd"] == "BRD.01.01.01"
        assert tags["req"] == "REQ-01.01.01"
        assert tags["spec"] == "PENDING"
        assert tags["code"] == "PENDING"

    def test_extract_test_classes(self, sample_test_file: Path):
        """Test extraction of test classes from file."""
        analyzer = TestRequirementAnalyzer()
        content = sample_test_file.read_text()

        classes = analyzer._extract_test_classes(content)

        assert len(classes) >= 1
        assert any(c.name == "TestSampleRequirement" for c in classes)

    def test_extract_test_methods(self, sample_test_file: Path):
        """Test extraction of test methods."""
        analyzer = TestRequirementAnalyzer()
        content = sample_test_file.read_text()

        classes = analyzer._extract_test_classes(content)
        test_class = next(c for c in classes if c.name == "TestSampleRequirement")

        assert len(test_class.methods) >= 3
        method_names = [m.name for m in test_class.methods]
        assert "test_validate_input" in method_names
        assert "test_process_request" in method_names
        assert "test_error_handling" in method_names

    def test_analyze_file(self, sample_test_file: Path):
        """Test full file analysis."""
        analyzer = TestRequirementAnalyzer()

        result = analyzer.analyze_file(sample_test_file)

        assert isinstance(result, TestFileInfo)
        assert result.file_path == str(sample_test_file)
        assert result.req_id == "REQ-01"
        assert len(result.test_classes) >= 1

    def test_analyze_directory(self, temp_test_dir: Path, sample_test_file: Path):
        """Test directory analysis."""
        analyzer = TestRequirementAnalyzer()

        results = analyzer.analyze_directory(temp_test_dir)

        assert len(results) >= 1
        assert any(r.file_path == str(sample_test_file) for r in results)

    def test_analyze_empty_directory(self, temp_test_dir: Path):
        """Test analysis of empty directory."""
        # Clear directory
        for f in temp_test_dir.glob("*.py"):
            f.unlink()

        analyzer = TestRequirementAnalyzer()
        results = analyzer.analyze_directory(temp_test_dir)

        assert len(results) == 0

    def test_generate_json_output(self, temp_test_dir: Path, sample_test_file: Path, temp_project_dir: Path):
        """Test JSON output generation."""
        analyzer = TestRequirementAnalyzer()
        output_file = temp_project_dir / "tmp" / "test_requirements.json"

        analyzer.generate_output(temp_test_dir, output_file)

        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert "test_files" in data
        assert "summary" in data
        assert data["summary"]["total_files"] >= 1


@pytest.mark.unit
class TestTestFileInfo:
    """Tests for TestFileInfo dataclass."""

    def test_create_basic(self):
        """Test basic creation."""
        info = TestFileInfo(
            file_path="/test/path.py",
            req_id="REQ-01"
        )
        assert info.file_path == "/test/path.py"
        assert info.req_id == "REQ-01"

    def test_create_with_traceability(self):
        """Test creation with traceability."""
        info = TestFileInfo(
            file_path="/test/path.py",
            req_id="REQ-01",
            traceability={"brd": "BRD.01.01.01", "spec": "PENDING"}
        )
        assert info.traceability["brd"] == "BRD.01.01.01"
        assert info.traceability["spec"] == "PENDING"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        info = TestFileInfo(
            file_path="/test/path.py",
            req_id="REQ-01",
            traceability={"brd": "BRD.01.01.01"}
        )
        d = info.to_dict()

        assert isinstance(d, dict)
        assert d["file_path"] == "/test/path.py"
        assert d["req_id"] == "REQ-01"


@pytest.mark.unit
class TestTestClassInfo:
    """Tests for TestClassInfo dataclass."""

    def test_create_basic(self):
        """Test basic creation."""
        info = TestClassInfo(name="TestExample")
        assert info.name == "TestExample"
        assert info.methods == []

    def test_create_with_methods(self):
        """Test creation with methods."""
        methods = [
            TestMethodInfo(name="test_one", docstring="Test one"),
            TestMethodInfo(name="test_two", docstring="Test two")
        ]
        info = TestClassInfo(name="TestExample", methods=methods)

        assert len(info.methods) == 2
        assert info.methods[0].name == "test_one"


@pytest.mark.unit
class TestTestMethodInfo:
    """Tests for TestMethodInfo dataclass."""

    def test_create_basic(self):
        """Test basic creation."""
        info = TestMethodInfo(name="test_example")
        assert info.name == "test_example"
        assert info.docstring == ""

    def test_create_with_docstring(self):
        """Test creation with docstring."""
        info = TestMethodInfo(name="test_example", docstring="Example test.")
        assert info.docstring == "Example test."
