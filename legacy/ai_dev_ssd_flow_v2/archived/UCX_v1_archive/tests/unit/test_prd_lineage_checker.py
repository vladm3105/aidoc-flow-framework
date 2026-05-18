"""Unit tests for ucx.validators.prd.lineage_checker (PLAN-012)."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ucx.validators.prd.lineage_checker import (
    LineageFailure,
    _classify,
    _is_remediated_copy,
    _is_validation_copy,
    _is_validation_report,
    _is_source,
    check_folder,
    main,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_prd(folder: Path, name: str, frontmatter: str, body: str = "# Content\n") -> Path:
    """Write a PRD markdown file with the given frontmatter and body."""
    p = folder / name
    p.write_text(f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8")
    return p


_BASE_FM = textwrap.dedent("""\
    doc_id: PRD-01
    version: 0.2.0
    title: Test PRD
    tags:
      - prd
    custom_fields:
      document_type: prd
      processing_stage: source
""")

_VALIDATION_FM = textwrap.dedent("""\
    doc_id: PRD-01
    version: 0.2.0
    title: Test PRD
    tags:
      - prd
    custom_fields:
      document_type: prd
      processing_stage: validation-fixed
      source_doc_id: PRD-01
      source_version: 0.2.0
      derived_from: PRD-01_architecture.md
""")

_REMEDIATED_FM = textwrap.dedent("""\
    doc_id: PRD-01
    version: 0.2.0
    title: Test PRD
    tags:
      - prd
    custom_fields:
      document_type: prd
      processing_stage: remediated
      source_doc_id: PRD-01
      source_version: 0.2.0
      derived_from: PRD-01_architecture_validation.md
""")


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

class TestClassification:
    def test_source_file(self):
        assert _classify(Path("PRD-01_architecture.md")) == "source"

    def test_validation_file(self):
        assert _classify(Path("PRD-01_architecture_validation.md")) == "validation-fixed"

    def test_remediated_file(self):
        assert _classify(Path("PRD-01_architecture_remediated.md")) == "remediated"

    def test_validation_report(self):
        assert _classify(Path("PRD-01_validation_report.md")) == "report"

    def test_remediation_report(self):
        assert _classify(Path("PRD-01_validation_remediation_report_v001.md")) == "report"

    def test_is_source(self):
        assert _is_source(Path("PRD-01_arch.md")) is True
        assert _is_source(Path("PRD-01_arch_validation.md")) is False

    def test_is_validation_copy(self):
        assert _is_validation_copy(Path("PRD-01_arch_validation.md")) is True
        assert _is_validation_copy(Path("PRD-01_arch.md")) is False

    def test_is_remediated_copy(self):
        assert _is_remediated_copy(Path("PRD-01_arch_remediated.md")) is True
        assert _is_remediated_copy(Path("PRD-01_arch.md")) is False

    def test_is_validation_report(self):
        assert _is_validation_report(Path("PRD-01_validation_report.md")) is True
        assert _is_validation_report(Path("PRD-01_arch.md")) is False


# ---------------------------------------------------------------------------
# CHECK 1: Source PRD exists when derived copies exist
# ---------------------------------------------------------------------------

class TestCheck1:
    def test_passes_when_source_present(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Validation Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk1 = [f for f in failures if f.check == "CHK-1"]
        assert chk1 == []

    def test_fails_when_source_missing(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk1 = [f for f in failures if f.check == "CHK-1"]
        assert len(chk1) == 1
        assert "PRD-01_architecture_validation.md" in chk1[0].file


# ---------------------------------------------------------------------------
# CHECK 2: Validation report exists when _validation copy exists
# ---------------------------------------------------------------------------

class TestCheck2:
    def test_passes_when_report_present(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk2 = [f for f in failures if f.check == "CHK-2"]
        assert chk2 == []

    def test_fails_when_report_missing(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        failures = check_folder(tmp_path)
        chk2 = [f for f in failures if f.check == "CHK-2"]
        assert len(chk2) == 1

    def test_no_failure_when_no_validation_copy(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        failures = check_folder(tmp_path)
        chk2 = [f for f in failures if f.check == "CHK-2"]
        assert chk2 == []


# ---------------------------------------------------------------------------
# CHECK 3: _validation copy exists when _remediated copy exists
# ---------------------------------------------------------------------------

class TestCheck3:
    def test_passes_when_validation_copy_present(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        _write_prd(tmp_path, "PRD-01_architecture_remediated.md", _REMEDIATED_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        (tmp_path / "PRD-01_validation_remediation_report_v001.md").write_text("# Rem report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk3 = [f for f in failures if f.check == "CHK-3"]
        assert chk3 == []

    def test_fails_when_validation_copy_missing(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_remediated.md", _REMEDIATED_FM)
        (tmp_path / "PRD-01_validation_remediation_report_v001.md").write_text("# Rem", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk3 = [f for f in failures if f.check == "CHK-3"]
        assert len(chk3) == 1


# ---------------------------------------------------------------------------
# CHECK 4: Remediation report exists when _remediated copy exists
# ---------------------------------------------------------------------------

class TestCheck4:
    def test_fails_when_remediation_report_missing(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        _write_prd(tmp_path, "PRD-01_architecture_remediated.md", _REMEDIATED_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk4 = [f for f in failures if f.check == "CHK-4"]
        assert len(chk4) == 1

    def test_passes_when_remediation_report_present(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        _write_prd(tmp_path, "PRD-01_architecture_remediated.md", _REMEDIATED_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        (tmp_path / "PRD-01_validation_remediation_report_v001.md").write_text("# Rem", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk4 = [f for f in failures if f.check == "CHK-4"]
        assert chk4 == []


# ---------------------------------------------------------------------------
# CHECK 5: doc_id consistency
# ---------------------------------------------------------------------------

class TestCheck5:
    def test_passes_when_consistent(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk5 = [f for f in failures if f.check == "CHK-5"]
        assert chk5 == []

    def test_fails_when_source_doc_id_mismatches(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        bad_fm = _VALIDATION_FM.replace("source_doc_id: PRD-01", "source_doc_id: PRD-99")
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", bad_fm)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk5 = [f for f in failures if f.check == "CHK-5"]
        assert len(chk5) == 1


# ---------------------------------------------------------------------------
# CHECK 6: version consistency
# ---------------------------------------------------------------------------

class TestCheck6:
    def test_fails_when_version_mismatches(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        bad_fm = _VALIDATION_FM.replace("version: 0.2.0", "version: 0.9.0", 1)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", bad_fm)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk6 = [f for f in failures if f.check == "CHK-6"]
        assert len(chk6) == 1

    def test_passes_when_version_consistent(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk6 = [f for f in failures if f.check == "CHK-6"]
        assert chk6 == []


# ---------------------------------------------------------------------------
# CHECK 7: processing_stage correctness
# ---------------------------------------------------------------------------

class TestCheck7:
    def test_fails_when_validation_stage_wrong(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        bad_fm = _VALIDATION_FM.replace(
            "processing_stage: validation-fixed",
            "processing_stage: source",
        )
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", bad_fm)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk7 = [f for f in failures if f.check == "CHK-7"]
        assert len(chk7) >= 1
        assert any("processing_stage" in f.message for f in chk7)

    def test_passes_when_all_stages_correct(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk7 = [f for f in failures if f.check == "CHK-7"]
        assert chk7 == []

    def test_fails_when_validation_copy_missing_stage(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        no_stage_fm = textwrap.dedent("""\
            doc_id: PRD-01
            version: 0.2.0
            custom_fields:
              source_doc_id: PRD-01
              derived_from: PRD-01_architecture.md
        """)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", no_stage_fm)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk7 = [f for f in failures if f.check == "CHK-7"]
        assert len(chk7) >= 1


# ---------------------------------------------------------------------------
# CHECK 8: derived_from points to existing sibling
# ---------------------------------------------------------------------------

class TestCheck8:
    def test_fails_when_derived_from_missing(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        no_derived_fm = _VALIDATION_FM.replace(
            "derived_from: PRD-01_architecture.md",
            "",
        )
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", no_derived_fm)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk8 = [f for f in failures if f.check == "CHK-8"]
        assert len(chk8) >= 1

    def test_fails_when_derived_from_nonexistent_file(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        bad_derived_fm = _VALIDATION_FM.replace(
            "derived_from: PRD-01_architecture.md",
            "derived_from: PRD-01_nonexistent.md",
        )
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", bad_derived_fm)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk8 = [f for f in failures if f.check == "CHK-8"]
        assert len(chk8) >= 1

    def test_passes_when_derived_from_exists(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        _write_prd(tmp_path, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        chk8 = [f for f in failures if f.check == "CHK-8"]
        assert chk8 == []


# ---------------------------------------------------------------------------
# Empty folder / source-only: all checks pass
# ---------------------------------------------------------------------------

class TestCleanFolders:
    def test_empty_folder_passes(self, tmp_path):
        failures = check_folder(tmp_path)
        assert failures == []

    def test_source_only_passes(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        failures = check_folder(tmp_path)
        assert failures == []

    def test_source_plus_report_only_passes(self, tmp_path):
        _write_prd(tmp_path, "PRD-01_architecture.md", _BASE_FM)
        (tmp_path / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        failures = check_folder(tmp_path)
        assert failures == []


# ---------------------------------------------------------------------------
# main() function (CLI entry point)
# ---------------------------------------------------------------------------

class TestMainFunction:
    def test_main_exits_0_on_clean_folder(self, tmp_path):
        prd_folder = tmp_path / "PRD-01"
        prd_folder.mkdir()
        _write_prd(prd_folder, "PRD-01_architecture.md", _BASE_FM)
        code = main([str(prd_folder)])
        assert code == 0

    def test_main_exits_1_on_failures(self, tmp_path):
        prd_folder = tmp_path / "PRD-01"
        prd_folder.mkdir()
        # Validation copy without source — triggers CHK-1
        _write_prd(prd_folder, "PRD-01_architecture_validation.md", _VALIDATION_FM)
        (prd_folder / "PRD-01_validation_report.md").write_text("# Report", encoding="utf-8")
        code = main([str(prd_folder)])
        assert code == 1

    def test_main_nonexistent_path_passes(self, tmp_path):
        # Non-existent path should not crash — just skip
        code = main([str(tmp_path / "does_not_exist")])
        assert code == 0

    def test_main_discovers_nested_prd_folders(self, tmp_path):
        prd_folder = tmp_path / "02_PRD" / "PRD-01"
        prd_folder.mkdir(parents=True)
        _write_prd(prd_folder, "PRD-01_architecture.md", _BASE_FM)
        code = main([str(tmp_path)])
        assert code == 0
