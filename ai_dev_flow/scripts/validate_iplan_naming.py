#!/usr/bin/env python3
"""
IPLAN Naming Convention Validator

Validates IPLAN (Implementation Plan) files against non-timestamped naming standards.

Format: IPLAN-NN_{descriptive_slug}.md
- NN+: Sequential ID (2 or more digits, zero-padded e.g., 01, 02, 003)
- descriptive_slug: Lowercase, underscore-separated description

Validation Checks:
1. Filename pattern compliance
2. Sequential ID format (2+ digits)
3. Descriptive slug format (lowercase, underscores only)
4. File extension (.md)
5. H1 ID format inside file
6. Sequential ID ordering

Reference: ID_NAMING_STANDARDS.md lines 123-145
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional


class IPLANValidator:
    """Validates IPLAN files against naming conventions."""

    # Regex pattern for IPLAN filename (no timestamps)
    FILENAME_PATTERN = re.compile(r'^IPLAN-(\d{2,})_([a-z0-9_]+)\.md$')

    # Regex pattern for H1 ID inside file
    H1_PATTERN = re.compile(r'^#\s+IPLAN-(\d{2,}):\s+(.+)$', re.MULTILINE)

    def __init__(self, base_path: Path):
        """Initialize validator with base path."""
        self.base_path = base_path
        self.iplan_dir = base_path / "IPLAN"
        self.errors = []
        self.warnings = []

    def validate_filename(self, filename: str) -> Optional[Tuple[str, str]]:
        """
        Validate IPLAN filename format.

        Returns tuple of (id, slug) if valid, None otherwise.
        """
        match = self.FILENAME_PATTERN.match(filename)
        if not match:
            return None

        iplan_id, slug = match.groups()
        return iplan_id, slug

    # Timestamp validation removed: timestamps are not part of the filename pattern

    def validate_slug(self, slug: str, filename: str) -> bool:
        """Validate descriptive slug format."""
        # Check lowercase only
        if slug != slug.lower():
            self.errors.append(f"{filename}: Slug must be lowercase (found '{slug}')")
            return False

        # Check valid characters (alphanumeric and underscores only)
        if not re.match(r'^[a-z0-9]+(?:_[a-z0-9]+)*$', slug):
            self.errors.append(
                f"{filename}: Slug must contain only lowercase letters, "
                f"numbers, and underscores (found '{slug}')"
            )
            return False

        # Check no consecutive underscores
        if '__' in slug:
            self.errors.append(f"{filename}: Slug contains consecutive underscores")
            return False

        # Check no leading/trailing underscores
        if slug.startswith('_') or slug.endswith('_'):
            self.errors.append(f"{filename}: Slug cannot start or end with underscore")
            return False

        return True

    def validate_id_format(self, iplan_id: str, filename: str) -> bool:
        """Validate IPLAN ID format (2+ digits)."""
        if not iplan_id.isdigit():
            self.errors.append(f"{filename}: ID must be numeric (found '{iplan_id}')")
            return False

        id_len = len(iplan_id)
        if id_len < 2:
            self.errors.append(
                f"{filename}: ID must be at least 2 digits (zero-padded)"
            )
            return False

        return True

    def validate_h1_id(self, filepath: Path, expected_id: str) -> bool:
        """Validate H1 ID inside file matches filename ID."""
        try:
            content = filepath.read_text(encoding='utf-8')
            match = self.H1_PATTERN.search(content)

            if not match:
                self.errors.append(
                    f"{filepath.name}: Missing or invalid H1 ID "
                    f"(expected '# IPLAN-{expected_id}: [Title]')"
                )
                return False

            h1_id = match.group(1)
            if h1_id != expected_id:
                self.errors.append(
                    f"{filepath.name}: H1 ID mismatch "
                    f"(filename has IPLAN-{expected_id}, H1 has IPLAN-{h1_id})"
                )
                return False

            return True

        except Exception as e:
            self.errors.append(f"{filepath.name}: Error reading file - {e}")
            return False

    def validate_sequential_ordering(self, iplan_files: List[Tuple[str, str]]) -> bool:
        """Validate IPLAN IDs are sequential without gaps."""
        if not iplan_files:
            return True

        # Sort by ID
        sorted_files = sorted(iplan_files, key=lambda x: int(x[1]))

        # Check for gaps
        expected_id = 1
        for filename, iplan_id in sorted_files:
            id_num = int(iplan_id)
            if id_num != expected_id:
                self.warnings.append(
                    f"Sequential gap: Expected IPLAN-{expected_id:03d}, "
                    f"found IPLAN-{iplan_id} in {filename}"
                )
            expected_id = id_num + 1

        return True

    def validate_all(self) -> bool:
        """
        Validate all IPLAN files in IPLAN directory.

        Returns True if all validations pass, False otherwise.
        """
        if not self.iplan_dir.exists():
            print(f"IPLAN directory not found: {self.iplan_dir}")
            return True  # Not an error if directory doesn't exist yet

        # Find all IPLAN markdown files
        iplan_files = []
        all_files = list(self.iplan_dir.glob("IPLAN-*.md"))

        # Filter out template and index files
        template_files = {"IPLAN-TEMPLATE.md", "IPLAN-000_index.md",
                         "IPLAN-000_TRACEABILITY_MATRIX-TEMPLATE.md"}

        for filepath in all_files:
            filename = filepath.name

            # Skip template files
            if filename in template_files:
                continue

            # Validate filename format
            result = self.validate_filename(filename)
            if not result:
                self.errors.append(
                    f"{filename}: Invalid filename format. "
                    f"Expected: IPLAN-NN_{{descriptive_slug}}.md"
                )
                continue

            iplan_id, slug = result

            # Validate components
            valid = True
            valid &= self.validate_id_format(iplan_id, filename)
            valid &= self.validate_slug(slug, filename)

            if valid:
                # Validate H1 ID inside file
                self.validate_h1_id(filepath, iplan_id)
                iplan_files.append((filename, iplan_id))

        # Validate sequential ordering
        if iplan_files:
            self.validate_sequential_ordering(iplan_files)

        return len(self.errors) == 0

    def print_results(self) -> None:
        """Print validation results."""
        if self.errors:
            print("\n❌ IPLAN Naming Validation FAILED")
            print("=" * 80)
            print("\nERRORS:")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ IPLAN Naming Validation PASSED")
            print("=" * 80)
            print("All IPLAN files follow naming conventions.")

        if not self.errors and self.warnings:
            print("\n✅ IPLAN Naming Validation PASSED (with warnings)")
            print("=" * 80)


def main():
    """Main entry point."""
    # Determine base path
    script_dir = Path(__file__).parent
    base_path = script_dir.parent

    # Allow custom base path as argument
    if len(sys.argv) > 1:
        base_path = Path(sys.argv[1])

    print(f"Validating IPLAN files in: {base_path}/IPLAN/")
    print("=" * 80)

    # Run validation
    validator = IPLANValidator(base_path)
    success = validator.validate_all()
    validator.print_results()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
