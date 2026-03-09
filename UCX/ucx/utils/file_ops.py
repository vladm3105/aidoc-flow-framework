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
