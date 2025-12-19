#!/usr/bin/env python3
"""
PRD (Product Requirements Document) Validator - Layer 2

Validates PRD documents against PRD_SCHEMA.yaml requirements.

Usage:
    python validate_prd.py <file_or_directory>
    python validate_prd.py /path/to/docs/PRD
    python validate_prd.py /path/to/docs/PRD/PRD-001_example.md

Exit Codes:
    0 = Pass (no errors, no warnings)
    1 = Warnings only
    2 = Errors present
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from error_codes import Severity, calculate_exit_code, format_error


# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

# Required metadata custom_fields
REQUIRED_CUSTOM_FIELDS = {
    "document_type": {"allowed": ["prd"]},
    "artifact_type": {"allowed": ["PRD"]},
    "layer": {"allowed": [2]},
    "architecture_approaches": {"type": "array"},
    "priority": {"allowed": ["primary", "shared", "fallback"]},
    "development_status": {"allowed": ["active", "draft", "deprecated", "reference"]},
}

# Required tags
REQUIRED_TAGS = ["prd", "layer-2-artifact"]

# Forbidden tag patterns
FORBIDDEN_TAG_PATTERNS = [
    r"^product-prd$",
    r"^feature-prd$",
    r"^product-requirements$",
    r"^product_requirements$",
    r"^prd-\d{3}$",
]

# Required sections (patterns)
REQUIRED_SECTIONS = [
    (r"^# PRD-\d{3}:", "Title (H1 with PRD-NNN format)"),
    (r"^## 0\. Document Control", "Section 0: Document Control"),
    (r"^## 1\. Executive Summary", "Section 1: Executive Summary"),
    (r"^## 2\. Product Vision", "Section 2: Product Vision"),
    (r"^## 3\. Functional Requirements", "Section 3: Functional Requirements"),
]

# BRD reference pattern
BRD_REF_PATTERN = r"@brd:\s*BRD\.\d{2,9}\.\d{2,9}\.\d{2,9}"

# File naming patterns
# Monolithic: PRD-NNN_slug.md
FILE_NAME_PATTERN_MONOLITHIC = r"^PRD-\d{3}_[a-z0-9_]+\.md$"
# Section (shortened): PRD-NNN.S_section_type.md (PREFERRED for nested folders)
FILE_NAME_PATTERN_SECTION_SHORT = r"^PRD-\d{3}\.\d+_[a-z_]+\.md$"
# Section (full): PRD-NNN.S_slug_section_type.md (backward compatible)
FILE_NAME_PATTERN_SECTION_FULL = r"^PRD-\d{3}\.\d+_[a-z0-9_]+_[a-z_]+\.md$"


# =============================================================================
# VALIDATION RESULT TYPES
# =============================================================================

class ValidationResult:
    """Holds validation results for a single file."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors: List[Tuple[str, str]] = []  # (code, message)
        self.warnings: List[Tuple[str, str]] = []

    def add_error(self, code: str, message: str):
        self.errors.append((code, message))

    def add_warning(self, code: str, message: str):
        self.warnings.append((code, message))

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def print_results(self):
        """Print validation results."""
        if not self.errors and not self.warnings:
            print(f"[INFO] VAL-I002: {self.file_path} - All checks passed")
            return

        for code, msg in self.errors:
            print(f"[ERROR] {code}: {self.file_path} - {msg}")

        for code, msg in self.warnings:
            print(f"[WARNING] {code}: {self.file_path} - {msg}")


# =============================================================================
# PARSING FUNCTIONS
# =============================================================================

def parse_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """
    Extract YAML frontmatter from markdown content.

    Returns:
        Tuple of (metadata dict or None, remaining content)
    """
    if not content.startswith("---"):
        return None, content

    # Find closing ---
    end_match = re.search(r"\n---\n", content[3:])
    if not end_match:
        return None, content

    yaml_content = content[3:end_match.start() + 3]
    remaining = content[end_match.end() + 3:]

    try:
        metadata = yaml.safe_load(yaml_content)
        return metadata, remaining
    except yaml.YAMLError:
        return None, content


def extract_sections(content: str) -> List[Tuple[str, int]]:
    """
    Extract section headers and their line numbers.

    Returns:
        List of (header text, line number)
    """
    sections = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        if line.startswith("#"):
            sections.append((line, i))

    return sections


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_file_name(file_path: Path, result: ValidationResult):
    """Validate file naming convention."""
    file_name = file_path.name

    # Skip template files
    if "TEMPLATE" in file_name.upper():
        return

    # Check against all valid patterns
    is_monolithic = re.match(FILE_NAME_PATTERN_MONOLITHIC, file_name)
    is_section_short = re.match(FILE_NAME_PATTERN_SECTION_SHORT, file_name)
    is_section_full = re.match(FILE_NAME_PATTERN_SECTION_FULL, file_name)

    if not (is_monolithic or is_section_short or is_section_full):
        result.add_warning(
            "PRD-W002",
            f"File name '{file_name}' doesn't match valid PRD format. "
            "Expected: PRD-NNN_slug.md (monolithic) or PRD-NNN.S_section.md (nested)"
        )


def validate_metadata(metadata: Optional[Dict], result: ValidationResult):
    """Validate YAML frontmatter metadata."""
    if metadata is None:
        result.add_error("PRD-E002", "Missing YAML frontmatter")
        return

    # Check for custom_fields
    custom_fields = metadata.get("custom_fields", {})
    if not custom_fields:
        result.add_error("PRD-E002", "Missing custom_fields in frontmatter")
        return

    # Validate required custom fields
    for field, rules in REQUIRED_CUSTOM_FIELDS.items():
        value = custom_fields.get(field)

        if value is None:
            result.add_error("PRD-E002", f"Missing required field: custom_fields.{field}")
            continue

        # Check allowed values
        if "allowed" in rules:
            if value not in rules["allowed"]:
                result.add_error(
                    "PRD-E002",
                    f"Invalid value for {field}: '{value}'. Allowed: {rules['allowed']}"
                )

        # Check type
        if "type" in rules:
            if rules["type"] == "array" and not isinstance(value, list):
                result.add_error(
                    "PRD-E002",
                    f"Field {field} must be an array, got {type(value).__name__}"
                )

    # Validate required tags
    tags = metadata.get("tags", [])
    if not isinstance(tags, list):
        result.add_error("PRD-E003", "Tags must be an array")
        tags = []

    for required_tag in REQUIRED_TAGS:
        if required_tag not in tags:
            if required_tag == "prd":
                result.add_error("PRD-E003", f"Missing required tag: '{required_tag}'")
            elif required_tag == "layer-2-artifact":
                result.add_error("PRD-E004", f"Missing required tag: '{required_tag}'")

    # Check for forbidden tags
    for tag in tags:
        for pattern in FORBIDDEN_TAG_PATTERNS:
            if re.match(pattern, str(tag)):
                result.add_error("PRD-E003", f"Forbidden tag pattern: '{tag}'")


def validate_structure(content: str, sections: List[Tuple[str, int]], result: ValidationResult):
    """Validate document structure."""
    # Check H1 format
    h1_sections = [s for s in sections if s[0].startswith("# ") and not s[0].startswith("## ")]

    if len(h1_sections) == 0:
        result.add_error("PRD-E001", "Missing H1 title")
    elif len(h1_sections) > 1:
        result.add_error("PRD-E001", f"Multiple H1 headings found ({len(h1_sections)})")
    else:
        h1_text = h1_sections[0][0]
        if not re.match(r"^# PRD-\d{3}:", h1_text):
            result.add_error("PRD-E001", f"Invalid H1 format. Expected '# PRD-NNN: Title', got '{h1_text[:50]}'")

    # Check required sections
    section_headers = [s[0] for s in sections]
    for pattern, section_name in REQUIRED_SECTIONS[1:]:  # Skip H1, already checked
        found = any(re.match(pattern, h) for h in section_headers)
        if not found:
            result.add_error("PRD-E002", f"Missing required section: {section_name}")

    # Check for duplicate section numbers
    section_numbers = []
    for header, line_num in sections:
        match = re.match(r"^## (\d+)\.", header)
        if match:
            num = int(match.group(1))
            if num in section_numbers:
                result.add_error("PRD-E002", f"Duplicate section number: {num} at line {line_num}")
            section_numbers.append(num)

    # Check section numbering sequence
    if section_numbers:
        expected = list(range(section_numbers[0], section_numbers[0] + len(section_numbers)))
        if section_numbers != expected:
            result.add_warning("PRD-W001", "Section numbers not sequential")


def validate_traceability(content: str, result: ValidationResult):
    """Validate upstream traceability (BRD reference)."""
    # Look for @brd: reference in Document Control section
    doc_control_match = re.search(
        r"## 0\. Document Control.*?(?=## \d+\.|\Z)",
        content,
        re.DOTALL
    )

    if doc_control_match:
        doc_control = doc_control_match.group(0)

        # Check for @brd: reference
        if not re.search(BRD_REF_PATTERN, doc_control):
            # Check if there's a Related BRD row without proper format
            if re.search(r"Related BRD", doc_control, re.IGNORECASE):
                if not re.search(r"@brd:", doc_control):
                    result.add_error("PRD-E005", "Related BRD missing @brd: prefix")
            else:
                result.add_error("PRD-E005", "Missing BRD traceability in Document Control")


def validate_feature_ids(content: str, result: ValidationResult):
    """Validate feature ID format."""
    # Look for Feature ID patterns in tables
    # Expected format: simple 3-digit (001, 015, 042)
    feature_table_match = re.search(
        r"\| Feature ID \|.*?\n\|[-:\s|]+\n(.*?)(?=\n\n|\n##|\Z)",
        content,
        re.DOTALL
    )

    if feature_table_match:
        table_rows = feature_table_match.group(1)

        # Extract feature IDs from first column
        for line in table_rows.split("\n"):
            if "|" in line:
                cols = [c.strip() for c in line.split("|")]
                if len(cols) >= 2:
                    feature_id = cols[1].strip()
                    if feature_id and not re.match(r"^\d{3}$", feature_id):
                        # Skip header-like content
                        if not feature_id.startswith("-") and feature_id != "Feature ID":
                            result.add_warning(
                                "PRD-W001",
                                f"Feature ID '{feature_id}' not in 3-digit format (NNN)"
                            )


def validate_prd_file(file_path: Path) -> ValidationResult:
    """
    Validate a single PRD file.

    Args:
        file_path: Path to PRD markdown file

    Returns:
        ValidationResult with all issues found
    """
    result = ValidationResult(str(file_path))

    # Check file exists
    if not file_path.exists():
        result.add_error("VAL-E001", "File not found")
        return result

    # Check file extension
    if file_path.suffix.lower() not in [".md", ".markdown"]:
        result.add_error("VAL-E003", f"Invalid file extension: {file_path.suffix}")
        return result

    # Read content
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        result.add_error("VAL-E005", f"Failed to read file: {e}")
        return result

    # Parse frontmatter
    metadata, body = parse_frontmatter(content)

    # Extract sections
    sections = extract_sections(content)

    # Run validations
    validate_file_name(file_path, result)
    validate_metadata(metadata, result)
    validate_structure(content, sections, result)
    validate_traceability(content, result)
    validate_feature_ids(content, result)

    return result


def validate_directory(dir_path: Path) -> List[ValidationResult]:
    """
    Validate all PRD files in a directory.

    Args:
        dir_path: Path to directory containing PRD files

    Returns:
        List of ValidationResult for each file
    """
    results = []

    # Find PRD files
    patterns = ["PRD-*.md", "prd-*.md", "PRD_*.md"]
    prd_files = []

    for pattern in patterns:
        prd_files.extend(dir_path.glob(f"**/{pattern}"))

    if not prd_files:
        print(f"[WARNING] VAL-W001: No PRD files found in {dir_path}")
        return results

    for file_path in sorted(set(prd_files)):
        result = validate_prd_file(file_path)
        results.append(result)

    return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PRD Document Validator (Layer 2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_prd.py /path/to/docs/PRD
  python validate_prd.py /path/to/PRD-001_example.md
  python validate_prd.py . --verbose
        """
    )

    parser.add_argument(
        "path",
        type=Path,
        help="PRD file or directory to validate"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output"
    )

    args = parser.parse_args()

    # Validate path exists
    if not args.path.exists():
        print(f"[ERROR] VAL-E001: Path not found: {args.path}")
        return 2

    # Run validation
    if args.path.is_file():
        results = [validate_prd_file(args.path)]
    else:
        results = validate_directory(args.path)

    # Collect all issues
    all_errors = []
    all_warnings = []

    for result in results:
        result.print_results()
        all_errors.extend(result.errors)
        all_warnings.extend(result.warnings)

    # Print summary
    if args.verbose or results:
        print(f"\n{'=' * 40}")
        print(f"PRD Validation Summary")
        print(f"{'=' * 40}")
        print(f"Files validated: {len(results)}")
        print(f"Errors: {len(all_errors)}")
        print(f"Warnings: {len(all_warnings)}")
        print(f"Status: {'PASS' if not all_errors else 'FAIL'}")

    # Return exit code
    return calculate_exit_code(all_errors, all_warnings, args.strict)


if __name__ == "__main__":
    sys.exit(main())
