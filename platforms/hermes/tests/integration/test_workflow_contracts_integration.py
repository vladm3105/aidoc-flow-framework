from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.core.workflow_contracts import (  # noqa: E402
    apply_source_eligibility,
    evaluate_upstream_missing,
    route_optional_layer,
)


def test_pipeline_discovery_excludes_archived_artifacts_by_default() -> None:
    discovered = [
        "docs/01_BRD/BRD-01.md",
        "docs/02_PRD/PRD-01.md",
        "docs/00_REF/archived/reference.md",
        "tmp/archive/stale-output.md",
    ]

    selection = apply_source_eligibility(discovered, archive_override_enabled=False)
    selected = selection["eligible_sources"]

    assert "docs/01_BRD/BRD-01.md" in selected
    assert "docs/02_PRD/PRD-01.md" in selected
    assert "docs/00_REF/archived/reference.md" not in selected
    assert "tmp/archive/stale-output.md" not in selected
    assert selection["source_filter"]["excluded_archived_candidates"] == 2


def test_downstream_operation_skips_when_required_upstream_missing() -> None:
    decision = evaluate_upstream_missing(
        operation="prd_remediate_apply",
        upstream_type="review_report",
        upstream_id="PRD-01.R_review_report_v3.md",
        upstream_exists=False,
        optional_upstream=False,
    )

    assert decision["status"] == "required-upstream-missing"
    assert decision["skip"] is True
    assert decision["skip_metadata"] == {
        "skipped_operation": "prd_remediate_apply",
        "missing_upstream_type": "review_report",
        "missing_upstream_id": "PRD-01.R_review_report_v3.md",
        "skip_reason": "required_upstream_missing",
    }


def test_missing_optional_ctr_reroutes_to_next_layer_with_skip_metadata() -> None:
    route = route_optional_layer(
        requested_layer="ctr",
        next_layer="spec",
        operation="spec_review",
        upstream_type="ctr_artifact",
        upstream_id="CTR-11",
        upstream_exists=False,
        optional_layer=True,
    )

    assert route["rerouted"] is True
    assert route["route_to_layer"] == "spec"
    assert route["routing_metadata"] == {
        "optional_layer_skipped": True,
        "requested_layer": "ctr",
        "resolved_layer": "spec",
    }
    assert route["skip_metadata"] == {
        "skipped_operation": "spec_review",
        "missing_upstream_type": "ctr_artifact",
        "missing_upstream_id": "CTR-11",
        "skip_reason": "optional_upstream_missing",
    }
