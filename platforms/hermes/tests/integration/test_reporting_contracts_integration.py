from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.reporting import (  # noqa: E402
    ReportFamilySelection,
    apply_repository_timezone_policy,
    choose_preferred_review_input,
    enforce_drift_hash_requirements,
    map_lifecycle_to_audit_wrapper,
    normalize_combined_fix_queue,
)


def test_audit_wrapper_outputs_deterministic_family_selection_and_versioned_names() -> None:
    candidates = [
        ReportFamilySelection(
            family="review",
            path="SPEC-001.R_review_report_v5.md",
            version=5,
            timestamp="2026-03-24T10:00:00+00:00",
        ),
        ReportFamilySelection(
            family="audit",
            path="SPEC-001.A_audit_report_v5.md",
            version=5,
            timestamp="2026-03-24T10:00:00+00:00",
        ),
    ]
    selected_first = choose_preferred_review_input(candidates)
    selected_second = choose_preferred_review_input(candidates)
    assert selected_first.path == "SPEC-001.A_audit_report_v5.md"
    assert selected_first == selected_second


def test_multi_stage_run_preserves_deterministic_name_mapping_across_reports() -> None:
    review_map = map_lifecycle_to_audit_wrapper(
        doc_id="SPEC-001",
        source_stage="validation-fixed",
        lifecycle="review",
        version=1,
        source_artifact_file="SPEC-001_doc_validation.md",
    )
    remediation_map = map_lifecycle_to_audit_wrapper(
        doc_id="SPEC-001",
        source_stage="validation-fixed",
        lifecycle="remediate_apply",
        version=2,
        source_artifact_file="SPEC-001_doc_validation.md",
    )
    assert review_map["report_name"] == "SPEC-001.A_audit_report_v1.md"
    assert remediation_map["report_name"] == "SPEC-001.F_fix_report_v2.md"
    assert review_map["source_artifact_id"] == remediation_map["source_artifact_id"]


def test_report_generation_applies_repository_timezone_policy_when_enabled() -> None:
    ts = apply_repository_timezone_policy(
        dt=datetime(2026, 3, 24, 12, 0, 0, tzinfo=UTC),
        timezone_name="America/New_York",
    )
    assert ts.endswith("-04:00") or ts.endswith("-05:00")


def test_fixer_consumes_combined_queue_and_classifies_findings_by_bucket() -> None:
    queue = {
        "auto_fixable": [
            {
                "source": "validator",
                "code": "GATE-01",
                "severity": "P1",
                "file": "a.md",
                "section": "1.0",
                "action_hint": "replace placeholder",
                "confidence": "high",
            }
        ],
        "manual_required": [
            {
                "source": "reviewer",
                "code": "GATE-06",
                "severity": "P0",
                "file": "b.md",
                "section": "2.0",
                "action_hint": "manual architecture decision",
                "confidence": "manual-required",
            }
        ],
        "blocked": [],
    }
    normalized = normalize_combined_fix_queue(queue)
    assert len(normalized["auto_fixable"]) == 1
    assert len(normalized["manual_required"]) == 1
    assert normalized["blocked"] == []


def test_drift_enabled_run_enforces_required_upstream_hash_entries() -> None:
    errors = enforce_drift_hash_requirements(
        drift_enabled=True,
        required_upstreams=["REQ-001", "SYS-001"],
        entries=[
            {
                "upstream_artifact": "REQ-001",
                "hash_algorithm": "sha256",
                "hash_value": "sha256:" + "a" * 64,
            },
        ],
    )
    assert "missing_upstream:SYS-001" in errors
