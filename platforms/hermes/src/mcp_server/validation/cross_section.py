"""Generic cross-section validation rules for all SDD layers.

Rules implemented:
  SDD-XS-001  Traceability ID Existence
  SDD-XS-002  Readiness Score Plausibility
  SDD-XS-003  Diagram Registry Present
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ELEMENT_ID_RE = re.compile(r"^[A-Z]{2,8}\.\d{2,}\.\d{2,}\.[0-9a-f]{4,8}$")
_ELEMENT_ID_INLINE_RE = re.compile(r"[A-Z]{2,8}\.\d{2,}\.\d{2,}\.[0-9a-f]{4,8}")
_SCORE_RE = re.compile(r"(\d+)\s*/\s*(\d+)")

READINESS_SCORE_FIELDS: dict[str, str] = {
    "brd": "prd_ready_score",
    "prd": "ears_ready_score",
    "ears": "bdd_ready_score",
    "bdd": "adr_ready_score",
    "adr": "spec_ready_score",
    "spec": "tdd_ready_score",
    "tdd": "iplan_ready_score",
}

MAX_CUMULATIVE_TAGS: dict[str, int] = {
    "brd": 1,
    "prd": 2,
    "ears": 3,
    "bdd": 4,
    "adr": 5,
    "spec": 6,
    "tdd": 7,
    "iplan": 8,
}

_DIAGRAM_LAYERS: frozenset[str] = frozenset({"brd", "prd", "adr", "spec"})

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _collect_ids_recursive(node: object) -> set[str]:
    """Walk *node* and return every ``id`` value matching the element-ID pattern."""
    ids: set[str] = set()

    if isinstance(node, dict):
        for key, value in node.items():
            if key == "id" and isinstance(value, str) and _ELEMENT_ID_RE.match(value):
                ids.add(value)
            ids.update(_collect_ids_recursive(value))
    elif isinstance(node, list):
        for item in node:
            ids.update(_collect_ids_recursive(item))

    return ids


def _collect_string_ids(node: object) -> set[str]:
    """Extract all element-ID-shaped strings from *node* (any depth)."""
    ids: set[str] = set()

    if isinstance(node, str):
        ids.update(_ELEMENT_ID_INLINE_RE.findall(node))
    elif isinstance(node, dict):
        for value in node.values():
            ids.update(_collect_string_ids(value))
    elif isinstance(node, list):
        for item in node:
            ids.update(_collect_string_ids(item))

    return ids


def _find_field_recursive(node: object, field_name: str) -> object | None:
    """Return the first value whose key equals *field_name* (depth-first)."""
    if isinstance(node, dict):
        if field_name in node:
            return node[field_name]
        for value in node.values():
            result = _find_field_recursive(value, field_name)
            if result is not None:
                return result
    elif isinstance(node, list):
        for item in node:
            result = _find_field_recursive(item, field_name)
            if result is not None:
                return result
    return None


# ---------------------------------------------------------------------------
# SDD-XS-001 -- Traceability ID Existence
# ---------------------------------------------------------------------------


def _check_traceability_id_existence(
    yaml_data: dict[str, object],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Verify every ID referenced in ``traceability`` exists in the document."""
    # Build ID registry from the entire document.
    id_registry = _collect_ids_recursive(yaml_data)

    traceability = yaml_data.get("traceability")
    if traceability is None:
        passes.append("SDD-XS-001: No traceability section found (skipped)")
        return

    referenced_ids = _collect_string_ids(traceability)
    if not referenced_ids:
        passes.append("SDD-XS-001: No traceability section found (skipped)")
        return

    missing = sorted(referenced_ids - id_registry)
    if missing:
        for mid in missing:
            errors.append(f"SDD-XS-001: Traceability references non-existent ID: {mid}")
    else:
        passes.append(f"SDD-XS-001: All {len(referenced_ids)} traceability IDs exist in document")


# ---------------------------------------------------------------------------
# SDD-XS-002 -- Readiness Score Plausibility
# ---------------------------------------------------------------------------


def _check_readiness_score_plausibility(
    yaml_data: dict[str, object],
    doc_type: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Flag perfect readiness scores when validation has errors or warnings."""
    normalized = doc_type.strip().lower()
    field = READINESS_SCORE_FIELDS.get(normalized)
    if field is None:
        # Unknown layer -- skip silently.
        return

    raw_value = _find_field_recursive(yaml_data, field)
    if raw_value is None:
        passes.append(f"SDD-XS-002: {field} not found in document (skipped)")
        return

    score_str = str(raw_value)
    match = _SCORE_RE.search(score_str)
    if match is None:
        passes.append(f"SDD-XS-002: {field} format not parseable as N/M (skipped)")
        return

    numerator = int(match.group(1))
    denominator = int(match.group(2))

    n_err = len(errors)
    n_warn = len(warnings)

    if numerator == denominator and (n_err > 0 or n_warn > 0):
        warnings.append(
            f"SDD-XS-002: {field} is {score_str} but validation has "
            f"{n_err} errors and {n_warn} warnings \u2014 recalculate"
        )
    else:
        passes.append(f"SDD-XS-002: {field} is {score_str} (plausible)")


# ---------------------------------------------------------------------------
# SDD-XS-003 -- Diagram Registry Present
# ---------------------------------------------------------------------------


def _check_diagram_registry(
    yaml_data: dict[str, object],
    doc_type: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Check diagram contract consistency for applicable layers."""
    normalized = doc_type.strip().lower()
    if normalized not in _DIAGRAM_LAYERS:
        return

    metadata: Any = yaml_data.get("metadata")
    if not isinstance(metadata, dict):
        return

    diagram_standard: Any = metadata.get("diagram_standard")
    if not isinstance(diagram_standard, dict):
        return

    if "tags" not in diagram_standard:
        return

    # Diagram contract exists -- verify items.
    diagrams: Any = yaml_data.get("diagrams")
    if not isinstance(diagrams, dict):
        warnings.append(
            "SDD-XS-003: Document has diagram contract but diagrams.items is missing or empty"
        )
        return

    items: Any = diagrams.get("items")
    if not isinstance(items, list) or len(items) == 0:
        warnings.append(
            "SDD-XS-003: Document has diagram contract but diagrams.items is missing or empty"
        )
        return

    passes.append(f"SDD-XS-003: Diagram registry present with {len(items)} items")


# ---------------------------------------------------------------------------
# SDD-XS-004 -- Cumulative Tags Ceiling
# ---------------------------------------------------------------------------


def _check_cumulative_tags(
    yaml_data: dict[str, object],
    doc_type: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Enforce cumulative metadata tag ceiling by layer."""
    normalized = doc_type.strip().lower()
    max_tags = MAX_CUMULATIVE_TAGS.get(normalized)
    if max_tags is None:
        return

    metadata = yaml_data.get("metadata")
    if not isinstance(metadata, dict):
        passes.append("SDD-XS-004: metadata.tags not found in document (skipped)")
        return

    tags = metadata.get("tags")
    if not isinstance(tags, list):
        passes.append("SDD-XS-004: metadata.tags not found in document (skipped)")
        return

    tag_count = len([item for item in tags if isinstance(item, str)])
    if tag_count > max_tags:
        errors.append(
            f"SDD-XS-004: metadata.tags has {tag_count} tags; max {max_tags} for {normalized}"
        )
    else:
        passes.append(
            f"SDD-XS-004: metadata.tags count {tag_count} within max {max_tags} for {normalized}"
        )


# ---------------------------------------------------------------------------
# SDD-XS-001 (Markdown fallback)
# ---------------------------------------------------------------------------

_MD_TRACEABILITY_HEADING_RE = re.compile(r"^##\s+(?:Traceability|19\.)", re.MULTILINE)


def _check_traceability_id_existence_md(
    content: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Regex-based traceability check for Markdown documents."""
    # Collect IDs from lines that look like ``id: SOME.01.03.abcd`` or in YAML
    # frontmatter blocks.
    id_registry: set[str] = set()
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("id:"):
            ids_in_line = _ELEMENT_ID_INLINE_RE.findall(stripped)
            id_registry.update(ids_in_line)

    # Also scan YAML frontmatter (between --- markers).
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        fm_ids = _ELEMENT_ID_INLINE_RE.findall(fm_match.group(1))
        id_registry.update(fm_ids)

    # Locate the traceability section.
    trace_match = _MD_TRACEABILITY_HEADING_RE.search(content)
    if trace_match is None:
        passes.append("SDD-XS-001: No traceability section found (skipped)")
        return

    trace_section = content[trace_match.start() :]
    # Truncate at next H2 heading (if any).
    next_heading = re.search(r"\n##\s+", trace_section[1:])
    if next_heading is not None:
        trace_section = trace_section[: next_heading.start() + 1]

    referenced_ids = set(_ELEMENT_ID_INLINE_RE.findall(trace_section))
    if not referenced_ids:
        passes.append("SDD-XS-001: No traceability section found (skipped)")
        return

    missing = sorted(referenced_ids - id_registry)
    if missing:
        for mid in missing:
            errors.append(f"SDD-XS-001: Traceability references non-existent ID: {mid}")
    else:
        passes.append(f"SDD-XS-001: All {len(referenced_ids)} traceability IDs exist in document")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_cross_section_checks(
    *,
    yaml_data: dict[str, object],
    doc_type: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Generic cross-section validation for all SDD layers (YAML documents)."""
    _check_traceability_id_existence(yaml_data, errors, warnings, passes)
    _check_diagram_registry(yaml_data, doc_type, errors, warnings, passes)
    _check_cumulative_tags(yaml_data, doc_type, errors, warnings, passes)
    # Score plausibility runs LAST (relies on populated errors/warnings).
    _check_readiness_score_plausibility(yaml_data, doc_type, errors, warnings, passes)


def run_cross_section_checks_md(
    *,
    content: str,
    doc_type: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Cross-section checks for MD-format documents (regex-based, limited)."""
    # Only SDD-XS-001 is feasible via regex.
    _check_traceability_id_existence_md(content, errors, warnings, passes)
    # SDD-XS-002 and SDD-XS-003 require structured YAML -- skip with info.
