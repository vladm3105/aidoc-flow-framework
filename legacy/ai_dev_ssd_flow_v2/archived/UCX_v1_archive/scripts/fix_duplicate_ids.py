#!/usr/bin/env python3
"""
Standalone script to fix duplicate element IDs in BRD documents.

Usage:
    python scripts/fix_duplicate_ids.py <brd_path> [--dry-run] [--verbose]

Examples:
    # Preview changes without modifying files
    python scripts/fix_duplicate_ids.py docs/01_BRD/BRD-01_platform --dry-run

    # Apply fixes with verbose output
    python scripts/fix_duplicate_ids.py docs/01_BRD/BRD-01_platform --verbose

    # Fix all BRDs in a directory
    for d in docs/01_BRD/BRD-*/; do python scripts/fix_duplicate_ids.py "$d"; done
"""

import argparse
import sys
from pathlib import Path

# Add UCX to path for standalone execution
ucx_root = Path(__file__).parent.parent
sys.path.insert(0, str(ucx_root))

from ucx.validators.brd.duplicate_fixer import DuplicateElementFixer, DuplicateFixResult


def main():
    parser = argparse.ArgumentParser(
        description="Fix duplicate element IDs in BRD documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "brd_path",
        type=Path,
        help="Path to BRD document directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Validate path
    if not args.brd_path.exists():
        print(f"Error: Path does not exist: {args.brd_path}", file=sys.stderr)
        sys.exit(1)

    if not args.brd_path.is_dir():
        print(f"Error: Path is not a directory: {args.brd_path}", file=sys.stderr)
        sys.exit(1)

    # Run fixer
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Scanning {args.brd_path}...")

    fixer = DuplicateElementFixer(
        args.brd_path,
        verbose=args.verbose,
        dry_run=args.dry_run,
    )
    result = fixer.fix_duplicates()

    # Print results
    print(f"\n{'='*60}")
    print(f"Duplicate Element ID Fixer Results")
    print(f"{'='*60}")
    print(f"Files scanned:      {result.files_scanned}")
    print(f"Duplicates found:   {result.duplicates_found}")
    print(f"IDs renamed:        {len(result.renames)}")
    print(f"References updated: {result.references_updated}")

    if result.renames:
        print(f"\nRename Operations:")
        for rename in result.renames:
            print(f"  {rename.old_id} → {rename.new_id}")
            print(f"    File: {rename.file_path.name}:{rename.line_number}")

    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  ❌ {error}")

    if args.dry_run and result.renames:
        print(f"\n[DRY RUN] No files were modified. Run without --dry-run to apply changes.")

    # Exit code
    if result.errors:
        sys.exit(1)
    elif result.renames:
        sys.exit(0)
    else:
        print("\n✅ No duplicates found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
