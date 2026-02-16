#!/usr/bin/env python3
"""
Test Result Archival Script for AI Dev Flow.

Archives test results for historical tracking and trend analysis.

Usage:
    python archive_test_results.py                    # Archive all results
    python archive_test_results.py --type utest       # Archive specific type
    python archive_test_results.py --keep 30          # Keep last 30 days
    python archive_test_results.py --list             # List archived results
    python archive_test_results.py --restore <id>     # Restore from archive
"""

import argparse
import gzip
import json
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


# Paths
SCRIPT_DIR = Path(__file__).parent
TSPEC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = TSPEC_DIR.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
RESULTS_DIR = TESTS_DIR / "results"
ARCHIVE_DIR = TESTS_DIR / "results" / "archive"


def ensure_archive_dir() -> None:
    """Create archive directory if it doesn't exist."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def get_result_files(
    test_type: Optional[str] = None,
    older_than_days: Optional[int] = None,
) -> List[Path]:
    """Get result files matching criteria."""
    if not RESULTS_DIR.exists():
        return []

    pattern = f"{test_type}_*.json" if test_type else "*.json"
    files = list(RESULTS_DIR.glob(pattern))

    # Exclude pytest output files and already archived files
    files = [
        f for f in files
        if not f.name.startswith("pytest_output")
        and not f.name.endswith(".gz")
        and f.parent == RESULTS_DIR  # Not in subdirectories
    ]

    if older_than_days is not None:
        cutoff = datetime.now() - timedelta(days=older_than_days)
        files = [f for f in files if datetime.fromtimestamp(f.stat().st_mtime) < cutoff]

    return sorted(files, key=lambda f: f.stat().st_mtime)


def archive_file(filepath: Path, compress: bool = True) -> Optional[Path]:
    """Archive a single result file."""
    ensure_archive_dir()

    if compress:
        archive_name = filepath.name + ".gz"
        archive_path = ARCHIVE_DIR / archive_name

        with open(filepath, "rb") as f_in:
            with gzip.open(archive_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        archive_path = ARCHIVE_DIR / filepath.name
        shutil.copy2(filepath, archive_path)

    # Remove original after successful archive
    filepath.unlink()
    return archive_path


def restore_file(archive_name: str) -> Optional[Path]:
    """Restore a file from archive."""
    archive_path = ARCHIVE_DIR / archive_name

    if not archive_path.exists():
        # Try with .gz extension
        archive_path = ARCHIVE_DIR / (archive_name + ".gz")

    if not archive_path.exists():
        print(f"Error: Archive not found: {archive_name}")
        return None

    if archive_path.suffix == ".gz":
        # Decompress
        restored_name = archive_path.stem  # Remove .gz
        restored_path = RESULTS_DIR / restored_name

        with gzip.open(archive_path, "rb") as f_in:
            with open(restored_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        restored_path = RESULTS_DIR / archive_path.name
        shutil.copy2(archive_path, restored_path)

    return restored_path


def list_archives() -> List[Dict]:
    """List all archived results."""
    if not ARCHIVE_DIR.exists():
        return []

    archives = []
    for filepath in sorted(ARCHIVE_DIR.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True):
        if filepath.is_file():
            stat = filepath.stat()
            archives.append({
                "name": filepath.name,
                "size": stat.st_size,
                "archived_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "compressed": filepath.suffix == ".gz",
            })

    return archives


def cleanup_old_archives(keep_days: int) -> int:
    """Remove archives older than specified days."""
    if not ARCHIVE_DIR.exists():
        return 0

    cutoff = datetime.now() - timedelta(days=keep_days)
    removed = 0

    for filepath in ARCHIVE_DIR.glob("*"):
        if filepath.is_file():
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            if mtime < cutoff:
                filepath.unlink()
                removed += 1
                print(f"Removed: {filepath.name}")

    return removed


def print_archive_list(archives: List[Dict]) -> None:
    """Print list of archives."""
    if not archives:
        print("No archived results found.")
        return

    print(f"\n{'Name':<50} {'Size':>10} {'Archived At':<20}")
    print("-" * 80)

    total_size = 0
    for arch in archives:
        size_str = f"{arch['size'] / 1024:.1f} KB"
        archived_at = arch["archived_at"][:19]  # Trim to seconds
        print(f"{arch['name']:<50} {size_str:>10} {archived_at:<20}")
        total_size += arch["size"]

    print("-" * 80)
    print(f"Total: {len(archives)} files, {total_size / 1024 / 1024:.2f} MB")


def main():
    parser = argparse.ArgumentParser(
        description="Archive test results for historical tracking"
    )
    parser.add_argument(
        "--type",
        choices=["utest", "itest", "stest", "ftest"],
        help="Archive only specific test type",
    )
    parser.add_argument(
        "--keep",
        type=int,
        help="Keep only results from last N days (archive older)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List archived results",
    )
    parser.add_argument(
        "--restore",
        type=str,
        help="Restore specific archive by name",
    )
    parser.add_argument(
        "--cleanup",
        type=int,
        metavar="DAYS",
        help="Remove archives older than N days",
    )
    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Don't compress archived files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be archived without doing it",
    )

    args = parser.parse_args()

    # List archives
    if args.list:
        archives = list_archives()
        print_archive_list(archives)
        return 0

    # Restore from archive
    if args.restore:
        restored = restore_file(args.restore)
        if restored:
            print(f"Restored: {restored}")
            return 0
        return 1

    # Cleanup old archives
    if args.cleanup:
        removed = cleanup_old_archives(args.cleanup)
        print(f"Removed {removed} old archives")
        return 0

    # Archive results
    files = get_result_files(
        test_type=args.type,
        older_than_days=args.keep,
    )

    if not files:
        print("No files to archive")
        return 0

    if args.dry_run:
        print("Would archive:")
        for f in files:
            print(f"  - {f.name}")
        return 0

    print(f"Archiving {len(files)} result files...")
    archived = 0

    for filepath in files:
        archive_path = archive_file(filepath, compress=not args.no_compress)
        if archive_path:
            print(f"  ✓ {filepath.name} → {archive_path.name}")
            archived += 1
        else:
            print(f"  ✗ Failed: {filepath.name}")

    print(f"\nArchived {archived}/{len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
