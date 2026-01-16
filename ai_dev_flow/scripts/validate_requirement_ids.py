#!/usr/bin/env python3
"""
Requirement ID and Structure Validator

Validates REQ document IDs, naming conventions, and V2 template compliance.
Ensures:
- REQ-NN ID format compliance
- Filename matches document ID
- V2 mandatory sections present
- No duplicate REQ-IDs
- Proper hierarchical organization
- ID pattern consistency (IDPAT-E001 to IDPAT-W001)
- Element code validation (ELEM-E001, ELEM-W001)

Usage:
    python validate_requirement_ids.py --directory REQ/
    python validate_requirement_ids.py --req-file REQ/api/REQ-01.md
    python validate_requirement_ids.py --directory REQ/ --check-v2-sections
    python validate_requirement_ids.py --directory docs/ --check-id-patterns

Error Codes:
- IDPAT-E001: Inconsistent document ID format
- IDPAT-E002: Inconsistent element ID format
- IDPAT-E003: Mixed ID notation (hyphen vs dot)
- IDPAT-W001: Legacy ID format detected
- ELEM-E001: Undefined element type code
- ELEM-W001: Undocumented custom code
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

try:
    from error_codes import format_error
except ImportError:
    def format_error(code: str, message: str) -> str:
        return f"[{code}] {message}"


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
    REQ_ID_PATTERN = r"^REQ-(\d{2,})$"
    FILENAME_PATTERN = r"^REQ-(\d{2,})_[a-z0-9_]+\.md$"

    # Document ID patterns (hyphen notation: TYPE-NN)
    DOC_ID_HYPHEN_PATTERN = re.compile(
        r'\b(BRD|PRD|EARS|BDD|ADR|SYS|REQ|IMPL|CTR|SPEC|TASKS)-(\d{2,})\b'
    )

    # Element ID patterns (dot notation: TYPE.NN.TT.SS)
    ELEM_ID_DOT_PATTERN = re.compile(
        r'\b(BRD|PRD|EARS|BDD|ADR|SYS|REQ|IMPL|CTR|SPEC|TASKS)\.(\d{2,})\.(\d{2})\.(\d{2,})\b'
    )

    # Mixed notation detection (invalid patterns)
    MIXED_HYPHEN_DOT_PATTERN = re.compile(
        r'\b(BRD|PRD|EARS|BDD|ADR|SYS|REQ|IMPL|CTR|SPEC|TASKS)-(\d{2,})\.(\d{2})\b'
    )
    MIXED_DOT_HYPHEN_PATTERN = re.compile(
        r'\b(BRD|PRD|EARS|BDD|ADR|SYS|REQ|IMPL|CTR|SPEC|TASKS)\.(\d{2,})-(\d{2})\b'
    )

    # Standard element type codes (2-digit codes)
    ELEMENT_TYPE_CODES = {
        "01": "Core Component",
        "02": "API Interface",
        "03": "Data Model",
        "04": "Business Logic",
        "05": "Integration",
        "06": "Security",
        "07": "Error Handling",
        "08": "Configuration",
        "09": "Logging/Monitoring",
        "10": "UI Component",
        "11": "Background Process",
        "12": "Testing",
        "13": "Documentation",
        "14": "Infrastructure",
        "15": "Performance",
        "16": "Caching",
        "17": "Messaging",
        "18": "Workflow",
        "19": "Reporting",
        "20": "Utility",
        # Reserved codes 21-49 for project-specific use
        # Codes 50-99 are considered custom and require documentation
    }

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

    def __init__(
        self,
        check_v2_sections: bool = False,
        check_id_patterns: bool = False,
        check_element_codes: bool = False
    ):
        """Initialize validator."""
        self.check_v2_sections = check_v2_sections
        self.check_id_patterns = check_id_patterns
        self.check_element_codes = check_element_codes
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

        # Check ID patterns if requested
        if self.check_id_patterns:
            self._validate_id_patterns(content, file_path, result)

        # Check element codes if requested
        if self.check_element_codes:
            self._validate_element_codes(content, file_path, result)

        return result

    def _validate_filename(self, file_path: Path, result: ValidationResult) -> bool:
        """Validate filename format."""
        filename = file_path.name

        if not re.match(self.FILENAME_PATTERN, filename):
            result.errors.append(
                f"Invalid filename format: {filename}. "
                "Expected: REQ-NN_descriptive_title.md"
            )
            result.valid = False
            return False

        return True

    def _extract_req_id(self, content: str, result: ValidationResult) -> str:
        """Extract REQ-ID from document header."""
        # Look for ## REQ-NN: Title or # REQ-NN: Title
        id_patterns = [
            r"^##?\s*(REQ-\d{3})",  # ## REQ-01 or # REQ-01
            r"^\*\*ID\*\*:\s*(REQ-\d{3})",  # **ID**: REQ-01
            r"^\|\s*\*\*ID\*\*\s*\|\s*(REQ-\d{3})"  # | **ID** | REQ-01 |
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
                "Expected: REQ-NN (e.g., REQ-01)"
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

    def _validate_id_patterns(
        self,
        content: str,
        file_path: Path,
        result: ValidationResult
    ) -> None:
        """
        Validate ID pattern consistency across the document.

        Checks:
        - IDPAT-E003: Mixed hyphen/dot notation
        - IDPAT-E002: Invalid element ID format
        - IDPAT-W001: Legacy ID format
        """
        filename = file_path.name

        # Check for mixed notation (e.g., REQ-01.02 or REQ.01-02)
        for match in self.MIXED_HYPHEN_DOT_PATTERN.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            result.errors.append(format_error(
                "IDPAT-E003",
                f"{filename}:{line_num}: Mixed ID notation '{match.group(0)}' - "
                "use TYPE-NN for documents, TYPE.NN.TT.SS for elements"
            ))
            result.valid = False

        for match in self.MIXED_DOT_HYPHEN_PATTERN.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            result.errors.append(format_error(
                "IDPAT-E003",
                f"{filename}:{line_num}: Mixed ID notation '{match.group(0)}' - "
                "use TYPE-NN for documents, TYPE.NN.TT.SS for elements"
            ))
            result.valid = False

        # Check document IDs for consistency (should use 3+ digit padding)
        doc_ids = list(self.DOC_ID_HYPHEN_PATTERN.finditer(content))
        if doc_ids:
            # Group by type and check digit consistency
            type_digits = defaultdict(set)
            for match in doc_ids:
                doc_type = match.group(1)
                digits = match.group(2)
                type_digits[doc_type].add(len(digits))

            for doc_type, digit_counts in type_digits.items():
                if len(digit_counts) > 1:
                    line_num = 1  # Report at top of file
                    result.warnings.append(format_error(
                        "IDPAT-E001",
                        f"{filename}: Inconsistent {doc_type} ID digit padding - "
                        f"found {', '.join(sorted(str(d) for d in digit_counts))} digit formats"
                    ))

        # Check for legacy 2-digit ID format
        legacy_pattern = re.compile(
            r'\b(BRD|PRD|ADR|SYS|REQ|SPEC|TASKS)-(\d{2})\b(?!\d)'
        )
        for match in legacy_pattern.finditer(content):
            # Verify it's truly 2-digit (not start of longer ID)
            end_pos = match.end()
            if end_pos < len(content) and content[end_pos].isdigit():
                continue  # Part of longer ID

            line_num = content[:match.start()].count('\n') + 1
            result.warnings.append(format_error(
                "IDPAT-W001",
                f"{filename}:{line_num}: Legacy 2-digit ID format '{match.group(0)}' - "
                "recommend using 3-digit format (TYPE-NNN)"
            ))

    def _validate_element_codes(
        self,
        content: str,
        file_path: Path,
        result: ValidationResult
    ) -> None:
        """
        Validate element type codes in element IDs.

        Checks:
        - ELEM-E001: Unknown element type code
        - ELEM-W001: Custom code (50-99) without documentation
        """
        filename = file_path.name

        # Find all element IDs (TYPE.NN.TT.SS format)
        for match in self.ELEM_ID_DOT_PATTERN.finditer(content):
            doc_type = match.group(1)
            doc_num = match.group(2)
            type_code = match.group(3)
            elem_num = match.group(4)
            line_num = content[:match.start()].count('\n') + 1

            # Check if type code is standard
            if type_code in self.ELEMENT_TYPE_CODES:
                continue  # Valid standard code

            # Check if it's in reserved range (21-49)
            code_int = int(type_code)
            if 21 <= code_int <= 49:
                # Reserved for project-specific - check if documented
                # Look for element type table in document
                elem_table_pattern = rf'\|\s*{type_code}\s*\|[^|]+\|'
                if not re.search(elem_table_pattern, content):
                    result.warnings.append(format_error(
                        "ELEM-W001",
                        f"{filename}:{line_num}: Custom element code '{type_code}' "
                        f"in '{match.group(0)}' should be documented in element type table"
                    ))
            elif 50 <= code_int <= 99:
                # Custom range - must be documented
                elem_table_pattern = rf'\|\s*{type_code}\s*\|[^|]+\|'
                if not re.search(elem_table_pattern, content):
                    result.errors.append(format_error(
                        "ELEM-E001",
                        f"{filename}:{line_num}: Undefined element type code '{type_code}' "
                        f"in '{match.group(0)}' - add to element type table or use standard code"
                    ))
                    result.valid = False
            elif code_int > 99 or code_int < 1:
                # Invalid code range
                result.errors.append(format_error(
                    "ELEM-E001",
                    f"{filename}:{line_num}: Invalid element type code '{type_code}' "
                    f"in '{match.group(0)}' - must be 01-99"
                ))
                result.valid = False

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

            # Skip REF documents (minimal validation only)
            if "-REF-" in req_file.name:
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
    parser.add_argument(
        "--check-id-patterns",
        action="store_true",
        help="Validate ID pattern consistency (IDPAT errors)"
    )
    parser.add_argument(
        "--check-element-codes",
        action="store_true",
        help="Validate element type codes (ELEM errors)"
    )
    parser.add_argument(
        "--all-checks",
        action="store_true",
        help="Run all validation checks"
    )

    args = parser.parse_args()

    if not args.req_file and not args.directory:
        parser.error("Must specify either --req-file or --directory")

    # Determine which checks to run
    check_v2 = args.check_v2_sections or args.all_checks
    check_id = args.check_id_patterns or args.all_checks
    check_elem = args.check_element_codes or args.all_checks

    validator = RequirementIDValidator(
        check_v2_sections=check_v2,
        check_id_patterns=check_id,
        check_element_codes=check_elem
    )

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
