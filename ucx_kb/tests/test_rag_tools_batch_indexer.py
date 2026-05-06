from pathlib import Path

from ucx_kb.rag_tools.batch_indexer import scan_documents


def test_scan_documents_excludes_archived_by_default(tmp_path: Path) -> None:
    active = tmp_path / "ucx_hermes" / "docs" / "README.md"
    active.parent.mkdir(parents=True, exist_ok=True)
    active.write_text("active", encoding="utf-8")

    archived = tmp_path / "ai_dev_ssd_flow_v2" / "archived" / "ROOT_README_v2.md"
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_text("legacy", encoding="utf-8")

    docs = scan_documents(tmp_path)
    paths = {p.resolve() for p in docs}

    assert active.resolve() in paths
    assert archived.resolve() not in paths


def test_scan_documents_include_archived_flag(tmp_path: Path) -> None:
    archived = tmp_path / "legacy" / "archive" / "BRD-01.md"
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_text("legacy", encoding="utf-8")

    docs = scan_documents(tmp_path, include_archived=True)
    paths = {p.resolve() for p in docs}

    assert archived.resolve() in paths
