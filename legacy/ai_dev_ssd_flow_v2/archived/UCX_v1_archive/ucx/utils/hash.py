"""Hash utilities for drift detection."""

import hashlib
from pathlib import Path
from typing import Optional


def compute_hash(path: Path, algorithm: str = "sha256") -> str:
    """
    Compute hash of file content.

    Args:
        path: Path to file
        algorithm: Hash algorithm (sha256, md5, etc.)

    Returns:
        Hash string in format "algorithm:hexdigest"
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    hasher = hashlib.new(algorithm)
    content = path.read_bytes()
    hasher.update(content)

    return f"{algorithm}:{hasher.hexdigest()}"


def verify_hash(path: Path, expected_hash: str) -> bool:
    """
    Verify file hash matches expected value.

    Args:
        path: Path to file
        expected_hash: Expected hash in "algorithm:hexdigest" format

    Returns:
        True if hash matches, False otherwise
    """
    if ":" not in expected_hash:
        # Assume sha256 if no algorithm prefix
        algorithm = "sha256"
        expected_digest = expected_hash
    else:
        algorithm, expected_digest = expected_hash.split(":", 1)

    actual_hash = compute_hash(path, algorithm)
    actual_digest = actual_hash.split(":", 1)[1]

    return actual_digest == expected_digest


def compute_content_hash(content: str, algorithm: str = "sha256") -> str:
    """
    Compute hash of string content.

    Args:
        content: String content
        algorithm: Hash algorithm

    Returns:
        Hash string
    """
    hasher = hashlib.new(algorithm)
    hasher.update(content.encode("utf-8"))
    return f"{algorithm}:{hasher.hexdigest()}"
