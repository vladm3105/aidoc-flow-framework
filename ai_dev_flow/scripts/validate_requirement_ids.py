#!/usr/bin/env python3
"""
Requirement ID and Structure Validator

Validates REQ document IDs, naming conventions, and V2 template compliance.
Ensures:
- REQ-NNN ID format compliance
- Filename matches document ID
- V2 mandatory sections present
- No duplicate REQ-IDs
- Proper hierarchical organization

Usage:
    python validate_requirement_ids.py --directory REQ/
    python validate_requirement_ids.py --req-file REQ/api/REQ-001.md
    python validate_requirement_ids.py --directory REQ/ --check-v2-sections
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ValidationResult:
    """Result of requirement ID validation."""
    file_path: Path
    req_id: str = ""
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class RequirementIDValidator:
    """Validator for REQ document IDs and structure."""

    # ID patterns
    REQ_ID_PATTERN = r"^REQ-(\d{3})$"
    FILENAME_PATTERN = r"^REQ-(\d{3})_[a-z0-9_]+\.md$"

    # V2 mandatory sections
    V2_SECTIONS = {
        1: r"##\s*1\.\s*Description",
        2: r"##\s*2\.\s*Document\s+Control",
        3: r"##\s*3\.\s*Interface\s+Specifications?",
        4: r"##\s*4\.\s*Data\s+Schemas?",
        5: r"##\s*5\.\s*Error\s+Handling\s+Specifications?",
        6: r"##\s*6\.\s*Configuration\s+Specifications?",
        7: r"##\s*7\.\s*Quality\s+Attributes",
        8: r"##\s*8\.\s*Implementation\s+Guidance",
        9: r"##\s*9\.\s*Acceptance\s+Criteria",
        10: r"##\s*10\.\s*Verification\s+Methods",
        11: r"##\s*11\.\s*Traceability",
        12: r"##\s*12\.\s*Change\s+History"
    }

    def __init__(self, check_v2_sections: bool = False):
        """Initialize validator."""
        self.check_v2_sections = check_v2_sections
        self.seen_ids: Set[str] = set()
        self.id_to_files: Dict[str, List[Path]] = defaultdict(list)

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single REQ file."""
        result = ValidationResult(file_path=file_path)

        # Check filename format
        if not self._validate_filename(file_path, result):
            return result

        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            result.errors.append(f"Failed to read file: {e}")
            result.valid = False
            return result

        # Extract REQ-ID from content
        req_id = self._extract_req_id(content, result)
        if not req_id:
            result.valid = False
            return result

        result.req_id = req_id

        # Check ID format
        if not self._validate_id_format(req_id, result):
            result.valid = False
            return result

        # Check filename matches ID
        self._validate_filename_id_match(file_path, req_id, result)

        # Check for duplicate IDs
        self._check_duplicate_id(req_id, file_path, result)

        # Check V2 sections if requested
        if self.check_v2_sections:
            self._validate_v2_sections(content, result)

        # Check document control metadata
        self._validate_document_control(content, result)

        return result

    def _validate_filename(self, file_path: Path, result: ValidationResult) -> bool:
        """Validate filename format."""
        filename = file_path.name

        if not re.match(self.FILENAME_PATTERN, filename):
            result.errors.append(
                f"Invalid filename format: {filename}. "
                "Expected: REQ-NNN_descriptive_title.md"
            )
            result.valid = False
            return False

        return True

    def _extract_req_id(self, content: str, result: ValidationResult) -> str:
        """Extract REQ-ID from document header."""
        # Look for ## REQ-NNN: Title or # REQ-NNN: Title
        id_patterns = [
            r"^##?\s*(REQ-\d{3})",  # ## REQ-001 or # REQ-001
            r"^\*\*ID\*\*:\s*(REQ-\d{3})",  # **ID**: REQ-001
            r"^\|\s*\*\*ID\*\*\s*\|\s*(REQ-\d{3})"  # | **ID** | REQ-001 |
        ]

        for pattern in id_patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return match.group(1)

        result.errors.append("REQ-ID not found in document header")
        return ""

    def _validate_id_format(self, req_id: str, result: ValidationResult) -> bool:
        """Validate REQ-ID format."""
        if not re.match(self.REQ_ID_PATTERN, req_id):
            result.errors.append(
                f"Invalid REQ-ID format: {req_id}. "
                "Expected: REQ-NNN (e.g., REQ-001)"
            )
            return False

        return True

    def _validate_filename_id_match(
        self,
        file_path: Path,
        req_id: str,
        result: ValidationResult
    ) -> None:
        """Check if filename matches document ID."""
        filename = file_path.name
        id_in_filename = filename.split('_')[0]

        if id_in_filename != req_id:
            result.errors.append(
                f"Filename ID ({id_in_filename}) does not match "
                f"document ID ({req_id})"
            )
            result.valid = False

    def _check_duplicate_id(
        self,
        req_id: str,
        file_path: Path,
        result: ValidationResult
    ) -> None:
        """Check for duplicate REQ-IDs."""
        self.id_to_files[req_id].append(file_path)

        if req_id in self.seen_ids:
            result.errors.append(
                f"Duplicate REQ-ID: {req_id} found in multiple files"
            )
            result.valid = False
        else:
            self.seen_ids.add(req_id)

    def _validate_v2_sections(self, content: str, result: ValidationResult) -> None:
        """Validate presence of V2 mandatory sections."""
        missing_sections = []

        for section_num, pattern in self.V2_SECTIONS.items():
            if not re.search(pattern, content, re.IGNORECASE):
                missing_sections.append(section_num)

        if missing_sections:
            result.warnings.append(
                f"Missing V2 sections: {', '.join(map(str, missing_sections))}"
            )

            # Critical sections (3-6) are errors
            critical_missing = [s for s in missing_sections if 3 <= s <= 6]
            if critical_missing:
                result.errors.append(
                    f"Missing critical V2 sections: {', '.join(map(str, critical_missing))}. "
                    "Sections 3-6 are mandatory for SPEC-ready REQs"
                )
                result.valid = False

    def _validate_document_control(self, content: str, result: ValidationResult) -> None:
        """Validate document control metadata."""
        required_fields = [
            (r"\*\*Status\*\*", "Status"),
            (r"\*\*Version\*\*", "Version"),
            (r"\*\*Priority\*\*", "Priority"),
            (r"\*\*Category\*\*", "Category")
        ]

        missing_fields = []

        for pattern, field_name in required_fields:
            if not re.search(pattern, content):
                missing_fields.append(field_name)

        if missing_fields:
            result.warnings.append(
                f"Missing Document Control fields: {', '.join(missing_fields)}"
            )

    def validate_directory(self, directory: Path) -> List[ValidationResult]:
        """Validate all REQ files in a directory."""
        results = []

        for req_file in directory.rglob("REQ-*.md"):
            # Skip archived files
            if "archived" in str(req_file).lower():
                continue

            # Skip templates
            if "TEMPLATE" in req_file.name:
                continue

            # Skip index files
            if "REQ-000" in req_file.name or "index" in req_file.name.lower():
                continue

            result = self.validate_file(req_file)
            results.append(result)

        # Report duplicate IDs
        for req_id, files in self.id_to_files.items():
            if len(files) > 1:
                print(f"\n❌ DUPLICATE ID: {req_id} found in:")
                for file_path in files:
                    print(f"    - {file_path}")

        return results

    def print_report(self, results: List[ValidationResult]) -> None:
        """Print validation report."""
        print("\n" + "=" * 80)
        print("REQUIREMENT ID VALIDATION REPORT")
        print("=" * 80 + "\n")

        valid = [r for r in results if r.valid]
        invalid = [r for r in results if not r.valid]

        print(f"Total Files: {len(results)}")
        print(f"Valid: {len(valid)}")
        print(f"Invalid: {len(invalid)}")
        print(f"Unique REQ-IDs: {len(self.seen_ids)}\n")

        # Check for ID gaps
        id_numbers = sorted([
            int(req_id.split('-')[1])
            for req_id in self.seen_ids
        ])

        if id_numbers:
            gaps = []
            for i in range(id_numbers[0], id_numbers[-1] + 1):
                if i not in id_numbers and i != 0:  # Skip REQ-000 (index)
                    gaps.append(i)

            if gaps:
                print(f"⚠️  ID Gaps: REQ-{', REQ-'.join(f'{g:03d}' for g in gaps)}\n")

        # Detailed results
        for result in results:
            if not result.valid:
                print(f"❌ FAIL {result.file_path.name}")

                for error in result.errors:
                    print(f"    ❌ ERROR: {error}")

                for warning in result.warnings:
                    print(f"    ⚠️  WARNING: {warning}")

                print()

        # Summary of warnings for valid files
        valid_with_warnings = [r for r in valid if r.warnings]
        if valid_with_warnings:
            print(f"\n✅ Valid files with warnings: {len(valid_with_warnings)}")
            for result in valid_with_warnings:
                print(f"    {result.file_path.name}")
                for warning in result.warnings:
                    print(f"        ⚠️  {warning}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate REQ document IDs and structure"
    )
    parser.add_argument(
        "--req-file",
        type=Path,
        help="Path to specific REQ file to validate"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        help="Path to directory containing REQ files"
    )
    parser.add_argument(
        "--check-v2-sections",
        action="store_true",
        help="Validate V2 template section compliance"
    )

    args = parser.parse_args()

    if not args.req_file and not args.directory:
        parser.error("Must specify either --req-file or --directory")

    validator = RequirementIDValidator(check_v2_sections=args.check_v2_sections)

    if args.req_file:
        results = [validator.validate_file(args.req_file)]
    else:
        results = validator.validate_directory(args.directory)

    if not results:
        print("No REQ files found to validate")
        sys.exit(0)

    validator.print_report(results)

    # Exit with error code if any validations failed
    if any(not r.valid for r in results):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
