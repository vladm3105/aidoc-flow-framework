#!/usr/bin/env python3
"""
BRD (Business Requirements Document) Validator - Layer 1

Validates BRD documents against BRD_SCHEMA.yaml requirements.

Usage:
    python validate_brd.py <file_or_directory>
    python validate_brd.py /path/to/docs/BRD
    python validate_brd.py /path/to/docs/BRD/BRD-01_example.md

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
    "document_type": {"allowed": ["brd", "template"]},
    "artifact_type": {"allowed": ["BRD"]},
    "layer": {"allowed": [1]},
    "architecture_approaches": {"type": "array"},
    "priority": {"allowed": ["primary", "shared", "fallback"]},
    "development_status": {"allowed": ["active", "draft", "deprecated", "reference"]},
}

# Required tags
REQUIRED_TAGS = ["brd", "layer-1-artifact"]

# Forbidden tag patterns
FORBIDDEN_TAG_PATTERNS = [
    r"^business-brd$",
    r"^business-requirements$",
    r"^business_requirements$",
    r"^brd-\d{3}$",
]

# Required sections (patterns)
# Required sections (patterns)
REQUIRED_SECTIONS_STANDARD = [
    (r"^# BRD-\d{2,}:", "Title (H1 with BRD-NN format)"),
    (r"^## 0\. Document Control", "Section 0: Document Control"),
    (r"^## 1\. Executive Summary", "Section 1: Executive Summary"),
    (r"^## 2\. Business Context", "Section 2: Business Context"),
    (r"^## 3\. Business Requirements", "Section 3: Business Requirements"),
]

REQUIRED_SECTIONS_MVP = [
    (r"^# BRD-\d{2,}:", "Title (H1 with BRD-NN format)"),
    (r"^## 0\. Document Control", "Section 0: Document Control"),
    (r"^## 1\. Introduction", "Section 1: Introduction"),
    (r"^## 2\. Business Objectives", "Section 2: Business Objectives"),
    (r"^## 3\. Project Scope", "Section 3: Project Scope"),
    (r"^## 4\. Stakeholders", "Section 4: Stakeholders"),
    (r"^## 5\. User Stories", "Section 5: User Stories"),
    (r"^## 6\. Functional Requirements", "Section 6: Functional Requirements"),
    (r"^## 7\. Quality Attributes", "Section 7: Quality Attributes"),
    (r"^## 8\. Business Constraints and Assumptions", "Section 8: Business Constraints and Assumptions"),
    (r"^## 9\. Acceptance Criteria", "Section 9: Acceptance Criteria"),
    (r"^## 10\. Business Risk Management", "Section 10: Business Risk Management"),
    (r"^## 11\. Implementation Approach", "Section 11: Implementation Approach"),
    (r"^## 12\. Cost-Benefit Analysis", "Section 12: Cost-Benefit Analysis"),
    (r"^## 13\. Traceability", "Section 13: Traceability"),
    (r"^## 14\. Glossary", "Section 14: Glossary"),
    (r"^## 15\. Appendices", "Section 15: Appendices"),
]

# Map profiles to section lists
SECTION_MAP = {
    "standard": REQUIRED_SECTIONS_STANDARD,
    "mvp": REQUIRED_SECTIONS_MVP
}

# File naming patterns
# Monolithic: BRD-NN_slug.md
FILE_NAME_PATTERN_MONOLITHIC = r"^BRD-\d{2,}_[a-z0-9_]+\.md$"
# Section (shortened): BRD-NN.S_section_type.md (PREFERRED for nested folders)
FILE_NAME_PATTERN_SECTION_SHORT = r"^BRD-\d{2,}\.\d+_[a-z_]+\.md$"
# Section (full): BRD-NN.S_slug_section_type.md (backward compatible)
FILE_NAME_PATTERN_SECTION_FULL = r"^BRD-\d{2,}\.\d+_[a-z0-9_]+_[a-z_]+\.md$"


# =============================================================================
# VALIDATION RESULT TYPES
# =============================================================================

class ValidationResult:
    """Holds validation results for a single file."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors: List[Tuple[str, str]] = []  # (code, message)
        self.warnings: List[Tuple[str, str]] = []
        self.info: List[Tuple[str, str]] = []

    def add_error(self, code: str, message: str):
        self.errors.append((code, message))

    def add_warning(self, code: str, message: str):
        self.warnings.append((code, message))

    def add_info(self, code: str, message: str):
        self.info.append((code, message))

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

        for code, msg in self.info:
            print(f"[INFO] {code}: {self.file_path} - {msg}")


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
            "BRD-W002",
            f"File name '{file_name}' doesn't match valid BRD format. "
            "Expected: BRD-NN_slug.md (monolithic) or BRD-NN.S_section.md (nested)"
        )


def validate_metadata(metadata: Optional[Dict], result: ValidationResult, is_template: bool = False):
    """Validate YAML frontmatter metadata."""
    if metadata is None:
        result.add_error("BRD-E002", "Missing YAML frontmatter")
        return

    # Check for custom_fields
    custom_fields = metadata.get("custom_fields", {})
    if not custom_fields:
        result.add_error("BRD-E002", "Missing custom_fields in frontmatter")
        return

    # Validate required custom fields
    for field, rules in REQUIRED_CUSTOM_FIELDS.items():
        value = custom_fields.get(field)

        if value is None:
            result.add_error("BRD-E002", f"Missing required field: custom_fields.{field}")
            continue

        # Check allowed values
        if "allowed" in rules:
            if value not in rules["allowed"]:
                result.add_error(
                    "BRD-E002",
                    f"Invalid value for {field}: '{value}'. Allowed: {rules['allowed']}"
                )

        # Check type
        if "type" in rules:
            if rules["type"] == "array" and not isinstance(value, list):
                result.add_error(
                    "BRD-E002",
                    f"Field {field} must be an array, got {type(value).__name__}"
                )

    # Validate required tags
    tags = metadata.get("tags", [])
    if not isinstance(tags, list):
        result.add_error("BRD-E003", "Tags must be an array")
        tags = []

    # Skip tag validation for templates
    if not is_template:
        for required_tag in REQUIRED_TAGS:
            if required_tag not in tags:
                if required_tag == "brd":
                    result.add_error("BRD-E003", f"Missing required tag: '{required_tag}'")
                elif required_tag == "layer-1-artifact":
                    result.add_error("BRD-E004", f"Missing required tag: '{required_tag}'")

    # Check for forbidden tags
    for tag in tags:
        for pattern in FORBIDDEN_TAG_PATTERNS:
            if re.match(pattern, str(tag)):
                result.add_error("BRD-E003", f"Forbidden tag pattern: '{tag}'")


def validate_structure(content: str, sections: List[Tuple[str, int]], result: ValidationResult, metadata: Optional[Dict] = None):
    """Validate document structure."""
    # Check H1 format
    h1_sections = [s for s in sections if s[0].startswith("# ") and not s[0].startswith("## ")]

    if len(h1_sections) == 0:
        result.add_error("BRD-E001", "Missing H1 title")
    elif len(h1_sections) > 1:
        result.add_error("BRD-E001", f"Multiple H1 headings found ({len(h1_sections)})")
    else:
        h1_text = h1_sections[0][0]
        if not re.match(r"^# BRD-\d{2,}:", h1_text):
            # Relax check for templates which might use placeholders
            if "TEMPLATE" in getattr(result, 'file_path', '').upper():
                pass
            else:
                result.add_error("BRD-E001", f"Invalid H1 format. Expected '# BRD-NN: Title', got '{h1_text[:50]}'")

    # Determine profile and required sections
    profile = "standard"
    if metadata and "custom_fields" in metadata:
        profile = metadata["custom_fields"].get("template_profile", "standard")
        if profile == "standard" and "template_variant" in metadata["custom_fields"]:
            profile = metadata["custom_fields"]["template_variant"]
    
    # Handle unknown profile (default to standard)
    if profile not in SECTION_MAP:
        result.add_warning("BRD-W001", f"Unknown template_profile '{profile}', defaulting to standard validation")
        profile = "standard"
        
    required_sections = SECTION_MAP[profile]

    # Check required sections
    section_headers = [s[0] for s in sections]
    for pattern, section_name in required_sections[1:]:  # Skip H1, already checked
        found = any(re.match(pattern, h) for h in section_headers)
        if not found:
            result.add_error("BRD-E002", f"Missing required section for {profile} profile: {section_name}")

    # Check for duplicate section numbers
    section_numbers = []
    for header, line_num in sections:
        match = re.match(r"^## (\d+)\.", header)
        if match:
            num = int(match.group(1))
            if num in section_numbers:
                result.add_error("BRD-E002", f"Duplicate section number: {num} at line {line_num}")
            section_numbers.append(num)

    # Check section numbering sequence
    if section_numbers:
        expected = list(range(section_numbers[0], section_numbers[0] + len(section_numbers)))
        if section_numbers != expected:
            result.add_warning("BRD-W001", "Section numbers not sequential")


def validate_document_control(content: str, result: ValidationResult):
    """Validate Document Control section."""
    doc_control_match = re.search(
        r"## 0\. Document Control.*?(?=## \d+\.|\Z)",
        content,
        re.DOTALL
    )

    if not doc_control_match:
        result.add_error("BRD-E002", "Missing Section 0: Document Control")
        return

    doc_control = doc_control_match.group(0)

    # Check for required fields in document control
    required_fields = ["Project Name", "Document Version", "Date", "Document Owner", "Status"]
    for field in required_fields:
        if field not in doc_control:
            result.add_warning("BRD-W001", f"Missing field in Document Control: {field}")


def validate_business_requirements(content: str, result: ValidationResult, metadata: Optional[Dict] = None):
    """Validate Business Requirements (Sec 3 Standard / Sec 6 MVP) structure."""
    
    # Determine profile
    profile = "standard"
    if metadata and "custom_fields" in metadata:
        profile = metadata["custom_fields"].get("template_profile", "standard")
        if profile == "standard" and "template_variant" in metadata["custom_fields"]:
            profile = metadata["custom_fields"]["template_variant"]
        
    if profile == "mvp":
        # MVP: Section 6. Functional Requirements
        pattern = r"## 6\. Functional Requirements.*?(?=## \d+\.|\Z)"
        section_name = "Section 6: Functional Requirements"
        err_code = "BRD-E005"
    else:
        # Standard: Section 3. Business Requirements
        pattern = r"## 3\. Business Requirements.*?(?=## \d+\.|\Z)"
        section_name = "Section 3: Business Requirements"
        err_code = "BRD-E005"

    brd_section_match = re.search(pattern, content, re.DOTALL)

    if not brd_section_match:
        result.add_error(err_code, f"Missing {section_name}")
        return

    brd_section = brd_section_match.group(0)

    # Check for requirement IDs or tables
    has_req_table = "|" in brd_section and ("Requirement" in brd_section or "ID" in brd_section)
    has_req_bullets = re.search(r"^\s*[-*]\s+", brd_section, re.MULTILINE)

    if not (has_req_table or has_req_bullets):
        result.add_warning("BRD-W001", f"{section_name} appears to lack structured requirements (no tables or bullet lists)")


def validate_brd_file(file_path: Path) -> ValidationResult:
    """
    Validate a single BRD file.

    Args:
        file_path: Path to BRD markdown file

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

    # Determine if template
    is_template = "TEMPLATE" in file_path.name.upper()

    # Parse frontmatter
    metadata, body = parse_frontmatter(content)

    # Extract sections
    sections = extract_sections(content)

    # Run validations
    validate_file_name(file_path, result)
    validate_metadata(metadata, result, is_template)
    validate_structure(content, sections, result, metadata)
    validate_document_control(content, result)
    validate_business_requirements(content, result, metadata)

    return result


def validate_directory(dir_path: Path) -> List[ValidationResult]:
    """
    Validate all BRD files in a directory.

    Args:
        dir_path: Path to directory containing BRD files

    Returns:
        List of ValidationResult for each file
    """
    results = []

    # Find BRD files
    patterns = ["BRD-*.md", "brd-*.md", "BRD_*.md"]
    brd_files = []

    for pattern in patterns:
        brd_files.extend(dir_path.glob(f"**/{pattern}"))

    if not brd_files:
        print(f"[WARNING] VAL-W001: No BRD files found in {dir_path}")
        return results

    for file_path in sorted(set(brd_files)):
        result = validate_brd_file(file_path)
        results.append(result)

    return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BRD Document Validator (Layer 1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_brd.py /path/to/docs/BRD
  python validate_brd.py /path/to/BRD-01_example.md
  python validate_brd.py . --verbose
        """
    )

    parser.add_argument(
        "path",
        type=Path,
        help="BRD file or directory to validate"
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
        results = [validate_brd_file(args.path)]
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
        print(f"BRD Validation Summary")
        print(f"{'=' * 40}")
        print(f"Files validated: {len(results)}")
        print(f"Errors: {len(all_errors)}")
        print(f"Warnings: {len(all_warnings)}")
        print(f"Status: {'PASS' if not all_errors else 'FAIL'}")

    # Return exit code
    return calculate_exit_code(all_errors, all_warnings, args.strict)


if __name__ == "__main__":
    sys.exit(main())
