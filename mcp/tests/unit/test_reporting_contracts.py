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
    build_action_id,
    build_finding_id,
    evaluate_legacy_report_set,
    parse_compatible_finding_id,
    resolve_legacy_report_policy,
    validate_action_id,
    validate_compatible_finding_id,
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


def test_hash_identity_generation_is_deterministic_and_parseable() -> None:
    finding_id_first = build_finding_id(
        priority="P1",
        identity_fields={
            "file": "docs/01_BRD/BRD-01_sample.md",
            "category": "frontmatter",
            "message": "Missing YAML frontmatter",
        },
    )
    finding_id_second = build_finding_id(
        priority="P1",
        identity_fields={
            "file": "docs/01_BRD/BRD-01_sample.md",
            "category": "frontmatter",
            "message": "Missing YAML frontmatter",
        },
    )
    action_id = build_action_id(
        identity_fields={
            "file": "docs/01_BRD/BRD-01_sample.md",
            "recommended_action": "add_frontmatter",
        }
    )

    assert finding_id_first == finding_id_second
    assert validate_compatible_finding_id(finding_id_first) is True
    assert parse_compatible_finding_id(finding_id_first)["family"] == "hash"
    assert validate_action_id(action_id) is True


def test_finding_id_compatibility_accepts_legacy_families() -> None:
    persona_id = parse_compatible_finding_id("ARCHITECT-P1-007")
    remediation_id = parse_compatible_finding_id("REM-P2-013")

    assert persona_id["family"] == "legacy-persona"
    assert remediation_id["family"] == "legacy-remediation"
    assert validate_compatible_finding_id("ARCHITECT-P1-007") is True
    assert validate_compatible_finding_id("REM-P2-013") is True
    assert validate_compatible_finding_id("invalid-id") is False


def test_hash_identity_collision_extends_prefix_length(monkeypatch) -> None:
    import importlib

    module = importlib.import_module("mcp_server.reporting.contracts")
    digests = iter(
        [
            "abcabcabcabc1111111111111111111111111111111111111111111111111111",
            "abcabcabcabc2222222222222222222222222222222222222222222222222222",
        ]
    )
    monkeypatch.setattr(module, "_compute_identity_digest", lambda **_: next(digests))

    used_ids: set[str] = set()
    first = build_finding_id(priority="P1", identity_fields={"file": "a.md"}, existing_ids=used_ids)
    used_ids.add(first)
    second = build_finding_id(priority="P1", identity_fields={"file": "b.md"}, existing_ids=used_ids)

    assert first == "P1-abcabcabcabc"
    assert second.startswith("P1-abcabcabcabc")
    assert second != first


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
