from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.reporting import (  # noqa: E402
    build_derived_artifact_name,
    build_family_report_name,
    build_lifecycle_report_name,
    build_source_artifact_name,
    build_validation_report_name,
    resolve_operation_inputs,
    write_versioned_report_atomic,
)


def _touch(path: Path, content: str = "fixture") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_staged_workflow_resolves_required_artifacts_across_full_lifecycle(tmp_path: Path) -> None:
    doc_id = "SPEC-001"
    slug = "platform_architecture"

    _touch(tmp_path / build_source_artifact_name(doc_id=doc_id, slug=slug))
    _touch(tmp_path / build_validation_report_name(doc_id=doc_id))
    _touch(tmp_path / build_derived_artifact_name(doc_id=doc_id, slug=slug, stage="validation-fixed"))
    _touch(tmp_path / build_family_report_name(doc_id=doc_id, family="review", version=1))
    _touch(tmp_path / build_family_report_name(doc_id=doc_id, family="audit", version=1))
    _touch(tmp_path / build_lifecycle_report_name(doc_id=doc_id, source_stage="validation-fixed", report_type="remediation", version=1))

    create_inputs = resolve_operation_inputs(folder=tmp_path, doc_id=doc_id, slug=slug, operation="create")
    validate_inputs = resolve_operation_inputs(folder=tmp_path, doc_id=doc_id, slug=slug, operation="validate")
    validate_fix_inputs = resolve_operation_inputs(folder=tmp_path, doc_id=doc_id, slug=slug, operation="validate_fix")
    review_inputs = resolve_operation_inputs(folder=tmp_path, doc_id=doc_id, slug=slug, operation="review")
    remediate_content_inputs = resolve_operation_inputs(folder=tmp_path, doc_id=doc_id, slug=slug, operation="remediate_content")
    remediate_apply_inputs = resolve_operation_inputs(folder=tmp_path, doc_id=doc_id, slug=slug, operation="remediate_apply")

    assert create_inputs["status"] == "ready"
    assert validate_inputs["source_artifact"] == build_source_artifact_name(doc_id=doc_id, slug=slug)
    assert validate_fix_inputs["validation_report"] == build_validation_report_name(doc_id=doc_id)
    assert review_inputs["validation_fixed_artifact"] == build_derived_artifact_name(doc_id=doc_id, slug=slug, stage="validation-fixed")
    assert remediate_content_inputs["review_report"] == build_family_report_name(doc_id=doc_id, family="audit", version=1)
    assert remediate_apply_inputs["remediation_report"] == build_lifecycle_report_name(
        doc_id=doc_id,
        source_stage="validation-fixed",
        report_type="remediation",
        version=1,
    )


def test_review_operation_fails_explicitly_when_validation_fixed_artifact_absent(tmp_path: Path) -> None:
    doc_id = "SPEC-002"
    slug = "review_contracts"

    _touch(tmp_path / build_source_artifact_name(doc_id=doc_id, slug=slug))
    _touch(tmp_path / build_validation_report_name(doc_id=doc_id))

    result = resolve_operation_inputs(folder=tmp_path, doc_id=doc_id, slug=slug, operation="review")

    assert result["status"] == "error"
    assert result["missing_prerequisite_type"] == "validation_fixed_artifact"
    assert result["expected_filename_pattern"] == build_derived_artifact_name(doc_id=doc_id, slug=slug, stage="validation-fixed")


def test_versioned_report_write_retries_after_collision_and_allocates_next_version(tmp_path: Path) -> None:
    _touch(tmp_path / build_family_report_name(doc_id="SPEC-003", family="audit", version=1), "existing v1")

    collision_state = {"used": False}

    def collision_hook(candidate_path: Path) -> None:
        if collision_state["used"]:
            return
        collision_state["used"] = True
        candidate_path.write_text("competing writer", encoding="utf-8")

    written = write_versioned_report_atomic(
        report_dir=tmp_path,
        report_name_factory=lambda version: build_family_report_name(doc_id="SPEC-003", family="audit", version=version),
        content="new content",
        collision_hook=collision_hook,
    )

    assert written.name == build_family_report_name(doc_id="SPEC-003", family="audit", version=3)
    assert written.read_text(encoding="utf-8") == "new content"
