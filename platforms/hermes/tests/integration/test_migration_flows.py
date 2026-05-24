from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402


def _write_schema_assets(project_root: Path) -> None:
    layer_root = project_root / "UCX/templates/layers/01_BRD"
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


def _write_ears_schema_assets(project_root: Path) -> None:
    layer_root = project_root / "UCX/templates/layers/03_EARS"
    layer_root.mkdir(parents=True, exist_ok=True)
    (layer_root / "EARS_MVP_SCHEMA.yaml").write_text(
        """
metadata:
  required_custom_fields:
    document_type:
      required: true
    status:
      required: true
  required_tags:
    - ears
structure:
  required_sections:
    - name: Title
      pattern: '^# '
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_validate_to_fix_to_remediate_flow(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_schema_assets(tmp_path)

    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    # Document missing frontmatter — will fail validation and trigger fix generation
    document.write_text(
        "# BRD-01: Sample\nTODO refine content\n",
        encoding="utf-8",
    )

    validate_out = tmp_path / "tmp/validate"
    remediate_out = tmp_path / "tmp/remediate"

    # Merged validate now runs validation + fix in one call
    assert (
        main(
            [
                "validate",
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
        == 1  # Validation fails (errors found)
    )

    validation_report = next(
        validate_out.glob("*.ucx.validate.json"), validate_out / "validation_report.json"
    )
    assert validation_report.exists()

    # Merged validate produces the derived copy automatically when errors exist
    validation_copy = validate_out / "BRD-01_sample_validated.md"
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

    remediation_report = next(
        remediate_out.glob("*.ucx.remediate.json"), remediate_out / "remediation_report.json"
    )
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

    assert (remediate_out / "BRD-01_sample_remediate_v1.md").exists()


def test_validate_ears_directory_flow_passes_for_section_set(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_ears_schema_assets(tmp_path)

    document_dir = tmp_path / "docs/03_EARS/EARS-01_sectioned"
    document_dir.mkdir(parents=True, exist_ok=True)
    (document_dir / "EARS-01.1_requirement.md").write_text(
        """---
title: Sample
tags: [ears]
custom_fields:
  document_type: ears
  status: draft
---

# EARS-01: Sample

WHEN request is accepted THE SYSTEM SHALL persist the record.
""",
        encoding="utf-8",
    )

    validate_out = tmp_path / "tmp/ears-validate"
    assert (
        main(
            [
                "validate",
                "--project",
                str(tmp_path),
                "--doc-type",
                "ears",
                "--layer",
                "03_EARS",
                "--document",
                str(document_dir),
                "--format",
                "json",
                "--out",
                str(validate_out),
            ]
        )
        == 0
    )

    validation_report = next(
        validate_out.glob("*.ucx.validate.json"), validate_out / "validation_report.json"
    )
    payload = json.loads(validation_report.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    assert summary.get("is_valid") is True
