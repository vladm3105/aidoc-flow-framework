from __future__ import annotations

from pathlib import Path


def _is_archived_path(path: str) -> bool:
    normalized = path.replace("\\", "/").casefold()
    segments = [segment for segment in normalized.split("/") if segment]
    return any(segment in {"archive", "archived"} for segment in segments)


def apply_source_eligibility(
    candidates: list[str | Path],
    *,
    archive_override_enabled: bool = False,
) -> dict[str, object]:
    """Filter source candidates under the SPEC-001 archive exclusion contract."""

    candidate_paths = [str(candidate) for candidate in candidates]
    archive_exclusion_enabled = not archive_override_enabled

    if not archive_exclusion_enabled:
        return {
            "eligible_sources": candidate_paths,
            "source_filter": {
                "archive_exclusion_enabled": False,
                "excluded_archived_candidates": 0,
                "excluded_archived_paths": [],
            },
        }

    eligible_sources: list[str] = []
    excluded_archived_paths: list[str] = []
    for path in candidate_paths:
        if _is_archived_path(path):
            excluded_archived_paths.append(path)
        else:
            eligible_sources.append(path)

    return {
        "eligible_sources": eligible_sources,
        "source_filter": {
            "archive_exclusion_enabled": True,
            "excluded_archived_candidates": len(excluded_archived_paths),
            "excluded_archived_paths": excluded_archived_paths,
        },
    }


def evaluate_upstream_missing(
    *,
    operation: str,
    upstream_type: str,
    upstream_id: str,
    upstream_exists: bool,
    optional_upstream: bool = False,
) -> dict[str, object]:
    """Emit machine-parseable skip metadata for missing required upstream artifacts."""

    if upstream_exists:
        return {
            "operation": operation,
            "status": "ready",
            "skip": False,
        }

    if optional_upstream:
        return {
            "operation": operation,
            "status": "optional-upstream-missing",
            "skip": False,
            "skip_metadata": {
                "skipped_operation": operation,
                "missing_upstream_type": upstream_type,
                "missing_upstream_id": upstream_id,
                "skip_reason": "optional_upstream_missing",
            },
        }

    return {
        "operation": operation,
        "status": "required-upstream-missing",
        "skip": True,
        "skip_metadata": {
            "skipped_operation": operation,
            "missing_upstream_type": upstream_type,
            "missing_upstream_id": upstream_id,
            "skip_reason": "required_upstream_missing",
        },
    }


def route_optional_layer(
    *,
    requested_layer: str,
    next_layer: str,
    operation: str,
    upstream_type: str,
    upstream_id: str,
    upstream_exists: bool,
    optional_layer: bool,
) -> dict[str, object]:
    """Route to next layer when an optional upstream layer is missing."""

    if upstream_exists:
        return {
            "route_to_layer": requested_layer,
            "rerouted": False,
            "routing_metadata": {
                "optional_layer_skipped": False,
                "requested_layer": requested_layer,
                "resolved_layer": requested_layer,
            },
        }

    if not optional_layer:
        missing = evaluate_upstream_missing(
            operation=operation,
            upstream_type=upstream_type,
            upstream_id=upstream_id,
            upstream_exists=False,
            optional_upstream=False,
        )
        return {
            "route_to_layer": requested_layer,
            "rerouted": False,
            "routing_metadata": {
                "optional_layer_skipped": False,
                "requested_layer": requested_layer,
                "resolved_layer": requested_layer,
            },
            "skip_metadata": missing["skip_metadata"],
        }

    optional_missing = evaluate_upstream_missing(
        operation=operation,
        upstream_type=upstream_type,
        upstream_id=upstream_id,
        upstream_exists=False,
        optional_upstream=True,
    )
    return {
        "route_to_layer": next_layer,
        "rerouted": True,
        "routing_metadata": {
            "optional_layer_skipped": True,
            "requested_layer": requested_layer,
            "resolved_layer": next_layer,
        },
        "skip_metadata": optional_missing["skip_metadata"],
    }


def run_rollback_smoke(
    *, source_artifact: str | None, derived_artifacts: list[str]
) -> dict[str, object]:
    """Validate that rollback can target the canonical source artifact without mutating derived artifacts."""

    if source_artifact is None:
        return {
            "status": "error",
            "rollback_ready": False,
            "missing_prerequisite_type": "source_artifact",
        }

    active_artifact = derived_artifacts[-1] if derived_artifacts else source_artifact
    return {
        "status": "ok",
        "rollback_ready": True,
        "rollback_action": "switch_execution_target_to_source",
        "source_artifact": source_artifact,
        "active_artifact": active_artifact,
        "preserved_artifacts": list(derived_artifacts),
    }
