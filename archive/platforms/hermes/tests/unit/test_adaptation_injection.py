"""Tests for adaptation-knob injection into the creation prompt + ProjectContext
profile wiring (HERMES-REVIEW-001 PR-ADAPT A1)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.profile import ProjectProfile  # noqa: E402
from mcp_server.project_context import ProjectContext  # noqa: E402
from mcp_server.prompts.context_builder import (  # noqa: E402
    _format_adaptation_profile_block,
    _normalize_layer_key,
)


def test_normalize_layer_key() -> None:
    assert _normalize_layer_key("04_BDD") == "BDD"
    assert _normalize_layer_key("bdd") == "BDD"
    assert _normalize_layer_key("BDD") == "BDD"


def test_no_profile_injects_nothing() -> None:
    assert _format_adaptation_profile_block(None, "04_BDD") == ""


def test_empty_profile_injects_nothing() -> None:
    # A default profile (unprofiled project) must be byte-identical to before.
    assert _format_adaptation_profile_block(ProjectProfile(), "04_BDD") == ""


def test_glossary_injected() -> None:
    profile = ProjectProfile(
        glossary={"URL": "Uniform Resource Locator", "API": "App Prog Interface"}
    )
    block = _format_adaptation_profile_block(profile, "04_BDD")
    assert "## Project Adaptation Profile" in block
    assert "### Glossary" in block
    assert "- **API**: App Prog Interface" in block
    assert "- **URL**: Uniform Resource Locator" in block


def test_section_toggles_layer_scoped_and_normalized() -> None:
    # toggles keyed as "BDD"; layer passed as "04_BDD" must still resolve.
    profile = ProjectProfile(
        section_toggles={
            "BDD": {"edge_cases": False, "security": True},
            "ADR": {"alt_options": False},
        }
    )
    block = _format_adaptation_profile_block(profile, "04_BDD")
    assert "Optional sections DISABLED for this artifact (do not author): edge_cases" in block
    assert "Optional sections ENABLED for this artifact: security" in block
    # a different layer's toggles (ADR) must NOT leak into the BDD block
    assert "alt_options" not in block


def test_other_layer_toggles_do_not_leak() -> None:
    profile = ProjectProfile(section_toggles={"ADR": {"alt_options": False}})
    assert _format_adaptation_profile_block(profile, "04_BDD") == ""


def test_active_layers_injected() -> None:
    profile = ProjectProfile(active_layers=("BRD", "PRD", "EARS"))
    block = _format_adaptation_profile_block(profile, "01_BRD")
    assert "Active layers for this project: BRD, PRD, EARS" in block


def test_project_context_loads_profile(tmp_path: Path) -> None:
    aidoc = tmp_path / ".aidoc"
    aidoc.mkdir(parents=True)
    (aidoc / "profile.yaml").write_text("review_mode: single_pass\n", encoding="utf-8")
    ctx = ProjectContext.resolve(str(tmp_path))
    assert ctx is not None
    assert ctx.profile.review_mode == "single_pass"
    assert ctx.profile.review_mode_declared is True
    assert ctx.profile.hermes_review_mode == "prompt_only"


def test_project_context_default_profile_when_absent(tmp_path: Path) -> None:
    ctx = ProjectContext.resolve(str(tmp_path))
    assert ctx is not None
    assert ctx.profile == ProjectProfile()
