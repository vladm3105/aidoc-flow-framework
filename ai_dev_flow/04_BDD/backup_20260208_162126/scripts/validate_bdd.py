#!/usr/bin/env python3
"""
BDD (Behavior-Driven Development) Validator - Layer 4

Validates BDD .feature files against BDD_MVP_SCHEMA.yaml requirements.
Supports Gherkin syntax validation.

Usage:
    python validate_bdd.py <file_or_directory>
    python validate_bdd.py /path/to/tests/bdd
    python validate_bdd.py /path/to/docs/BDD/BDD-01_example/BDD-01.1_example.feature

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
# Monolithic: BDD-NN+_slug.feature (2+ digits per ID_NAMING_STANDARDS.md)
FILE_NAME_PATTERN_MONOLITHIC = r"^BDD-\d{2,}_[A-Za-z0-9_]+\.feature$"
# Decimal suffix (one-to-many): BDD-NN.DD_slug.feature (Vertical ID Alignment)
FILE_NAME_PATTERN_DECIMAL = r"^BDD-\d{2,}\.\d+_[A-Za-z0-9_]+\.feature$"

# Gherkin keywords
FEATURE_KEYWORD = "Feature:"
BACKGROUND_KEYWORD = "Background:"
SCENARIO_KEYWORD = "Scenario:"
SCENARIO_OUTLINE_KEYWORD = "Scenario Outline:"
EXAMPLES_KEYWORD = "Examples:"

# Step keywords
STEP_KEYWORDS = ["Given", "When", "Then", "And", "But"]

# User story patterns
USER_STORY_PATTERNS = [
    r"^\s+As a\s",
    r"^\s+I want\s",
    r"^\s+So that\s",
]

# Required traceability tags (Layer 4)
REQUIRED_TRACE_TAGS = ["@brd", "@prd", "@ears"]

# Valid scenario tags
VALID_TAG_PREFIXES = [
    "@primary", "@negative", "@functional", "@quality_attribute",
    "@acceptance", "@integration", "@edge_case", "@boundary",
    "@performance", "@security", "@robustness", "@error_handling",
    "@data_driven", "@failure_recovery", "@reliability", "@alternative",
    "@end_to_end", "@data_flow", "@latency", "@resilience",
    "@data_integrity", "@monitoring", "@recovery",
]


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

def parse_feature_file(content: str) -> Dict:
    """
    Parse a Gherkin feature file into structured data.

    Returns:
        Dictionary with feature, scenarios, tags, etc.
    """
    result = {
        "feature": None,
        "feature_tags": [],
        "user_story": [],
        "background": None,
        "scenarios": [],
        "tags": [],
        "header_comments": [],
    }

    lines = content.split("\n")
    current_scenario = None
    in_examples = False
    current_tags = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Collect header comments
        if stripped.startswith("#") and result["feature"] is None:
            result["header_comments"].append(stripped)
            continue

        # Collect tags
        if stripped.startswith("@"):
            current_tags.extend(stripped.split())
            result["tags"].extend(stripped.split())
            continue

        # Feature declaration
        if stripped.startswith(FEATURE_KEYWORD):
            result["feature"] = stripped
            result["feature_tags"] = current_tags.copy()
            current_tags = []
            continue

        # User story lines
        for pattern in USER_STORY_PATTERNS:
            if re.match(pattern, line):
                result["user_story"].append(stripped)
                break

        # Background
        if stripped.startswith(BACKGROUND_KEYWORD):
            result["background"] = {"line": i, "steps": []}
            current_scenario = result["background"]
            in_examples = False
            continue

        # Scenario or Scenario Outline
        if stripped.startswith(SCENARIO_KEYWORD) or stripped.startswith(SCENARIO_OUTLINE_KEYWORD):
            is_outline = stripped.startswith(SCENARIO_OUTLINE_KEYWORD)
            current_scenario = {
                "line": i,
                "name": stripped,
                "is_outline": is_outline,
                "tags": current_tags.copy(),
                "steps": [],
                "has_given": False,
                "has_when": False,
                "has_then": False,
                "has_examples": False,
            }
            result["scenarios"].append(current_scenario)
            current_tags = []
            in_examples = False
            continue

        # Examples section
        if stripped.startswith(EXAMPLES_KEYWORD):
            in_examples = True
            if current_scenario:
                current_scenario["has_examples"] = True
            continue

        # Step lines
        for keyword in STEP_KEYWORDS:
            if stripped.startswith(keyword + " "):
                if current_scenario:
                    current_scenario["steps"].append({
                        "keyword": keyword,
                        "line": i,
                        "text": stripped
                    })
                    if keyword == "Given":
                        current_scenario["has_given"] = True
                    elif keyword == "When":
                        current_scenario["has_when"] = True
                    elif keyword == "Then":
                        current_scenario["has_then"] = True
                break

    return result


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
        result.add_warning(
            "BDD-E004",
            f"File name '{file_name}' doesn't match valid BDD format. "
            "Expected: BDD-NNN_slug.feature or BDD-NN.DD_slug.feature"
        )


def validate_file_extension(file_path: Path, result: ValidationResult):
    """Validate file extension is .feature."""
    if file_path.suffix.lower() != ".feature":
        result.add_error("BDD-E004", f"Invalid file extension: {file_path.suffix}. Expected .feature")
        return False
    return True


def validate_feature_declaration(parsed: Dict, result: ValidationResult):
    """Validate Feature declaration."""
    if not parsed["feature"]:
        result.add_error("BDD-E001", "Missing Feature declaration")
        return

    # Check for multiple Feature declarations (already handled by parser)
    # The parser only captures the first Feature


def validate_user_story(parsed: Dict, result: ValidationResult):
    """Validate user story (As a / I want / So that)."""
    user_story = parsed["user_story"]

    has_as_a = any("As a" in line for line in user_story)
    has_i_want = any("I want" in line for line in user_story)
    has_so_that = any("So that" in line for line in user_story)

    if not (has_as_a and has_i_want and has_so_that):
        missing = []
        if not has_as_a:
            missing.append("As a")
        if not has_i_want:
            missing.append("I want")
        if not has_so_that:
            missing.append("So that")
        result.add_warning(
            "BDD-W001",
            f"Feature missing user story components: {', '.join(missing)}"
        )


def validate_scenarios(parsed: Dict, result: ValidationResult):
    """Validate scenarios have required structure."""
    scenarios = parsed["scenarios"]

    if not scenarios:
        result.add_error("BDD-E002", "No Scenario or Scenario Outline found")
        return

    for scenario in scenarios:
        name = scenario["name"]

        # Check for When step (required)
        if not scenario["has_when"]:
            result.add_error("BDD-E003", f"Scenario missing When step: {name[:50]}")

        # Check for Then step (required)
        if not scenario["has_then"]:
            result.add_error("BDD-E003", f"Scenario missing Then step: {name[:50]}")

        # Check for Given step (recommended)
        if not scenario["has_given"]:
            result.add_warning("BDD-W002", f"Scenario missing Given step: {name[:50]}")

        # Check Scenario Outline has Examples
        if scenario["is_outline"] and not scenario["has_examples"]:
            result.add_error("BDD-E002", f"Scenario Outline missing Examples: {name[:50]}")


def validate_step_order(parsed: Dict, result: ValidationResult):
    """Validate Given-When-Then step order."""
    for scenario in parsed["scenarios"]:
        steps = scenario["steps"]
        if not steps:
            continue

        # Track step type progression
        last_type = None  # 'G', 'W', 'T'

        for step in steps:
            keyword = step["keyword"]

            if keyword == "Given":
                current_type = "G"
            elif keyword == "When":
                current_type = "W"
            elif keyword == "Then":
                current_type = "T"
            else:  # And/But - inherit previous type
                current_type = last_type

            # Check order violations
            if last_type == "W" and current_type == "G":
                result.add_error(
                    "BDD-E003",
                    f"Invalid step order: Given after When at line {step['line']}"
                )
            elif last_type == "T" and current_type in ["G", "W"]:
                result.add_error(
                    "BDD-E003",
                    f"Invalid step order: {keyword} after Then at line {step['line']}"
                )

            last_type = current_type


def validate_traceability_tags(parsed: Dict, result: ValidationResult):
    """Validate cumulative traceability tags (Layer 4 requires @brd, @prd, @ears)."""
    all_tags = parsed["tags"]
    header = "\n".join(parsed["header_comments"])

    # Check for required tags
    has_brd = any("@brd" in tag or "@brd:" in header for tag in all_tags) or "@brd:" in header
    has_prd = any("@prd" in tag or "@prd:" in header for tag in all_tags) or "@prd:" in header
    has_ears = any("@ears" in tag or "@ears:" in header for tag in all_tags) or "@ears:" in header

    missing = []
    if not has_brd:
        missing.append("@brd")
    if not has_prd:
        missing.append("@prd")
    if not has_ears:
        missing.append("@ears")

    if missing:
        result.add_error(
            "BDD-E005",
            f"Missing cumulative traceability tags (Layer 4 requires): {', '.join(missing)}"
        )


def validate_scenario_categories(parsed: Dict, result: ValidationResult):
    """Check for recommended scenario categories."""
    scenarios = parsed["scenarios"]

    has_primary = any("@primary" in s.get("tags", []) for s in scenarios)
    has_negative = any("@negative" in s.get("tags", []) or "@error_handling" in s.get("tags", []) for s in scenarios)

    if not has_primary:
        result.add_warning("BDD-W001", "No success path scenarios (@primary) detected")

    if not has_negative:
        result.add_info("BDD-I001", "Consider adding error path scenarios (@negative)")


def validate_scenario_names(parsed: Dict, result: ValidationResult):
    """Validate scenario naming conventions."""
    for scenario in parsed["scenarios"]:
        name = scenario["name"]

        # Extract name after keyword
        if name.startswith(SCENARIO_KEYWORD):
            actual_name = name[len(SCENARIO_KEYWORD):].strip()
        elif name.startswith(SCENARIO_OUTLINE_KEYWORD):
            actual_name = name[len(SCENARIO_OUTLINE_KEYWORD):].strip()
        else:
            continue

        # Check first letter is capitalized
        if actual_name and not actual_name[0].isupper():
            result.add_warning(
                "BDD-W001",
                f"Scenario name should start with capital letter: '{actual_name[:30]}'"
            )


def validate_crosslinking_tags(content: str, result: ValidationResult):
    """Detect and report cross-linking tags for AI assistance (info-level)."""
    # Detect @depends tags
    depends_matches = re.findall(r'@depends:\s*(BDD-\d+)', content)
    if depends_matches:
        unique_deps = set(depends_matches)
        result.add_info(
            "BDD-I001",
            f"Document has @depends cross-links: {', '.join(sorted(unique_deps))} (for AI relationship discovery)"
        )
    
    # Detect @discoverability tags
    discoverability_matches = re.findall(r'@discoverability:\s*(BDD-\d+)', content)
    if discoverability_matches:
        unique_disc = set(discoverability_matches)
        result.add_info(
            "BDD-I002",
            f"Document has @discoverability tags: {', '.join(sorted(unique_disc))} (for AI ranking)"
        )


def validate_bdd_file(file_path: Path) -> ValidationResult:
    """
    Validate a single BDD feature file.

    Args:
        file_path: Path to BDD .feature file

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

    # Read content
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        result.add_error("VAL-E005", f"Failed to read file: {e}")
        return result

    # Parse feature file
    parsed = parse_feature_file(content)

    # Run validations
    validate_feature_declaration(parsed, result)
    validate_user_story(parsed, result)
    validate_scenarios(parsed, result)
    validate_step_order(parsed, result)
    validate_traceability_tags(parsed, result)
    validate_scenario_categories(parsed, result)
    validate_scenario_names(parsed, result)
    validate_crosslinking_tags(content, result)

    return result


def validate_directory(dir_path: Path) -> List[ValidationResult]:
    """
    Validate all BDD feature files in a directory.

    Args:
        dir_path: Path to directory containing .feature files

    Returns:
        List of ValidationResult for each file
    """
    results = []

    # Find .feature files
    # Find .feature files
    feature_files = []
    # Use glob recursively
    raw_files = dir_path.glob("**/*.feature")

    # Exclude supporting documents (templates, indexes, planning docs)
    excluded_patterns = ['TEMPLATE', 'INDEX', '_CREATION_PLAN']
    
    for f in raw_files:
        # Check exclusion patterns in filename
        if any(excl in f.name.upper() for excl in excluded_patterns):
            continue
        # Also exclude framework infrastructure files (BDD-00_*)
        if re.match(r'^BDD-00[_.]', f.name):
            continue
        feature_files.append(f)

    if not feature_files:
        print(f"[WARNING] VAL-W001: No .feature files found in {dir_path}")
        return results

    for file_path in sorted(set(feature_files)):
        result = validate_bdd_file(file_path)
        results.append(result)

    return results


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="BDD Feature File Validator (Layer 4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_bdd.py /path/to/tests/bdd
  python validate_bdd.py /path/to/BDD/BDD-01_example/BDD-01.1_example.feature
  python validate_bdd.py . --verbose
        """
    )

    parser.add_argument(
        "path",
        type=Path,
        help="BDD file or directory to validate"
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
        results = [validate_bdd_file(args.path)]
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
        print(f"BDD Validation Summary")
        print(f"{'=' * 40}")
        print(f"Files validated: {len(results)}")
        print(f"Errors: {len(all_errors)}")
        print(f"Warnings: {len(all_warnings)}")
        print(f"Status: {'PASS' if not all_errors else 'FAIL'}")

    # Return exit code
    return calculate_exit_code(all_errors, all_warnings, args.strict)


if __name__ == "__main__":
    sys.exit(main())
