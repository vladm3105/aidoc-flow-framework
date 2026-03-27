from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402


def _write_schema_assets(project_root: Path) -> None:
    layer_root = project_root / "docs/UCX/templates/layers/01_BRD"
    layer_root.mkdir(parents=True, exist_ok=True)
    (layer_root / "BRD_MVP_SCHEMA.yaml").write_text(
        """
metadata:
  required_custom_fields:
    document_type:
      required: true
  required_tags:
    - brd
structure:
  required_sections:
    - name: Intro
      pattern: '^## 1\\. Intro$'
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_validate_to_fix_to_remediate_flow(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_schema_assets(tmp_path)

    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(
        """---
title: Sample
tags: [brd]
custom_fields:
  document_type: brd
---

## 1. Intro
TODO refine content
""",
        encoding="utf-8",
    )

    validate_out = tmp_path / "tmp/validate"
    remediate_out = tmp_path / "tmp/remediate"

    assert (
        main(
            [
                "validate-build",
                "--project",
                str(tmp_path),
                "--doc-type",
                "brd",
                "--layer",
                "01_BRD",
                "--document",
                str(document),
                "--format",
                "json",
                "--out",
                str(validate_out),
            ]
        )
        == 0
    )

    validation_report = validate_out / "validation_report.json"
    assert validation_report.exists()

    assert (
        main(
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
                str(validation_report),
                "--out",
                str(validate_out),
            ]
        )
        == 0
    )

    validation_copy = validate_out / "BRD-01_sample_validation.md"
    assert validation_copy.exists()

    assert (
        main(
            [
                "remediate",
                "--project",
                str(tmp_path),
                "--doc-type",
                "brd",
                "--layer",
                "01_BRD",
                "--document",
                str(validation_copy),
                "--out",
                str(remediate_out),
            ]
        )
        == 0
    )

    remediation_report = remediate_out / "remediation_report.json"
    assert remediation_report.exists()

    payload = json.loads(remediation_report.read_text(encoding="utf-8"))
    assert payload["summary"]["total_findings"] >= 1

    assert (
        main(
            [
                "remediate-fix",
                "--project",
                str(tmp_path),
                "--doc-type",
                "brd",
                "--layer",
                "01_BRD",
                "--document",
                str(validation_copy),
                "--remediation-report",
                str(remediation_report),
                "--out",
                str(remediate_out),
            ]
        )
        == 0
    )

    assert (remediate_out / "BRD-01_sample_validation_remediated.md").exists()
