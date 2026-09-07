"""Tests for `.aidoc/profile.yaml` runtime consumption (HERMES-REVIEW-001 PR-ADAPT)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.profile import (  # noqa: E402
    REVIEW_MODE_ALIAS,
    ProjectProfile,
    load_project_profile,
)


def _write_profile(project_root: Path, body: str) -> None:
    aidoc = project_root / ".aidoc"
    aidoc.mkdir(parents=True, exist_ok=True)
    (aidoc / "profile.yaml").write_text(body, encoding="utf-8")


def test_missing_file_returns_all_defaults(tmp_path: Path) -> None:
    profile = load_project_profile(tmp_path)
    assert profile == ProjectProfile()
    assert profile.source_path is None
    assert profile.active_layers is None
    assert profile.review_mode == "team"
    assert profile.review_mode_declared is False
    assert profile.quality_loop_max_iterations == 3
    assert profile.hermes_review_mode == "saga_parallel"


def test_full_valid_profile_parsed(tmp_path: Path) -> None:
    _write_profile(
        tmp_path,
        """
active_layers: [BRD, PRD, EARS, SPEC, TDD, IPLAN]
section_toggles:
  BDD:
    edge_cases: false
    security: true
audit_threshold:
  BRD: 92
glossary:
  URL: Uniform Resource Locator
  SLA: Service Level Agreement
review_mode: single_pass
quality_loop_max_iterations: 5
""",
    )
    profile = load_project_profile(tmp_path)
    assert profile.active_layers == ("BRD", "PRD", "EARS", "SPEC", "TDD", "IPLAN")
    assert profile.section_toggles == {"BDD": {"edge_cases": False, "security": True}}
    assert profile.audit_threshold == {"BRD": 92}
    assert profile.glossary == {"URL": "Uniform Resource Locator", "SLA": "Service Level Agreement"}
    assert profile.review_mode == "single_pass"
    assert profile.review_mode_declared is True
    assert profile.hermes_review_mode == "prompt_only"
    assert profile.quality_loop_max_iterations == 5
    assert profile.source_path == tmp_path / ".aidoc" / "profile.yaml"


def test_malformed_yaml_falls_back_to_defaults(tmp_path: Path) -> None:
    _write_profile(tmp_path, "active_layers: [BRD\n  : : broken")
    profile = load_project_profile(tmp_path)
    assert profile.review_mode == "team"
    assert profile.review_mode_declared is False


def test_non_mapping_document_falls_back(tmp_path: Path) -> None:
    _write_profile(tmp_path, "- just\n- a\n- list")
    assert load_project_profile(tmp_path) == ProjectProfile()


def test_non_utf8_file_falls_back_not_crashes(tmp_path: Path) -> None:
    # A profile saved as latin-1 with an accented byte raises UnicodeDecodeError
    # inside read_text — the loader must fall back gracefully, not crash the tool.
    aidoc = tmp_path / ".aidoc"
    aidoc.mkdir(parents=True, exist_ok=True)
    (aidoc / "profile.yaml").write_bytes(b"glossary:\n  caf\xe9: coffee\n")  # 0xe9 = é in latin-1
    assert load_project_profile(tmp_path) == ProjectProfile()


def test_invalid_review_mode_uses_default_and_not_declared(tmp_path: Path) -> None:
    _write_profile(tmp_path, "review_mode: turbo")
    profile = load_project_profile(tmp_path)
    assert profile.review_mode == "team"
    assert profile.review_mode_declared is False  # invalid → not honored as a declaration


def test_out_of_range_quality_loop_falls_back(tmp_path: Path) -> None:
    _write_profile(tmp_path, "quality_loop_max_iterations: 42")
    assert load_project_profile(tmp_path).quality_loop_max_iterations == 3


def test_bool_quality_loop_rejected(tmp_path: Path) -> None:
    _write_profile(tmp_path, "quality_loop_max_iterations: true")
    assert load_project_profile(tmp_path).quality_loop_max_iterations == 3


def test_malformed_active_layers_treated_as_all_active(tmp_path: Path) -> None:
    _write_profile(tmp_path, "active_layers: not-a-list")
    assert load_project_profile(tmp_path).active_layers is None


def test_review_mode_alias_map() -> None:
    assert REVIEW_MODE_ALIAS == {"team": "saga_parallel", "single_pass": "prompt_only"}


def test_partial_profile_defaults_per_knob(tmp_path: Path) -> None:
    # only glossary declared; every other knob independently defaults
    _write_profile(tmp_path, "glossary:\n  API: Application Programming Interface")
    profile = load_project_profile(tmp_path)
    assert profile.glossary == {"API": "Application Programming Interface"}
    assert profile.review_mode == "team"
    assert profile.review_mode_declared is False
    assert profile.quality_loop_max_iterations == 3
    assert profile.active_layers is None
