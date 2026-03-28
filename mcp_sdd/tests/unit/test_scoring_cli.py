from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402


def _write_report(path: Path, errors: int, warnings: int) -> None:
    payload = {
        "summary": {
            "errors": errors,
            "warnings": warnings,
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_scan_style_report(path: Path, errors: int, warnings: int) -> None:
    payload = {
        "summary": {
            "error_count": errors,
            "warning_count": warnings,
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_validate_style_report(path: Path, errors: int, warnings: int) -> None:
    payload = {
        "errors": [f"err-{index}" for index in range(errors)],
        "warnings": [f"warn-{index}" for index in range(warnings)],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_scoring_show_validate_compare(tmp_path: Path, capsys) -> None:
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    _write_report(baseline, errors=2, warnings=1)
    _write_report(candidate, errors=0, warnings=1)

    assert main(["scoring", "show", "--report-file", str(candidate)]) == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["score"] == 95

    assert main(["scoring", "validate", "--report-file", str(candidate), "--threshold", "90"]) == 0
    validate_payload = json.loads(capsys.readouterr().out)
    assert validate_payload["passed"] is True

    assert main(["scoring", "compare", "--baseline-report-file", str(baseline), "--candidate-report-file", str(candidate)]) == 0
    compare_payload = json.loads(capsys.readouterr().out)
    assert compare_payload["delta"] > 0


def test_scoring_supports_scan_and_validate_report_shapes(tmp_path: Path, capsys) -> None:
    scan_report = tmp_path / "scan.json"
    validate_report = tmp_path / "validate.json"
    _write_scan_style_report(scan_report, errors=1, warnings=2)
    _write_validate_style_report(validate_report, errors=2, warnings=1)

    assert main(["scoring", "show", "--report-file", str(scan_report)]) == 0
    scan_payload = json.loads(capsys.readouterr().out)
    assert scan_payload["score"] == 70

    assert main(["scoring", "show", "--report-file", str(validate_report)]) == 0
    validate_payload = json.loads(capsys.readouterr().out)
    assert validate_payload["score"] == 55
