"""
Sample smoke tests demonstrating STEST patterns.

These tests verify system health after deployment.

Reference: ai_dev_flow/10_TSPEC/STEST/
Test ID: STEST-001
"""

import pytest
from pathlib import Path
from typing import Any, Dict, List


class TestSystemHealth:
    """Smoke tests for system health verification."""

    def test_project_structure_exists(self, project_root: Path):
        """Verify project structure is intact."""
        required_dirs = [
            "ai_dev_flow",
            "tests",
            "scripts",
        ]

        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Required directory missing: {dir_name}"

    def test_critical_files_present(self, project_root: Path):
        """Verify critical files are present."""
        critical_files = [
            "pytest.ini",
            "README.md",
            "requirements-test.txt",
        ]

        for file_name in critical_files:
            file_path = project_root / file_name
            assert file_path.exists(), f"Critical file missing: {file_name}"

    def test_test_directories_exist(self, project_root: Path):
        """Verify test directories are set up."""
        test_dirs = ["unit", "integration", "smoke", "functional"]

        tests_path = project_root / "tests"
        for dir_name in test_dirs:
            dir_path = tests_path / dir_name
            assert dir_path.exists(), f"Test directory missing: {dir_name}"


class TestConfigurationHealth:
    """Smoke tests for configuration verification."""

    def test_pytest_config_valid(self, project_root: Path):
        """Verify pytest configuration is valid."""
        pytest_ini = project_root / "pytest.ini"
        assert pytest_ini.exists()

        content = pytest_ini.read_text()
        assert "[pytest]" in content
        assert "testpaths" in content

    def test_test_config_loadable(self, test_config: Dict[str, Any]):
        """Verify test configuration can be loaded."""
        assert test_config is not None
        assert "environment" in test_config

    def test_health_thresholds_defined(self, health_thresholds: Dict[str, Any]):
        """Verify health thresholds are properly defined."""
        required_thresholds = ["response_time_ms", "memory_percent"]

        for threshold in required_thresholds:
            assert threshold in health_thresholds
            assert isinstance(health_thresholds[threshold], (int, float))


class TestArtifactHealth:
    """Smoke tests for SDD artifact verification."""

    def test_tspec_layer_exists(self, ai_dev_flow_path: Path):
        """Verify TSPEC layer documentation exists."""
        tspec_path = ai_dev_flow_path / "10_TSPEC"
        assert tspec_path.exists(), "TSPEC layer missing"
        assert (tspec_path / "README.md").exists()

    def test_test_type_templates_exist(self, ai_dev_flow_path: Path):
        """Verify all test type templates exist."""
        tspec_path = ai_dev_flow_path / "10_TSPEC"
        test_types = ["UTEST", "ITEST", "STEST", "FTEST"]

        for test_type in test_types:
            type_dir = tspec_path / test_type
            assert type_dir.exists(), f"{test_type} directory missing"

    def test_registry_files_exist(self, ai_dev_flow_path: Path):
        """Verify test registry files exist."""
        tspec_path = ai_dev_flow_path / "10_TSPEC"

        registry_files = [
            "test_registry.yaml",
            "test_registry_schema.yaml",
            "test_result_schema.yaml",
        ]

        for filename in registry_files:
            file_path = tspec_path / filename
            assert file_path.exists(), f"Registry file missing: {filename}"


class TestScriptHealth:
    """Smoke tests for script availability."""

    def test_test_scripts_exist(self, project_root: Path):
        """Verify test management scripts exist."""
        scripts = [
            "scripts/run_tests.py",
            "scripts/compare_test_results.py",
            "scripts/archive_test_results.py",
            "scripts/generate_coverage_report.py",
        ]

        for script in scripts:
            script_path = project_root / script
            assert script_path.exists(), f"Script missing: {script}"

    def test_scripts_are_valid_python(self, project_root: Path):
        """Verify test scripts are valid Python."""
        import ast

        scripts = [
            "scripts/run_tests.py",
            "scripts/compare_test_results.py",
        ]

        for script in scripts:
            script_path = project_root / script
            if script_path.exists():
                content = script_path.read_text()
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    pytest.fail(f"Script {script} has syntax error: {e}")
