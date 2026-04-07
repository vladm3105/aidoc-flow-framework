"""Tests for YAML document support in the review pipeline (PLAN-028)."""

from __future__ import annotations

from pathlib import Path

import pytest

from mcp_server.cli.main import (
    _build_review_sections_from_document,
    _collect_review_document_files,
    _find_canonical_source,
    _list_review_document_candidates,
)


# ---------------------------------------------------------------------------
# _list_review_document_candidates
# ---------------------------------------------------------------------------


def test_list_candidates_includes_yaml(tmp_path: Path) -> None:
    (tmp_path / "BRD-05_multi_agent.yaml").write_text("title: test")
    (tmp_path / "BRD-05.18_appendices.md").write_text("# appendix")
    result = _list_review_document_candidates(tmp_path)
    names = [p.name for p in result]
    assert "BRD-05_multi_agent.yaml" in names
    assert "BRD-05.18_appendices.md" in names


def test_list_candidates_excludes_legacy(tmp_path: Path) -> None:
    (tmp_path / "BRD-50_octo_LEGACY.md").write_text("legacy")
    (tmp_path / "BRD-50_octo.yaml").write_text("title: octo")
    result = _list_review_document_candidates(tmp_path)
    names = [p.name for p in result]
    assert "BRD-50_octo.yaml" in names
    assert "BRD-50_octo_LEGACY.md" not in names


def test_list_candidates_excludes_review_report(tmp_path: Path) -> None:
    (tmp_path / "BRD-05_multi_agent.yaml").write_text("title: test")
    (tmp_path / "BRD-05_REVIEW.md").write_text("review")
    (tmp_path / "BRD-05_report.yaml").write_text("report")
    result = _list_review_document_candidates(tmp_path)
    names = [p.name for p in result]
    assert "BRD-05_multi_agent.yaml" in names
    assert len(names) == 1


# ---------------------------------------------------------------------------
# _find_canonical_source
# ---------------------------------------------------------------------------


def test_find_canonical_yaml_only(tmp_path: Path) -> None:
    (tmp_path / "BRD-05_multi_agent.yaml").write_text("title: test")
    (tmp_path / "BRD-05.18_appendices.md").write_text("# appendix")
    result = _find_canonical_source(tmp_path)
    assert result is not None
    assert result.name == "BRD-05_multi_agent.yaml"


def test_find_canonical_md_only(tmp_path: Path) -> None:
    (tmp_path / "BRD-01_platform.md").write_text("# BRD-01")
    result = _find_canonical_source(tmp_path)
    assert result is not None
    assert result.name == "BRD-01_platform.md"


def test_find_canonical_yaml_preferred_over_md(tmp_path: Path) -> None:
    """When both .yaml and .md canonical sources exist, YAML wins."""
    (tmp_path / "BRD-01_platform.yaml").write_text("title: platform")
    (tmp_path / "BRD-01_platform.md").write_text("# BRD-01")
    result = _find_canonical_source(tmp_path)
    assert result is not None
    assert result.name == "BRD-01_platform.yaml"


def test_find_canonical_ignores_legacy(tmp_path: Path) -> None:
    (tmp_path / "BRD-50_octo.yaml").write_text("title: octo")
    (tmp_path / "BRD-50_octo_LEGACY.md").write_text("legacy content")
    result = _find_canonical_source(tmp_path)
    assert result is not None
    assert result.name == "BRD-50_octo.yaml"


def test_find_canonical_appendix_not_canonical(tmp_path: Path) -> None:
    """Appendix files should not match as canonical source."""
    (tmp_path / "BRD-14.19_appendices.md").write_text("# appendix")
    (tmp_path / "BRD-14_feature.yaml").write_text("title: feature")
    result = _find_canonical_source(tmp_path)
    assert result is not None
    assert result.name == "BRD-14_feature.yaml"


def test_find_canonical_no_match(tmp_path: Path) -> None:
    (tmp_path / "random_notes.md").write_text("notes")
    result = _find_canonical_source(tmp_path)
    assert result is None


# ---------------------------------------------------------------------------
# _collect_review_document_files
# ---------------------------------------------------------------------------


def test_collect_yaml_with_appendix(tmp_path: Path) -> None:
    (tmp_path / "BRD-05_multi_agent.yaml").write_text("title: test")
    (tmp_path / "BRD-05.18_appendices.md").write_text("# appendix")
    result = _collect_review_document_files(tmp_path)
    names = [p.name for p in result]
    assert names[0] == "BRD-05_multi_agent.yaml"
    assert "BRD-05.18_appendices.md" in names
    assert len(result) == 2


def test_collect_direct_yaml_file(tmp_path: Path) -> None:
    yaml_file = tmp_path / "BRD-05_multi_agent.yaml"
    yaml_file.write_text("title: test")
    result = _collect_review_document_files(yaml_file)
    assert len(result) == 1
    assert result[0].name == "BRD-05_multi_agent.yaml"


def test_collect_direct_md_file(tmp_path: Path) -> None:
    md_file = tmp_path / "BRD-01_platform.md"
    md_file.write_text("# BRD-01")
    result = _collect_review_document_files(md_file)
    assert len(result) == 1
    assert result[0].name == "BRD-01_platform.md"


def test_collect_empty_folder(tmp_path: Path) -> None:
    result = _collect_review_document_files(tmp_path)
    assert result == []


def test_collect_section19_appendix_detected(tmp_path: Path) -> None:
    """BRD-14 through BRD-17 use .19_appendices.md — should be detected."""
    (tmp_path / "BRD-14_feature.yaml").write_text("title: feature")
    (tmp_path / "BRD-14.19_appendices.md").write_text("# appendix")
    result = _collect_review_document_files(tmp_path)
    names = [p.name for p in result]
    assert "BRD-14_feature.yaml" in names
    assert "BRD-14.19_appendices.md" in names


# ---------------------------------------------------------------------------
# _build_review_sections_from_document
# ---------------------------------------------------------------------------


def test_build_sections_yaml_folder(tmp_path: Path) -> None:
    (tmp_path / "BRD-05_multi_agent.yaml").write_text("title: test yaml")
    sections, files = _build_review_sections_from_document(tmp_path)
    assert len(sections) == 1
    assert sections[0].section_id == "BRD-05_multi_agent"
    assert "test yaml" in sections[0].content
    assert files[0].name == "BRD-05_multi_agent.yaml"


def test_build_sections_md_backward_compat(tmp_path: Path) -> None:
    (tmp_path / "BRD-01_platform.md").write_text("# BRD-01 content")
    sections, files = _build_review_sections_from_document(tmp_path)
    assert len(sections) == 1
    assert "BRD-01 content" in sections[0].content
