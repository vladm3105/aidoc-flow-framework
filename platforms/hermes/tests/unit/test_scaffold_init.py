from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.skills.scaffold import scaffold_project_ucx  # noqa: E402


def _create_canonical_scaffold(root: Path) -> None:
    (root / "skills/personas").mkdir(parents=True, exist_ok=True)
    (root / "skills/layer_aliases").mkdir(parents=True, exist_ok=True)
    (root / "prompts/templates/creation").mkdir(parents=True, exist_ok=True)
    (root / "prompts/templates/review").mkdir(parents=True, exist_ok=True)
    (root / "prompts/templates/remediation").mkdir(parents=True, exist_ok=True)
    (root / "templates").mkdir(parents=True, exist_ok=True)

    (root / "skills/personas/architect.md").write_text("architect persona", encoding="utf-8")
    (root / "skills/persona_mappings.yaml").write_text('version: "1.0"\ncreation:\n  brd:\n    personas: [architect]\n    mode: sequential\n', encoding="utf-8")
    (root / "skills/layer_aliases/default.yaml").write_text("aliases: {}\n", encoding="utf-8")
    (root / "prompts/templates/creation/base.md").write_text("create", encoding="utf-8")
    (root / "prompts/templates/review/base.md").write_text("review", encoding="utf-8")
    (root / "prompts/templates/remediation/base.md").write_text("remediate", encoding="utf-8")
    (root / "templates/BRD-MVP-TEMPLATE.md").write_text("brd template", encoding="utf-8")


def _create_authoritative_ssd(root: Path) -> None:
    (root / "01_BRD").mkdir(parents=True, exist_ok=True)
    (root / "01_BRD/BRD-MVP-TEMPLATE.md").write_text("authoritative brd md", encoding="utf-8")
    (root / "01_BRD/BRD-MVP-TEMPLATE.yaml").write_text("doc_id: BRD-01\n", encoding="utf-8")
    (root / "01_BRD/BRD_MVP_SCHEMA.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")


def test_scaffold_project_ucx_creates_expected_files(tmp_path: Path) -> None:
    canonical_root = tmp_path / "canonical"
    ssd_root = tmp_path / "framework"
    project_root = tmp_path / "project"
    _create_canonical_scaffold(canonical_root)
    _create_authoritative_ssd(ssd_root)

    result = scaffold_project_ucx(project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root)

    assert result.created_count >= 6
    assert result.skipped_count == 0
    assert (project_root / "UCX/skills/personas/architect.md").exists()
    assert (project_root / "UCX/skills/persona_mappings.yaml").exists()
    assert (project_root / "UCX/skills/layer_aliases/default.yaml").exists()
    assert (project_root / "UCX/prompts/templates/review/base.md").exists()
    assert (project_root / "UCX/templates/BRD-MVP-TEMPLATE.md").exists()
    assert (project_root / "UCX/templates/layers/01_BRD/BRD-MVP-TEMPLATE.yaml").exists()
    assert (project_root / "UCX/templates/layers/01_BRD/BRD_MVP_SCHEMA.yaml").exists()


def test_scaffold_project_ucx_does_not_overwrite_existing_files(tmp_path: Path) -> None:
    canonical_root = tmp_path / "canonical"
    ssd_root = tmp_path / "framework"
    project_root = tmp_path / "project"
    _create_canonical_scaffold(canonical_root)
    _create_authoritative_ssd(ssd_root)

    existing = project_root / "UCX/skills/personas/architect.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("project override", encoding="utf-8")

    result = scaffold_project_ucx(project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root)

    assert result.skipped_count >= 1
    assert result.updated_count == 0
    assert existing.read_text(encoding="utf-8") == "project override"


def test_scaffold_update_overwrites_stale_files(tmp_path: Path) -> None:
    canonical_root = tmp_path / "canonical"
    ssd_root = tmp_path / "framework"
    project_root = tmp_path / "project"
    _create_canonical_scaffold(canonical_root)
    _create_authoritative_ssd(ssd_root)

    # First init — creates files.
    scaffold_project_ucx(project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root)

    # Simulate framework update — change canonical source content.
    (canonical_root / "skills/personas/architect.md").write_text("architect persona v2", encoding="utf-8")
    (ssd_root / "01_BRD/BRD-MVP-TEMPLATE.yaml").write_text("doc_id: BRD-01-v2\n", encoding="utf-8")

    # Re-init WITHOUT update — stale files should be skipped.
    result_no_update = scaffold_project_ucx(
        project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root,
    )
    assert result_no_update.updated_count == 0
    assert (project_root / "UCX/skills/personas/architect.md").read_text(encoding="utf-8") == "architect persona"

    # Re-init WITH update — stale files should be overwritten.
    result_update = scaffold_project_ucx(
        project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root,
        force_update=True,
    )
    assert result_update.updated_count >= 2
    assert (project_root / "UCX/skills/personas/architect.md").read_text(encoding="utf-8") == "architect persona v2"
    assert (project_root / "UCX/templates/layers/01_BRD/BRD-MVP-TEMPLATE.yaml").read_text(encoding="utf-8") == "doc_id: BRD-01-v2\n"


def test_scaffold_update_skips_identical_files(tmp_path: Path) -> None:
    canonical_root = tmp_path / "canonical"
    ssd_root = tmp_path / "framework"
    project_root = tmp_path / "project"
    _create_canonical_scaffold(canonical_root)
    _create_authoritative_ssd(ssd_root)

    # First init.
    scaffold_project_ucx(project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root)

    # Re-init with update but no source changes — nothing should be updated.
    # persona_mappings.yaml is always reported as protected during --update.
    result = scaffold_project_ucx(
        project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root,
        force_update=True,
    )
    assert result.updated_count == 0
    assert result.protected_count == 1  # persona_mappings.yaml
    assert result.skipped_count >= 6


def test_scaffold_update_protects_persona_mappings(tmp_path: Path) -> None:
    """--update must NOT overwrite persona_mappings.yaml (project-owned)."""
    canonical_root = tmp_path / "canonical"
    ssd_root = tmp_path / "framework"
    project_root = tmp_path / "project"
    _create_canonical_scaffold(canonical_root)
    _create_authoritative_ssd(ssd_root)

    # First init.
    scaffold_project_ucx(project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root)

    # Project customizes persona_mappings.yaml.
    mappings_path = project_root / "UCX/skills/persona_mappings.yaml"
    mappings_path.write_text('version: "1.0"\ncreation:\n  brd:\n    personas: [architect, auditor]\n    mode: sequential\n', encoding="utf-8")

    # Framework updates source.
    (canonical_root / "skills/persona_mappings.yaml").write_text('version: "2.0"\ncreation:\n  brd:\n    personas: [architect]\n    mode: sequential\n', encoding="utf-8")

    # --update should protect persona_mappings.yaml.
    result = scaffold_project_ucx(
        project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root,
        force_update=True,
    )
    assert result.protected_count >= 1
    assert any("persona_mappings.yaml" in p for p in result.protected_paths)
    # Project customization preserved.
    assert "auditor" in mappings_path.read_text(encoding="utf-8")


def test_scaffold_update_mappings_resets_persona_mappings(tmp_path: Path) -> None:
    """--update --update-mappings explicitly resets persona_mappings.yaml."""
    canonical_root = tmp_path / "canonical"
    ssd_root = tmp_path / "framework"
    project_root = tmp_path / "project"
    _create_canonical_scaffold(canonical_root)
    _create_authoritative_ssd(ssd_root)

    # First init + project customization.
    scaffold_project_ucx(project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root)
    mappings_path = project_root / "UCX/skills/persona_mappings.yaml"
    mappings_path.write_text('version: "1.0"\ncreation:\n  brd:\n    personas: [architect, auditor]\n    mode: sequential\n', encoding="utf-8")

    # Framework updates source.
    (canonical_root / "skills/persona_mappings.yaml").write_text('version: "2.0"\ncreation:\n  brd:\n    personas: [architect]\n    mode: sequential\n', encoding="utf-8")

    # --update-mappings should overwrite persona_mappings.yaml.
    result = scaffold_project_ucx(
        project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root,
        force_update=True,
        force_update_mappings=True,
    )
    assert result.protected_count == 0
    assert any("persona_mappings.yaml" in p for p in result.updated_paths)
    content = mappings_path.read_text(encoding="utf-8")
    assert 'version: "2.0"' in content
    assert "auditor" not in content
