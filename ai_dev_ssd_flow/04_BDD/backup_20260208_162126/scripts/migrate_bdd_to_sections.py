#!/usr/bin/env python3
"""
BDD Migration Script: Legacy to Section-Based Format

Purpose: Automate migration from legacy BDD formats to section-based structure.

Supports two migration paths:

Path A: Single-File BDD → Section-Based
  Input: BDD-NN_slug.feature (single large file)
  Output: BDD-NN.1_section1.feature, BDD-NN.2_section2.feature, etc.
  User must manually split scenarios into logical sections

Path B: Directory-Based → Section-Based
  Input: BDD-NN_{slug}/features/*.feature
  Output: Flat structure at BDD/ root with section-based naming

Features:
  - Dry-run mode (preview changes without modification)
  - Extracts suite number from directory/file name
  - Generates section filenames from existing files
  - Moves companion docs to BDD root
  - Archives legacy structure
  - Validates after migration

Usage:
  # Dry run (preview only)
  python migrate_bdd_to_sections.py --root docs/BDD --suite BDD-02_knowledge_engine --dry-run
  
  # Actual migration
  python migrate_bdd_to_sections.py --root docs/BDD --suite BDD-02_knowledge_engine
  
  # Validate after migration
  python validate_bdd_suite.py --root docs/BDD

Exit codes:
  0 = success, 1 = errors encountered
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class MigrationAction:
    """Represents a single migration action."""
    action_type: str  # move_file, create_file, archive_dir, create_dir
    source: Path | None
    dest: Path | None
    description: str


def extract_suite_number(name: str) -> str | None:
    """
    Extract suite number from directory or file name.
    
    Examples:
      BDD-02_knowledge_engine → 02
      BDD-03_user_auth.feature → 03
    """
    match = re.match(r"BDD-(\d{2,})", name)
    return match.group(1) if match else None


def detect_migration_type(root: Path, suite_name: str) -> Tuple[str, Path | None]:
    """
    Detect which migration path applies.
    
    Returns:
      ("directory-based", suite_dir) - BDD-NN_{slug}/features/ structure
      ("single-file", feature_file) - BDD-NN_slug.feature file
      ("already-migrated", None) - Already section-based
      ("unknown", None) - Cannot detect
    """
    suite_dir = root / suite_name
    
    # Check for directory-based structure
    if suite_dir.is_dir():
        features_dir = suite_dir / "features"
        if features_dir.exists() and any(features_dir.glob("*.feature")):
            return ("directory-based", suite_dir)
    
    # Check for single-file format
    single_file = root / f"{suite_name}.feature"
    if single_file.exists():
        # Verify it's not already section-based
        if not re.match(r"^BDD-\d{2,}\.\d+_[a-z0-9_]+\.feature$", single_file.name):
            return ("single-file", single_file)
    
    # Check if already migrated (has section-based files)
    suite_num = extract_suite_number(suite_name)
    if suite_num:
        section_files = list(root.glob(f"BDD-{suite_num}.*_*.feature"))
        if section_files:
            return ("already-migrated", None)
    
    return ("unknown", None)


def plan_directory_migration(root: Path, suite_dir: Path, dry_run: bool = False) -> List[MigrationAction]:
    """
    Plan migration from directory-based to section-based format.
    
    Path B: BDD-NN_{slug}/features/*.feature → BDD-NN.S_{slug}.feature
    """
    actions: List[MigrationAction] = []
    suite_num = extract_suite_number(suite_dir.name)
    
    if not suite_num:
        return actions
    
    features_dir = suite_dir / "features"
    if not features_dir.exists():
        return actions
    
    # Find all .feature files in features/ directory
    feature_files = sorted(features_dir.glob("*.feature"))
    
    # Generate section-based filenames
    for idx, feature_file in enumerate(feature_files, start=1):
        # Extract slug from original filename
        # BDD-02_ingest.feature → ingest
        # BDD-02_query_processing.feature → query_processing
        original_slug = feature_file.stem
        # Remove BDD-NN_ prefix if present
        slug = re.sub(r"^BDD-\d{2,}_", "", original_slug)
        
        # Generate section-based filename: BDD-NN.S_{slug}.feature
        new_filename = f"BDD-{suite_num}.{idx}_{slug}.feature"
        dest_path = root / new_filename
        
        actions.append(
            MigrationAction(
                action_type="move_file",
                source=feature_file,
                dest=dest_path,
                description=f"Migrate {feature_file.relative_to(root)} → {new_filename}"
            )
        )
    
    # Move companion docs (README, TRACEABILITY, GLOSSARY) to BDD root
    companion_docs = [
        suite_dir / f"BDD-{suite_num}_README.md",
        suite_dir / f"BDD-{suite_num}_TRACEABILITY.md",
        suite_dir / f"BDD-{suite_num}_GLOSSARY.md",
        suite_dir / "README.md",
    ]
    
    for doc in companion_docs:
        if doc.exists():
            # Move to BDD root with suite prefix
            if doc.name == "README.md":
                dest_name = f"BDD-{suite_num}_README.md"
            else:
                dest_name = doc.name
            dest_path = root / dest_name
            
            actions.append(
                MigrationAction(
                    action_type="move_file",
                    source=doc,
                    dest=dest_path,
                    description=f"Move companion doc {doc.name} → {dest_name}"
                )
            )
    
    # Create index file (BDD-NN.0_index.md) from template
    index_file = root / f"BDD-{suite_num}.0_index.md"
    actions.append(
        MigrationAction(
            action_type="create_file",
            source=None,
            dest=index_file,
            description=f"Create index file: BDD-{suite_num}.0_index.md (from template)"
        )
    )
    
    # Archive the old directory structure
    archive_dir = root / "archive"
    archive_dest = archive_dir / suite_dir.name
    actions.append(
        MigrationAction(
            action_type="archive_dir",
            source=suite_dir,
            dest=archive_dest,
            description=f"Archive legacy directory: {suite_dir.name} → archive/{suite_dir.name}"
        )
    )
    
    return actions


def plan_single_file_migration(root: Path, single_file: Path, dry_run: bool = False) -> List[MigrationAction]:
    """
    Plan migration from single-file to section-based format.
    
    Path A: BDD-NN_slug.feature → Manual section splitting required
    
    This function creates guidance for manual splitting.
    """
    actions: List[MigrationAction] = []
    suite_num = extract_suite_number(single_file.name)
    
    if not suite_num:
        return actions
    
    actions.append(
        MigrationAction(
            action_type="create_file",
            source=single_file,
            dest=root / f"MIGRATION_GUIDE_BDD-{suite_num}.md",
            description=(
                f"Single-file migration requires manual splitting. "
                f"Create MIGRATION_GUIDE_BDD-{suite_num}.md with instructions."
            )
        )
    )
    
    # Archive the single file
    archive_dir = root / "archive"
    archive_dest = archive_dir / f"{single_file.stem}.feature.txt"
    actions.append(
        MigrationAction(
            action_type="archive_dir",
            source=single_file,
            dest=archive_dest,
            description=f"Archive legacy file: {single_file.name} → archive/{single_file.stem}.feature.txt"
        )
    )
    
    return actions


def execute_migration(actions: List[MigrationAction], dry_run: bool = False) -> bool:
    """
    Execute migration actions.
    
    Returns True if successful, False if errors occurred.
    """
    if dry_run:
        print("\n=== DRY RUN MODE - No changes will be made ===\n")
    
    errors = 0
    
    for action in actions:
        if dry_run:
            print(f"[DRY RUN] {action.action_type.upper()}: {action.description}")
            continue
        
        try:
            if action.action_type == "move_file":
                print(f"Moving: {action.source} → {action.dest}")
                action.dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(action.source), str(action.dest))
            
            elif action.action_type == "create_file":
                print(f"Creating: {action.dest}")
                action.dest.parent.mkdir(parents=True, exist_ok=True)
                
                # Create index file from template
                if action.dest.name.endswith(".0_index.md"):
                    suite_num = extract_suite_number(action.dest.name)
                    create_index_file(action.dest, suite_num)
                
                # Create migration guide for single-file
                elif action.dest.name.startswith("MIGRATION_GUIDE"):
                    create_migration_guide(action.dest, action.source)
            
            elif action.action_type == "archive_dir":
                print(f"Archiving: {action.source} → {action.dest}")
                action.dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(action.source), str(action.dest))
        
        except Exception as e:
            print(f"ERROR: {action.description}: {e}")
            errors += 1
    
    return errors == 0


def create_index_file(dest: Path, suite_num: str) -> None:
    """Create index file from template."""
    template = f"""# BDD-{suite_num}.0: Test Suite Index

**Version**: 1.0
**Last Updated**: [YYYY-MM-DD]
**Status**: Active
**Parent Document**: BDD-{suite_num}

---

## Document Control

| Field | Value |
|-------|-------|
| **Document ID** | BDD-{suite_num}.0 |
| **Document Type** | BDD Suite Index |
| **Version** | 1.0 |
| **Status** | Active |
| **Created** | [YYYY-MM-DD] |
| **Last Updated** | [YYYY-MM-DD] |
| **Owner** | [Team/Role] |

---

## Suite Overview

**Purpose**: [Brief description of what this BDD suite tests]

**Scope**: Define boundaries of test coverage
- ✅ **In Scope**: What is tested
- ❌ **Out of Scope**: What is not tested

---

## Section File Map

| Section | File | Scenarios | Lines | Status | Description |
|---------|------|-----------|-------|--------|-------------|
| {suite_num}.1 | BDD-{suite_num}.1_[slug].feature | XX | XXX | Active | [Description] |
| {suite_num}.2 | BDD-{suite_num}.2_[slug].feature | XX | XXX | Active | [Description] |
| {suite_num}.3 | BDD-{suite_num}.3_[slug].feature | XX | XXX | Active | [Description] |

**TODO**: Update section map with actual file details

---

## Traceability Matrix

### Upstream Dependencies

| BDD Section | Upstream Source | Description |
|-------------|----------------|-------------|
| BDD-{suite_num}.1 | [BRD/PRD/EARS] | [Description] |
| BDD-{suite_num}.2 | [BRD/PRD/EARS] | [Description] |

**TODO**: Update traceability links

---

**Document Path**: `BDD/BDD-{suite_num}.0_index.md`
**Framework**: AI Dev Flow SDD
**Layer**: 4 (BDD - Behavior-Driven Development)
**Last Updated**: [YYYY-MM-DD]
"""
    
    dest.write_text(template, encoding="utf-8")


def create_migration_guide(dest: Path, source_file: Path) -> None:
    """Create migration guide for single-file splitting."""
    suite_num = extract_suite_number(source_file.name)
    
    guide = f"""# Migration Guide: BDD-{suite_num} Single-File to Section-Based

## Source File
- **Original**: `{source_file.name}`
- **Location**: `{source_file.parent}`

## Migration Steps

### 1. Analyze Current Structure
- Open `{source_file.name}` (now archived)
- Identify logical domain groupings (3-6 sections recommended)
- Count scenarios per logical group

### 2. Design Section Split
Recommended split criteria (in priority order):
1. **Domain modules** (e.g., Ingest, Query, Learning)
2. **Lifecycle phases** (e.g., Setup, Operation, Teardown)
3. **Quality attributes** (e.g., Performance, Security, Reliability)
4. **Requirement groups** (align with EARS/PRD sections)

### 3. Create Section Files
For each logical section:
1. Create file: `BDD-{suite_num}.S_{{slug}}.feature`
   - S = section number (1, 2, 3, ...)
   - slug = descriptive name (lowercase, underscores)
2. Add section metadata tags:
   ```gherkin
   @section: {suite_num}.S
   @parent_doc: BDD-{suite_num}
   @index: BDD-{suite_num}.0_index.md
   @brd:BRD.XX.YY.ZZ
   @prd:PRD.AA.BB.CC
   @ears:EARS.NN.SS.RR
   ```
3. Update Feature title: `Feature: BDD-{suite_num}.S: [Section Name]`
4. Copy scenarios to appropriate section (max 12 per section)
5. Verify each file ≤500 lines

### 4. Create Index File
1. Create `BDD-{suite_num}.0_index.md` from template
2. Update section file map with actual files
3. Add traceability matrix linking to upstream requirements

### 5. Validate
```bash
python3 scripts/validate_bdd_suite.py --root BDD
```

### 6. Archive Original
Original file already archived at: `archive/{source_file.stem}.feature.txt`

## Example Section Split

Assuming original file has ~100 scenarios across 3 domains:

```
BDD-{suite_num}.1_ingest_analysis.feature (35 scenarios, 387 lines)
BDD-{suite_num}.2_query_search.feature (40 scenarios, 421 lines)
BDD-{suite_num}.3_learning_adaptation.feature (25 scenarios, 298 lines)
```

Each section file:
- ≤500 lines
- ≤12 scenarios per Feature block (may need multiple Feature blocks)
- Section-based metadata tags
- Proper traceability to upstream requirements

---

**Next Step**: Manually create section files following this guide
"""
    
    dest.write_text(guide, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate BDD from legacy formats to section-based structure"
    )
    parser.add_argument(
        "--root",
        default="BDD",
        help="Root directory for BDD files (default: BDD)",
    )
    parser.add_argument(
        "--suite",
        required=True,
        help="Suite to migrate (e.g., BDD-02_knowledge_engine)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    args = parser.parse_args()
    
    root = Path(args.root).resolve()
    suite_name = args.suite
    
    # Detect migration type
    migration_type, source_path = detect_migration_type(root, suite_name)
    
    print(f"Migration analysis for: {suite_name}")
    print(f"Migration type: {migration_type}")
    
    if migration_type == "already-migrated":
        print("✓ Suite already uses section-based format. No migration needed.")
        return 0
    
    if migration_type == "unknown":
        print(f"ERROR: Cannot detect migration path for {suite_name}")
        print("Expected one of:")
        print(f"  - Directory: {root}/{suite_name}/features/*.feature")
        print(f"  - Single file: {root}/{suite_name}.feature")
        return 1
    
    # Plan migration
    actions: List[MigrationAction] = []
    
    if migration_type == "directory-based":
        print(f"Source: {source_path}")
        actions = plan_directory_migration(root, source_path, args.dry_run)
    elif migration_type == "single-file":
        print(f"Source: {source_path}")
        actions = plan_single_file_migration(root, source_path, args.dry_run)
    
    if not actions:
        print("ERROR: No migration actions planned")
        return 1
    
    print(f"\nPlanned actions: {len(actions)}")
    for action in actions:
        print(f"  - {action.description}")
    
    # Execute migration
    print("\nExecuting migration...")
    success = execute_migration(actions, dry_run=args.dry_run)
    
    if not success:
        print("\n❌ Migration completed with errors")
        return 1
    
    if args.dry_run:
        print("\n✓ Dry run completed successfully. Run without --dry-run to apply changes.")
    else:
        print("\n✓ Migration completed successfully")
        print("\nNext steps:")
        print("  1. Review migrated files")
        print("  2. Update section metadata tags (@section, @brd, @prd, @ears)")
        print("  3. Update index file (BDD-NN.0_index.md)")
        print("  4. Run validation: python3 scripts/validate_bdd_suite.py --root BDD")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
