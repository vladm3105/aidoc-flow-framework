from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402


def test_cli_prescreen_reports_candidates(tmp_path: Path, capsys) -> None:
    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("TODO content without frontmatter\n", encoding="utf-8")

    exit_code = main(["prescreen", "--document", str(document)])

    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["summary"]["candidates_found"] == 1


def test_cli_prescreen_scans_yaml_documents(tmp_path: Path, capsys) -> None:
    document = tmp_path / "docs/07_TDD/TDD-01_sample.yaml"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("TODO: add content\n", encoding="utf-8")

    exit_code = main(["prescreen", "--document", str(document)])

    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["summary"]["files_scanned"] == 1
    assert payload["summary"]["candidates_found"] == 1
