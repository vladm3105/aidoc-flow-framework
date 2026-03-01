"""Smoke tests for BRD hook wrapper scripts."""

import subprocess
from pathlib import Path

import pytest


@pytest.mark.stest
def test_brd_standardized_hook_runs_from_arbitrary_cwd(tmp_path: Path, project_root: Path):
    """BRD standardized hook should execute from any working directory."""
    hook_path = project_root / "ai_dev_ssd_flow/01_BRD/scripts/brd_standardized_element_codes_hook.sh"

    brd_root = tmp_path / "01_BRD"
    brd_root.mkdir(parents=True, exist_ok=True)
    (brd_root / "BRD-99_smoke.md").write_text("# BRD-99: Smoke\n\n## 1. Intro\n")

    result = subprocess.run(
        ["bash", str(hook_path), str(brd_root)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "[PASS]" in result.stdout


@pytest.mark.stest
def test_claude_brd_skill_audit_hook_disabled_by_default(tmp_path: Path, project_root: Path):
    """Claude BRD audit hook should skip cleanly when not explicitly enabled."""
    hook_path = project_root / "ai_dev_ssd_flow/01_BRD/scripts/claude_brd_skill_audit_hook.sh"

    result = subprocess.run(
        ["bash", str(hook_path), "ai_dev_ssd_flow/01_BRD/does_not_matter.md"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "[SKIP]" in result.stdout


@pytest.mark.stest
def test_brd_wrapper_help(project_root: Path):
    """BRD wrapper should provide help output."""
    wrapper_path = project_root / "ai_dev_ssd_flow/01_BRD/scripts/validate_brd_wrapper.sh"

    result = subprocess.run(
        ["bash", str(wrapper_path), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "BRD validation wrapper" in result.stdout


@pytest.mark.stest
def test_brd_wrapper_core_only_on_empty_root(tmp_path: Path, project_root: Path):
    """BRD wrapper should run core-only mode on empty BRD root without crashing."""
    wrapper_path = project_root / "ai_dev_ssd_flow/01_BRD/scripts/validate_brd_wrapper.sh"

    brd_root = tmp_path / "01_BRD"
    brd_root.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        ["bash", str(wrapper_path), str(brd_root), "--skip-advisory"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "[PASS]" in result.stdout
