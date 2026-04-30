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
    layer_root = project_root / f"UCX/templates/layers/{layer}"
    layer_root.mkdir(parents=True, exist_ok=True)

    canonical_root = project_root / f"ai_dev_flow_v3/{layer}"
    canonical_root.mkdir(parents=True, exist_ok=True)

    (layer_root / "BRD-MVP-TEMPLATE.md").write_text(
        "# BRD Template\n\n## 1. Intro\n",
        encoding="utf-8",
    )
    (layer_root / "BRD_MVP_SCHEMA.yaml").write_text(
        (
            "metadata:\n"
            "  required_custom_fields:\n"
            "    document_type:\n"
            "      required: true\n"
            "    status:\n"
            "      required: true\n"
            "  required_tags:\n"
            "    - brd\n"
            "structure:\n"
            "  required_sections:\n"
            "    - name: Intro\n"
            "      pattern: '^## 1\\\\. Intro$'\n"
        ),
        encoding="utf-8",
    )
    (layer_root / "BRD-MVP-TEMPLATE.yaml").write_text(
        (
            "id: BRD-01\n"
            "title: \"Sample BRD\"\n"
            "metadata: {}\n"
            "sections:\n"
            "  - number: 1\n"
            "    title: \"Intro\"\n"
            "    required: true\n"
        ),
        encoding="utf-8",
    )
    (canonical_root / "BRD-MVP-TEMPLATE.yaml").write_text(
        (
            "id: BRD-01\n"
            "title: \"Sample BRD\"\n"
            "metadata:\n"
            "  required_custom_fields:\n"
            "    document_type:\n"
            "      required: true\n"
            "    status:\n"
            "      required: true\n"
            "  required_tags:\n"
            "    - brd\n"
            "sections:\n"
            "  - number: 1\n"
            "    title: \"Intro\"\n"
            "    required: true\n"
        ),
        encoding="utf-8",
    )


def _write_minimal_generic_layer_assets(
    project_root: Path,
    *,
    layer: str,
    artifact_prefix: str,
    required_tag: str,
) -> None:
    layer_root = project_root / f"UCX/templates/layers/{layer}"
    layer_root.mkdir(parents=True, exist_ok=True)

    canonical_root = project_root / f"ai_dev_flow_v3/{layer}"
    canonical_root.mkdir(parents=True, exist_ok=True)

    (layer_root / f"{artifact_prefix}-MVP-TEMPLATE.md").write_text(
        f"# {artifact_prefix} Template\n",
        encoding="utf-8",
    )
    (layer_root / f"{artifact_prefix}_MVP_SCHEMA.yaml").write_text(
        f"""
metadata:
  required_custom_fields:
    document_type:
      required: true
    status:
      required: true
  required_tags:
    - {required_tag}
structure:
  required_sections:
    - name: Title (H1)
      pattern: '^# '
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (layer_root / f"{artifact_prefix}-MVP-TEMPLATE.yaml").write_text(
        f"""
id: {artifact_prefix}-01
title: "{artifact_prefix} Sample"
metadata: {{}}
sections: []
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (canonical_root / f"{artifact_prefix}-MVP-TEMPLATE.yaml").write_text(
        f"""
id: {artifact_prefix}-01
title: "{artifact_prefix} Sample"
metadata:
  required_custom_fields:
    document_type:
      required: true
    status:
      required: true
  required_tags:
    - {required_tag}
sections: []
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_run_project_validation_build_uses_canonical_yaml_template_not_project_layer_assets(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_layer_assets(tmp_path)

    # Make project-layer template deliberately incompatible with the document.
    layer_root = tmp_path / "UCX/templates/layers/01_BRD"
    (layer_root / "BRD-MVP-TEMPLATE.yaml").write_text(
        """
id: BRD-01
title: "Project Local BRD"
metadata:
  required_custom_fields:
    document_type:
      required: true
    status:
      required: true
  required_tags:
    - brd
sections:
  - number: 99
    title: "Project-Only Section"
    required: true
""".strip()
        + "\n",
        encoding="utf-8",
    )

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

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="brd",
        layer="01_BRD",
        document_path=document,
        output_dir=None,
    )

    assert result.is_valid
    payload = json.loads(result.report_json)
    assert not any("Project-Only Section" in error for error in payload["errors"])


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


def test_run_project_validation_build_directory_prefers_source_artifact(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_layer_assets(tmp_path)

    doc_dir = tmp_path / "docs/01_BRD/BRD-01_platform"
    doc_dir.mkdir(parents=True, exist_ok=True)

    source_doc = doc_dir / "BRD-01_platform.md"
    source_doc.write_text(
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

    # Derived artifact intentionally invalid; validation should ignore this file
    (doc_dir / "BRD-01_platform_validated.md").write_text(
        """---
title: "Validation Copy"
tags: [brd]
custom_fields:
  document_type: brd
  status: draft
---

# BRD-01: Validation Copy
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="brd",
        layer="01_BRD",
        document_path=doc_dir,
        output_dir=None,
    )

    assert result.is_valid
    payload = json.loads(result.report_json)
    checked = payload.get("files_checked", [])
    assert checked == [str(source_doc)]


def test_run_project_validation_build_file_appendix_redirects_to_source_artifact(tmp_path: Path) -> None:
        main(["init", "--project", str(tmp_path)])
        _write_minimal_layer_assets(tmp_path)

        doc_dir = tmp_path / "docs/01_BRD/BRD-01_platform"
        doc_dir.mkdir(parents=True, exist_ok=True)

        source_doc = doc_dir / "BRD-01_platform.md"
        source_doc.write_text(
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

        appendix_doc = doc_dir / "BRD-01_appendices.md"
        appendix_doc.write_text(
                """---
title: "Appendices"
tags: [brd]
custom_fields:
    document_type: brd
    status: draft
---

# BRD-01: Appendices
""",
                encoding="utf-8",
        )

        result = run_project_validation_build(
                project_root=tmp_path,
                doc_type="brd",
                layer="01_BRD",
                document_path=appendix_doc,
                output_dir=None,
        )

        assert result.is_valid
        payload = json.loads(result.report_json)
        checked = payload.get("files_checked", [])
        assert checked == [str(source_doc)]


def test_run_project_validation_build_directory_fallback_to_section_set(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_layer_assets(tmp_path)

    doc_dir = tmp_path / "docs/01_BRD/BRD-02_sectioned"
    doc_dir.mkdir(parents=True, exist_ok=True)

    (doc_dir / "BRD-02.1_intro.md").write_text(
        """---
title: "Sectioned"
tags: [brd]
custom_fields:
  document_type: brd
  status: draft
---

# BRD-02: Sectioned

## 1. Intro
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="brd",
        layer="01_BRD",
        document_path=doc_dir,
        output_dir=None,
    )

    assert result.is_valid
    payload = json.loads(result.report_json)
    checked = payload.get("files_checked", [])
    assert len(checked) == 1
    assert checked[0].endswith("BRD-02.1_intro.md")


def test_run_project_validation_build_ears_parity_pass(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_generic_layer_assets(
        tmp_path,
        layer="03_EARS",
        artifact_prefix="EARS",
        required_tag="ears",
    )

    document = tmp_path / "docs/03_EARS/EARS-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(
        """---
title: "Sample"
tags: [ears]
custom_fields:
  document_type: ears
  status: draft
---

# EARS-01: Sample

WHEN user submits valid input THE SYSTEM SHALL persist the record.
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="ears",
        layer="03_EARS",
        document_path=document,
        output_dir=None,
    )

    assert result.is_valid


def test_run_project_validation_build_ears_parity_fail(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_generic_layer_assets(
        tmp_path,
        layer="03_EARS",
        artifact_prefix="EARS",
        required_tag="ears",
    )

    document = tmp_path / "docs/03_EARS/EARS-01_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(
        """---
title: "Sample"
tags: [ears]
custom_fields:
  document_type: ears
  status: draft
---

# EARS-01: Sample

The system records user input.
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="ears",
        layer="03_EARS",
        document_path=document,
        output_dir=None,
    )

    assert not result.is_valid
    payload = json.loads(result.report_json)
    assert any("Missing EARS trigger clause" in error for error in payload["errors"])


def test_run_project_validation_build_ears_parity_fail_without_system_actor_clause(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_generic_layer_assets(
        tmp_path,
        layer="03_EARS",
        artifact_prefix="EARS",
        required_tag="ears",
    )

    document = tmp_path / "docs/03_EARS/EARS-02_sample.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(
        """---
title: "Sample"
tags: [ears]
custom_fields:
  document_type: ears
  status: draft
---

# EARS-02: Sample

WHEN user submits valid input SHALL persist the record.
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="ears",
        layer="03_EARS",
        document_path=document,
        output_dir=None,
    )

    assert not result.is_valid
    payload = json.loads(result.report_json)
    assert any("Missing EARS actor clause" in error for error in payload["errors"])


def test_run_project_validation_build_ears_directory_fallback_passes_with_section_files(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_generic_layer_assets(
        tmp_path,
        layer="03_EARS",
        artifact_prefix="EARS",
        required_tag="ears",
    )

    doc_dir = tmp_path / "docs/03_EARS/EARS-03_sectioned"
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / "EARS-03.1_requirement.md").write_text(
        """---
title: "Sectioned"
tags: [ears]
custom_fields:
  document_type: ears
  status: draft
---

# EARS-03: Sectioned

WHEN request payload is accepted THE SYSTEM SHALL persist the record.
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="ears",
        layer="03_EARS",
        document_path=doc_dir,
        output_dir=None,
    )

    assert result.is_valid
    payload = json.loads(result.report_json)
    checked = payload.get("files_checked", [])
    assert len(checked) == 1
    assert checked[0].endswith("EARS-03.1_requirement.md")


def test_run_project_validation_build_spec_tasks_ctr_parity(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    _write_minimal_generic_layer_assets(tmp_path, layer="09_SPEC", artifact_prefix="SPEC", required_tag="spec")
    _write_minimal_generic_layer_assets(tmp_path, layer="11_TASKS", artifact_prefix="TASKS", required_tag="tasks")
    _write_minimal_generic_layer_assets(tmp_path, layer="08_CTR", artifact_prefix="CTR", required_tag="ctr")

    spec_doc = tmp_path / "docs/09_SPEC/SPEC-01_sample.md"
    spec_doc.parent.mkdir(parents=True, exist_ok=True)
    spec_doc.write_text(
        """---
title: "Spec"
tags: [spec]
custom_fields:
  document_type: spec
  status: draft
---

# SPEC-01: Sample

```yaml
service:
  name: api
```
""",
        encoding="utf-8",
    )

    tasks_doc = tmp_path / "docs/11_TASKS/TASKS-01_sample.md"
    tasks_doc.parent.mkdir(parents=True, exist_ok=True)
    tasks_doc.write_text(
        """---
title: "Tasks"
tags: [tasks]
custom_fields:
  document_type: tasks
  status: draft
---

# TASKS-01: Sample

- [ ] Implement parser
""",
        encoding="utf-8",
    )

    ctr_doc = tmp_path / "docs/08_CTR/CTR-01_sample.md"
    ctr_doc.parent.mkdir(parents=True, exist_ok=True)
    ctr_doc.write_text(
        """---
title: "Contract"
tags: [ctr]
custom_fields:
  document_type: ctr
  status: draft
---

# CTR-01: Sample

openapi: 3.0.0
""",
        encoding="utf-8",
    )

    spec_result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="spec",
        layer="09_SPEC",
        document_path=spec_doc,
        output_dir=None,
    )
    tasks_result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="tasks",
        layer="11_TASKS",
        document_path=tasks_doc,
        output_dir=None,
    )
    ctr_result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="ctr",
        layer="08_CTR",
        document_path=ctr_doc,
        output_dir=None,
    )

    assert spec_result.is_valid
    assert tasks_result.is_valid
    assert ctr_result.is_valid


def test_run_project_validation_build_spec_parity_fail_without_yaml_block(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_generic_layer_assets(tmp_path, layer="09_SPEC", artifact_prefix="SPEC", required_tag="spec")

    spec_doc = tmp_path / "docs/09_SPEC/SPEC-02_sample.md"
    spec_doc.parent.mkdir(parents=True, exist_ok=True)
    spec_doc.write_text(
        """---
title: "Spec"
tags: [spec]
custom_fields:
  document_type: spec
  status: draft
---

# SPEC-02: Sample

service: api
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="spec",
        layer="09_SPEC",
        document_path=spec_doc,
        output_dir=None,
    )

    assert not result.is_valid
    payload = json.loads(result.report_json)
    assert any("Missing SPEC structure" in error for error in payload["errors"])


def test_run_project_validation_build_tasks_parity_fail_without_checkbox_item(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_generic_layer_assets(tmp_path, layer="11_TASKS", artifact_prefix="TASKS", required_tag="tasks")

    tasks_doc = tmp_path / "docs/11_TASKS/TASKS-02_sample.md"
    tasks_doc.parent.mkdir(parents=True, exist_ok=True)
    tasks_doc.write_text(
        """---
title: "Tasks"
tags: [tasks]
custom_fields:
  document_type: tasks
  status: draft
---

# TASKS-02: Sample

- Implement parser
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="tasks",
        layer="11_TASKS",
        document_path=tasks_doc,
        output_dir=None,
    )

    assert not result.is_valid
    payload = json.loads(result.report_json)
    assert any("Missing TASKS structure" in error for error in payload["errors"])


def test_run_project_validation_build_ctr_parity_fail_without_contract_token(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    _write_minimal_generic_layer_assets(tmp_path, layer="08_CTR", artifact_prefix="CTR", required_tag="ctr")

    ctr_doc = tmp_path / "docs/08_CTR/CTR-02_sample.md"
    ctr_doc.parent.mkdir(parents=True, exist_ok=True)
    ctr_doc.write_text(
        """---
title: "Interface"
tags: [ctr]
custom_fields:
  document_type: ctr
  status: draft
---

# CTR-02: Interface

This file documents integration context only.
""",
        encoding="utf-8",
    )

    result = run_project_validation_build(
        project_root=tmp_path,
        doc_type="ctr",
        layer="08_CTR",
        document_path=ctr_doc,
        output_dir=None,
    )

    assert not result.is_valid
    payload = json.loads(result.report_json)
    assert any("Missing CTR structure" in error for error in payload["errors"])


def test_run_project_validation_build_file_section_redirects_to_source_artifact_across_layers(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    layer_cases = [
        ("02_PRD", "PRD", "prd", "PRD-22_product_flow"),
        ("06_SYS", "SYS", "sys", "SYS-17_runtime_controls"),
    ]

    for layer, artifact_prefix, required_tag, stem in layer_cases:
        _write_minimal_generic_layer_assets(
            tmp_path,
            layer=layer,
            artifact_prefix=artifact_prefix,
            required_tag=required_tag,
        )

        doc_dir = tmp_path / f"docs/{layer}/{stem}"
        doc_dir.mkdir(parents=True, exist_ok=True)

        source_doc = doc_dir / f"{stem}.md"
        source_doc.write_text(
            f"""---
title: "Sample"
tags: [{required_tag}]
custom_fields:
  document_type: {required_tag}
  status: draft
---

# {stem}: Sample
""",
            encoding="utf-8",
        )

        section_doc = doc_dir / f"{artifact_prefix}-22.7_execution_notes.md"
        section_doc.write_text(
            f"""---
title: "Section"
tags: [{required_tag}]
custom_fields:
  document_type: {required_tag}
  status: draft
---

# {artifact_prefix}-22: Section
""",
            encoding="utf-8",
        )

        result = run_project_validation_build(
            project_root=tmp_path,
            doc_type=required_tag,
            layer=layer,
            document_path=section_doc,
            output_dir=None,
        )

        assert result.is_valid
        payload = json.loads(result.report_json)
        checked = payload.get("files_checked", [])
        assert checked == [str(source_doc)]


# =============================================================================
# Template naming migration tests (PLAN-002)
# =============================================================================


def test_template_naming_new_name_only(tmp_path: Path) -> None:
    """BRD-TEMPLATE.yaml (unified) is found when no MVP name exists."""
    from mcp_server.utils.template_naming import resolve_template_path

    layer_dir = tmp_path / "01_BRD"
    layer_dir.mkdir()
    (layer_dir / "BRD-TEMPLATE.yaml").write_text("id: BRD-01\n", encoding="utf-8")

    result = resolve_template_path(layer_dir, "BRD", ".yaml")
    assert result is not None
    assert result.name == "BRD-TEMPLATE.yaml"


def test_template_naming_old_name_only(tmp_path: Path) -> None:
    """BRD-MVP-TEMPLATE.yaml (legacy) is found via fallback."""
    from mcp_server.utils.template_naming import resolve_template_path

    layer_dir = tmp_path / "01_BRD"
    layer_dir.mkdir()
    (layer_dir / "BRD-MVP-TEMPLATE.yaml").write_text("id: BRD-01\n", encoding="utf-8")

    result = resolve_template_path(layer_dir, "BRD", ".yaml")
    assert result is not None
    assert result.name == "BRD-MVP-TEMPLATE.yaml"


def test_template_naming_new_takes_precedence(tmp_path: Path) -> None:
    """When both exist, unified name takes precedence over MVP name."""
    from mcp_server.utils.template_naming import resolve_template_path

    layer_dir = tmp_path / "01_BRD"
    layer_dir.mkdir()
    (layer_dir / "BRD-TEMPLATE.yaml").write_text("id: unified\n", encoding="utf-8")
    (layer_dir / "BRD-MVP-TEMPLATE.yaml").write_text("id: legacy\n", encoding="utf-8")

    result = resolve_template_path(layer_dir, "BRD", ".yaml")
    assert result is not None
    assert result.name == "BRD-TEMPLATE.yaml"


def test_template_naming_non_brd_layer_still_works(tmp_path: Path) -> None:
    """Non-BRD layers using old naming convention still resolve."""
    from mcp_server.utils.template_naming import resolve_template_path

    layer_dir = tmp_path / "02_PRD"
    layer_dir.mkdir()
    (layer_dir / "PRD-MVP-TEMPLATE.yaml").write_text("id: PRD-01\n", encoding="utf-8")

    result = resolve_template_path(layer_dir, "PRD", ".yaml")
    assert result is not None
    assert result.name == "PRD-MVP-TEMPLATE.yaml"
