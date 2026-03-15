"""File utilities for UCX validators.

Provides:
- Companion report file detection
- Source file collection
- Section-based layout detection
"""

import re
from pathlib import Path
from typing import List, Optional

# Pattern for companion report files (audit, review, fix, validation reports)
# Matches patterns like:
# - BRD-01.A_audit_report.md, BRD-01.R_review_report_v003.md
# - BRD-01.UCA_audit_report.md, BRD-01.UCR_review_report_v003.md
# - BRD-01.UCRem_fix_report.md
# - .precommit_validation_report.md (current validation format, hidden file)
COMPANION_REPORT_PATTERN = re.compile(
    r"(\.(A_audit_report|R_review_report|F_fix_report|V_validation_report|"
    r"UCA_audit_report|UCR_review_report|UCR_remediation_report|"
    r"UCRem_fix_report|UCRem_remediation_report|UCRem_report)"
    r"(_v[0-9]+)?\.md$|^\.precommit_validation_report\.md$)"
)

# Pattern for section-based BRD layout (e.g., BRD-01.0_index.md)
SECTION_FILE_PATTERN = re.compile(r"^[A-Z]+-\d+\.\d+_.*\.md$")


def is_companion_report(file_path: Path) -> bool:
    """
    Check if a file is a companion report (audit/review/fix/validation).

    Args:
        file_path: Path to check

    Returns:
        True if file is a companion report
    """
    return bool(COMPANION_REPORT_PATTERN.search(file_path.name))


def collect_source_files(
    doc_path: Path,
    pattern: str = "*.md",
    exclude_companions: bool = True,
) -> List[Path]:
    """
    Collect source files for validation, excluding companion reports.

    Args:
        doc_path: Directory or file path
        pattern: Glob pattern for files
        exclude_companions: If True, exclude companion report files

    Returns:
        List of source file paths
    """
    if doc_path.is_file():
        if exclude_companions and is_companion_report(doc_path):
            return []
        return [doc_path]

    if not doc_path.is_dir():
        return []

    files = list(doc_path.glob(pattern))

    # Also check subdirectories for nested document structures
    for subdir in doc_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("."):
            files.extend(subdir.glob(pattern))

    if exclude_companions:
        files = [f for f in files if not is_companion_report(f)]

    # Sort by path for consistent ordering
    return sorted(files)


def is_section_based_layout(doc_path: Path) -> bool:
    """
    Check if document uses section-based layout (multi-file BRD).

    Section-based layout has files like:
    - BRD-01.0_index.md
    - BRD-01.1_overview.md
    - BRD-01.2_requirements.md

    Args:
        doc_path: Path to document directory

    Returns:
        True if section-based layout detected
    """
    if doc_path.is_file():
        doc_path = doc_path.parent

    if not doc_path.is_dir():
        return False

    # Look for section files (TYPE-NN.S_name.md pattern)
    for f in doc_path.iterdir():
        if f.is_file() and SECTION_FILE_PATTERN.match(f.name):
            return True

    return False


def get_document_id(doc_path: Path) -> Optional[str]:
    """
    Extract document ID from path or filename.

    Args:
        doc_path: Path to document

    Returns:
        Document ID (e.g., 'BRD-01') or None
    """
    # Try directory name first (for nested layouts)
    if doc_path.is_dir():
        name = doc_path.name
    else:
        name = doc_path.stem

    # Match patterns like BRD-01, PRD-02, etc.
    match = re.match(r"^([A-Z]+-\d+)", name)
    if match:
        return match.group(1)

    return None


def get_main_document(doc_path: Path) -> Optional[Path]:
    """
    Get the main document file from a directory.

    For section-based layouts, returns the index file (*.0_*.md).
    For single-file documents, returns that file.

    Args:
        doc_path: Path to document directory or file

    Returns:
        Path to main document or None
    """
    if doc_path.is_file():
        return doc_path

    if not doc_path.is_dir():
        return None

    # Look for index file (section 0)
    index_files = list(doc_path.glob("*.0_*.md"))
    if index_files:
        return index_files[0]

    # Look for single main document matching directory name
    doc_id = get_document_id(doc_path)
    if doc_id:
        candidates = list(doc_path.glob(f"{doc_id}*.md"))
        # Filter out companion reports
        candidates = [f for f in candidates if not is_companion_report(f)]
        if candidates:
            return candidates[0]

    # Fallback: first markdown file
    md_files = [f for f in doc_path.glob("*.md") if not is_companion_report(f)]
    if md_files:
        return sorted(md_files)[0]

    return None


def count_tokens_estimate(content: str) -> int:
    """
    Estimate token count for content.

    Uses rough approximation: ~4 characters per token for English text.

    Args:
        content: Text content

    Returns:
        Estimated token count
    """
    return len(content) // 4


def sort_section_files(files: List[Path]) -> List[Path]:
    """
    Sort section files numerically by section number.

    Handles patterns like:
    - BRD-01.0_index.md (section 0)
    - BRD-01.1_introduction.md (section 1)
    - BRD-01.10_risk_management.md (section 10)

    Standard lexicographic sort produces: 0, 10, 11, ..., 18, 1, 2, ...
    This function sorts numerically: 0, 1, 2, ..., 10, 11, ..., 18

    Non-section files (e.g., review reports) are placed at the end.

    Args:
        files: List of Path objects to sort

    Returns:
        Sorted list with section files in numerical order
    """
    def extract_section_number(path: Path) -> tuple:
        """Extract section number for sorting, fallback to name."""
        name = path.name
        # Pattern: {DOC_ID}.{SECTION_NUM}_{description}.md
        # Examples: BRD-01.0_index.md, BRD-01.10_risk_management.md
        match = re.match(r'^[A-Z]+-\d+\.(\d+)_', name)
        if match:
            return (int(match.group(1)), name)
        # Fallback: sort by filename (for non-section files)
        return (999999, name)

    return sorted(files, key=extract_section_number)
