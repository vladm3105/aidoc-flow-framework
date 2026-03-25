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
    ssd_root = tmp_path / "ai_dev_ssd_flow"
    project_root = tmp_path / "project"
    _create_canonical_scaffold(canonical_root)
    _create_authoritative_ssd(ssd_root)

    result = scaffold_project_ucx(project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root)

    assert result.created_count >= 6
    assert result.skipped_count == 0
    assert (project_root / "docs/UCX/skills/personas/architect.md").exists()
    assert (project_root / "docs/UCX/skills/layer_aliases/default.yaml").exists()
    assert (project_root / "docs/UCX/prompts/templates/review/base.md").exists()
    assert (project_root / "docs/UCX/templates/BRD-MVP-TEMPLATE.md").exists()
    assert (project_root / "docs/UCX/templates/layers/01_BRD/BRD-MVP-TEMPLATE.yaml").exists()
    assert (project_root / "docs/UCX/templates/layers/01_BRD/BRD_MVP_SCHEMA.yaml").exists()


def test_scaffold_project_ucx_does_not_overwrite_existing_files(tmp_path: Path) -> None:
    canonical_root = tmp_path / "canonical"
    ssd_root = tmp_path / "ai_dev_ssd_flow"
    project_root = tmp_path / "project"
    _create_canonical_scaffold(canonical_root)
    _create_authoritative_ssd(ssd_root)

    existing = project_root / "docs/UCX/skills/personas/architect.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("project override", encoding="utf-8")

    result = scaffold_project_ucx(project_root=project_root, canonical_root=canonical_root, ssd_root=ssd_root)

    assert result.skipped_count >= 1
    assert existing.read_text(encoding="utf-8") == "project override"
