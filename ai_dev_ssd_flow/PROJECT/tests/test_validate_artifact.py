"""
Unit tests for validate_artifact.py script.

Tests artifact type detection, gate validation, and validator dispatch.
TASKS Reference: TASKS-05.02.02
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from validate_artifact import (
    ArtifactTypeDetector,
    GateValidator,
    ValidatorRunner,
    detect_gates_for_path,
)


class TestArtifactTypeDetector:
    """Tests for ArtifactTypeDetector class."""

    def test_detect_type_from_filename(self, temp_dir):
        """Test detecting artifact type from filename."""
        detector = ArtifactTypeDetector()

        brd_file = temp_dir / 'BRD-01.md'
        brd_file.touch()
        assert detector.detect_type(brd_file) == 'BRD'

        prd_file = temp_dir / 'PRD-02.md'
        prd_file.touch()
        assert detector.detect_type(prd_file) == 'PRD'

    def test_detect_type_from_parent_directory(self, temp_dir):
        """Test detecting artifact type from parent directory."""
        detector = ArtifactTypeDetector()

        spec_dir = temp_dir / '09_SPEC'
        spec_dir.mkdir()
        spec_file = spec_dir / 'implementation.md'
        spec_file.touch()

        assert detector.detect_type(spec_file) == 'SPEC'

    def test_detect_type_code_file(self, temp_dir):
        """Test detecting code files."""
        detector = ArtifactTypeDetector()

        py_file = temp_dir / 'module.py'
        py_file.touch()
        assert detector.detect_type(py_file) == 'CODE'

    def test_detect_type_test_file(self, temp_dir):
        """Test detecting test files."""
        detector = ArtifactTypeDetector()

        tests_dir = temp_dir / 'tests'
        tests_dir.mkdir()
        test_file = tests_dir / 'test_module.py'
        test_file.touch()

        assert detector.detect_type(test_file) == 'TESTS'

    def test_detect_layer(self, temp_dir):
        """Test detecting layer from file path."""
        detector = ArtifactTypeDetector()

        brd_file = temp_dir / 'BRD-01.md'
        brd_file.touch()
        assert detector.detect_layer(brd_file) == 1

        tasks_file = temp_dir / 'TASKS-01.yaml'
        tasks_file.touch()
        assert detector.detect_layer(tasks_file) == 11

    def test_get_validator_path(self):
        """Test getting validator path for artifact type."""
        detector = ArtifactTypeDetector()

        assert 'validate_cross_document.py' in detector.get_validator_path('BRD')
        assert '--type BRD' in detector.get_validator_path('BRD')
        assert 'validate_schema_sync.py' in detector.get_validator_path('CTR')

    def test_get_gate(self):
        """Test getting gate for layer."""
        detector = ArtifactTypeDetector()

        assert detector.get_gate(1) == 'GATE-01'  # BRD
        assert detector.get_gate(4) == 'GATE-01'  # BDD
        assert detector.get_gate(5) == 'GATE-05'  # ADR
        assert detector.get_gate(9) == 'GATE-09'  # SPEC
        assert detector.get_gate(12) == 'GATE-12'  # CODE


class TestGateValidator:
    """Tests for GateValidator class."""

    def test_get_applicable_gate(self, sample_config_file):
        """Test getting applicable gate for layer."""
        from validate_artifact import ConfigLoader
        config = ConfigLoader(sample_config_file)
        validator = GateValidator(config)

        assert validator.get_applicable_gate(1) == 'GATE-01'
        assert validator.get_applicable_gate(5) == 'GATE-05'
        assert validator.get_applicable_gate(11) == 'GATE-09'

    def test_get_gate_config(self, sample_config_file):
        """Test getting gate configuration."""
        from validate_artifact import ConfigLoader
        config = ConfigLoader(sample_config_file)
        validator = GateValidator(config)

        gate_config = validator.get_gate_config('GATE-01')
        assert gate_config['name'] == 'Business Requirements Gate'
        assert gate_config['threshold'] == 90
        assert 1 in gate_config['layers']

    def test_check_upstream_gates(self, temp_dir, sample_config_file):
        """Test checking upstream gate requirements."""
        from validate_artifact import ConfigLoader
        config = ConfigLoader(sample_config_file)
        validator = GateValidator(config)

        # SPEC (L9) requires GATE-01 and GATE-05
        spec_file = temp_dir / 'SPEC-01.yaml'
        spec_file.touch()

        upstream = validator.check_upstream_gates(spec_file)
        assert 'GATE-01' in upstream
        assert 'GATE-05' in upstream


class TestDetectGatesForPath:
    """Tests for detect_gates_for_path function."""

    def test_detect_gates_single_file(self, temp_dir):
        """Test detecting gates for single file."""
        brd_file = temp_dir / 'BRD-01.md'
        brd_file.touch()

        gates = detect_gates_for_path(brd_file)
        assert 'GATE-01' in gates

    def test_detect_gates_directory(self, sample_docs_structure):
        """Test detecting gates for directory."""
        gates = detect_gates_for_path(sample_docs_structure)

        # Should include gates for BRD, PRD, ADR
        assert 'GATE-01' in gates  # BRD, PRD
        assert 'GATE-05' in gates  # ADR

    def test_detect_gates_empty_directory(self, temp_dir):
        """Test detecting gates for empty directory."""
        empty_dir = temp_dir / 'empty'
        empty_dir.mkdir()

        gates = detect_gates_for_path(empty_dir)
        assert gates == []
