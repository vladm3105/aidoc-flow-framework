from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.skills import PersonaMappingError  # noqa: E402
from mcp_server.skills.persona_manager import (  # noqa: E402
    check_persona_mapping_health,
    diff_persona_mappings,
    set_persona_mapping,
    show_persona_mappings,
)
from mcp_server.skills.project_ucx_loader import _invalidate_persona_mapping_cache  # noqa: E402

# Reuse helpers from test_project_ucx_loader.
from test_project_ucx_loader import REQUIRED_RELATIVE_PATHS  # noqa: E402

_FULL_MAPPINGS = """\
# UCX Persona Mappings v1.0
# Test header comment

version: "1.0"

creation:
  brd:
    personas: [architect, auditor]
    mode: sequential
  prd:
    personas: [architect]
    mode: sequential

review:
  brd:
    personas: [auditor, architect]
    mode: sequential

remediation:
  _default:
    personas: [architect, auditor]
    mode: sequential
"""


def _create_ucx_tree(project_root: Path, mappings: str = _FULL_MAPPINGS) -> None:
    for relative in REQUIRED_RELATIVE_PATHS:
        (project_root / relative).mkdir(parents=True, exist_ok=True)
    (project_root / "UCX/skills/personas/architect.md").write_text(
        "Architect stub", encoding="utf-8"
    )
    (project_root / "UCX/skills/personas/auditor.md").write_text("Auditor stub", encoding="utf-8")
    mappings_path = project_root / "UCX/skills/persona_mappings.yaml"
    mappings_path.write_text(mappings, encoding="utf-8")
    _invalidate_persona_mapping_cache(project_root)


# ── show ──────────────────────────────────────────────────────────────


def test_show_returns_all_phases(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    result = show_persona_mappings(project_root=tmp_path)
    assert "creation" in result["mappings"]
    assert "review" in result["mappings"]
    assert "remediation" in result["mappings"]


def test_show_filters_by_phase(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    result = show_persona_mappings(project_root=tmp_path, phase="creation")
    assert "creation" in result["mappings"]
    assert "review" not in result["mappings"]


def test_show_filters_by_doc_type(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    result = show_persona_mappings(project_root=tmp_path, phase="creation", doc_type="brd")
    assert "brd" in result["mappings"]["creation"]
    assert "prd" not in result["mappings"]["creation"]


# ── set ───────────────────────────────────────────────────────────────


def test_set_updates_existing_entry(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    result = set_persona_mapping(
        project_root=tmp_path,
        phase="creation",
        doc_type="brd",
        personas=["auditor"],
    )
    assert result["updated"]["personas"] == ["auditor"]
    assert result["previous_personas"] == ["architect", "auditor"]
    # Verify persisted.
    reloaded = show_persona_mappings(project_root=tmp_path, phase="creation", doc_type="brd")
    assert reloaded["mappings"]["creation"]["brd"]["personas"] == ["auditor"]


def test_set_creates_new_entry(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    result = set_persona_mapping(
        project_root=tmp_path,
        phase="creation",
        doc_type="ears",
        personas=["architect"],
    )
    assert result["previous_personas"] == []
    reloaded = show_persona_mappings(project_root=tmp_path, phase="creation", doc_type="ears")
    assert reloaded["mappings"]["creation"]["ears"]["personas"] == ["architect"]


def test_set_rejects_invalid_persona(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    try:
        set_persona_mapping(
            project_root=tmp_path,
            phase="creation",
            doc_type="brd",
            personas=["nonexistent"],
        )
        assert False, "Expected PersonaMappingError"
    except PersonaMappingError:
        pass


def test_set_rejects_empty_list(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    try:
        set_persona_mapping(
            project_root=tmp_path,
            phase="creation",
            doc_type="brd",
            personas=[],
        )
        assert False, "Expected PersonaMappingError"
    except PersonaMappingError:
        pass


def test_set_rejects_invalid_phase(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    try:
        set_persona_mapping(
            project_root=tmp_path,
            phase="unknown",
            doc_type="brd",
            personas=["architect"],
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_set_supports_default_key(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    set_persona_mapping(
        project_root=tmp_path,
        phase="remediation",
        doc_type="_default",
        personas=["architect"],
    )
    reloaded = show_persona_mappings(
        project_root=tmp_path, phase="remediation", doc_type="_default"
    )
    assert reloaded["mappings"]["remediation"]["_default"]["personas"] == ["architect"]


def test_set_invalidates_cache(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    # Load once to populate cache.
    show_persona_mappings(project_root=tmp_path)
    # Set changes the file.
    set_persona_mapping(
        project_root=tmp_path,
        phase="creation",
        doc_type="brd",
        personas=["auditor"],
    )
    # Next load should see the change (cache was invalidated).
    from mcp_server.skills.project_ucx_loader import load_persona_mapping

    mapping = load_persona_mapping(project_root=tmp_path)
    assert mapping["creation"]["brd"]["personas"] == ["auditor"]


def test_set_preserves_yaml_header(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    set_persona_mapping(
        project_root=tmp_path,
        phase="creation",
        doc_type="brd",
        personas=["auditor"],
    )
    raw = (tmp_path / "UCX/skills/persona_mappings.yaml").read_text(encoding="utf-8")
    assert raw.startswith("# UCX Persona Mappings v1.0")


# ── diff ──────────────────────────────────────────────────────────────


def test_diff_detects_changes(tmp_path: Path) -> None:
    _create_ucx_tree(tmp_path)
    # Project mapping differs from framework default, so there should be changes.
    result = diff_persona_mappings(project_root=tmp_path)
    # The test fixture has fewer doctypes than framework default.
    assert result["summary"]["changed"] > 0 or result["summary"]["removed"] > 0


def test_diff_identical_returns_no_changes(tmp_path: Path) -> None:
    # Use a framework-identical mapping.
    framework_path = Path(__file__).resolve().parents[2] / "skills" / "persona_mappings.yaml"
    if not framework_path.exists():
        return  # Skip if running outside framework repo.
    framework_text = framework_path.read_text(encoding="utf-8")
    _create_ucx_tree(tmp_path, mappings=framework_text)
    # Also need all referenced persona .md files to exist for validation.
    import yaml

    data = yaml.safe_load(framework_text)
    all_personas: set[str] = set()
    for phase_map in [
        data.get("creation", {}),
        data.get("review", {}),
        data.get("remediation", {}),
    ]:
        if isinstance(phase_map, dict):
            for config in phase_map.values():
                if isinstance(config, dict):
                    all_personas.update(config.get("personas", []))
    for name in all_personas:
        p = tmp_path / f"UCX/skills/personas/{name}.md"
        if not p.exists():
            p.write_text(f"{name} stub", encoding="utf-8")
    _invalidate_persona_mapping_cache(tmp_path)

    result = diff_persona_mappings(project_root=tmp_path)
    assert result["summary"]["changed"] == 0
    assert result["summary"]["added"] == 0
    assert result["summary"]["removed"] == 0


# ── health ────────────────────────────────────────────────────────────


def test_health_detects_missing_persona_files(tmp_path: Path) -> None:
    # Create mapping that references a persona without a .md file.
    mappings = 'version: "1.0"\ncreation:\n  brd:\n    personas: [architect, missing_persona]\n    mode: sequential\n'
    _create_ucx_tree(tmp_path, mappings=mappings)
    result = check_persona_mapping_health(project_root=tmp_path)
    assert result["status"] == "error"
    assert "missing_persona" in result["missing_persona_files"]


def test_health_detects_missing_doctypes(tmp_path: Path) -> None:
    # The test fixture has fewer doctypes than framework default.
    _create_ucx_tree(tmp_path)
    result = check_persona_mapping_health(project_root=tmp_path)
    # Framework default has 10 doctypes per phase; our fixture has 2 in creation.
    assert len(result["missing_doctypes"]) > 0
    assert result["status"] in ("warning", "error")
