#!/usr/bin/env python3
"""
ADR (Architecture Decision Record) Validator - Layer 5

Validates ADR documents against ADR_MVP_SCHEMA.yaml requirements.

Usage:
    python validate_adr.py <file_or_directory>
    python validate_adr.py /path/to/docs/ADR
    python validate_adr.py /path/to/docs/ADR/ADR-001_example.md

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
SCRIPT_DIR = Path(__file__).resolve().parent
# Add shared scripts directory to path (2 levels up + scripts)
SHARED_SCRIPTS_DIR = SCRIPT_DIR.parents[1] / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

from error_codes import Severity, calculate_exit_code, format_error


# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

# Required metadata custom_fields
REQUIRED_CUSTOM_FIELDS = {
    "document_type": {"allowed": ["adr", "template"]},
    "artifact_type": {"allowed": ["ADR"]},
    "layer": {"allowed": [5]},
    "architecture_approaches": {"type": "array"},
    "priority": {"allowed": ["primary", "shared", "fallback"]},
    "development_status": {"allowed": ["active", "draft", "deprecated", "reference"]},
}

# Required tags
REQUIRED_TAGS = ["adr", "layer-5-artifact"]
TEMPLATE_TAGS = ["adr-template", "layer-5-artifact"]

# Forbidden tag patterns
FORBIDDEN_TAG_PATTERNS = [
    r"^architecture-decision$",
    r"^decision-record$",
    r"^adr-\d{3}$",
]

# Required sections (patterns)
# Required regions (patterns) - Standard
REQUIRED_SECTIONS_STANDARD = [
    (r"^# ADR-\d{2,}:", "Title (H1 with ADR-NN+ format)"),
    (r"^## 1\. Document Control", "Section 1: Document Control"),
    (r"^## 2\. Position in Development Workflow", "Section 2: Position in Development Workflow"),
    (r"^## 3\. Status", "Section 3: Status"),
    (r"^## 4\. Context", "Section 4: Context"),
    (r"^## 5\. Decision", "Section 5: Decision"),
    (r"^## 6\. Requirements Satisfied", "Section 6: Requirements Satisfied"),
    (r"^## 7\. Consequences", "Section 7: Consequences"),
    (r"^## 8\. Architecture Flow", "Section 8: Architecture Flow"),
    (r"^## 9\. Implementation Assessment", "Section 9: Implementation Assessment"),
    (r"^## 10\. Impact Analysis", "Section 10: Impact Analysis"),
]

# Required regions (patterns) - MVP
REQUIRED_SECTIONS_MVP = [
    (r"^# ADR-\d{2,}:", "Title (H1 with ADR-NN+ format)"),
    (r"^## 1\. Document Control", "Section 1: Document Control"),
    (r"^## 2\. Context", "Section 2: Context"),
    (r"^## 3\. Decision", "Section 3: Decision"),
    (r"^## 4\. Alternatives Considered", "Section 4: Alternatives Considered"),
    (r"^## 5\. Consequences", "Section 5: Consequences"),
    (r"^## 6\. Architecture Flow", "Section 6: Architecture Flow"),
    (r"^## 7\. Implementation Assessment", "Section 7: Implementation Assessment"),
    (r"^## 8\. Verification", "Section 8: Verification"),
    (r"^## 9\. Traceability", "Section 9: Traceability"),
    (r"^## 10\. Related Decisions", "Section 10: Related Decisions"),
]

# Map profiles to section lists
SECTION_MAP = {
    "standard": REQUIRED_SECTIONS_STANDARD,
    "mvp": REQUIRED_SECTIONS_MVP
}

# Required subsections
CONTEXT_SUBSECTIONS = [
    (r"### 4\.1 Problem Statement", "4.1 Problem Statement"),
    (r"### 4\.2 Background", "4.2 Background"),
    (r"### 4\.3 Driving Forces", "4.3 Driving Forces"),
    (r"### 4\.4 Constraints", "4.4 Constraints"),
]

DECISION_SUBSECTIONS = [
    (r"### 5\.1 Chosen Solution", "5.1 Chosen Solution"),
    (r"### 5\.2 Key Components", "5.2 Key Components"),
    (r"### 5\.3 Implementation Approach", "5.3 Implementation Approach"),
]

CONSEQUENCES_SUBSECTIONS = [
    (r"### 7\.1 Positive Outcomes", "7.1 Positive Outcomes"),
    (r"### 7\.2 Negative Outcomes", "7.2 Negative Outcomes"),
]

# Valid status values
VALID_STATUS_VALUES = ["Proposed", "Accepted", "Deprecated", "Superseded", "Draft", "In Review", "Approved"]

# File naming patterns
# Monolithic: ADR-NN+_slug.md (2+ digits per ID_NAMING_STANDARDS.md)
FILE_NAME_PATTERN_MONOLITHIC = r"^ADR-\d{2,}_[a-z0-9_]+\.md$"
# Section (shortened): ADR-NN+.S_section_type.md (PREFERRED for nested folders)
FILE_NAME_PATTERN_SECTION_SHORT = r"^ADR-\d{2,}\.\d+_[a-z_]+\.md$"
# Section (full): ADR-NN+.S_slug_section_type.md (backward compatible)
FILE_NAME_PATTERN_SECTION_FULL = r"^ADR-\d{2,}\.\d+_[a-z0-9_]+_[a-z_]+\.md$"


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

    # Check against all valid patterns
    is_monolithic = re.match(FILE_NAME_PATTERN_MONOLITHIC, file_name)
    is_section_short = re.match(FILE_NAME_PATTERN_SECTION_SHORT, file_name)
    is_section_full = re.match(FILE_NAME_PATTERN_SECTION_FULL, file_name)

    if not (is_monolithic or is_section_short or is_section_full):
        result.add_warning(
            "ADR-E001",
            f"File name '{file_name}' doesn't match valid ADR format. "
            "Expected: ADR-NNN_slug.md (monolithic) or ADR-NNN.S_section.md (nested)"
        )


def validate_metadata(metadata: Optional[Dict], result: ValidationResult, is_template: bool = False):
    """Validate YAML frontmatter metadata."""
    if metadata is None:
        result.add_error("ADR-E002", "Missing YAML frontmatter")
        return

    # Check for custom_fields
    custom_fields = metadata.get("custom_fields", {})
    if not custom_fields:
        result.add_error("ADR-E002", "Missing custom_fields in frontmatter")
        return

    # Validate required custom fields
    for field, rules in REQUIRED_CUSTOM_FIELDS.items():
        value = custom_fields.get(field)

        if value is None:
            result.add_error("ADR-E002", f"Missing required field: custom_fields.{field}")
            continue

        # Check allowed values
        if "allowed" in rules:
            if value not in rules["allowed"]:
                result.add_error(
                    "ADR-E002",
                    f"Invalid value for {field}: '{value}'. Allowed: {rules['allowed']}"
                )

        # Check type
        if "type" in rules:
            if rules["type"] == "array" and not isinstance(value, list):
                result.add_error(
                    "ADR-E002",
                    f"Field {field} must be an array, got {type(value).__name__}"
                )

    # Validate required tags
    tags = metadata.get("tags", [])
    if not isinstance(tags, list):
        result.add_error("ADR-E006", "Tags must be an array")
        tags = []

    required = TEMPLATE_TAGS if is_template else REQUIRED_TAGS

    for required_tag in required:
        if required_tag not in tags:
            if required_tag in ["adr", "adr-template"]:
                result.add_error("ADR-E006", f"Missing required tag: '{required_tag}'")
            elif required_tag == "layer-5-artifact":
                result.add_error("ADR-E007", f"Missing required tag: '{required_tag}'")

    # Check for forbidden tags
    for tag in tags:
        for pattern in FORBIDDEN_TAG_PATTERNS:
            if re.match(pattern, str(tag)):
                result.add_error("ADR-E006", f"Forbidden tag pattern: '{tag}'")


def validate_structure(content: str, sections: List[Tuple[str, int]], result: ValidationResult, metadata: Optional[Dict] = None):
    """Validate document structure."""
    # Check H1 format
    h1_sections = [s for s in sections if s[0].startswith("# ") and not s[0].startswith("## ")]

    if len(h1_sections) == 0:
        result.add_error("ADR-E001", "Missing H1 title")
    elif len(h1_sections) > 1:
        result.add_error("ADR-E001", f"Multiple H1 headings found ({len(h1_sections)})")
    else:
        h1_text = h1_sections[0][0]
        if not re.match(r"^# ADR-\d{2,}:", h1_text):
            result.add_error("ADR-E001", f"Invalid H1 format. Expected '# ADR-NN+: Title', got '{h1_text[:50]}'")

    # Determine profile and required sections
    profile = "standard"
    if metadata and "custom_fields" in metadata:
        profile = metadata["custom_fields"].get("template_profile", "standard")
    
    # Handle unknown profile (default to standard)
    if profile not in SECTION_MAP:
        result.add_warning("ADR-W001", f"Unknown template_profile '{profile}', defaulting to standard validation")
        profile = "standard"
        
    required_sections = SECTION_MAP[profile]

    # Check required sections
    section_headers = [s[0] for s in sections]
    for pattern, section_name in required_sections[1:]:  # Skip H1, already checked
        found = any(re.match(pattern, h) for h in section_headers)
        if not found:
            result.add_error("ADR-E002", f"Missing required section for {profile} profile: {section_name}")


def validate_context_section(content: str, result: ValidationResult, metadata: Optional[Dict] = None):
    """Validate Context section and its subsections."""
    # Determine profile
    profile = "standard"
    if metadata and "custom_fields" in metadata:
        profile = metadata["custom_fields"].get("template_profile", "standard")

    if profile == "mvp":
        section_pattern = r"## 2\. Context"
        subsections = [
            (r"### 2\.1 Problem Statement", "2.1 Problem Statement"),
            (r"### 2\.2 Technical Context", "2.2 Technical Context"), # MVP specific
        ]
        # MVP has different subsections than Standard?
        # Template: 2.1 Problem Statement, 2.2 Technical Context
        # Standard: 4.1 Problem Statement, 4.2 Background, 4.3 Driving Forces, 4.4 Constraints
    else:
        section_pattern = r"## 4\. Context"
        subsections = CONTEXT_SUBSECTIONS

    context_content = extract_section_content(content, section_pattern)

    if not context_content:
        # Error is added by validate_structure, but we can add warning here or return
        # If structure validation failed, this might fail too. 
        # But let's check content if section exists.
        return

    # Check required subsections
    for pattern, subsection_name in subsections:
        if not re.search(pattern, context_content):
            if "Problem Statement" in subsection_name:
                result.add_error("ADR-E002", f"Missing required subsection: {subsection_name}")
            else:
                 # In MVP, Technical Context is required? Template has it.
                 # Let's warn.
                result.add_warning("ADR-W001", f"Missing subsection: {subsection_name}")


def validate_decision_section(content: str, result: ValidationResult, metadata: Optional[Dict] = None):
    """Validate Decision section and its subsections."""
    # Determine profile
    profile = "standard"
    if metadata and "custom_fields" in metadata:
        profile = metadata["custom_fields"].get("template_profile", "standard")

    if profile == "mvp":
        section_pattern = r"## 3\. Decision"
        # MVP: 3.1 Chosen Solution, 3.2 Key Components, 3.3 Implementation Approach
        subsections = [
            (r"### 3\.1 Chosen Solution", "3.1 Chosen Solution"),
            (r"### 3\.2 Key Components", "3.2 Key Components"),
            (r"### 3\.3 Implementation Approach", "3.3 Implementation Approach"),
        ]
    else:
        section_pattern = r"## 5\. Decision"
        subsections = DECISION_SUBSECTIONS

    decision_content = extract_section_content(content, section_pattern)

    if not decision_content:
        return

    # Check required subsections
    for pattern, subsection_name in subsections:
        if not re.search(pattern, decision_content):
            if "Chosen Solution" in subsection_name:
                result.add_error("ADR-E003", f"Missing required subsection: {subsection_name}")
            else:
                result.add_warning("ADR-W001", f"Missing subsection: {subsection_name}")


def validate_consequences_section(content: str, result: ValidationResult, metadata: Optional[Dict] = None):
    """Validate Consequences section and its subsections."""
     # Determine profile
    profile = "standard"
    if metadata and "custom_fields" in metadata:
        profile = metadata["custom_fields"].get("template_profile", "standard")

    if profile == "mvp":
        section_pattern = r"## 5\. Consequences"
        # MVP: 5.1 Positive Outcomes, 5.2 Trade-offs & Risks, 5.3 Cost Estimate
        subsections = [
            (r"### 5\.1 Positive Outcomes", "5.1 Positive Outcomes"),
            (r"### 5\.2 Trade-offs & Risks", "5.2 Trade-offs & Risks"),
            # Cost Estimate is new in MVP? It's in template.
        ]
    else:
        section_pattern = r"## 7\. Consequences"
        subsections = CONSEQUENCES_SUBSECTIONS

    consequences_content = extract_section_content(content, section_pattern)

    if not consequences_content:
        return

    # Check required subsections
    for pattern, subsection_name in subsections:
        if not re.search(pattern, consequences_content):
            result.add_error("ADR-E004", f"Missing required subsection: {subsection_name}")


def validate_architecture_section(content: str, result: ValidationResult, metadata: Optional[Dict] = None):
    """Validate Architecture Flow/Overview section contains Mermaid diagram."""
    # Determine profile
    profile = "standard"
    if metadata and "custom_fields" in metadata:
        profile = metadata["custom_fields"].get("template_profile", "standard")
    
    if profile == "mvp":
        section_pattern = r"## 6\. Architecture Overview"
    else:
        section_pattern = r"## 8\. Architecture Flow"

    arch_content = extract_section_content(content, section_pattern)

    if not arch_content:
        # validate_structure checks existence
        return

    # Check for Mermaid diagram
    if "```mermaid" not in arch_content:
        result.add_warning("ADR-E005", f"Architecture section missing Mermaid diagram")


def validate_status(content: str, result: ValidationResult, metadata: Optional[Dict] = None):
    """Validate Status section has valid status value."""
    # Determine profile
    profile = "standard"
    if metadata and "custom_fields" in metadata:
        profile = metadata["custom_fields"].get("template_profile", "standard")
    
    if profile == "mvp":
        # MVP has status in Document Control, validated by existence of Section 1 but generic validator doesn't check table content yet
        # We skip separate Status section check
        return

    status_content = extract_section_content(content, r"## 3\. Status")

    if not status_content:
        result.add_warning("ADR-W001", "Missing Section 3: Status")
        return

    # Check for valid status value
    found_valid = False
    for status in VALID_STATUS_VALUES:
        if status.lower() in status_content.lower():
            found_valid = True
            break

    if not found_valid:
        result.add_warning(
            "ADR-W001",
            f"Status section doesn't contain valid status. Expected one of: {', '.join(VALID_STATUS_VALUES)}"
        )


def validate_traceability(content: str, result: ValidationResult):
    """Validate upstream traceability tags."""
    # Look for cumulative tags
    has_brd = bool(re.search(r"@brd:", content))
    has_prd = bool(re.search(r"@prd:", content))
    has_ears = bool(re.search(r"@ears:", content))
    has_bdd = bool(re.search(r"@bdd:", content))

    missing = []
    if not has_brd:
        missing.append("@brd")
    if not has_prd:
        missing.append("@prd")
    if not has_ears:
        missing.append("@ears")
    if not has_bdd:
        missing.append("@bdd")

    if missing:
        result.add_warning(
            "ADR-W001",
            f"Missing upstream traceability tags: {', '.join(missing)}"
        )


def validate_optional_sections(content: str, result: ValidationResult):
    """Check for recommended optional sections."""
    if "## 11. Alternatives Considered" not in content:
        result.add_info("ADR-I001", "Consider adding Section 11: Alternatives Considered")

    if "## 12. Security Considerations" not in content:
        result.add_info("ADR-I002", "Consider adding Section 12: Security Considerations")


def validate_adr_file(file_path: Path) -> ValidationResult:
    """
    Validate a single ADR file.

    Args:
        file_path: Path to ADR markdown file

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
    validate_structure(content, sections, result, metadata)
    validate_context_section(content, result, metadata)
    validate_decision_section(content, result, metadata)
    validate_consequences_section(content, result, metadata)
    validate_architecture_section(content, result, metadata)
    validate_status(content, result, metadata)
    validate_traceability(content, result)
    validate_optional_sections(content, result)

    return result


def validate_directory(dir_path: Path) -> List[ValidationResult]:
    """
    Validate all ADR files in a directory.

    Args:
        dir_path: Path to directory containing ADR files

    Returns:
        List of ValidationResult for each file
    """
    results = []

    # Find ADR files
    patterns = ["ADR-*.md", "adr-*.md", "ADR_*.md"]
    adr_files = []

    for pattern in patterns:
        adr_files.extend(dir_path.glob(f"**/{pattern}"))

    if not adr_files:
        print(f"[WARNING] VAL-W001: No ADR files found in {dir_path}")
        return results

    for file_path in sorted(set(adr_files)):
        result = validate_adr_file(file_path)
        results.append(result)

    return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ADR Document Validator (Layer 5)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_adr.py /path/to/docs/ADR
  python validate_adr.py /path/to/ADR-001_example.md
  python validate_adr.py . --verbose
        """
    )

    parser.add_argument(
        "path",
        type=Path,
        help="ADR file or directory to validate"
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
        results = [validate_adr_file(args.path)]
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
        print(f"ADR Validation Summary")
        print(f"{'=' * 40}")
        print(f"Files validated: {len(results)}")
        print(f"Errors: {len(all_errors)}")
        print(f"Warnings: {len(all_warnings)}")
        print(f"Status: {'PASS' if not all_errors else 'FAIL'}")

    # Return exit code
    return calculate_exit_code(all_errors, all_warnings, args.strict)


if __name__ == "__main__":
    sys.exit(main())
