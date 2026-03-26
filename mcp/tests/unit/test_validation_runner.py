from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402  # type: ignore[import-not-found]
from mcp_server.validation import run_project_validation_build  # noqa: E402  # type: ignore[import-not-found]


def _write_minimal_layer_assets(project_root: Path, layer: str = "01_BRD") -> None:
    layer_root = project_root / f"docs/UCX/templates/layers/{layer}"
    layer_root.mkdir(parents=True, exist_ok=True)

    (layer_root / "BRD-MVP-TEMPLATE.md").write_text(
        "# BRD Template\n\n## 1. Intro\n",
        encoding="utf-8",
    )
    (layer_root / "BRD_MVP_SCHEMA.yaml").write_text(
        """
metadata:
  required_custom_fields:
    document_type:
      required: true
    status:
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


def test_run_project_validation_build_passes_for_compliant_doc(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_layer_assets(tmp_path)

    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(
        """---
title: "Sample"
tags: [brd]
custom_fields:
  document_type: brd
  status: draft
---

# BRD-01: Sample

## 1. Intro
""",
        encoding="utf-8",
    )

    out_dir = tmp_path / "tmp/validate"
    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="brd",
        layer="01_BRD",
        document_path=document,
        output_dir=out_dir,
    )

    assert result.is_valid
    assert result.report_path is not None and result.report_path.exists()
    assert result.summary_path is not None and result.summary_path.exists()


def test_run_project_validation_build_fails_on_missing_required_section(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_layer_assets(tmp_path)

    document = tmp_path / "docs/01_BRD/BRD-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(
        """---
title: "Sample"
tags: [brd]
custom_fields:
  document_type: brd
  status: draft
---

# BRD-01: Sample
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="brd",
        layer="01_BRD",
        document_path=document,
        output_dir=None,
    )

    assert not result.is_valid
    payload = json.loads(result.report_json)
    assert any("Missing required section" in error for error in payload["errors"])
