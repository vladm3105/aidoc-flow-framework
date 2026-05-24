from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, cast
from zoneinfo import ZoneInfo

FAMILY_PREFIX = {
    "audit": "A",
    "review": "R",
    "fix": "F",
}

LEGACY_REPORT_POLICY_VALUES = ("import", "ignore", "fail-fast")
DEFAULT_LEGACY_REPORT_POLICY = "ignore"

REQUIRED_FIX_BUCKETS = ("auto_fixable", "manual_required", "blocked")
REQUIRED_FIX_FIELDS = ("source", "code", "severity", "file", "section", "action_hint", "confidence")
ALLOWED_CONFIDENCE = {"high", "medium", "manual-required"}
FINDING_PRIORITY_CODES = ("P0", "P1", "P2", "P3")
HASH_FINDING_ID_PATTERN = re.compile(r"^(P[0-3])-([0-9a-f]{8,64})$")
HASH_ACTION_ID_PATTERN = re.compile(r"^ACT-([0-9a-f]{8,64})$")
LEGACY_PERSONA_FINDING_ID_PATTERN = re.compile(r"^([A-Z]+)-P([0-3])-(\d{3})$")
LEGACY_REMEDIATION_FINDING_ID_PATTERN = re.compile(r"^(REM)-P([0-3])-(\d{3})$")


@dataclass(frozen=True)
class ReportFamilySelection:
    family: str
    path: str
    version: int
    timestamp: str


@dataclass(frozen=True)
class ArtifactDiscoveryResult:
    source_artifact: str | None
    validation_report: str | None
    validation_fixed_artifact: str | None
    remediated_artifact: str | None
    latest_review_report: str | None
    latest_remediation_report: str | None
    errors: tuple[str, ...]


def build_family_report_name(*, doc_id: str, family: str, version: int) -> str:
    if family not in FAMILY_PREFIX:
        raise ValueError(f"Unsupported family: {family}")
    if version <= 0:
        raise ValueError("Version must be positive")
    prefix = FAMILY_PREFIX[family]
    suffix = "audit" if family == "audit" else "review" if family == "review" else "fix"
    return f"{doc_id}.{prefix}_{suffix}_report_v{version}.md"


def build_source_artifact_name(*, doc_id: str, slug: str) -> str:
    return f"{doc_id}_{slug}.md"


def build_derived_artifact_name(*, doc_id: str, slug: str, stage: str) -> str:
    if stage == "validation-fixed":
        return f"{doc_id}_{slug}_validation.md"
    if stage == "remediated":
        return f"{doc_id}_{slug}_remediated.md"
    raise ValueError(f"Unsupported derived stage: {stage}")


def build_validation_report_name(*, doc_id: str) -> str:
    return f"{doc_id}_validation_report.md"


def build_lifecycle_report_name(
    *, doc_id: str, source_stage: str, report_type: str, version: int
) -> str:
    if report_type not in {"review", "remediation"}:
        raise ValueError(f"Unsupported lifecycle report type: {report_type}")
    if version <= 0:
        raise ValueError("Version must be positive")
    return f"{doc_id}_{source_stage}_{report_type}_report_v{version}.md"


def choose_preferred_review_input(candidates: list[ReportFamilySelection]) -> ReportFamilySelection:
    if not candidates:
        raise ValueError("No candidates provided")

    ranked = sorted(
        candidates,
        key=lambda item: (
            item.version,
            item.timestamp,
            1 if item.family == "audit" else 0,
        ),
        reverse=True,
    )

    top = ranked[0]
    tie_group = [c for c in ranked if c.version == top.version and c.timestamp == top.timestamp]
    audit_tie = next((c for c in tie_group if c.family == "audit"), None)
    return audit_tie or top


def _extract_version(path_name: str) -> int | None:
    match = re.search(r"_v(\d+)\.md$", path_name)
    if not match:
        return None
    return int(match.group(1))


def _select_latest_lifecycle_report(file_names: list[str], *, suffix: str) -> str | None:
    candidates = [name for name in file_names if name.endswith(suffix)]
    raw_ranked = [(name, _extract_version(name)) for name in candidates]
    ranked: list[tuple[str, int]] = [
        (name, version) for name, version in raw_ranked if version is not None
    ]
    if not ranked:
        return None
    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[0][0]


def discover_artifacts(*, folder: Path, doc_id: str, slug: str) -> ArtifactDiscoveryResult:
    file_names = sorted(path.name for path in folder.iterdir() if path.is_file())

    source_name = build_source_artifact_name(doc_id=doc_id, slug=slug)
    validation_name = build_validation_report_name(doc_id=doc_id)
    validation_fixed_name = build_derived_artifact_name(
        doc_id=doc_id, slug=slug, stage="validation-fixed"
    )
    remediated_name = build_derived_artifact_name(doc_id=doc_id, slug=slug, stage="remediated")

    audit_candidates: list[ReportFamilySelection] = []
    for name in file_names:
        if not name.startswith(f"{doc_id}."):
            continue
        version = _extract_version(name)
        if version is None:
            continue
        if ".A_audit_report_" in name:
            audit_candidates.append(
                ReportFamilySelection(
                    family="audit", path=name, version=version, timestamp=f"v{version}"
                )
            )
        elif ".R_review_report_" in name:
            audit_candidates.append(
                ReportFamilySelection(
                    family="review", path=name, version=version, timestamp=f"v{version}"
                )
            )

    latest_review_report = (
        choose_preferred_review_input(audit_candidates).path
        if audit_candidates
        else _select_latest_lifecycle_report(
            file_names,
            suffix="_review_report_v1.md",
        )
    )
    if latest_review_report is None:
        lifecycle_review_candidates = [name for name in file_names if "_review_report_v" in name]
        latest_review_report = _select_latest_lifecycle_report(
            lifecycle_review_candidates, suffix=".md"
        )

    lifecycle_remediation_candidates = [
        name for name in file_names if "_remediation_report_v" in name or ".F_fix_report_v" in name
    ]
    latest_remediation_report = None
    if lifecycle_remediation_candidates:
        latest_remediation_report = sorted(
            lifecycle_remediation_candidates,
            key=lambda item: (_extract_version(item) or 0, item),
            reverse=True,
        )[0]

    source_matches = [name for name in file_names if name == source_name]
    errors: list[str] = []
    if len(source_matches) > 1:
        errors.append(f"duplicate_source:{source_name}")

    return ArtifactDiscoveryResult(
        source_artifact=source_name if source_name in file_names else None,
        validation_report=validation_name if validation_name in file_names else None,
        validation_fixed_artifact=validation_fixed_name
        if validation_fixed_name in file_names
        else None,
        remediated_artifact=remediated_name if remediated_name in file_names else None,
        latest_review_report=latest_review_report,
        latest_remediation_report=latest_remediation_report,
        errors=tuple(errors),
    )


def resolve_operation_inputs(
    *, folder: Path, doc_id: str, slug: str, operation: str
) -> dict[str, object]:
    discovered = discover_artifacts(folder=folder, doc_id=doc_id, slug=slug)
    source_name = build_source_artifact_name(doc_id=doc_id, slug=slug)

    if discovered.errors:
        return {
            "status": "error",
            "operation": operation,
            "errors": list(discovered.errors),
        }

    if operation == "create":
        return {
            "status": "ready",
            "operation": operation,
            "target_path": str(folder / source_name),
        }

    if discovered.source_artifact is None:
        return {
            "status": "error",
            "operation": operation,
            "missing_prerequisite_type": "source_artifact",
            "expected_filename_pattern": source_name,
        }

    if operation == "validate":
        return {
            "status": "ready",
            "operation": operation,
            "source_artifact": discovered.source_artifact,
        }

    if operation == "validate_fix":
        if discovered.validation_report is None:
            return {
                "status": "error",
                "operation": operation,
                "missing_prerequisite_type": "validation_report",
                "expected_filename_pattern": build_validation_report_name(doc_id=doc_id),
            }
        return {
            "status": "ready",
            "operation": operation,
            "source_artifact": discovered.source_artifact,
            "validation_report": discovered.validation_report,
        }

    if operation == "review":
        if discovered.validation_fixed_artifact is None:
            return {
                "status": "error",
                "operation": operation,
                "missing_prerequisite_type": "validation_fixed_artifact",
                "expected_filename_pattern": build_derived_artifact_name(
                    doc_id=doc_id, slug=slug, stage="validation-fixed"
                ),
            }
        return {
            "status": "ready",
            "operation": operation,
            "validation_fixed_artifact": discovered.validation_fixed_artifact,
        }

    if operation == "remediate_content":
        if discovered.validation_fixed_artifact is None:
            return {
                "status": "error",
                "operation": operation,
                "missing_prerequisite_type": "validation_fixed_artifact",
                "expected_filename_pattern": build_derived_artifact_name(
                    doc_id=doc_id, slug=slug, stage="validation-fixed"
                ),
            }
        if discovered.latest_review_report is None:
            return {
                "status": "error",
                "operation": operation,
                "missing_prerequisite_type": "review_report",
                "expected_filename_pattern": f"{doc_id}.A_audit_report_vN.md | {doc_id}.R_review_report_vN.md | {doc_id}_validation-fixed_review_report_vN.md",
            }
        return {
            "status": "ready",
            "operation": operation,
            "validation_fixed_artifact": discovered.validation_fixed_artifact,
            "review_report": discovered.latest_review_report,
        }

    if operation == "remediate_apply":
        if discovered.validation_fixed_artifact is None:
            return {
                "status": "error",
                "operation": operation,
                "missing_prerequisite_type": "validation_fixed_artifact",
                "expected_filename_pattern": build_derived_artifact_name(
                    doc_id=doc_id, slug=slug, stage="validation-fixed"
                ),
            }
        if discovered.latest_remediation_report is None:
            return {
                "status": "error",
                "operation": operation,
                "missing_prerequisite_type": "remediation_report",
                "expected_filename_pattern": f"{doc_id}_validation-fixed_remediation_report_vN.md | {doc_id}.F_fix_report_vN.md",
            }
        return {
            "status": "ready",
            "operation": operation,
            "validation_fixed_artifact": discovered.validation_fixed_artifact,
            "remediation_report": discovered.latest_remediation_report,
        }

    raise ValueError(f"Unsupported operation: {operation}")


def write_versioned_report_atomic(
    *,
    report_dir: Path,
    report_name_factory: Callable[[int], str],
    content: str,
    max_attempts: int = 3,
    collision_hook: Callable[[Path], None] | None = None,
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)

    for _attempt in range(max_attempts):
        existing_versions = [
            version
            for path in report_dir.iterdir()
            if path.is_file()
            for version in [_extract_version(path.name)]
            if version is not None
        ]
        candidate_version = (max(existing_versions) if existing_versions else 0) + 1
        candidate_name = report_name_factory(candidate_version)
        candidate_path = report_dir / candidate_name
        temp_path = report_dir / f".{candidate_name}.tmp"

        temp_path.write_text(content, encoding="utf-8")
        if collision_hook is not None:
            collision_hook(candidate_path)

        if candidate_path.exists():
            temp_path.unlink(missing_ok=True)
            continue

        os.replace(temp_path, candidate_path)
        return candidate_path

    raise FileExistsError("Version allocation failed after bounded retries")


def map_lifecycle_to_audit_wrapper(
    *,
    doc_id: str,
    source_stage: str,
    lifecycle: str,
    version: int,
    source_artifact_file: str,
) -> dict[str, str]:
    if lifecycle == "review":
        family = "audit"
    elif lifecycle == "remediate_apply":
        family = "fix"
    else:
        raise ValueError(f"Unsupported lifecycle: {lifecycle}")

    report_name = build_family_report_name(doc_id=doc_id, family=family, version=version)
    return {
        "report_name": report_name,
        "family": family,
        "source_artifact_id": doc_id,
        "source_processing_stage": source_stage,
        "source_artifact_file": source_artifact_file,
    }


def _normalize_identity_value(value: object) -> object:
    if isinstance(value, str):
        return " ".join(value.split()).casefold()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {
            str(key): _normalize_identity_value(val)
            for key, val in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_identity_value(item) for item in value]
    return value


def _compute_identity_digest(*, namespace: str, identity_fields: dict[str, object]) -> str:
    normalized = {
        "namespace": namespace,
        "identity_fields": {
            key: _normalize_identity_value(value) for key, value in sorted(identity_fields.items())
        },
    }
    serialized = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _allocate_hash_identity(
    *, prefix: str, digest: str, existing_ids: set[str] | None, initial_hex_length: int
) -> str:
    if initial_hex_length < 8:
        raise ValueError("initial_hex_length must be at least 8")

    reserved = existing_ids or set()
    for length in range(initial_hex_length, len(digest) + 1):
        candidate = f"{prefix}-{digest[:length]}"
        if candidate not in reserved:
            return candidate

    raise ValueError(f"Unable to allocate unique {prefix} identity from digest")


def build_finding_id(
    *,
    priority: str,
    identity_fields: dict[str, object],
    existing_ids: set[str] | None = None,
    initial_hex_length: int = 12,
) -> str:
    if priority not in FINDING_PRIORITY_CODES:
        supported = ", ".join(FINDING_PRIORITY_CODES)
        raise ValueError(
            f"Unsupported finding priority: {priority!r}. Supported values: {supported}"
        )

    digest = _compute_identity_digest(
        namespace="finding", identity_fields={"priority": priority, **identity_fields}
    )
    return _allocate_hash_identity(
        prefix=priority,
        digest=digest,
        existing_ids=existing_ids,
        initial_hex_length=initial_hex_length,
    )


def build_action_id(
    *,
    identity_fields: dict[str, object],
    existing_ids: set[str] | None = None,
    initial_hex_length: int = 12,
) -> str:
    digest = _compute_identity_digest(namespace="action", identity_fields=identity_fields)
    return _allocate_hash_identity(
        prefix="ACT",
        digest=digest,
        existing_ids=existing_ids,
        initial_hex_length=initial_hex_length,
    )


def parse_compatible_finding_id(value: str) -> dict[str, object]:
    match = HASH_FINDING_ID_PATTERN.match(value)
    if match:
        return {
            "family": "hash",
            "priority": match.group(1),
            "hex": match.group(2),
            "legacy": False,
        }

    match = LEGACY_REMEDIATION_FINDING_ID_PATTERN.match(value)
    if match:
        return {
            "family": "legacy-remediation",
            "persona": match.group(1),
            "priority": f"P{match.group(2)}",
            "sequence": int(match.group(3)),
            "legacy": True,
        }

    match = LEGACY_PERSONA_FINDING_ID_PATTERN.match(value)
    if match:
        return {
            "family": "legacy-persona",
            "persona": match.group(1),
            "priority": f"P{match.group(2)}",
            "sequence": int(match.group(3)),
            "legacy": True,
        }

    raise ValueError(f"Unsupported finding ID format: {value!r}")


def validate_compatible_finding_id(value: str) -> bool:
    try:
        parse_compatible_finding_id(value)
    except ValueError:
        return False
    return True


def validate_action_id(value: str) -> bool:
    return HASH_ACTION_ID_PATTERN.match(value) is not None


def validate_generated_at_has_offset(value: str) -> bool:
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:\d{2})$"
    return re.match(pattern, value) is not None


def apply_repository_timezone_policy(*, dt: datetime, timezone_name: str | None) -> str:
    if timezone_name:
        dt = dt.astimezone(ZoneInfo(timezone_name))
    return dt.isoformat()


def validate_combined_fix_queue_schema(queue: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for bucket in REQUIRED_FIX_BUCKETS:
        if bucket not in queue:
            errors.append(f"missing_bucket:{bucket}")
            continue

        entries = queue[bucket]
        if not isinstance(entries, list):
            errors.append(f"bucket_not_list:{bucket}")
            continue

        for idx, item in enumerate(entries):
            if not isinstance(item, dict):
                errors.append(f"entry_not_dict:{bucket}:{idx}")
                continue
            for field in REQUIRED_FIX_FIELDS:
                if field not in item:
                    errors.append(f"missing_field:{bucket}:{idx}:{field}")
            confidence = item.get("confidence")
            if confidence is not None and confidence not in ALLOWED_CONFIDENCE:
                errors.append(f"invalid_confidence:{bucket}:{idx}:{confidence}")

    return errors


def normalize_combined_fix_queue(queue: dict[str, object]) -> dict[str, list[dict[str, object]]]:
    errors = validate_combined_fix_queue_schema(queue)
    if errors:
        raise ValueError(";".join(errors))

    normalized: dict[str, list[dict[str, object]]] = {}
    for bucket in REQUIRED_FIX_BUCKETS:
        bucket_entries = cast(list[dict[str, Any]], queue[bucket])
        normalized[bucket] = sorted(
            bucket_entries,
            key=lambda item: (str(item["file"]), str(item["code"]), str(item["section"])),
        )
    return normalized


def validate_sha256_hash_value(value: str) -> bool:
    return re.match(r"^sha256:[0-9a-f]{64}$", value) is not None


def enforce_drift_hash_requirements(
    *,
    drift_enabled: bool,
    required_upstreams: list[str],
    entries: list[dict[str, str]],
) -> list[str]:
    if not drift_enabled:
        return []

    errors: list[str] = []
    by_upstream = {entry.get("upstream_artifact", ""): entry for entry in entries}

    for upstream in required_upstreams:
        if upstream not in by_upstream:
            errors.append(f"missing_upstream:{upstream}")
            continue
        entry = by_upstream[upstream]
        hash_value = entry.get("hash_value", "")
        if not validate_sha256_hash_value(hash_value):
            errors.append(f"invalid_hash:{upstream}")

    return errors


def resolve_legacy_report_policy(configured_policy: str | None) -> str:
    policy = (configured_policy or DEFAULT_LEGACY_REPORT_POLICY).strip().casefold()
    if policy not in LEGACY_REPORT_POLICY_VALUES:
        supported = ", ".join(LEGACY_REPORT_POLICY_VALUES)
        raise ValueError(
            f"Unsupported legacy report policy: {configured_policy!r}. Supported values: {supported}"
        )
    return policy


def evaluate_legacy_report_set(
    *,
    policy: str,
    discovered_legacy_reports: list[str],
) -> dict[str, object]:
    resolved_policy = resolve_legacy_report_policy(policy)

    if not discovered_legacy_reports:
        return {
            "legacy_policy": resolved_policy,
            "legacy_reports_found": 0,
            "decision": "none",
            "action_required": False,
        }

    if resolved_policy == "ignore":
        decision = "ignored"
        action_required = False
    elif resolved_policy == "import":
        decision = "import-required"
        action_required = True
    else:
        decision = "fail-fast"
        action_required = True

    return {
        "legacy_policy": resolved_policy,
        "legacy_reports_found": len(discovered_legacy_reports),
        "legacy_reports": sorted(discovered_legacy_reports),
        "decision": decision,
        "action_required": action_required,
    }
