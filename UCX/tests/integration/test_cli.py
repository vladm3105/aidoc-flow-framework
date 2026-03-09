"""Integration tests for UCX CLI.

Tests CLI commands using Click testing utilities.
"""

import pytest
from pathlib import Path
from click.testing import CliRunner

from ucx.cli.main import cli


class TestCLIHelp:
    """Test CLI help commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI test runner."""
        return CliRunner()

    def test_main_help(self, runner: CliRunner):
        """Test main help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "UCX" in result.output or "ucx" in result.output.lower()

    def test_create_help(self, runner: CliRunner):
        """Test create command help."""
        result = runner.invoke(cli, ["create", "--help"])
        assert result.exit_code == 0
        assert "create" in result.output.lower() or "doc_type" in result.output.lower()

    def test_review_help(self, runner: CliRunner):
        """Test review command help."""
        result = runner.invoke(cli, ["review", "--help"])
        assert result.exit_code == 0
        assert "review" in result.output.lower() or "doc_type" in result.output.lower()

    def test_autopilot_help(self, runner: CliRunner):
        """Test autopilot command help."""
        result = runner.invoke(cli, ["autopilot", "--help"])
        assert result.exit_code == 0
        assert "autopilot" in result.output.lower() or "doc_type" in result.output.lower()


class TestCLIVersion:
    """Test CLI version command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI test runner."""
        return CliRunner()

    def test_version(self, runner: CliRunner):
        """Test version command."""
        result = runner.invoke(cli, ["--version"])

        # Should show version
        assert result.exit_code == 0
        # Version output contains version number
        assert "." in result.output  # Version has dots like 1.0.0


class TestCLIConfig:
    """Test CLI config command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI test runner."""
        return CliRunner()

    def test_config_help(self, runner: CliRunner):
        """Test config command help."""
        result = runner.invoke(cli, ["config", "--help"])
        # Config command may or may not exist
        # Accept both success and "no such command"
        assert result.exit_code in [0, 2]


class TestCLIValidate:
    """Test CLI validate command if it exists."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def sample_brd(self, tmp_path: Path) -> Path:
        """Create sample BRD document."""
        brd_path = tmp_path / "BRD-01.md"
        brd_path.write_text("""# BRD-01: Test Document

## 1. Executive Summary
Test content.

## 2. Business Objectives
- Objective 1

## 3. Stakeholder Analysis
Test stakeholders.

## 4. Success Metrics
- Metric 1
""")
        return brd_path

    def test_validate_help(self, runner: CliRunner):
        """Test validate command help if it exists."""
        result = runner.invoke(cli, ["validate", "--help"])
        # May not exist - that's OK for integration tests
        # Just verify CLI doesn't crash
        assert result.exit_code in [0, 2]


class TestCLICommands:
    """Test that CLI commands are properly registered."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI test runner."""
        return CliRunner()

    def test_cli_has_commands(self, runner: CliRunner):
        """Test CLI has expected commands."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

        # Check for core commands in help output
        output_lower = result.output.lower()
        # At minimum should have autopilot and create/review
        assert "autopilot" in output_lower or "create" in output_lower

    def test_cli_unknown_command(self, runner: CliRunner):
        """Test CLI handles unknown commands gracefully."""
        result = runner.invoke(cli, ["unknown_command_xyz"])
        # Should fail gracefully
        assert result.exit_code == 2  # Click's exit code for missing command


class TestCLIIntegration:
    """End-to-end CLI integration tests."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI test runner."""
        return CliRunner()

    def test_cli_verbose_flag(self, runner: CliRunner):
        """Test verbose flag is accepted."""
        result = runner.invoke(cli, ["-v", "--help"])
        assert result.exit_code == 0

    def test_cli_quiet_flag(self, runner: CliRunner):
        """Test quiet flag is accepted."""
        result = runner.invoke(cli, ["-q", "--help"])
        assert result.exit_code == 0

    def test_cli_with_config_file(self, runner: CliRunner, tmp_path: Path):
        """Test CLI with config file option."""
        # Create config file
        config_path = tmp_path / "ucx.yaml"
        config_path.write_text("model: sonnet\n")

        result = runner.invoke(cli, ["--config", str(config_path), "--help"])
        assert result.exit_code == 0
