"""Tests for the shared source-file collector at mcp_server.utils.source_files."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.utils.source_files import collect_source_files, is_yaml_document  # noqa: E402


# ── collect_source_files ─────────────────────────────────────────────────────


def test_collect_source_files_finds_yaml(tmp_path: Path) -> None:
    f = tmp_path / "BRD-01_test.yaml"
    f.write_text("title: test\n")
    result = collect_source_files(tmp_path)
    assert f in result


def test_collect_source_files_finds_md(tmp_path: Path) -> None:
    f = tmp_path / "BRD-01_test.md"
    f.write_text("# BRD\n")
    result = collect_source_files(tmp_path)
    assert f in result


def test_collect_source_files_excludes_validation_copy(tmp_path: Path) -> None:
    src = tmp_path / "BRD-01_test.yaml"
    src.write_text("title: test\n")
    val = tmp_path / "BRD-01_test_validate_copy.yaml"
    val.write_text("title: validation copy\n")
    result = collect_source_files(tmp_path)
    assert src in result
    assert val not in result


def test_collect_source_files_excludes_remediated_copy(tmp_path: Path) -> None:
    src = tmp_path / "BRD-01_test.yaml"
    src.write_text("title: test\n")
    rem = tmp_path / "BRD-01_test_remediate_copy.yaml"
    rem.write_text("title: remediated copy\n")
    result = collect_source_files(tmp_path)
    assert src in result
    assert rem not in result


def test_collect_source_files_excludes_template(tmp_path: Path) -> None:
    tpl = tmp_path / "BRD-TEMPLATE.yaml"
    tpl.write_text("title: template\n")
    result = collect_source_files(tmp_path)
    assert tpl not in result


def test_collect_source_files_file_input(tmp_path: Path) -> None:
    f = tmp_path / "BRD-01_test.yaml"
    f.write_text("title: test\n")
    result = collect_source_files(f)
    assert result == [f]


# ── is_yaml_document ─────────────────────────────────────────────────────────


def test_is_yaml_document() -> None:
    assert is_yaml_document(Path("doc.yaml")) is True
    assert is_yaml_document(Path("doc.yml")) is True
    assert is_yaml_document(Path("doc.md")) is False
