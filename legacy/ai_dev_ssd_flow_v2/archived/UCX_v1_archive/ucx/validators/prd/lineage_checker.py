"""
ucx.validators.prd.lineage_checker
====================================
Pre-commit PRD artifact folder consistency checker (PLAN-012).

Performs structural availability and consistency checks on PRD artifact
folders to ensure the PLAN-012 derived-artifact chain is coherent.
No LLM calls or heavy validation are performed here.

**Eight checks performed:**

1. If ``_validation`` or ``_remediated`` copies exist, a canonical source PRD must exist.
2. If a ``_validation`` copy exists, a validation report (``PRD-NN_validation_report.md``) must exist.
3. If a ``_remediated`` copy exists, a ``_validation`` copy must also exist.
4. If a ``_remediated`` copy exists, at least one remediation report must exist.
5. The ``doc_id`` field must be consistent across source, ``_validation``, and ``_remediated`` copies.
6. The ``version`` field must be consistent across source and derived copies.
7. Each file must declare the correct ``processing_stage`` for its role.
8. Each derived file must declare a ``derived_from`` pointing to an existing sibling file.

Exit codes:
  0  - All checks passed (or no PRD folder found)
  1  - One or more checks failed

Usage::

    python -m ucx.validators.prd.lineage_checker <prd_folder_or_parent>

    # via pre-commit (pass_filenames: false, entry: python -m ucx.validators.prd.lineage_checker)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_VERSION_RE = re.compile(r"^\s*version:\s*(.+)$", re.MULTILINE)
_DOC_ID_RE = re.compile(r"^\s*doc_id:\s*(.+)$", re.MULTILINE)
_SOURCE_DOC_ID_RE = re.compile(r"^\s*source_doc_id:\s*(.+)$", re.MULTILINE)
_PROCESSING_STAGE_RE = re.compile(r"^\s*processing_stage:\s*(.+)$", re.MULTILINE)
_DERIVED_FROM_RE = re.compile(r"^\s*derived_from:\s*(.+)$", re.MULTILINE)

_VALIDATION_SUFFIX = "_validation"
_REMEDIATED_SUFFIX = "_remediated"
_VALIDATION_REPORT_PATTERN = re.compile(r"PRD-\d+_validation_report\.md$")
_REMEDIATION_REPORT_PATTERN = re.compile(r"PRD-\d+_.*remediat.*_report.*\.md$", re.IGNORECASE)


def _read_frontmatter(path: Path) -> str:
    """Return raw YAML frontmatter block (without delimiters) or empty string."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m = _FRONTMATTER_RE.match(text)
    return m.group(1) if m else ""


def _extract(pattern: re.Pattern[str], text: str) -> str | None:
    m = pattern.search(text)
    return m.group(1).strip() if m else None


# ---------------------------------------------------------------------------
# Folder discovery
# ---------------------------------------------------------------------------

def _find_prd_folders(root: Path) -> list[Path]:
    """Yield all PRD-NN/ artifact folders under *root* (non-recursive beyond PRD-NN)."""
    prd_folder_re = re.compile(r"^PRD-\d+$")
    folders: list[Path] = []

    def _scan(d: Path) -> None:
        for child in sorted(d.iterdir()):
            if child.is_dir() and prd_folder_re.match(child.name):
                folders.append(child)
            elif child.is_dir() and not child.name.startswith("."):
                _scan(child)

    _scan(root)
    return folders


def _prd_files_in(folder: Path) -> Iterator[Path]:
    """Yield all ``.md`` files directly in *folder*."""
    return folder.glob("*.md")


# ---------------------------------------------------------------------------
# Stage classification
# ---------------------------------------------------------------------------

def _classify(path: Path) -> str:
    """Return 'source', 'validation-fixed', 'remediated', or 'report'."""
    stem = path.stem
    if stem.endswith(_REMEDIATED_SUFFIX):
        return "remediated"
    if stem.endswith(_VALIDATION_SUFFIX):
        return "validation-fixed"
    if _VALIDATION_REPORT_PATTERN.search(path.name) or _REMEDIATION_REPORT_PATTERN.search(path.name):
        return "report"
    return "source"


def _is_source(path: Path) -> bool:
    return _classify(path) == "source"


def _is_validation_copy(path: Path) -> bool:
    return _classify(path) == "validation-fixed"


def _is_remediated_copy(path: Path) -> bool:
    return _classify(path) == "remediated"


def _is_validation_report(path: Path) -> bool:
    return bool(_VALIDATION_REPORT_PATTERN.search(path.name))


def _is_remediation_report(path: Path) -> bool:
    return bool(_REMEDIATION_REPORT_PATTERN.search(path.name))


# ---------------------------------------------------------------------------
# Per-folder checks
# ---------------------------------------------------------------------------

class LineageFailure:
    def __init__(self, check: str, file: str, message: str) -> None:
        self.check = check
        self.file = file
        self.message = message

    def __str__(self) -> str:
        return f"  [{self.check}] {self.file}: {self.message}"


def check_folder(folder: Path) -> list[LineageFailure]:
    """Run all 8 lineage checks on a single PRD artifact folder."""
    failures: list[LineageFailure] = []
    md_files = list(_prd_files_in(folder))

    sources = [f for f in md_files if _is_source(f)]
    validation_copies = [f for f in md_files if _is_validation_copy(f)]
    remediated_copies = [f for f in md_files if _is_remediated_copy(f)]
    validation_reports = [f for f in md_files if _is_validation_report(f)]
    remediation_reports = [f for f in md_files if _is_remediation_report(f)]

    # ------------------------------------------------------------------
    # CHECK 1: Source PRD exists if derived copies exist
    # ------------------------------------------------------------------
    if (validation_copies or remediated_copies) and not sources:
        for f in validation_copies + remediated_copies:
            failures.append(LineageFailure(
                "CHK-1",
                f.name,
                "Derived copy exists but no canonical source PRD found in folder.",
            ))

    # ------------------------------------------------------------------
    # CHECK 2: Validation report exists if _validation copy exists
    # ------------------------------------------------------------------
    for f in validation_copies:
        if not validation_reports:
            failures.append(LineageFailure(
                "CHK-2",
                f.name,
                "No validation report (PRD-NN_validation_report.md) found; "
                "run 'ucx validate prd' first.",
            ))

    # ------------------------------------------------------------------
    # CHECK 3: _validation copy exists if _remediated copy exists
    # ------------------------------------------------------------------
    for f in remediated_copies:
        if not validation_copies:
            failures.append(LineageFailure(
                "CHK-3",
                f.name,
                "_remediated copy exists but no _validation copy found.",
            ))

    # ------------------------------------------------------------------
    # CHECK 4: Remediation report exists if _remediated copy exists
    # ------------------------------------------------------------------
    for f in remediated_copies:
        if not remediation_reports:
            failures.append(LineageFailure(
                "CHK-4",
                f.name,
                "_remediated copy exists but no remediation report found.",
            ))

    # No further checks needed if there are no source PRDs
    if not sources:
        return failures

    source = sources[0]  # Primary source for comparison
    source_fm = _read_frontmatter(source)
    source_doc_id = _extract(_DOC_ID_RE, source_fm)
    source_version = _extract(_VERSION_RE, source_fm)

    # ------------------------------------------------------------------
    # CHECK 5: doc_id consistency
    # ------------------------------------------------------------------
    for f in validation_copies + remediated_copies:
        fm = _read_frontmatter(f)
        # Derived copies store their doc_id as source_doc_id
        declared_source_id = _extract(_SOURCE_DOC_ID_RE, fm) or _extract(_DOC_ID_RE, fm)
        if source_doc_id and declared_source_id and declared_source_id != source_doc_id:
            failures.append(LineageFailure(
                "CHK-5",
                f.name,
                f"doc_id mismatch: source={source_doc_id!r}, this={declared_source_id!r}.",
            ))

    # ------------------------------------------------------------------
    # CHECK 6: version consistency
    # ------------------------------------------------------------------
    for f in validation_copies + remediated_copies:
        fm = _read_frontmatter(f)
        declared_version = _extract(_VERSION_RE, fm)
        if source_version and declared_version and declared_version != source_version:
            failures.append(LineageFailure(
                "CHK-6",
                f.name,
                f"version mismatch: source={source_version!r}, this={declared_version!r}.",
            ))

    # ------------------------------------------------------------------
    # CHECK 7: processing_stage correctness
    # ------------------------------------------------------------------
    stage_map = {
        "source": "source",
        "validation-fixed": "validation-fixed",
        "remediated": "remediated",
    }
    for f in sources + validation_copies + remediated_copies:
        fm = _read_frontmatter(f)
        expected_stage = stage_map[_classify(f)]
        declared_stage = _extract(_PROCESSING_STAGE_RE, fm)
        if declared_stage is None:
            # Source PRDs without processing_stage are fine (optional field)
            if _classify(f) != "source":
                failures.append(LineageFailure(
                    "CHK-7",
                    f.name,
                    f"Missing processing_stage; expected '{expected_stage}'.",
                ))
        elif declared_stage != expected_stage:
            failures.append(LineageFailure(
                "CHK-7",
                f.name,
                f"processing_stage mismatch: expected='{expected_stage}', got='{declared_stage}'.",
            ))

    # ------------------------------------------------------------------
    # CHECK 8: derived_from points to an existing sibling
    # ------------------------------------------------------------------
    for f in validation_copies + remediated_copies:
        fm = _read_frontmatter(f)
        derived_from = _extract(_DERIVED_FROM_RE, fm)
        if derived_from is None:
            failures.append(LineageFailure(
                "CHK-8",
                f.name,
                "Missing 'derived_from' field in frontmatter custom_fields.",
            ))
        else:
            # Strip potential path prefixes; look for the name in the folder
            derived_name = Path(derived_from).name
            sibling = folder / derived_name
            if not sibling.exists():
                failures.append(LineageFailure(
                    "CHK-8",
                    f.name,
                    f"derived_from='{derived_from}' does not exist in this folder.",
                ))

    return failures


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(paths: list[str]) -> int:
    """Check PRD artifact lineage under each given path.

    *paths* may be individual PRD-NN/ folders or parent directories.
    Returns 0 if all checks pass, 1 if any check fails.
    """
    all_failures: list[LineageFailure] = []
    checked_folders: list[Path] = []

    for path_str in paths:
        root = Path(path_str)
        if not root.exists():
            print(f"ucx-prd-lineage: path not found: {root}", file=sys.stderr)
            continue

        # If it looks like a PRD-NN folder, check it directly
        if re.match(r"^PRD-\d+$", root.name) and root.is_dir():
            folder_list = [root]
        else:
            folder_list = _find_prd_folders(root)

        for folder in folder_list:
            checked_folders.append(folder)
            failures = check_folder(folder)
            all_failures.extend(failures)

    if not checked_folders:
        # Nothing to check — pass silently (pre-commit no-op)
        return 0

    if all_failures:
        print(f"ucx-prd-lineage: {len(all_failures)} lineage issue(s) found:\n", file=sys.stderr)
        for f in all_failures:
            print(str(f), file=sys.stderr)
        print(
            "\nResolve issues before committing. "
            "See PLAN-012 for the PRD derived-artifact lifecycle.",
            file=sys.stderr,
        )
        return 1

    print(
        f"ucx-prd-lineage: ok ({len(checked_folders)} folder(s) checked)",
        file=sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
