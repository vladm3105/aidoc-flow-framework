"""Tests for cleanup runner (sdd_clean)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


from mcp_server.cleanup.runner import run_clean


def _create_files(tmp_path: Path, names: list[str]) -> None:
    for name in names:
        (tmp_path / name).write_text(f"# {name}", encoding="utf-8")


class TestVersionedRemediationCleanup:
    def test_keeps_latest_version(self, tmp_path: Path) -> None:
        _create_files(
            tmp_path,
            [
                "BRD-01_test.yaml",
                "BRD-01_test_remediate_v1.yaml",
                "BRD-01_test_remediate_v2.yaml",
                "BRD-01_test_remediate_v3.yaml",
            ],
        )
        result = run_clean(tmp_path, stages=["remediate"], keep=1, dry_run=False)
        assert len(result.deleted) == 2
        assert not (tmp_path / "BRD-01_test_remediate_v1.yaml").exists()
        assert not (tmp_path / "BRD-01_test_remediate_v2.yaml").exists()
        assert (tmp_path / "BRD-01_test_remediate_v3.yaml").exists()
        assert (tmp_path / "BRD-01_test.yaml").exists()  # Source protected

    def test_keep_two(self, tmp_path: Path) -> None:
        _create_files(
            tmp_path,
            [
                "BRD-01_test.yaml",
                "BRD-01_test_remediate_v1.yaml",
                "BRD-01_test_remediate_v2.yaml",
                "BRD-01_test_remediate_v3.yaml",
            ],
        )
        result = run_clean(tmp_path, stages=["remediate"], keep=2, dry_run=False)
        assert len(result.deleted) == 1
        assert not (tmp_path / "BRD-01_test_remediate_v1.yaml").exists()
        assert (tmp_path / "BRD-01_test_remediate_v2.yaml").exists()
        assert (tmp_path / "BRD-01_test_remediate_v3.yaml").exists()


class TestReportCleanup:
    def test_keeps_latest_report(self, tmp_path: Path) -> None:
        _create_files(
            tmp_path,
            [
                "BRD-01_test.yaml",
                "BRD-01.ucx.validate.json",
                "BRD-01.ucx.validate.txt",
                "BRD-01.ucx.validate.v1.json",
                "BRD-01.ucx.validate.v2.json",
            ],
        )
        result = run_clean(tmp_path, stages=["validate"], keep=1, dry_run=False)
        # Keeps latest versioned + latest unversioned per format
        assert (tmp_path / "BRD-01_test.yaml").exists()  # Source protected


class TestDryRun:
    def test_dry_run_does_not_delete(self, tmp_path: Path) -> None:
        _create_files(
            tmp_path,
            [
                "BRD-01_test.yaml",
                "BRD-01_test_remediate_v1.yaml",
                "BRD-01_test_remediate_v2.yaml",
            ],
        )
        result = run_clean(tmp_path, stages=["remediate"], keep=1, dry_run=True)
        assert result.dry_run is True
        assert len(result.deleted) == 1
        assert (tmp_path / "BRD-01_test_remediate_v1.yaml").exists()  # Still exists
        assert result.total_bytes_freed == 0


class TestStageFiltering:
    def test_only_cleans_selected_stage(self, tmp_path: Path) -> None:
        _create_files(
            tmp_path,
            [
                "BRD-01_test.yaml",
                "BRD-01_test_remediate_v1.yaml",
                "BRD-01_test_remediate_v2.yaml",
                "BRD-01_test_validated.yaml",
                "BRD-01.ucx.validate.json",
            ],
        )
        result = run_clean(tmp_path, stages=["remediate"], keep=1, dry_run=False)
        assert not (tmp_path / "BRD-01_test_remediate_v1.yaml").exists()
        assert (tmp_path / "BRD-01_test_validated.yaml").exists()  # Not touched
        assert (tmp_path / "BRD-01.ucx.validate.json").exists()  # Not touched


class TestKeepZero:
    def test_removes_all_stage_artifacts(self, tmp_path: Path) -> None:
        _create_files(
            tmp_path,
            [
                "BRD-01_test.yaml",
                "BRD-01_test_remediate_v1.yaml",
                "BRD-01_test_remediate_v2.yaml",
                "BRD-01.ucx.remediate.json",
            ],
        )
        result = run_clean(tmp_path, stages=["remediate"], keep=0, dry_run=False)
        assert not (tmp_path / "BRD-01_test_remediate_v1.yaml").exists()
        assert not (tmp_path / "BRD-01_test_remediate_v2.yaml").exists()
        assert not (tmp_path / "BRD-01.ucx.remediate.json").exists()
        assert (tmp_path / "BRD-01_test.yaml").exists()  # Source protected


class TestLegacyCompat:
    def test_legacy_copy_deleted_when_versioned_exist(self, tmp_path: Path) -> None:
        _create_files(
            tmp_path,
            [
                "BRD-01_test.yaml",
                "BRD-01_test_remediate_copy.yaml",
                "BRD-01_test_remediate_v1.yaml",
            ],
        )
        result = run_clean(tmp_path, stages=["remediate"], keep=1, dry_run=False)
        assert not (tmp_path / "BRD-01_test_remediate_copy.yaml").exists()
        assert (tmp_path / "BRD-01_test_remediate_v1.yaml").exists()


class TestSourceProtection:
    def test_source_document_never_deleted(self, tmp_path: Path) -> None:
        _create_files(
            tmp_path,
            [
                "BRD-01_test.yaml",
                "BRD-01.ucx.validate.json",
            ],
        )
        result = run_clean(tmp_path, stages=["all"], keep=0, dry_run=False)
        assert (tmp_path / "BRD-01_test.yaml").exists()
