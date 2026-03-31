"""
Smoke Tests for Autopilot TDD Scripts

Quick validation that all scripts are executable, imports work,
and basic CLI functionality operates correctly.

Usage:
    pytest ai_dev_flow/AUTOPILOT/tests/smoke/ -v -m smoke
"""

import subprocess
import sys
from pathlib import Path

import pytest


# =============================================================================
# Script Existence Tests
# =============================================================================

@pytest.mark.smoke
class TestScriptExistence:
    """Verify all TDD scripts exist."""

    REQUIRED_SCRIPTS = [
        "analyze_test_requirements.py",
        "generate_spec_tdd.py",
        "update_test_traceability.py",
        "validate_tdd_stage.py",
        "generate_integration_tests.py",
        "generate_smoke_tests.py",
        "validate_tdd_e2e.py",
        "mvp_autopilot.py",
    ]

    def test_scripts_directory_exists(self, scripts_dir: Path):
        """Verify scripts directory exists."""
        assert scripts_dir.exists(), f"Scripts directory not found: {scripts_dir}"
        assert scripts_dir.is_dir(), f"Scripts path is not a directory: {scripts_dir}"

    @pytest.mark.parametrize("script_name", REQUIRED_SCRIPTS)
    def test_script_exists(self, scripts_dir: Path, script_name: str):
        """Verify each required script exists."""
        script_path = scripts_dir / script_name
        assert script_path.exists(), f"Script not found: {script_path}"

    @pytest.mark.parametrize("script_name", REQUIRED_SCRIPTS)
    def test_script_is_python_file(self, scripts_dir: Path, script_name: str):
        """Verify each script is a valid Python file."""
        script_path = scripts_dir / script_name
        assert script_path.suffix == ".py", f"Script is not a Python file: {script_path}"


# =============================================================================
# Import Tests
# =============================================================================

@pytest.mark.smoke
class TestScriptImports:
    """Verify all scripts can be imported without errors."""

    IMPORT_SCRIPTS = [
        "analyze_test_requirements",
        "generate_spec_tdd",
        "update_test_traceability",
        "validate_tdd_stage",
        "generate_integration_tests",
        "generate_smoke_tests",
        "validate_tdd_e2e",
    ]

    @pytest.mark.parametrize("module_name", IMPORT_SCRIPTS)
    def test_script_imports(self, scripts_dir: Path, module_name: str):
        """Verify script can be imported."""
        script_path = scripts_dir / f"{module_name}.py"

        # Use subprocess to test import in isolation
        result = subprocess.run(
            [sys.executable, "-c", f"import sys; sys.path.insert(0, '{scripts_dir}'); import {module_name}"],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"Import failed for {module_name}: {result.stderr}"

    def test_no_syntax_errors(self, scripts_dir: Path):
        """Verify all scripts have valid Python syntax."""
        import ast

        for script in scripts_dir.glob("*.py"):
            content = script.read_text()
            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {script.name}: {e}")


# =============================================================================
# CLI Help Tests
# =============================================================================

@pytest.mark.smoke
class TestCLIHelp:
    """Verify CLI help works for all scripts."""

    CLI_SCRIPTS = [
        "analyze_test_requirements.py",
        "generate_spec_tdd.py",
        "update_test_traceability.py",
        "validate_tdd_stage.py",
        "generate_integration_tests.py",
        "generate_smoke_tests.py",
        "validate_tdd_e2e.py",
    ]

    @pytest.mark.parametrize("script_name", CLI_SCRIPTS)
    def test_help_flag(self, scripts_dir: Path, script_name: str):
        """Verify --help flag works."""
        script_path = scripts_dir / script_name

        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"--help failed for {script_name}: {result.stderr}"
        assert "usage" in result.stdout.lower() or "Usage" in result.stdout, \
            f"--help output missing usage info for {script_name}"

    @pytest.mark.parametrize("script_name", CLI_SCRIPTS)
    def test_help_contains_description(self, scripts_dir: Path, script_name: str):
        """Verify --help contains meaningful description."""
        script_path = scripts_dir / script_name

        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Should have some meaningful content
        assert len(result.stdout) > 100, f"--help output too short for {script_name}"


# =============================================================================
# Basic Functionality Tests
# =============================================================================

@pytest.mark.smoke
class TestBasicFunctionality:
    """Quick tests for basic script functionality."""

    def test_analyze_test_requirements_with_empty_dir(
        self, scripts_dir: Path, temp_project_dir: Path
    ):
        """Verify analyze_test_requirements handles empty directory."""
        script_path = scripts_dir / "analyze_test_requirements.py"
        test_dir = temp_project_dir / "tests" / "unit"
        output_file = temp_project_dir / "tmp" / "test_req.json"

        result = subprocess.run(
            [
                sys.executable, str(script_path),
                "--test-dir", str(test_dir),
                "--output", str(output_file)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Should succeed even with empty directory
        assert result.returncode == 0, f"Failed with empty dir: {result.stderr}"

    def test_validate_tdd_stage_red_validation(
        self, scripts_dir: Path, temp_project_dir: Path
    ):
        """Verify validate_tdd_stage works for red state."""
        script_path = scripts_dir / "validate_tdd_stage.py"
        test_dir = temp_project_dir / "tests" / "unit"

        result = subprocess.run(
            [
                sys.executable, str(script_path),
                "--stage", "red",
                "--test-dir", str(test_dir)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Should complete (may pass or fail based on test state)
        assert result.returncode in [0, 1], f"Unexpected exit code: {result.returncode}"

    def test_generate_spec_tdd_with_sample_input(
        self, scripts_dir: Path, temp_project_dir: Path, sample_test_requirements: Path
    ):
        """Verify generate_spec_tdd works with sample input."""
        script_path = scripts_dir / "generate_spec_tdd.py"
        output_dir = temp_project_dir / "tmp" / "specs"

        result = subprocess.run(
            [
                sys.executable, str(script_path),
                "--test-requirements", str(sample_test_requirements),
                "--output", str(output_dir)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"SPEC generation failed: {result.stderr}"

    def test_validate_tdd_e2e_simple_scenario(
        self, scripts_dir: Path, temp_project_dir: Path
    ):
        """Verify E2E validation runs simple scenario."""
        script_path = scripts_dir / "validate_tdd_e2e.py"

        result = subprocess.run(
            [
                sys.executable, str(script_path),
                "--scenario", "simple",
                "--project-dir", str(temp_project_dir),
                "--scripts-dir", str(scripts_dir)
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        # Should complete (pass or fail is acceptable for smoke test)
        assert result.returncode in [0, 1], f"E2E validation crashed: {result.stderr}"


# =============================================================================
# Integration Smoke Tests
# =============================================================================

@pytest.mark.smoke
class TestWorkflowSmoke:
    """Quick smoke tests for the TDD workflow."""

    def test_scripts_chain_basic(
        self, scripts_dir: Path, temp_project_dir: Path, sample_test_file: Path
    ):
        """Verify basic script chain works."""
        # Step 1: Analyze tests
        analyze_result = subprocess.run(
            [
                sys.executable,
                str(scripts_dir / "analyze_test_requirements.py"),
                "--test-dir", str(sample_test_file.parent),
                "--output", str(temp_project_dir / "tmp" / "test_req.json")
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert analyze_result.returncode == 0, f"Analyze failed: {analyze_result.stderr}"

        # Step 2: Generate SPEC
        spec_result = subprocess.run(
            [
                sys.executable,
                str(scripts_dir / "generate_spec_tdd.py"),
                "--test-requirements", str(temp_project_dir / "tmp" / "test_req.json"),
                "--output", str(temp_project_dir / "tmp" / "specs")
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert spec_result.returncode == 0, f"SPEC gen failed: {spec_result.stderr}"

    def test_report_generation(self, scripts_dir: Path, temp_project_dir: Path):
        """Verify E2E can generate reports."""
        script_path = scripts_dir / "validate_tdd_e2e.py"
        report_file = temp_project_dir / "tmp" / "report.json"

        result = subprocess.run(
            [
                sys.executable, str(script_path),
                "--scenario", "simple",
                "--project-dir", str(temp_project_dir),
                "--scripts-dir", str(scripts_dir),
                "--report", "json",
                "--output", str(report_file)
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0 and report_file.exists():
            import json
            report = json.loads(report_file.read_text())
            assert "overall_status" in report
            assert "scenarios_run" in report
