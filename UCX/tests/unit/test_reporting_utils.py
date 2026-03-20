"""Tests for UCX reporting naming utilities."""

from pathlib import Path

from ucx.models.enums import DocType
from ucx.utils.file_ops import find_latest_review_report
from ucx.utils.reporting import extract_doc_id, next_report_version, report_filename


def test_extract_doc_id_from_slug_folder(tmp_path: Path):
    doc_dir = tmp_path / "PRD-01_platform_architecture"
    doc_dir.mkdir()
    assert extract_doc_id(doc_dir, DocType.PRD) == "PRD-01"


def test_report_filename_uses_canonical_ucx_pattern():
    assert report_filename("PRD-01", "validation", 3) == "PRD-01.UCX_validation_report_v003.md"
    assert report_filename("BRD-09", "review", 12) == "BRD-09.UCX_review_report_v012.md"
    assert report_filename("EARS-02", "remediation", 1) == "EARS-02.UCX_remediation_report_v001.md"


def test_next_report_version_scans_canonical_reports(tmp_path: Path):
    (tmp_path / "PRD-01.UCX_validation_report_v001.md").write_text("a", encoding="utf-8")
    (tmp_path / "PRD-01.UCX_validation_report_v004.md").write_text("b", encoding="utf-8")
    assert next_report_version(tmp_path, "PRD-01", "validation") == 5


def test_find_latest_review_report_uses_canonical_ucx_pattern(tmp_path: Path):
    report_v1 = tmp_path / "PRD-01.UCX_review_report_v001.md"
    report_v2 = tmp_path / "PRD-01.UCX_review_report_v002.md"
    report_v1.write_text("v1", encoding="utf-8")
    report_v2.write_text("v2", encoding="utf-8")

    latest = find_latest_review_report(tmp_path)
    assert latest is not None
    assert latest.name == "PRD-01.UCX_review_report_v002.md"
