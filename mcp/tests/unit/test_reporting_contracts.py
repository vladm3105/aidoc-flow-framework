from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.reporting import (  # noqa: E402
    build_family_report_name,
    evaluate_legacy_report_set,
    resolve_legacy_report_policy,
    validate_combined_fix_queue_schema,
    validate_generated_at_has_offset,
    validate_sha256_hash_value,
)


def test_report_family_name_generation_uses_A_R_F_prefixes() -> None:
    assert build_family_report_name(doc_id="SPEC-001", family="audit", version=1) == "SPEC-001.A_audit_report_v001.md"
    assert build_family_report_name(doc_id="SPEC-001", family="review", version=2) == "SPEC-001.R_review_report_v002.md"
    assert build_family_report_name(doc_id="SPEC-001", family="fix", version=3) == "SPEC-001.F_fix_report_v003.md"


def test_lifecycle_to_audit_wrapper_name_mapping_preserves_lineage_fields() -> None:
    from mcp_server.reporting import map_lifecycle_to_audit_wrapper

    mapped = map_lifecycle_to_audit_wrapper(
        doc_id="SPEC-001",
        source_stage="validation-fixed",
        lifecycle="review",
        version=4,
        source_artifact_file="SPEC-001_doc_validation.md",
    )

    assert mapped["report_name"] == "SPEC-001.A_audit_report_v004.md"
    assert mapped["source_processing_stage"] == "validation-fixed"
    assert mapped["source_artifact_file"] == "SPEC-001_doc_validation.md"


def test_generated_at_requires_explicit_timezone_offset() -> None:
    with_offset = datetime.now(tz=timezone.utc).isoformat()
    without_offset = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    assert validate_generated_at_has_offset(with_offset)
    assert not validate_generated_at_has_offset(without_offset)


def test_combined_fix_queue_schema_requires_all_buckets_and_per_finding_fields() -> None:
    errors = validate_combined_fix_queue_schema({"auto_fixable": []})
    assert "missing_bucket:manual_required" in errors
    assert "missing_bucket:blocked" in errors


def test_drift_hash_format_requires_sha256_prefix_and_64_hex() -> None:
    assert validate_sha256_hash_value("sha256:" + "a" * 64)
    assert not validate_sha256_hash_value("sha256:xyz")


def test_legacy_report_policy_defaults_to_ignore() -> None:
    assert resolve_legacy_report_policy(None) == "ignore"


def test_legacy_report_policy_rejects_unknown_value() -> None:
    try:
        resolve_legacy_report_policy("archive")
    except ValueError as exc:
        assert "Unsupported legacy report policy" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_legacy_report_fail_fast_requires_action_when_legacy_reports_exist() -> None:
    decision = evaluate_legacy_report_set(
        policy="fail-fast",
        discovered_legacy_reports=["UCX_review_report.md"],
    )
    assert decision["legacy_policy"] == "fail-fast"
    assert decision["decision"] == "fail-fast"
    assert decision["action_required"] is True
