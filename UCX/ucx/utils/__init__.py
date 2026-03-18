"""UCX utilities."""

from ucx.utils.hash import compute_hash, verify_hash
from ucx.utils.file_ops import ensure_dir, read_file, write_file
from ucx.utils.finding_hash import (
    FindingIDGenerator,
    FindingIdentity,
    ActionIDGenerator,
    ActionIdentity,
    is_legacy_finding_id,
    is_hash_finding_id,
    is_legacy_action_id,
    is_hash_action_id,
    extract_priority_from_id,
    normalize_finding_id,
    DUAL_FORMAT_FINDING_PATTERN,
    DUAL_FORMAT_ACTION_PATTERN,
)

__all__ = [
    # Hash utilities
    "compute_hash",
    "verify_hash",
    # File operations
    "ensure_dir",
    "read_file",
    "write_file",
    # Finding ID generation (v1.19.0+)
    "FindingIDGenerator",
    "FindingIdentity",
    "ActionIDGenerator",
    "ActionIdentity",
    "is_legacy_finding_id",
    "is_hash_finding_id",
    "is_legacy_action_id",
    "is_hash_action_id",
    "extract_priority_from_id",
    "normalize_finding_id",
    "DUAL_FORMAT_FINDING_PATTERN",
    "DUAL_FORMAT_ACTION_PATTERN",
]
