from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402


def test_cli_validate_fix_creates_validation_artifacts(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# BRD-01\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/validate"
    exit_code = main(
        [
            "validate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "validate_fix_report.json").exists()
    assert (out_dir / "validate_fix_report.txt").exists()
    assert (out_dir / "BRD-01_sample_validation.md").exists()


def test_cli_remediate_and_remediate_fix_create_outputs(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("TODO: complete section\n", encoding="utf-8")

    remediation_out = tmp_path / "tmp/remediate"
    remediate_exit = main(
        [
            "remediate",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--out",
            str(remediation_out),
        ]
    )

    assert remediate_exit == 0
    report_path = remediation_out / "remediation_report.json"
    assert report_path.exists()

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_findings"] >= 1

    remediate_fix_exit = main(
        [
            "remediate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--remediation-report",
            str(report_path),
            "--out",
            str(remediation_out),
        ]
    )

    assert remediate_fix_exit == 0
    assert (remediation_out / "remediate_fix_report.json").exists()
    assert (remediation_out / "BRD-01_sample_remediated.md").exists()


def test_validate_fix_fails_for_invalid_validation_report_path(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# BRD-01\n", encoding="utf-8")

    missing_report = tmp_path / "tmp/missing_validation_report.json"
    exit_code = main(
        [
            "validate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--validation-report",
            str(missing_report),
        ]
    )

    assert exit_code == 1


def test_cli_validate_fix_directory_prefers_source_artifact(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    doc_dir = tmp_path / "docs/01_BRD/BRD-01_platform"
    doc_dir.mkdir(parents=True, exist_ok=True)
    source_doc = doc_dir / "BRD-01_platform.md"
    source_doc.write_text("# BRD-01\n", encoding="utf-8")
    (doc_dir / "BRD-01_platform_remediated.md").write_text("# remediated copy\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/validate"
    exit_code = main(
        [
            "validate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(doc_dir),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "BRD-01_platform_validation.md").exists()
    assert not (out_dir / "BRD-01_platform_validation" / "BRD-01_platform.md").exists()


def test_cli_remediate_fix_directory_prefers_validation_copy(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    doc_dir = tmp_path / "docs/02_PRD/PRD-01_platform"
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / "PRD-01_platform.md").write_text("# source\n", encoding="utf-8")
    (doc_dir / "PRD-01_platform_validation.md").write_text("# validation copy\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/remediate"
    exit_code = main(
        [
            "remediate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "prd",
            "--layer",
            "02_PRD",
            "--document",
            str(doc_dir),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    # Uses _validation copy as input → _remediated output with canonical base stem
    assert (out_dir / "PRD-01_platform_remediated.md").exists()
    # Must NOT create a tree copy of the whole folder
    assert not (out_dir / f"{doc_dir.name}_remediated").exists()
    # Must NOT create _validation_remediated (non-canonical name)
    assert not (out_dir / "PRD-01_platform_validation_remediated.md").exists()


def test_remediate_fix_fails_for_invalid_remediation_report_path(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("TODO: complete section\n", encoding="utf-8")

    missing_report = tmp_path / "tmp/missing_remediation_report.json"
    exit_code = main(
        [
            "remediate-fix",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(document),
            "--remediation-report",
            str(missing_report),
        ]
    )

    assert exit_code == 1
