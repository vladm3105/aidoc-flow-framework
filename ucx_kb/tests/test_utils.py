from pathlib import Path

from ucx_kb.utils import is_real_document


def test_is_real_document_excludes_archived_by_default(tmp_path: Path) -> None:
    active = tmp_path / "ucx_hermes" / "docs" / "README.md"
    active.parent.mkdir(parents=True, exist_ok=True)
    active.write_text("active", encoding="utf-8")

    archived = tmp_path / "ai_dev_ssd_flow_v2" / "archived" / "ROOT_README_v2.md"
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_text("legacy", encoding="utf-8")

    assert is_real_document(str(active)) is True
    assert is_real_document(str(archived)) is False


def test_is_real_document_can_include_archived(tmp_path: Path) -> None:
    archived = tmp_path / "legacy" / "archive" / "BRD-01.md"
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_text("legacy", encoding="utf-8")

    assert is_real_document(str(archived), include_archived=True) is True


def test_is_real_document_excludes_legacy_suffix(tmp_path: Path) -> None:
    legacy_file = tmp_path / "ucx_hermes" / "docs" / "BRD-50_octo_LEGACY.md"
    legacy_file.parent.mkdir(parents=True, exist_ok=True)
    legacy_file.write_text("legacy", encoding="utf-8")

    assert is_real_document(str(legacy_file), include_archived=True) is False
