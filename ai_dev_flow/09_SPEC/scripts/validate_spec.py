#!/usr/bin/env python3
"""
SPEC (Technical Specification) Validator - Layer 9

Validates SPEC YAML documents against SPEC_MVP_SCHEMA.yaml requirements.
SPEC is the most complex artifact in the SDD framework, requiring
comprehensive validation of interfaces, performance, security, and observability.

Usage:
    python validate_spec.py <file_or_directory>
    python validate_spec.py /path/to/docs/SPEC
    python validate_spec.py /path/to/docs/SPEC/SPEC-01_example/SPEC-01_example.yaml

Exit Codes:
    0 = Pass (no errors, no warnings)
    1 = Warnings only
    2 = Errors present
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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

# File naming patterns
# Monolithic: SPEC-NN+_slug.yaml (2+ digits per ID_NAMING_STANDARDS.md)
FILE_NAME_PATTERN_MONOLITHIC = r"^SPEC-\d{2,}_[A-Za-z0-9_]+\.yaml$"
# Decimal suffix (one-to-many): SPEC-NN.DD_slug.yaml (Vertical ID Alignment)
FILE_NAME_PATTERN_DECIMAL = r"^SPEC-\d{2,}\.\d+_[A-Za-z0-9_]+\.yaml$"

# Required top-level fields
REQUIRED_TOP_LEVEL = [
    "id",
    "summary",
    "metadata",
    "traceability",
    "architecture",
    "interfaces",
    "behavior",
    "performance",
    "security",
    "observability",
    "verification",
    "implementation",
]

# Optional top-level fields
OPTIONAL_TOP_LEVEL = [
    "caching",
    "rate_limiting",
    "circuit_breaker",
    "operations",
    "changelog",
    "maintenance",
    "notes",
]

# Required metadata fields
REQUIRED_METADATA = ["version", "status", "created_date", "last_updated", "authors"]

# Valid status values
VALID_STATUS = ["draft", "review", "approved", "implemented", "deprecated"]

# Semantic version pattern
SEMVER_PATTERN = r"^\d+\.\d+\.\d+$"

# Date pattern (YYYY-MM-DD)
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"

# ID pattern (snake_case)
ID_PATTERN = r"^[a-z][a-z0-9_]*$"

# Class name pattern (PascalCase)
PASCAL_CASE_PATTERN = r"^[A-Z][a-zA-Z0-9]+$"

# Method name pattern (snake_case, allowing dunder methods like __init__)
SNAKE_CASE_PATTERN = r"^_{0,2}[a-z][a-z0-9_]*_{0,2}$"

# Required cumulative tags (Layer 9)
REQUIRED_CUMULATIVE_TAGS = ["brd", "prd", "ears", "bdd", "adr", "sys", "req"]

# Optional cumulative tags
OPTIONAL_CUMULATIVE_TAGS = ["ctr"]


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
        if not self.errors and not self.warnings and not self.info:
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

def parse_yaml_file(file_path: Path) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Parse a YAML file.

    Returns:
        Tuple of (parsed dict or None, error message or None)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        return data, None
    except yaml.YAMLError as e:
        return None, f"YAML syntax error: {e}"
    except Exception as e:
        return None, str(e)


def get_nested(data: Dict, *keys, default=None) -> Any:
    """Safely get nested dictionary value."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is None:
            return default
    return current


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
    is_decimal = re.match(FILE_NAME_PATTERN_DECIMAL, file_name)

    if not (is_monolithic or is_decimal):
        result.add_error(
            "SPEC-E013",
            f"File name '{file_name}' doesn't match valid SPEC format. "
            "Expected: SPEC-NNN_slug.yaml or SPEC-NN.DD_slug.yaml"
        )


def validate_file_extension(file_path: Path, result: ValidationResult) -> bool:
    """Validate file extension is .yaml."""
    if file_path.suffix.lower() not in [".yaml", ".yml"]:
        result.add_error("SPEC-E001", f"Invalid file extension: {file_path.suffix}. Expected .yaml")
        return False
    return True


def validate_top_level_fields(data: Dict, result: ValidationResult):
    """Validate required top-level fields."""
    if not isinstance(data, dict):
        result.add_error("SPEC-E002", "Document root must be a YAML mapping")
        return

    for field in REQUIRED_TOP_LEVEL:
        if field not in data or data[field] is None:
            result.add_error("SPEC-E002", f"Missing required top-level field: {field}")


def validate_id_field(data: Dict, file_path: Path, result: ValidationResult):
    """Validate id field format and match with filename."""
    spec_id = data.get("id")
    if not spec_id:
        return  # Already caught by top-level validation

    if not re.match(ID_PATTERN, str(spec_id)):
        result.add_warning(
            "SPEC-W008",
            f"id '{spec_id}' should be snake_case (lowercase with underscores)"
        )

    # Check if id matches filename slug
    # Check if id matches filename slug
    file_name = file_path.stem  # SPEC-01_component_name
    
    # Try monolithic pattern
    match = re.match(r"SPEC-\d{3}_(.+)", file_name)
    if not match:
        # Try decimal pattern
        match = re.match(r"SPEC-\d{2,}\.\d+_(.+)", file_name)
    
    if match:
        expected_id = match.group(1)
        if str(spec_id) != expected_id:
            result.add_warning(
                "SPEC-W008",
                f"id '{spec_id}' doesn't match filename slug '{expected_id}'"
            )


def validate_metadata(data: Dict, result: ValidationResult):
    """Validate metadata section."""
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        result.add_error("SPEC-E003", "metadata must be a mapping")
        return

    # Check required metadata fields
    for field in REQUIRED_METADATA:
        if field not in metadata or metadata[field] is None:
            result.add_error("SPEC-E003", f"Missing required metadata field: {field}")

    # Validate version format
    version = metadata.get("version")
    if version and not re.match(SEMVER_PATTERN, str(version)):
        result.add_error(
            "SPEC-E004",
            f"Invalid version format: '{version}'. Expected MAJOR.MINOR.PATCH"
        )

    # Validate status
    status = metadata.get("status")
    if status and str(status) not in VALID_STATUS:
        result.add_error(
            "SPEC-E005",
            f"Invalid status: '{status}'. Allowed: {', '.join(VALID_STATUS)}"
        )

    # Validate dates
    for date_field in ["created_date", "last_updated"]:
        date_value = metadata.get(date_field)
        if date_value and not re.match(DATE_PATTERN, str(date_value)):
            # Relax check for templates
            if "TEMPLATE" in getattr(result, 'file_path', '').upper():
                pass
            else:
                result.add_error(
                    "SPEC-E006",
                    f"Invalid date format for {date_field}: '{date_value}'. Expected YYYY-MM-DD"
                )

    # Validate authors
    authors = metadata.get("authors")
    if not authors:
        result.add_error("SPEC-E007", "No authors specified in metadata")
    elif isinstance(authors, list):
        if len(authors) == 0:
            result.add_error("SPEC-E007", "authors list is empty")
        else:
            for i, author in enumerate(authors):
                if isinstance(author, dict):
                    if not author.get("name"):
                        result.add_warning(
                            "SPEC-W006",
                            f"Author at index {i} missing 'name' field"
                        )


def validate_traceability(data: Dict, result: ValidationResult):
    """Validate traceability section with cumulative tags."""
    traceability = data.get("traceability")
    if not isinstance(traceability, dict):
        result.add_error("SPEC-E014", "traceability must be a mapping")
        return

    # Check for upstream_sources
    upstream = traceability.get("upstream_sources")
    if not upstream:
        result.add_warning("SPEC-W001", "Missing upstream_sources in traceability")
    elif isinstance(upstream, dict):
        if not upstream.get("business_requirements"):
            result.add_warning("SPEC-W001", "Missing business_requirements in upstream_sources")

    # Check for cumulative_tags
    cumulative_tags = traceability.get("cumulative_tags")
    if not cumulative_tags:
        result.add_error("SPEC-E015", "Missing cumulative_tags in traceability")
    elif isinstance(cumulative_tags, dict):
        missing_tags = []
        for tag in REQUIRED_CUMULATIVE_TAGS:
            if tag not in cumulative_tags or not cumulative_tags[tag]:
                missing_tags.append(f"@{tag}")

        if missing_tags:
            result.add_warning(
                "SPEC-W002",
                f"Missing cumulative tags (Layer 9 requires 7): {', '.join(missing_tags)}"
            )


def validate_interfaces(data: Dict, result: ValidationResult):
    """Validate interfaces section."""
    interfaces = data.get("interfaces")
    if not isinstance(interfaces, dict):
        result.add_error("SPEC-E008", "interfaces must be a mapping")
        return

    classes = interfaces.get("classes")
    if not classes:
        result.add_error("SPEC-E008", "No classes defined in interfaces section")
        return

    if not isinstance(classes, list):
        result.add_error("SPEC-E008", "interfaces.classes must be an array")
        return

    if len(classes) == 0:
        result.add_error("SPEC-E008", "interfaces.classes array is empty")
        return

    # Validate each class
    for i, cls in enumerate(classes):
        if not isinstance(cls, dict):
            result.add_warning("SPEC-W007", f"Class at index {i} is not a valid mapping")
            continue

        class_name = cls.get("name", f"<unnamed class {i}>")

        # Check PascalCase naming
        if not re.match(PASCAL_CASE_PATTERN, str(class_name)):
            result.add_warning(
                "SPEC-W007",
                f"Class name '{class_name}' not in PascalCase format"
            )

        # Check for methods
        methods = cls.get("methods")
        if not methods:
            result.add_error("SPEC-E009", f"Class '{class_name}' has no methods defined")
            continue

        if not isinstance(methods, list) or len(methods) == 0:
            result.add_error("SPEC-E009", f"Class '{class_name}' has no methods defined")
            continue

        # Validate method names
        for method in methods:
            if isinstance(method, dict):
                method_name = method.get("name", "")
                if method_name and not re.match(SNAKE_CASE_PATTERN, str(method_name)):
                    result.add_warning(
                        "SPEC-W006",
                        f"Method name '{method_name}' (repr: {repr(method_name)}) in class '{class_name}' not in snake_case"
                    )


def validate_performance(data: Dict, result: ValidationResult):
    """Validate performance section."""
    performance = data.get("performance")
    if not isinstance(performance, dict):
        result.add_error("SPEC-E010", "performance must be a mapping")
        return

    # Check latency_targets
    latency = performance.get("latency_targets")
    if not latency:
        result.add_error("SPEC-E010", "Missing latency_targets in performance section")
    elif isinstance(latency, dict):
        # Relaxed check: Accept if keys contain p50/p95/p99 or if strict keys exist
        keys = latency.keys()
        has_p50 = "p50_milliseconds" in keys or any("p50" in k.lower() for k in keys)
        has_p95 = "p95_milliseconds" in keys or any("p95" in k.lower() for k in keys)
        has_p99 = "p99_milliseconds" in keys or any("p99" in k.lower() for k in keys)
        
        missing = []
        if not has_p50: missing.append("p50_milliseconds (or *p50*)")
        if not has_p95: missing.append("p95_milliseconds (or *p95*)")
        if not has_p99: missing.append("p99_milliseconds (or *p99*)")

        if missing:
            result.add_warning(
                "SPEC-W010",
                f"Missing latency targets: {', '.join(missing)}"
            )
        else:
            # Validate latency ordering (only if standard keys are used, for simplicity)
            if "p50_milliseconds" in latency and "p95_milliseconds" in latency and "p99_milliseconds" in latency:
                p50 = latency.get("p50_milliseconds", 0)
                p95 = latency.get("p95_milliseconds", 0)
                p99 = latency.get("p99_milliseconds", 0)

                try:
                    if int(p95) < int(p50):
                        result.add_warning("SPEC-W004", f"p95 latency ({p95}ms) should be >= p50 ({p50}ms)")
                    if int(p99) < int(p95):
                        result.add_warning("SPEC-W005", f"p99 latency ({p99}ms) should be >= p95 ({p95}ms)")
                except (ValueError, TypeError):
                    pass


def validate_security(data: Dict, result: ValidationResult):
    """Validate security section."""
    security = data.get("security")
    if not isinstance(security, dict):
        result.add_error("SPEC-E011", "security must be a mapping")
        return

    # Check authentication
    auth = security.get("authentication")
    if not auth:
        result.add_error("SPEC-E011", "Missing authentication specification in security section")
    elif isinstance(auth, dict):
        if "required" not in auth:
            result.add_error("SPEC-E011", "authentication.required must be specified")

    # Check authorization
    authz = security.get("authorization")
    if not authz:
        result.add_error("SPEC-E011", "Missing authorization specification in security section")
    elif isinstance(authz, dict):
        if "enabled" not in authz:
            result.add_error("SPEC-E011", "authorization.enabled must be specified")

    # Check input_validation
    input_val = security.get("input_validation")
    if not input_val:
        result.add_error("SPEC-E011", "Missing input_validation specification in security section")
    elif isinstance(input_val, dict):
        if "strategy" not in input_val:
            result.add_error("SPEC-E011", "input_validation.strategy must be specified")


def validate_observability(data: Dict, result: ValidationResult):
    """Validate observability section."""
    observability = data.get("observability")
    if not isinstance(observability, dict):
        result.add_error("SPEC-E012", "observability must be a mapping")
        return

    # Check metrics
    metrics = observability.get("metrics")
    if not metrics:
        result.add_error("SPEC-E012", "Missing metrics in observability section")
    elif isinstance(metrics, dict):
        standard_metrics = metrics.get("standard_metrics")
        if not standard_metrics or (isinstance(standard_metrics, list) and len(standard_metrics) == 0):
            result.add_error("SPEC-E012", "At least one standard_metric must be defined")

    # Check logging
    logging_config = observability.get("logging")
    if not logging_config:
        result.add_error("SPEC-E012", "Missing logging in observability section")
    elif isinstance(logging_config, dict):
        level = logging_config.get("level")
        if level and str(level) not in ["DEBUG", "INFO", "WARN", "ERROR"]:
            result.add_warning(
                "SPEC-W006",
                f"logging.level '{level}' not standard (DEBUG/INFO/WARN/ERROR)"
            )

    # Check health_checks
    health = observability.get("health_checks")
    if not health:
        result.add_error("SPEC-E012", "Missing health_checks in observability section")
    elif isinstance(health, dict):
        if "enabled" not in health:
            result.add_error("SPEC-E012", "health_checks.enabled must be specified")


def validate_verification(data: Dict, result: ValidationResult):
    """Validate verification section."""
    verification = data.get("verification")
    if not isinstance(verification, dict):
        return  # Already caught by top-level validation

    bdd_scenarios = verification.get("bdd_scenarios")
    if not bdd_scenarios or (isinstance(bdd_scenarios, list) and len(bdd_scenarios) == 0):
        result.add_warning("SPEC-W003", "No BDD scenarios referenced in verification section")


def validate_optional_sections(data: Dict, result: ValidationResult):
    """Suggest optional sections for completeness."""
    if "caching" not in data:
        result.add_info("SPEC-I001", "Consider adding caching section for performance")

    if "rate_limiting" not in data:
        result.add_info("SPEC-I002", "Consider adding rate_limiting section")

    if "circuit_breaker" not in data:
        result.add_info("SPEC-I003", "Consider adding circuit_breaker section for resilience")

    if "operations" not in data:
        result.add_info("SPEC-I004", "Consider adding operations runbook")


def validate_crosslinking_tags(content: str, result: ValidationResult):
    """Detect and report cross-linking tags for AI assistance (info-level)."""
    # Detect @depends tags
    depends_matches = re.findall(r'@depends:\s*(SPEC-\d+)', content)
    if depends_matches:
        unique_deps = set(depends_matches)
        result.add_info(
            "SPEC-I005",
            f"Document has @depends cross-links: {', '.join(sorted(unique_deps))} (for AI relationship discovery)"
        )
    
    # Detect @discoverability tags
    discoverability_matches = re.findall(r'@discoverability:\s*(SPEC-\d+)', content)
    if discoverability_matches:
        unique_disc = set(discoverability_matches)
        result.add_info(
            "SPEC-I006",
            f"Document has @discoverability tags: {', '.join(sorted(unique_disc))} (for AI ranking)"
        )


def validate_spec_file(file_path: Path) -> ValidationResult:
    """
    Validate a single SPEC YAML file.

    Args:
        file_path: Path to SPEC .yaml file

    Returns:
        ValidationResult with all issues found
    """
    result = ValidationResult(str(file_path))

    # Check file exists
    if not file_path.exists():
        result.add_error("VAL-E001", "File not found")
        return result

    # Check file extension
    if not validate_file_extension(file_path, result):
        return result

    # Validate file name
    validate_file_name(file_path, result)

    # Read content for cross-linking detection
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        content = ""

    # Parse YAML
    data, error = parse_yaml_file(file_path)
    if error:
        result.add_error("SPEC-E001", f"Invalid YAML: {error}")
        return result

    if not data:
        result.add_error("SPEC-E001", "Empty YAML document")
        return result

    # Run validations
    validate_top_level_fields(data, result)
    validate_id_field(data, file_path, result)
    validate_metadata(data, result)
    validate_traceability(data, result)
    validate_interfaces(data, result)
    validate_performance(data, result)
    validate_security(data, result)
    validate_observability(data, result)
    validate_verification(data, result)
    validate_optional_sections(data, result)
    validate_crosslinking_tags(content, result)

    return result


def validate_directory(dir_path: Path) -> List[ValidationResult]:
    """
    Validate all SPEC YAML files in a directory.

    Args:
        dir_path: Path to directory containing .yaml files

    Returns:
        List of ValidationResult for each file
    """
    results = []

    # Find SPEC files
    patterns = ["SPEC-*.yaml", "SPEC-*.yml", "spec-*.yaml"]
    spec_files = []

    raw_files = []
    for pattern in patterns:
        raw_files.extend(dir_path.glob(f"**/{pattern}"))

    # Exclude supporting documents (templates, indexes, planning docs)
    excluded_patterns = ['TEMPLATE', 'INDEX', '_CREATION_PLAN']
    
    for f in raw_files:
         # Check exclusion patterns in filename
        if any(excl in f.name.upper() for excl in excluded_patterns):
            continue
        # Also exclude framework infrastructure files (SPEC-00_*)
        if re.match(r'^SPEC-00[_.]', f.name):
            continue
        # Exclude archived specs (archive, archive2 buckets)
        if any(part in {"archive", "archive2"} for part in f.parts):
            continue
        spec_files.append(f)

    if not spec_files:
        print(f"[WARNING] VAL-W001: No SPEC files found in {dir_path}")
        return results

    for file_path in sorted(set(spec_files)):
        # Skip template files
        if "TEMPLATE" in file_path.name.upper():
            continue
        result = validate_spec_file(file_path)
        results.append(result)

    return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SPEC Document Validator (Layer 9)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_spec.py /path/to/docs/SPEC
  python validate_spec.py /path/to/SPEC-01_example.yaml
  python validate_spec.py . --verbose
        """
    )

    parser.add_argument(
        "path",
        type=Path,
        help="SPEC file or directory to validate"
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
        results = [validate_spec_file(args.path)]
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
        print(f"SPEC Validation Summary")
        print(f"{'=' * 40}")
        print(f"Files validated: {len(results)}")
        print(f"Errors: {len(all_errors)}")
        print(f"Warnings: {len(all_warnings)}")
        print(f"Status: {'PASS' if not all_errors else 'FAIL'}")

    # Return exit code
    return calculate_exit_code(all_errors, all_warnings, args.strict)


if __name__ == "__main__":
    sys.exit(main())
