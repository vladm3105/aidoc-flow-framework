from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.core import (  # noqa: E402
    apply_source_eligibility,
    evaluate_upstream_missing,
    route_optional_layer,
)


def test_source_eligibility_excludes_archived_paths_without_override() -> None:
    result = apply_source_eligibility(
        [
            "docs/01_BRD/BRD-01.md",
            "docs/archive/BRD-LEGACY.md",
            "docs/ARCHIVED/REQ-OLD.md",
        ],
        archive_override_enabled=False,
    )

    assert result["eligible_sources"] == ["docs/01_BRD/BRD-01.md"]
    source_filter = result["source_filter"]
    assert source_filter["archive_exclusion_enabled"] is True
    assert source_filter["excluded_archived_candidates"] == 2


def test_upstream_missing_emits_skip_metadata_fields() -> None:
    result = evaluate_upstream_missing(
        operation="brd_remediate_apply",
        upstream_type="review_report",
        upstream_id="BRD-01.R_review_report_v001.md",
        upstream_exists=False,
        optional_upstream=False,
    )

    assert result["skip"] is True
    metadata = result["skip_metadata"]
    assert metadata["skipped_operation"] == "brd_remediate_apply"
    assert metadata["missing_upstream_type"] == "review_report"
    assert metadata["missing_upstream_id"] == "BRD-01.R_review_report_v001.md"
    assert metadata["skip_reason"] == "required_upstream_missing"


def test_optional_layer_skip_populates_routing_metadata() -> None:
    result = route_optional_layer(
        requested_layer="ctr",
        next_layer="spec",
        operation="spec_validate",
        upstream_type="ctr_artifact",
        upstream_id="CTR-01",
        upstream_exists=False,
        optional_layer=True,
    )

    assert result["route_to_layer"] == "spec"
    assert result["rerouted"] is True
    assert result["routing_metadata"]["optional_layer_skipped"] is True
    assert result["routing_metadata"]["requested_layer"] == "ctr"
    assert result["routing_metadata"]["resolved_layer"] == "spec"
    assert result["skip_metadata"]["skip_reason"] == "optional_upstream_missing"
