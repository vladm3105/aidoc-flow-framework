#!/usr/bin/env python3
"""
REQ V1 to V2 Migration Script
Purpose: Update existing REQ files to allow for the new V2 metadata fields.
- Adds 'Category: Functional' (default)
- Adds 'Infrastructure Type: None' (default)
- Preserves existing values if already present
"""

import sys
import re
from pathlib import Path
import argparse

def migrate_file(file_path: Path, dry_run: bool = False) -> bool:
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Failed to read {file_path}: {e}")
        return False

    original_content = content
    modified = False

    # Check and add Category
    if not re.search(r"\|\s*\*\*Category\*\*", content):
        # Insert Category after Priority
        priority_pattern = r"(\|\s*\*\*Priority\*\*\s*\|[^|]+\|)"
        if re.search(priority_pattern, content):
            content = re.sub(
                priority_pattern,
                r"\1\n| **Category** | Functional |",
                content
            )
            modified = True
            print(f"  + Added Category: Functional")
        else:
            print(f"  ⚠️  Could not find Priority row to insert Category")

    # Check and add Infrastructure Type
    if not re.search(r"\|\s*\*\*Infrastructure Type\*\*", content):
        # Insert Infrastructure Type after Category (which we might have just added)
        category_pattern = r"(\|\s*\*\*Category\*\*\s*\|[^|]+\|)"
        if re.search(category_pattern, content):
            content = re.sub(
                category_pattern,
                r"\1\n| **Infrastructure Type** | None |",
                content
            )
            modified = True
            print(f"  + Added Infrastructure Type: None")
        else:
             print(f"  ⚠️  Could not find Category row to insert Infrastructure Type")

    if modified:
        if not dry_run:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Migrated {file_path.name}")
        else:
            print(f"🔍 [DRY RUN] Would migrate {file_path.name}")
        return True
    else:
        print(f"Example {file_path.name} is already up to date")
        return False

def main():
    parser = argparse.ArgumentParser(description="Migrate REQ files to V2 template metadata")
    parser.add_argument("directory", type=Path, help="Directory containing REQ files")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = parser.parse_args()

    if not args.directory.exists():
        print(f"Directory not found: {args.directory}")
        sys.exit(1)

    count = 0
    print(f"Scanning {args.directory}...")
    for file_path in args.directory.rglob("REQ-*.md"):
        if "TEMPLATE" in file_path.name:
            continue
        if migrate_file(file_path, args.dry_run):
            count += 1
    
    print(f"\nMigration complete. Modified {count} files.")

if __name__ == "__main__":
    main()
