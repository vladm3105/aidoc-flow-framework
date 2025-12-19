#!/usr/bin/env python3
"""
Unified Artifact Validator

Auto-detects artifact type from document's schema_reference field and validates
against the corresponding schema rules.

Usage:
    python scripts/validate_artifact.py <document_path> [--verbose] [--strict]
    python scripts/validate_artifact.py docs/PRD/PRD-01_example.md
    python scripts/validate_artifact.py docs/SPEC/SPEC-01_component.yaml --verbose

Options:
    --verbose    Show detailed validation results
    --strict     Treat warnings as errors
"""

import sys
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    """Validation message severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationMessage:
    """A single validation finding."""
    severity: Severity
    code: str
    message: str
    line: Optional[int] = None
    context: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result for a document."""
    document_path: Path
    artifact_type: Optional[str]
    schema_reference: Optional[str]
    is_valid: bool
    messages: List[ValidationMessage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, code: str, message: str, line: Optional[int] = None):
        """Add an error message."""
        self.messages.append(ValidationMessage(Severity.ERROR, code, message, line))
        self.is_valid = False

    def add_warning(self, code: str, message: str, line: Optional[int] = None):
        """Add a warning message."""
        self.messages.append(ValidationMessage(Severity.WARNING, code, message, line))

    def add_info(self, code: str, message: str, line: Optional[int] = None):
        """Add an info message."""
        self.messages.append(ValidationMessage(Severity.INFO, code, message, line))


# Artifact type detection patterns
ARTIFACT_PATTERNS = {
    "ADR": r"^ADR-\d{3}",
    "BDD": r"\.feature$",
    "BRD": r"^BRD-\d{3}",
    "CTR": r"^CTR-\d{3}",
    "EARS": r"^EARS-\d{3}",
    "IMPL": r"^IMPL-\d{3}",
    "IPLAN": r"^IPLAN-\d{3}",
    "PRD": r"^PRD-\d{3}",
    "REF": r"^[A-Z]{2,5}-REF-\d{3}",
    "REQ": r"^REQ-\d{3}",
    "SPEC": r"^SPEC-\d{3}",
    "SYS": r"^SYS-\d{3}",
    "TASKS": r"^TASKS-\d{3}",
}

# Schema file locations relative to ai_dev_flow
SCHEMA_LOCATIONS = {
    "ADR_SCHEMA.yaml": "ADR/ADR_SCHEMA.yaml",
    "BDD_SCHEMA.yaml": "BDD/BDD_SCHEMA.yaml",
    "CTR_SCHEMA.yaml": "CTR/CTR_SCHEMA.yaml",
    "EARS_SCHEMA.yaml": "EARS/EARS_SCHEMA.yaml",
    "IMPL_SCHEMA.yaml": "IMPL/IMPL_SCHEMA.yaml",
    "IPLAN_SCHEMA.yaml": "IPLAN/IPLAN_SCHEMA.yaml",
    "PRD_SCHEMA.yaml": "PRD/PRD_SCHEMA.yaml",
    "REQ_SCHEMA.yaml": "REQ/REQ_SCHEMA.yaml",
    "SPEC_SCHEMA.yaml": "SPEC/SPEC_SCHEMA.yaml",
    "SYS_SCHEMA.yaml": "SYS/SYS_SCHEMA.yaml",
    "TASKS_SCHEMA.yaml": "TASKS/TASKS_SCHEMA.yaml",
}


def find_ai_dev_flow_dir() -> Path:
    """Find the ai_dev_flow directory."""
    candidates = [
        Path("ai_dev_flow"),
        Path("../ai_dev_flow"),
        Path(__file__).parent.parent,
    ]

    for candidate in candidates:
        if candidate.exists() and (candidate / "PRD").exists():
            return candidate.resolve()

    raise FileNotFoundError("Could not find ai_dev_flow directory")


def extract_yaml_frontmatter(content: str) -> Tuple[Optional[Dict], int]:
    """Extract YAML frontmatter from markdown file and return end line."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            end_line = content[:match.end()].count('\n') + 1
            return yaml.safe_load(match.group(1)), end_line
        except yaml.YAMLError:
            return None, 0
    return None, 0


def detect_artifact_type_from_path(doc_path: Path) -> Optional[str]:
    """Detect artifact type from file path and name."""
    filename = doc_path.stem
    suffix = doc_path.suffix

    # Check file extension first (for .feature files)
    if suffix == '.feature':
        return "BDD"

    # Check filename patterns
    for artifact_type, pattern in ARTIFACT_PATTERNS.items():
        if re.match(pattern, filename):
            return artifact_type

    # Check parent directory
    parent_name = doc_path.parent.name.upper()
    if parent_name in ARTIFACT_PATTERNS:
        return parent_name

    return None


def detect_artifact_type_from_content(content: str, frontmatter: Optional[Dict]) -> Optional[str]:
    """Detect artifact type from document content."""
    if frontmatter:
        # Check custom_fields.artifact_type
        custom_fields = frontmatter.get('custom_fields', {})
        if 'artifact_type' in custom_fields:
            return custom_fields['artifact_type']

        # Check schema_reference
        schema_ref = custom_fields.get('schema_reference')
        if schema_ref and schema_ref != "none":
            # Extract type from schema filename (e.g., "PRD_SCHEMA.yaml" -> "PRD")
            match = re.match(r'([A-Z]+)_SCHEMA\.yaml', schema_ref)
            if match:
                return match.group(1)

    # Check for H1 heading with artifact ID pattern
    h1_match = re.search(r'^# ([A-Z]+)-\d{3}:', content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1)

    return None


def load_schema(schema_ref: str, base_dir: Path) -> Optional[Dict]:
    """Load schema file based on reference."""
    if schema_ref == "none" or not schema_ref:
        return None

    schema_path = SCHEMA_LOCATIONS.get(schema_ref)
    if not schema_path:
        return None

    full_path = base_dir / schema_path
    if not full_path.exists():
        return None

    try:
        return yaml.safe_load(full_path.read_text(encoding='utf-8'))
    except yaml.YAMLError:
        return None


def validate_metadata(frontmatter: Dict, schema: Dict, result: ValidationResult):
    """Validate document metadata against schema."""
    metadata_rules = schema.get('metadata', {})

    # Check required custom_fields
    required_fields = metadata_rules.get('required_custom_fields', {})
    custom_fields = frontmatter.get('custom_fields', {})

    for field_name, field_spec in required_fields.items():
        if field_spec.get('required', False):
            if field_name not in custom_fields:
                result.add_error("E_MISSING_FIELD", f"Missing required field: custom_fields.{field_name}")
            else:
                value = custom_fields[field_name]
                allowed = field_spec.get('allowed_values', [])
                if allowed and value not in allowed:
                    # For array fields, check if value matches any allowed array
                    if isinstance(allowed[0], list):
                        if value not in allowed:
                            result.add_error("E_INVALID_VALUE",
                                f"Invalid value for {field_name}: {value}. Allowed: {allowed}")
                    else:
                        result.add_error("E_INVALID_VALUE",
                            f"Invalid value for {field_name}: {value}. Allowed: {allowed}")

    # Check required tags
    required_tags = metadata_rules.get('required_tags', [])
    doc_tags = frontmatter.get('tags', [])
    for tag in required_tags:
        if tag not in doc_tags:
            result.add_error("E_MISSING_TAG", f"Missing required tag: {tag}")

    # Check forbidden tag patterns
    forbidden_patterns = metadata_rules.get('forbidden_tag_patterns', [])
    for pattern in forbidden_patterns:
        for tag in doc_tags:
            if re.match(pattern, tag):
                result.add_error("E_FORBIDDEN_TAG", f"Forbidden tag pattern: {tag} matches {pattern}")


def validate_structure(content: str, schema: Dict, result: ValidationResult):
    """Validate document structure against schema."""
    structure_rules = schema.get('structure', {})

    # Check required sections
    required_sections = structure_rules.get('required_sections', [])
    for section in required_sections:
        pattern = section.get('pattern')
        name = section.get('name', 'Unknown section')
        if pattern:
            if not re.search(pattern, content, re.MULTILINE):
                result.add_warning("W_MISSING_SECTION", f"Missing section: {name} (pattern: {pattern})")

    # Check for multiple H1 headings
    h1_matches = re.findall(r'^# ', content, re.MULTILINE)
    if len(h1_matches) > 1:
        result.add_error("E_MULTIPLE_H1", "Multiple H1 headings detected (only one allowed)")


def validate_traceability(content: str, frontmatter: Dict, schema: Dict, result: ValidationResult):
    """Validate traceability tags and references."""
    traceability_rules = schema.get('traceability', {})

    # Check upstream requirements
    upstream = traceability_rules.get('upstream', {})
    required_upstream = upstream.get('required', [])

    for req in required_upstream:
        tag_format = req.get('format', '')
        tag_type = req.get('type', '')
        tag_prefix = f"@{tag_type.lower()}:"

        # Check if tag exists in content
        if tag_prefix not in content.lower():
            result.add_warning("W_MISSING_UPSTREAM", f"Missing required upstream reference: {tag_format}")


def validate_document(doc_path: Path, verbose: bool = False) -> ValidationResult:
    """Validate a document against its schema."""
    result = ValidationResult(
        document_path=doc_path,
        artifact_type=None,
        schema_reference=None,
        is_valid=True
    )

    # Check file exists
    if not doc_path.exists():
        result.add_error("E_FILE_NOT_FOUND", f"File not found: {doc_path}")
        return result

    # Read content
    try:
        content = doc_path.read_text(encoding='utf-8')
    except Exception as e:
        result.add_error("E_READ_ERROR", f"Cannot read file: {e}")
        return result

    # Extract frontmatter (for markdown files)
    frontmatter = None
    if doc_path.suffix in ['.md', '.yaml', '.yml']:
        frontmatter, _ = extract_yaml_frontmatter(content)
        if doc_path.suffix in ['.yaml', '.yml'] and not frontmatter:
            # For YAML files, try loading the whole file
            try:
                frontmatter = yaml.safe_load(content)
            except yaml.YAMLError:
                pass

    # Detect artifact type
    artifact_type = detect_artifact_type_from_path(doc_path)
    if not artifact_type and frontmatter:
        artifact_type = detect_artifact_type_from_content(content, frontmatter)

    result.artifact_type = artifact_type

    if not artifact_type:
        result.add_warning("W_UNKNOWN_TYPE", "Could not detect artifact type")
        return result

    # Get schema reference
    if frontmatter:
        custom_fields = frontmatter.get('custom_fields', {})
        result.schema_reference = custom_fields.get('schema_reference')
    else:
        # For .feature files, check comments
        match = re.search(r'#\s*SCHEMA_REFERENCE:\s*(\S+)', content)
        if match:
            result.schema_reference = match.group(1)

    # Load schema
    try:
        base_dir = find_ai_dev_flow_dir()
    except FileNotFoundError:
        result.add_warning("W_NO_SCHEMA_DIR", "Cannot find ai_dev_flow directory for schema lookup")
        return result

    # If no schema_reference, construct from artifact type
    if not result.schema_reference or result.schema_reference == "none":
        if artifact_type == "BRD":
            result.add_info("I_NO_SCHEMA", "BRD has no schema (Layer 1 entry point)")
            return result
        result.schema_reference = f"{artifact_type}_SCHEMA.yaml"

    schema = load_schema(result.schema_reference, base_dir)
    if not schema:
        result.add_warning("W_SCHEMA_NOT_FOUND", f"Schema not found: {result.schema_reference}")
        return result

    # Store metadata for reporting
    result.metadata = {
        "artifact_type": artifact_type,
        "schema_version": schema.get('schema_version'),
        "layer": schema.get('layer'),
    }

    # Run validations
    if frontmatter:
        validate_metadata(frontmatter, schema, result)

    validate_structure(content, schema, result)
    validate_traceability(content, frontmatter or {}, schema, result)

    return result


def print_result(result: ValidationResult, verbose: bool = False, strict: bool = False):
    """Print validation result."""
    # Header
    status_icon = "✅" if result.is_valid else "❌"
    if result.is_valid and any(m.severity == Severity.WARNING for m in result.messages):
        status_icon = "⚠️"

    print(f"{status_icon} {result.document_path}")

    if verbose:
        print(f"   Artifact Type: {result.artifact_type or 'Unknown'}")
        print(f"   Schema: {result.schema_reference or 'None'}")
        if result.metadata:
            print(f"   Layer: {result.metadata.get('layer', 'N/A')}")
            print(f"   Schema Version: {result.metadata.get('schema_version', 'N/A')}")

    # Messages
    error_count = 0
    warning_count = 0

    for msg in result.messages:
        if msg.severity == Severity.ERROR:
            error_count += 1
            print(f"   ❌ [{msg.code}] {msg.message}")
        elif msg.severity == Severity.WARNING:
            warning_count += 1
            if verbose or strict:
                print(f"   ⚠️  [{msg.code}] {msg.message}")
        elif msg.severity == Severity.INFO and verbose:
            print(f"   ℹ️  [{msg.code}] {msg.message}")

    # Summary
    if error_count > 0 or (strict and warning_count > 0):
        print(f"   Summary: {error_count} errors, {warning_count} warnings")
    elif verbose and warning_count > 0:
        print(f"   Summary: {warning_count} warnings")


def main():
    """Main entry point."""
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        sys.exit(0)

    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    strict = "--strict" in sys.argv

    # Filter out flags to get document paths
    doc_paths = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

    if not doc_paths:
        print("Error: No document path provided")
        print(__doc__)
        sys.exit(1)

    exit_code = 0

    for doc_path_str in doc_paths:
        doc_path = Path(doc_path_str)
        result = validate_document(doc_path, verbose)
        print_result(result, verbose, strict)

        if not result.is_valid:
            exit_code = 1
        elif strict and any(m.severity == Severity.WARNING for m in result.messages):
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
