"""PRD Derived Artifact Operations (PLAN-012, UCX v1.22.0).

This module provides utilities for the PRD derived-artifact workflow:
- Deterministic PRD artifact naming (source, _validation, _remediated)
- Fixed validation report naming (PRD-01_validation_report.md)
- Processing-stage metadata injection/update
- Revision history provenance row appending
- Artifact stage identification from filename

Naming Contract (per PLAN-012):
  Source PRD:      PRD-01_platform_architecture.md
  Validation copy: PRD-01_platform_architecture_validation.md
  Remediated copy: PRD-01_platform_architecture_remediated.md
  Validation rpt:  PRD-01_validation_report.md  (fixed name, no versioning)
  Review rpts:     PRD-01_validation_review_report_v001.md  (versioned)
  Remediation rpts: PRD-01_validation_remediation_report_v001.md  (versioned)
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALIDATION_COPY_SUFFIX = "_validation"      # appended to source stem
REMEDIATED_COPY_SUFFIX = "_remediated"      # appended to source stem
VALIDATION_REPORT_SUFFIX = "_validation_report.md"   # fixed report name suffix

PROCESSING_STAGES = frozenset({"source", "validation-fixed", "remediated"})

# Reserved suffixes that identify derived (non-source) PRD artifacts
_DERIVED_SUFFIXES = (VALIDATION_COPY_SUFFIX, REMEDIATED_COPY_SUFFIX)


# ---------------------------------------------------------------------------
# Naming helpers
# ---------------------------------------------------------------------------

def prd_validation_report_name(doc_id: str) -> str:
    """Return the fixed validation report filename for a PRD doc_id.

    Example: ``prd_validation_report_name("PRD-01")`` → ``"PRD-01_validation_report.md"``
    """
    return f"{doc_id}{VALIDATION_REPORT_SUFFIX}"


def prd_validation_copy_name(source_stem: str) -> str:
    """Return the ``_validation`` copy filename stem (without ``.md``).

    Example: ``prd_validation_copy_name("PRD-01_platform_architecture")``
             → ``"PRD-01_platform_architecture_validation"``
    """
    _assert_source_stem(source_stem)
    return f"{source_stem}{VALIDATION_COPY_SUFFIX}"


def prd_remediated_copy_name(validation_stem: str) -> str:
    """Return the ``_remediated`` copy filename stem (without ``.md``).

    Accepts either a ``_validation`` stem or a plain source stem.

    Example: ``prd_remediated_copy_name("PRD-01_platform_architecture_validation")``
             → ``"PRD-01_platform_architecture_remediated"``
    """
    base = _strip_stage_suffix(validation_stem)
    return f"{base}{REMEDIATED_COPY_SUFFIX}"


# ---------------------------------------------------------------------------
# Artifact stage identification
# ---------------------------------------------------------------------------

def identify_prd_artifact_stage(file_path: Path) -> str:
    """Return the processing stage label based on filename suffix.

    Returns one of: ``"source"``, ``"validation-fixed"``, ``"remediated"``.
    """
    stem = file_path.stem
    if stem.endswith(VALIDATION_COPY_SUFFIX):
        return "validation-fixed"
    if stem.endswith(REMEDIATED_COPY_SUFFIX):
        return "remediated"
    return "source"


def is_source_prd(file_path: Path) -> bool:
    """Return True if the file is a canonical source PRD (no stage suffix)."""
    return identify_prd_artifact_stage(file_path) == "source"


def is_prd_validation_report(file_path: Path) -> bool:
    """Return True if the file is a fixed PRD validation report."""
    return file_path.name.endswith(VALIDATION_REPORT_SUFFIX)


def resolve_prd_review_target(doc_path: Path) -> Path:
    """Resolve the PRD artifact that should be used for PLAN-012 review.

    Rules:
    - If ``doc_path`` is a ``_validation``/``_remediated`` file, return as-is.
    - If ``doc_path`` is a source PRD file, return sibling ``_validation`` path.
    - If ``doc_path`` is a directory and exactly one ``*_validation.md`` exists,
      return that file.
    - Otherwise, return ``doc_path`` unchanged.
    """
    if doc_path.is_file():
        if identify_prd_artifact_stage(doc_path) != "source":
            return doc_path
        return doc_path.parent / f"{prd_validation_copy_name(doc_path.stem)}.md"

    if doc_path.is_dir():
        candidates = sorted(
            p for p in doc_path.glob("PRD-*_validation.md") if p.is_file()
        )
        if len(candidates) == 1:
            return candidates[0]

    return doc_path


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def parse_prd_frontmatter(content: str) -> dict[str, Any]:
    """Extract raw YAML frontmatter dict from PRD content.

    Returns an empty dict if frontmatter is absent or malformed.
    """
    match = re.match(r"\A---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        return {}
    try:
        parsed = yaml.safe_load(match.group(1))
        return parsed if isinstance(parsed, dict) else {}
    except yaml.YAMLError:
        return {}


def extract_prd_identity_fields(content: str) -> dict[str, str | None]:
    """Extract doc_id, version, processing_stage, and derived_from from frontmatter.

    Returns a dict with keys ``doc_id``, ``version``, ``processing_stage``,
    ``derived_from`` — all values may be ``None`` if absent.
    """
    fm = parse_prd_frontmatter(content)
    custom = fm.get("custom_fields") or {}
    return {
        "doc_id": fm.get("doc_id"),
        "version": str(fm.get("version", "")) or None,
        "processing_stage": custom.get("processing_stage"),
        "derived_from": custom.get("derived_from"),
    }


# ---------------------------------------------------------------------------
# Metadata injection
# ---------------------------------------------------------------------------

def inject_processing_stage_metadata(
    content: str,
    *,
    processing_stage: str,
    source_doc_id: str,
    source_version: str,
    derived_from: str,
) -> str:
    """Inject or overwrite processing-stage lineage fields in YAML frontmatter.

    Preserves all existing frontmatter fields; adds/overwrites inside
    ``custom_fields``:
    - ``processing_stage``
    - ``source_doc_id``
    - ``source_version``
    - ``derived_from``

    ``development_status`` is left unchanged unless absent (defaults to
    ``"active"``).

    Args:
        content: Full markdown content of the PRD copy.
        processing_stage: One of ``"source"``, ``"validation-fixed"``, ``"remediated"``.
        source_doc_id: The ``doc_id`` of the canonical source PRD.
        source_version: The ``version`` string of the canonical source PRD.
        derived_from: Filename of the immediate predecessor artifact.

    Returns:
        Updated markdown content with injected frontmatter.
    """
    if processing_stage not in PROCESSING_STAGES:
        raise ValueError(
            f"Invalid processing_stage '{processing_stage}'. "
            f"Must be one of: {sorted(PROCESSING_STAGES)}"
        )

    # Split content into frontmatter block and body
    fm_match = re.match(r"\A(---\n)(.*?)(\n---\n?)(.*)\Z", content, re.DOTALL)
    if not fm_match:
        # No frontmatter: prepend a minimal one
        fm_text = _build_minimal_frontmatter(
            processing_stage, source_doc_id, source_version, derived_from
        )
        return f"---\n{fm_text}\n---\n{content}"

    before_fm = fm_match.group(1)    # "---\n"
    raw_fm = fm_match.group(2)       # YAML body
    after_delim = fm_match.group(3)  # "\n---\n" or "\n---"
    body = fm_match.group(4)         # rest of document

    try:
        fm = yaml.safe_load(raw_fm) or {}
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}

    # Ensure custom_fields is a dict
    custom = fm.get("custom_fields")
    if not isinstance(custom, dict):
        custom = {}

    # Inject lineage fields
    custom["processing_stage"] = processing_stage
    custom["source_doc_id"] = source_doc_id
    custom["source_version"] = source_version
    custom["derived_from"] = derived_from
    custom.setdefault("development_status", "active")

    fm["custom_fields"] = custom

    # Serialise back to YAML preserving order as best as possible
    new_fm_text = _dump_frontmatter(fm)
    return f"{before_fm}{new_fm_text}{after_delim}{body}"


# ---------------------------------------------------------------------------
# Revision history provenance
# ---------------------------------------------------------------------------

def append_derivation_history_row(
    content: str,
    *,
    version: str,
    date: str,
    author: str,
    description: str,
) -> str:
    """Append a provenance row to the Document Control revision history table.

    Looks for a markdown table inside any section whose heading contains
    "Revision History" or "Document Revision". Appends the new row as the
    last row before the next heading or end of table.

    If no such table is found, appends a note at the end of the document.

    Args:
        content: Full markdown content.
        version: Semantic version string (e.g. ``"0.1.0"``).
        date: ISO date/datetime string.
        author: Author column value (e.g. ``"UCX Validation Fixer"``).
        description: Description column value.

    Returns:
        Updated markdown with provenance row appended.
    """
    row = f"| {version} | {date} | {author} | {description} |"

    # Try to find a revision history table
    # Pattern: heading with "revision history" → table rows → blank line or next heading
    history_heading = re.compile(
        r"(#{1,4}\s+.*?[Rr]evision [Hh]istory.*?\n)",
        re.IGNORECASE,
    )
    m = history_heading.search(content)
    if m:
        # Find the end of the table block after this heading
        after_heading = content[m.end():]
        # Find last table row in this block
        table_row_pattern = re.compile(r"^\|.+\|[ \t]*$", re.MULTILINE)
        rows = list(table_row_pattern.finditer(after_heading))
        if rows:
            last_row = rows[-1]
            insert_at = m.end() + last_row.end()
            return content[:insert_at] + "\n" + row + content[insert_at:]

    # Fallback: append at the end
    return content.rstrip() + f"\n\n{row}\n"


# ---------------------------------------------------------------------------
# Derived copy creation
# ---------------------------------------------------------------------------

def create_validation_copy(
    source_path: Path,
    *,
    source_doc_id: str,
    source_version: str,
    derivation_date: Optional[str] = None,
) -> tuple[Path, str]:
    """Create a ``_validation`` PRD copy with updated metadata.

    Reads the source PRD, injects ``processing_stage: validation-fixed``
    metadata and appends a provenance row. Does **not** write to disk.

    Args:
        source_path: Path to the source PRD ``.md`` file.
        source_doc_id: PRD document ID (e.g. ``"PRD-01"``).
        source_version: Version string from source frontmatter.
        derivation_date: ISO timestamp for the provenance row (defaults to now).

    Returns:
        Tuple of ``(output_path, updated_content)`` where ``output_path`` is
        the path the caller should write to.
    """
    if derivation_date is None:
        derivation_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")

    content = source_path.read_text(encoding="utf-8")

    output_stem = prd_validation_copy_name(source_path.stem)
    output_path = source_path.parent / f"{output_stem}.md"

    updated = inject_processing_stage_metadata(
        content,
        processing_stage="validation-fixed",
        source_doc_id=source_doc_id,
        source_version=source_version,
        derived_from=source_path.name,
    )
    updated = append_derivation_history_row(
        updated,
        version=source_version,
        date=derivation_date,
        author="UCX Validation Fixer",
        description=f"Derived validation-fixed copy from `{source_path.name}` using `{prd_validation_report_name(source_doc_id)}`",
    )
    return output_path, updated


def create_remediated_copy(
    validation_path: Path,
    *,
    source_doc_id: str,
    source_version: str,
    remediation_report_name: str,
    derivation_date: Optional[str] = None,
) -> tuple[Path, str]:
    """Create a ``_remediated`` PRD copy from a ``_validation`` PRD.

    The ``_validation`` PRD remains untouched. Does **not** write to disk.

    Args:
        validation_path: Path to the ``_validation`` PRD ``.md`` file.
        source_doc_id: PRD document ID (e.g. ``"PRD-01"``).
        source_version: Version string from source frontmatter.
        remediation_report_name: Filename of the remediation report that was consumed.
        derivation_date: ISO timestamp for the provenance row (defaults to now).

    Returns:
        Tuple of ``(output_path, updated_content)``.
    """
    if derivation_date is None:
        derivation_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")

    content = validation_path.read_text(encoding="utf-8")

    output_stem = prd_remediated_copy_name(validation_path.stem)
    output_path = validation_path.parent / f"{output_stem}.md"

    updated = inject_processing_stage_metadata(
        content,
        processing_stage="remediated",
        source_doc_id=source_doc_id,
        source_version=source_version,
        derived_from=validation_path.name,
    )
    updated = append_derivation_history_row(
        updated,
        version=source_version,
        date=derivation_date,
        author="UCX Remediation Apply",
        description=f"Derived remediated copy from `{validation_path.name}` using `{remediation_report_name}`",
    )
    return output_path, updated


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _assert_source_stem(stem: str) -> None:
    """Raise ValueError if stem already has a derived suffix."""
    for suffix in _DERIVED_SUFFIXES:
        if stem.endswith(suffix):
            raise ValueError(
                f"Stem '{stem}' already has a derived suffix '{suffix}'. "
                "Pass the source stem only."
            )


def _strip_stage_suffix(stem: str) -> str:
    """Strip any known stage suffix from a stem, returning the source stem."""
    for suffix in _DERIVED_SUFFIXES:
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def _build_minimal_frontmatter(
    processing_stage: str,
    source_doc_id: str,
    source_version: str,
    derived_from: str,
) -> str:
    fm: dict[str, Any] = {
        "custom_fields": {
            "processing_stage": processing_stage,
            "source_doc_id": source_doc_id,
            "source_version": source_version,
            "derived_from": derived_from,
            "development_status": "active",
        }
    }
    return _dump_frontmatter(fm).strip()


def _dump_frontmatter(fm: dict[str, Any]) -> str:
    """Serialise frontmatter dict to YAML string (no trailing newline)."""
    # Use default_flow_style=False and sort_keys=False to preserve insertion order
    return yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)


def apply_ucx_action_fixes(content: str, report_content: str) -> dict:
    """Parse UCX-ACTION blocks from a remediation report and apply auto-safe fixes.

    Looks for ``<!-- UCX-ACTION[...] ... suggested_fix: | ... -->`` blocks and
    applies text substitutions using ``old_content`` → ``suggested_fix`` pairs.

    Args:
        content: The document content to apply fixes to.
        report_content: The remediation report containing UCX-ACTION blocks.

    Returns:
        Dict with keys ``content`` (updated str) and ``count`` (int fixes applied).
    """
    import re

    ucx_action_pattern = re.compile(
        r"<!--\s*UCX-ACTION\[.*?\].*?(?:old_content:\s*\|\s*\n(.*?))?suggested_fix:\s*\|\s*\n(.*?)-->",
        re.DOTALL,
    )
    indent_re = re.compile(r"^[ \t]{4,}", re.MULTILINE)

    updated = content
    count = 0

    for m in ucx_action_pattern.finditer(report_content):
        old_raw = m.group(1)
        new_raw = m.group(2)
        if not new_raw:
            continue

        suggested = indent_re.sub("", new_raw).strip()

        if old_raw:
            old_text = indent_re.sub("", old_raw).strip()
            if old_text and old_text in updated:
                updated = updated.replace(old_text, suggested, 1)
                count += 1

    return {"content": updated, "count": count}
