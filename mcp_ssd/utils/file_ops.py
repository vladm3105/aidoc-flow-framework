"""File operation utilities."""

from pathlib import Path
from typing import Optional, List
import shutil


def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists, creating if necessary.

    Args:
        path: Directory path

    Returns:
        The path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_file(path: Path, encoding: str = "utf-8") -> str:
    """
    Read file content.

    Args:
        path: File path
        encoding: File encoding

    Returns:
        File content

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    return path.read_text(encoding=encoding)


def write_file(path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Write content to file, creating directories if needed.

    Args:
        path: File path
        content: Content to write
        encoding: File encoding
    """
    ensure_dir(path.parent)
    path.write_text(content, encoding=encoding)


def copy_file(src: Path, dst: Path) -> Path:
    """
    Copy file to destination.

    Args:
        src: Source path
        dst: Destination path

    Returns:
        Destination path
    """
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
    return dst


def find_files(
    directory: Path,
    pattern: str = "*.md",
    exclude_patterns: Optional[List[str]] = None,
) -> List[Path]:
    """
    Find files matching pattern.

    Args:
        directory: Directory to search
        pattern: Glob pattern
        exclude_patterns: Patterns to exclude (substring match)

    Returns:
        List of matching paths
    """
    exclude_patterns = exclude_patterns or []
    files = list(directory.glob(pattern))

    if exclude_patterns:
        files = [
            f for f in files
            if not any(ex in f.name for ex in exclude_patterns)
        ]

    return sorted(files)


def get_document_files(doc_path: Path) -> List[Path]:
    """
    Get document files from path, excluding reports.

    Args:
        doc_path: Document file or directory

    Returns:
        List of document file paths
    """
    exclude = ["REVIEW", "REPORT", "UCR", "UCRem"]

    if doc_path.is_dir():
        return find_files(doc_path, "*.md", exclude)

    if doc_path.is_file():
        return [doc_path]

    return []


def find_latest_review_report(doc_path: Path) -> Optional[Path]:
    """
    Find the latest UCR review report for a document.

    Searches for files matching the canonical pattern:
    - {DOC_ID}.UCX_review_report_v{NNN}.md

    Returns the report with the highest version number.

    Args:
        doc_path: Document file or directory

    Returns:
        Path to latest review report, or None if not found

    Examples:
        >>> find_latest_review_report(Path("docs/01_BRD/BRD-01_platform_architecture"))
        PosixPath('docs/01_BRD/BRD-01_platform_architecture/BRD-01.UCX_review_report_v003.md')
    """
    import re

    search_dir = doc_path if doc_path.is_dir() else doc_path.parent

    patterns = ["*.UCX_review_report_v*.md"]

    all_reports: List[Path] = []
    for pattern in patterns:
        all_reports.extend(search_dir.glob(pattern))

    if not all_reports:
        return None

    # Extract version numbers and sort
    def extract_version(path: Path) -> int:
        """Extract version number from filename."""
        # Match patterns like _v001, _v1, v003
        match = re.search(r"_v(\d+)\.md$", path.name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        # Fallback: use modification time
        return 0

    # Sort by version (highest first), then by mtime as tiebreaker
    all_reports.sort(key=lambda p: (extract_version(p), p.stat().st_mtime), reverse=True)

    return all_reports[0] if all_reports else None


def find_latest_remediation_report(doc_path: Path) -> Optional[Path]:
    """
    Find the latest UCRem remediation report for a document.

    Args:
        doc_path: Document file or directory

    Returns:
        Path to latest remediation report, or None if not found
    """
    import re

    search_dir = doc_path if doc_path.is_dir() else doc_path.parent

    patterns = ["*.UCX_remediation_report_v*.md"]

    all_reports: List[Path] = []
    for pattern in patterns:
        all_reports.extend(search_dir.glob(pattern))

    if not all_reports:
        return None

    # Sort by modification time (newest first)
    all_reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return all_reports[0] if all_reports else None
