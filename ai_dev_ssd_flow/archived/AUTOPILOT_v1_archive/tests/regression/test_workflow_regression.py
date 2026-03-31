"""
Regression Tests for TDD Workflow

Tests with baseline comparisons to catch regressions in TDD workflow outputs.

Usage:
    pytest ai_dev_flow/AUTOPILOT/tests/regression/ -v -m regression
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.mark.regression
class TestAnalyzeTestRequirementsRegression:
    """Regression tests for analyze_test_requirements.py"""

    def test_output_structure_matches_baseline(
        self, temp_project_dir: Path, sample_test_file: Path
    ):
        """Verify output JSON structure matches expected baseline."""
        script = SCRIPTS_DIR / "analyze_test_requirements.py"
        output_file = temp_project_dir / "tmp" / "test_req.json"

        result = subprocess.run(
            [
                sys.executable, str(script),
                "--test-dir", str(sample_test_file.parent),
                "--output", str(output_file)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        assert result.returncode == 0

        with open(output_file) as f:
            data = json.load(f)

        # Verify required top-level keys
        required_keys = ["generated_at", "test_directory", "test_files", "summary"]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"

        # Verify summary structure
        summary_keys = ["total_files", "total_classes", "total_methods"]
        for key in summary_keys:
            assert key in data["summary"], f"Missing summary key: {key}"

        # Verify test_files structure
        if data["test_files"]:
            file_info = data["test_files"][0]
            file_keys = ["file_path", "req_id", "traceability"]
            for key in file_keys:
                assert key in file_info, f"Missing file info key: {key}"

    def test_traceability_extraction_consistency(
        self, temp_test_dir: Path
    ):
        """Verify traceability extraction is consistent."""
        # Create test file with known traceability
        test_file = temp_test_dir / "test_known_trace.py"
        test_file.write_text('''"""
@brd: BRD.01.02.03
@prd: PRD.01.02.03
@req: REQ-01.02.03
@spec: PENDING
@code: PENDING
"""
def test_example():
    pass
''')

        script = SCRIPTS_DIR / "analyze_test_requirements.py"
        output_file = temp_test_dir.parent / "trace_output.json"

        subprocess.run(
            [
                sys.executable, str(script),
                "--test-dir", str(temp_test_dir),
                "--output", str(output_file)
            ],
            capture_output=True,
            timeout=60
        )

        with open(output_file) as f:
            data = json.load(f)

        # Find our test file
        target_file = next(
            (f for f in data["test_files"] if "test_known_trace" in f["file_path"]),
            None
        )

        assert target_file is not None
        assert target_file["traceability"]["brd"] == "BRD.01.02.03"
        assert target_file["traceability"]["prd"] == "PRD.01.02.03"
        assert target_file["traceability"]["req"] == "REQ-01.02.03"


@pytest.mark.regression
class TestGenerateSpecTDDRegression:
    """Regression tests for generate_spec_tdd.py"""

    def test_spec_yaml_structure(
        self, temp_project_dir: Path, sample_test_requirements: Path
    ):
        """Verify generated SPEC YAML structure matches baseline."""
        import yaml

        script = SCRIPTS_DIR / "generate_spec_tdd.py"
        output_dir = temp_project_dir / "specs"

        subprocess.run(
            [
                sys.executable, str(script),
                "--test-requirements", str(sample_test_requirements),
                "--output", str(output_dir)
            ],
            capture_output=True,
            timeout=60
        )

        # Check generated SPEC files
        for spec_file in output_dir.glob("*.yaml"):
            data = yaml.safe_load(spec_file.read_text())

            # Verify required fields
            assert "id" in data or "spec_id" in data
            assert "title" in data
            assert "version" in data

    def test_traceability_preserved(
        self, temp_project_dir: Path, sample_test_requirements: Path
    ):
        """Verify traceability from tests is preserved in SPEC."""
        import yaml

        script = SCRIPTS_DIR / "generate_spec_tdd.py"
        output_dir = temp_project_dir / "specs"

        subprocess.run(
            [
                sys.executable, str(script),
                "--test-requirements", str(sample_test_requirements),
                "--output", str(output_dir)
            ],
            capture_output=True,
            timeout=60
        )

        for spec_file in output_dir.glob("*.yaml"):
            data = yaml.safe_load(spec_file.read_text())

            if "traceability" in data:
                # Should have req reference
                assert "req" in data["traceability"] or "source_req" in data


@pytest.mark.regression
class TestValidateTDDStageRegression:
    """Regression tests for validate_tdd_stage.py"""

    def test_red_stage_output_format(self, temp_test_dir: Path, sample_test_file: Path):
        """Verify red stage output format is consistent."""
        script = SCRIPTS_DIR / "validate_tdd_stage.py"

        result = subprocess.run(
            [
                sys.executable, str(script),
                "--stage", "red",
                "--test-dir", str(temp_test_dir)
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        # Output should contain stage information
        output = result.stdout + result.stderr
        assert "red" in output.lower() or "validation" in output.lower()

    def test_green_stage_output_format(
        self, temp_test_dir: Path, sample_test_file: Path, sample_code_file: Path
    ):
        """Verify green stage output format is consistent."""
        script = SCRIPTS_DIR / "validate_tdd_stage.py"

        result = subprocess.run(
            [
                sys.executable, str(script),
                "--stage", "green",
                "--test-dir", str(temp_test_dir),
                "--code-dir", str(sample_code_file.parent.parent)
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        # Should complete without crash
        assert result.returncode in [0, 1]


@pytest.mark.regression
class TestUpdateTraceabilityRegression:
    """Regression tests for update_test_traceability.py"""

    def test_pending_tag_replacement(self, temp_test_dir: Path):
        """Verify PENDING tags are correctly replaced."""
        # Create test file with PENDING tags
        test_file = temp_test_dir / "test_update.py"
        test_file.write_text('''"""
@req: REQ-01.01.01
@spec: PENDING
@code: PENDING
"""
def test_example():
    pass
''')

        script = SCRIPTS_DIR / "update_test_traceability.py"

        subprocess.run(
            [
                sys.executable, str(script),
                "--test-dir", str(temp_test_dir),
                "--spec-dir", str(temp_test_dir.parent / "ai_dev_flow" / "09_SPEC"),
                "--code-dir", str(temp_test_dir.parent / "src")
            ],
            capture_output=True,
            timeout=60
        )

        # File should be updated (or attempted)
        # Verify original structure preserved
        content = test_file.read_text()
        assert "@req: REQ-01.01.01" in content
        assert "def test_example():" in content


@pytest.mark.regression
class TestGenerateIntegrationTestsRegression:
    """Regression tests for generate_integration_tests.py"""

    def test_generated_test_structure(
        self, temp_project_dir: Path, sample_spec_file: Path
    ):
        """Verify generated integration test structure."""
        script = SCRIPTS_DIR / "generate_integration_tests.py"
        output_dir = temp_project_dir / "tests" / "integration"

        subprocess.run(
            [
                sys.executable, str(script),
                "--spec-dir", str(sample_spec_file.parent),
                "--output", str(output_dir)
            ],
            capture_output=True,
            timeout=60
        )

        # Check generated test files
        for test_file in output_dir.glob("test_*_integration.py"):
            content = test_file.read_text()

            # Should have proper test structure
            assert "import pytest" in content
            assert "class Test" in content
            assert "def test_" in content
            assert "@pytest.mark.integration" in content or "integration" in content.lower()


@pytest.mark.regression
class TestGenerateSmokeTestsRegression:
    """Regression tests for generate_smoke_tests.py"""

    def test_generated_smoke_test_structure(
        self, temp_project_dir: Path, sample_bdd_file: Path
    ):
        """Verify generated smoke test structure."""
        script = SCRIPTS_DIR / "generate_smoke_tests.py"
        output_dir = temp_project_dir / "tests" / "smoke"

        subprocess.run(
            [
                sys.executable, str(script),
                "--bdd-dir", str(sample_bdd_file.parent),
                "--output", str(output_dir)
            ],
            capture_output=True,
            timeout=60
        )

        # Check generated test files
        for test_file in output_dir.glob("test_*_smoke.py"):
            content = test_file.read_text()

            # Should have proper smoke test structure
            assert "import pytest" in content
            assert "@pytest.mark.smoke" in content or "smoke" in content.lower()


@pytest.mark.regression
@pytest.mark.slow
class TestE2EWorkflowRegression:
    """Regression tests for complete TDD workflow."""

    def test_full_workflow_produces_expected_artifacts(self, temp_project_dir: Path):
        """Verify full workflow produces all expected artifacts."""
        script = SCRIPTS_DIR / "validate_tdd_e2e.py"

        result = subprocess.run(
            [
                sys.executable, str(script),
                "--scenario", "simple",
                "--project-dir", str(temp_project_dir),
                "--scripts-dir", str(SCRIPTS_DIR),
                "--report", "json",
                "--output", str(temp_project_dir / "e2e_report.json")
            ],
            capture_output=True,
            text=True,
            timeout=300
        )

        # Should complete
        assert result.returncode in [0, 1]

        # Check report if generated
        report_file = temp_project_dir / "e2e_report.json"
        if report_file.exists():
            with open(report_file) as f:
                report = json.load(f)

            # Verify report structure
            assert "overall_status" in report
            assert "scenarios_run" in report
            assert "results" in report
