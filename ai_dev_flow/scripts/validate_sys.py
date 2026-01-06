#!/usr/bin/env python3
"""
SYS (System Requirements) Validator - Layer 6

Validates SYS documents against SYS_SCHEMA.yaml requirements.

Usage:
    python validate_sys.py <file_or_directory>
    python validate_sys.py /path/to/docs/SYS
    python validate_sys.py /path/to/docs/SYS/SYS-001_example.md

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
    "document_type": {"allowed": ["sys", "template"]},
    "artifact_type": {"allowed": ["SYS"]},
    "layer": {"allowed": [6]},
    "architecture_approaches": {"type": "array"},
    "priority": {"allowed": ["primary", "shared", "fallback"]},
    "development_status": {"allowed": ["active", "draft", "deprecated", "reference"]},
}

# Required tags
REQUIRED_TAGS = ["sys", "layer-6-artifact"]
TEMPLATE_TAGS = ["sys-template", "layer-6-artifact"]

# Forbidden tag patterns
FORBIDDEN_TAG_PATTERNS = [
    r"^system-requirements$",
    r"^sys-doc$",
    r"^sys-\d{3}$",
]

# Required sections (patterns) - 15 sections
# Required sections (patterns) - Standard (15 sections)
REQUIRED_SECTIONS_STANDARD = [
    (r"^# SYS-\d{2,}:", "Title (H1 with SYS-NN+ format)"),
    (r"^## 1\. Document Control", "Section 1: Document Control"),
    (r"^## 2\. Executive Summary", "Section 2: Executive Summary"),
    (r"^## 3\. Scope", "Section 3: Scope"),
    (r"^## 4\. Functional Requirements", "Section 4: Functional Requirements"),
    (r"^## 5\. Quality Attributes", "Section 5: Quality Attributes"),
    (r"^## 6\. Interface Specifications", "Section 6: Interface Specifications"),
    (r"^## 7\. Data Management", "Section 7: Data Management"),
    (r"^## 8\. Testing Requirements", "Section 8: Testing Requirements"),
    (r"^## 9\. Deployment Requirements", "Section 9: Deployment Requirements"),
    (r"^## 10\. Compliance Requirements", "Section 10: Compliance Requirements"),
    (r"^## 11\. Acceptance Criteria", "Section 11: Acceptance Criteria"),
    (r"^## 12\. Risk Assessment", "Section 12: Risk Assessment"),
    (r"^## 13\. Traceability", "Section 13: Traceability"),
    (r"^## 14\. Implementation Notes", "Section 14: Implementation Notes"),
    (r"^## 15\. Change History", "Section 15: Change History"),
]

# Required sections (patterns) - MVP (12 sections)
REQUIRED_SECTIONS_MVP = [
    (r"^# SYS-\d{2,}:", "Title (H1 with SYS-NN+ format)"),
    (r"^## 1\. Document Control", "Section 1: Document Control"),
    (r"^## 2\. Executive Summary", "Section 2: Executive Summary"),
    (r"^## 3\. Scope", "Section 3: Scope"),
    (r"^## 4\. Functional Requirements", "Section 4: Functional Requirements"),
    (r"^## 5\. Quality Attributes", "Section 5: Quality Attributes"),
    (r"^## 6\. Interface Specifications", "Section 6: Interface Specifications"),
    (r"^## 7\. Data Management Requirements", "Section 7: Data Management Requirements"),
    # MVP combines or reorders:
    # 8. Deployment & Operations (matches standard 9 but different name/number)
    (r"^## 8\. Deployment and Operations Requirements", "Section 8: Deployment and Operations Requirements"),
    # 9. Testing Requirements (matches standard 8 but different number)
    (r"^## 9\. Testing and Validation Requirements", "Section 9: Testing and Validation Requirements"),
    # 10. Acceptance Criteria (matches standard 11)
    (r"^## 10\. Acceptance Criteria", "Section 10: Acceptance Criteria"),
    # 11. Risk Assessment (matches standard 12)
    (r"^## 11\. Risk Assessment", "Section 11: Risk Assessment"),
    # 12. Traceability (matches standard 13)
    (r"^## 12\. Traceability", "Section 12: Traceability"),
]

# Map profiles to section lists
SECTION_MAP = {
    "standard": REQUIRED_SECTIONS_STANDARD,
    "mvp": REQUIRED_SECTIONS_MVP
}

# Quality attribute categories to check
QUALITY_CATEGORIES = [
    "performance",
    "reliability",
    "scalability",
    "security",
    "observability",
    "maintainability",
]

# File naming pattern (2+ digits per ID_NAMING_STANDARDS.md)
FILE_NAME_PATTERN = r"^SYS-\d{2,}_[a-z0-9_]+\.md$"


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


def extract_section_content(content: str, section_pattern: str) -> Optional[str]:
    """
    Extract content between a section header and the next section.

    Returns:
        Section content or None if not found
    """
    match = re.search(
        f"({section_pattern}.*?)(?=^## \\d+\\.|\\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )
    return match.group(1) if match else None


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_file_name(file_path: Path, result: ValidationResult):
    """Validate file naming convention."""
    file_name = file_path.name

    # Skip template files
    if "TEMPLATE" in file_name.upper():
        return

    if not re.match(FILE_NAME_PATTERN, file_name):
        result.add_warning(
            "SYS-E001",
            f"File name '{file_name}' doesn't match SYS-NNN_name.md format"
        )


def validate_metadata(metadata: Optional[Dict], result: ValidationResult, is_template: bool = False):
    """Validate YAML frontmatter metadata."""
    if metadata is None:
        result.add_error("SYS-E002", "Missing YAML frontmatter")
        return

    # Check for custom_fields
    custom_fields = metadata.get("custom_fields", {})
    if not custom_fields:
        result.add_error("SYS-E002", "Missing custom_fields in frontmatter")
        return

    # Validate required custom fields
    for field, rules in REQUIRED_CUSTOM_FIELDS.items():
        value = custom_fields.get(field)

        if value is None:
            result.add_error("SYS-E002", f"Missing required field: custom_fields.{field}")
            continue

        # Check allowed values
        if "allowed" in rules:
            if value not in rules["allowed"]:
                result.add_error(
                    "SYS-E002",
                    f"Invalid value for {field}: '{value}'. Allowed: {rules['allowed']}"
                )

        # Check type
        if "type" in rules:
            if rules["type"] == "array" and not isinstance(value, list):
                result.add_error(
                    "SYS-E002",
                    f"Field {field} must be an array, got {type(value).__name__}"
                )

    # Validate required tags
    tags = metadata.get("tags", [])
    if not isinstance(tags, list):
        result.add_error("SYS-E002", "Tags must be an array")
        tags = []

    required = TEMPLATE_TAGS if is_template else REQUIRED_TAGS

    for required_tag in required:
        if required_tag not in tags:
            if required_tag in ["sys", "sys-template"]:
                result.add_error("SYS-E002", f"Missing required tag: '{required_tag}'")
            elif required_tag == "layer-6-artifact":
                result.add_error("SYS-E003", f"Missing required tag: '{required_tag}'")

    # Check for forbidden tags
    for tag in tags:
        for pattern in FORBIDDEN_TAG_PATTERNS:
            if re.match(pattern, str(tag)):
                result.add_error("SYS-E002", f"Forbidden tag pattern: '{tag}'")


def validate_structure(content: str, sections: List[Tuple[str, int]], result: ValidationResult, metadata: Optional[Dict] = None):
    """Validate document structure."""
    # Check H1 format
    h1_sections = [s for s in sections if s[0].startswith("# ") and not s[0].startswith("## ")]

    if len(h1_sections) == 0:
        result.add_error("SYS-E001", "Missing H1 title")
    elif len(h1_sections) > 1:
        result.add_error("SYS-E001", f"Multiple H1 headings found ({len(h1_sections)})")
    else:
        h1_text = h1_sections[0][0]
        if not re.match(r"^# SYS-\d{2,}:", h1_text):
            result.add_error("SYS-E001", f"Invalid H1 format. Expected '# SYS-NN+: Title', got '{h1_text[:50]}'")

    # Determine profile and required sections
    profile = "standard"
    if metadata and "custom_fields" in metadata:
        profile = metadata["custom_fields"].get("template_profile", "standard")
    
    # Handle unknown profile (default to standard)
    if profile not in SECTION_MAP:
        result.add_warning("SYS-W001", f"Unknown template_profile '{profile}', defaulting to standard validation")
        profile = "standard"
        
    required_sections = SECTION_MAP[profile]

    # Check required sections
    section_headers = [s[0] for s in sections]
    for pattern, section_name in required_sections[1:]:  # Skip H1, already checked
        found = any(re.match(pattern, h) for h in section_headers)
        if not found:
            result.add_error("SYS-E005", f"Missing required section for {profile} profile: {section_name}")

    # Check section numbering is sequential
    section_numbers = []
    for header, line_num in sections:
        match = re.match(r"^## (\d+)\.", header)
        if match:
            section_numbers.append(int(match.group(1)))

    if section_numbers:
        # Standard: 1-15, MVP: 1-12
        max_section = 12 if profile == "mvp" else 15
        expected = list(range(1, max_section + 1))
        
        # Check if we have roughly the right sections, allow some gaps if sections are optional in future
        # But for strictly defined templates, we expect exact matches
        missing = set(expected) - set(section_numbers)
        if missing:
             # Just warn if standard, because MVP might be stricter on fewer sections
             # But if we use SECTION_MAP, we effectively enforced presence.
             # This check is just for sequentiality and completeness of numbering range.
             # If MVP has 1-12, expected is 1-12.
             # If missing 10, it's missing.
             result.add_warning("SYS-E005", f"Missing section numbers: {sorted(missing)}")


def validate_functional_requirements(content: str, result: ValidationResult):
    """Validate Functional Requirements section (Section 4)."""
    fr_content = extract_section_content(content, r"## 4\. Functional Requirements")

    if not fr_content:
        result.add_error("SYS-E005", "Missing Section 4: Functional Requirements")
        return

    # Check for FR-NNN format
    fr_ids = re.findall(r"\bFR-(\d{3})\b", fr_content)
    if not fr_ids:
        result.add_warning("SYS-W001", "No FR-NNN format requirements found in Section 4")


def validate_quality_attributes(content: str, result: ValidationResult):
    """Validate Quality Attributes section (Section 5)."""
    qa_content = extract_section_content(content, r"## 5\. Quality Attributes")

    if not qa_content:
        result.add_warning("SYS-W001", "Missing Section 5: Quality Attributes")
        return

    qa_lower = qa_content.lower()

    # Check for required categories
    if "performance" not in qa_lower:
        result.add_warning("SYS-W001", "Quality Attributes missing Performance category")

    if "security" not in qa_lower:
        result.add_warning("SYS-W001", "Quality Attributes missing Security category")

    if "reliability" not in qa_lower:
        result.add_info("SYS-I001", "Consider adding Reliability category with MTBF/MTTR metrics")

    # Check for 4-segment numbering pattern
    qa_ids = re.findall(r"SYS\.\d{2,9}\.\d{2,9}\.\d{2,9}", qa_content)
    if not qa_ids:
        result.add_warning("SYS-W001", "Quality attributes not using 4-segment format (SYS.NN.EE.SS)")


def validate_traceability(content: str, result: ValidationResult):
    """Validate upstream traceability tags (Layer 6 requires 5 upstream refs)."""
    # Look for cumulative tags
    has_brd = bool(re.search(r"@brd:", content))
    has_prd = bool(re.search(r"@prd:", content))
    has_ears = bool(re.search(r"@ears:", content))
    has_bdd = bool(re.search(r"@bdd:", content))
    has_adr = bool(re.search(r"@adr:", content))

    missing = []
    if not has_brd:
        missing.append("@brd")
    if not has_prd:
        missing.append("@prd")
    if not has_ears:
        missing.append("@ears")
    if not has_bdd:
        missing.append("@bdd")
    if not has_adr:
        missing.append("@adr")

    if missing:
        result.add_warning(
            "SYS-E004",
            f"Missing cumulative traceability tags (Layer 6 requires 5): {', '.join(missing)}"
        )


def validate_testing_requirements(content: str, result: ValidationResult):
    """Validate Testing Requirements section (Section 8)."""
    test_content = extract_section_content(content, r"## 8\. Testing Requirements")

    if not test_content:
        result.add_warning("SYS-W001", "Missing Section 8: Testing Requirements")
        return

    test_lower = test_content.lower()

    # Check for coverage targets
    if "coverage" not in test_lower and "%" not in test_content:
        result.add_warning("SYS-W001", "Testing Requirements missing coverage targets")


def validate_interface_specs(content: str, result: ValidationResult):
    """Validate Interface Specifications section (Section 6)."""
    iface_content = extract_section_content(content, r"## 6\. Interface Specifications")

    if not iface_content:
        result.add_warning("SYS-E006", "Missing Section 6: Interface Specifications")
        return

    iface_lower = iface_content.lower()

    # Check for external interfaces
    if "external" not in iface_lower:
        result.add_warning("SYS-W001", "Interface Specifications missing External Interfaces")


def validate_sys_file(file_path: Path) -> ValidationResult:
    """
    Validate a single SYS file.

    Args:
        file_path: Path to SYS markdown file

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

    # Validate file name
    validate_file_name(file_path, result)

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
    validate_metadata(metadata, result, is_template)
    validate_structure(content, sections, result, metadata)
    validate_functional_requirements(content, result)
    validate_quality_attributes(content, result)
    validate_interface_specs(content, result)
    validate_testing_requirements(content, result)
    validate_traceability(content, result)

    return result


def validate_directory(dir_path: Path) -> List[ValidationResult]:
    """
    Validate all SYS files in a directory.

    Args:
        dir_path: Path to directory containing SYS files

    Returns:
        List of ValidationResult for each file
    """
    results = []

    # Find SYS files
    patterns = ["SYS-*.md", "sys-*.md", "SYS_*.md"]
    sys_files = []

    for pattern in patterns:
        sys_files.extend(dir_path.glob(f"**/{pattern}"))

    if not sys_files:
        print(f"[WARNING] VAL-W001: No SYS files found in {dir_path}")
        return results

    for file_path in sorted(set(sys_files)):
        result = validate_sys_file(file_path)
        results.append(result)

    return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SYS Document Validator (Layer 6)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_sys.py /path/to/docs/SYS
  python validate_sys.py /path/to/SYS-001_example.md
  python validate_sys.py . --verbose
        """
    )

    parser.add_argument(
        "path",
        type=Path,
        help="SYS file or directory to validate"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output including info messages"
    )

    args = parser.parse_args()

    # Validate path exists
    if not args.path.exists():
        print(f"[ERROR] VAL-E001: Path not found: {args.path}")
        return 2

    # Run validation
    if args.path.is_file():
        results = [validate_sys_file(args.path)]
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
        print(f"SYS Validation Summary")
        print(f"{'=' * 40}")
        print(f"Files validated: {len(results)}")
        print(f"Errors: {len(all_errors)}")
        print(f"Warnings: {len(all_warnings)}")
        print(f"Status: {'PASS' if not all_errors else 'FAIL'}")

    # Return exit code
    return calculate_exit_code(all_errors, all_warnings, args.strict)


if __name__ == "__main__":
    sys.exit(main())
