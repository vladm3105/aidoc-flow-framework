"""TASKS Error Code Registry v1.0 (2026-03-06)

Error codes for TASKS (Code Generation Plan) validation.
Provides standardized error messages and remediation guidance.

Error Code Format:
- TASKS-E###: Errors (critical issues blocking validation)
- TASKS-W###: Warnings (quality issues, non-blocking)
- TASKS-I###: Informational (context-specific notes)

Total Codes: 35
- Errors: 19 (E001-E012, E020-E024, E030, E035)
- Warnings: 33 (W001-W033)
- Info: 1 (I001)

Based on TASKS bash validator v1.0 (13 checks, 563 lines).
Designed for Python validator v2.0 implementation.

Usage:
    from tasks_error_codes import TASKS_ERROR_CODES, get_error_message, get_remediation

    msg = get_error_message("TASKS-E001", filename="TASKS_001.md")
    remedy = get_remediation("TASKS-E001")
"""

from typing import Dict, Tuple, Optional

# Error Code Format: (message_template, remediation_guidance, check_number)
ErrorCodeData = Tuple[str, str, int]

# ============================================================================
# ERROR CODES (E-prefix, 19 codes)
# ============================================================================

TASKS_ERROR_CODES: Dict[str, ErrorCodeData] = {
    # Structure Errors (E001-E008)
    "TASKS-E001": (
        "Invalid filename format: {filename}",
        "Rename file to TASKS-NNN_descriptive_slug.md format (e.g., TASKS-001_gateway_service.md)",
        1
    ),
    "TASKS-E002": (
        "Missing YAML frontmatter (--- delimiters)",
        "Add YAML frontmatter block at document start:\n---\nartifact_type: TASKS\nlayer: 10\n---",
        2
    ),

    # Metadata Errors (E003-E005)
    "TASKS-E003": (
        "Invalid artifact_type: {value} (must be 'TASKS')",
        "Set frontmatter field: artifact_type: TASKS",
        2
    ),
    "TASKS-E004": (
        "Invalid layer: {value} (must be 10)",
        "Set frontmatter field: layer: 10",
        2
    ),
    "TASKS-E005": (
        "Missing parent_spec field",
        "Add frontmatter field: parent_spec: SPEC-NNN",
        2
    ),

    # Document Control Errors (E006)
    "TASKS-E006": (
        "Missing document control field: {field}",
        "Add required field to Document Control table: {field}",
        3
    ),

    # Structure Errors (E007)
    "TASKS-E007": (
        "Missing required section: {section}",
        "Add section header: {section}",
        4
    ),

    # Phase Errors (E008, E035)
    "TASKS-E008": (
        "No phases defined (expected ≥1)",
        "Add at least one phase section: ### Phase 1: [Phase Name]",
        5
    ),
    "TASKS-E035": (
        "Duplicate task IDs found: {duplicates}",
        "Ensure all task IDs are unique within document",
        5
    ),

    # Element ID Errors (E009)
    "TASKS-E009": (
        "Deprecated element ID format found: {pattern}",
        "Use unified format TASKS.NN.TT.SS instead of FR-001, QA-001, AC-001, BC-001, BO-001, or TASKS-NNN-YY",
        10
    ),

    # Traceability Errors (E010-E011)
    "TASKS-E010": (
        "Missing required traceability tag: {tag}",
        "Add tag to Traceability section: {tag}: [ID]",
        11
    ),
    "TASKS-E011": (
        "Empty tag value found: {tag}",
        "Provide value for tag: {tag}: [ID]",
        11
    ),

    # Cross-Reference Errors (E012)
    "TASKS-E012": (
        "Parent SPEC file not found: {spec_id}",
        "Create parent SPEC file in ../09_SPEC/ or update reference",
        12
    ),

    # Implementation Contracts Errors (E020-E024)
    "TASKS-E020": (
        "Invalid Protocol definition: {protocol}",
        "Fix Protocol syntax: class {protocol}(Protocol): with typed method signatures",
        9
    ),
    "TASKS-E021": (
        "Invalid TypedDict schema: {typeddict}",
        "Fix TypedDict syntax: class {typeddict}(TypedDict): with field type annotations",
        9
    ),
    "TASKS-E022": (
        "Invalid BaseModel schema: {model}",
        "Fix Pydantic BaseModel syntax: class {model}(BaseModel): with field definitions",
        9
    ),
    "TASKS-E023": (
        "Invalid dataclass definition: {dataclass}",
        "Fix dataclass syntax: @dataclass decorator with typed fields",
        9
    ),
    "TASKS-E024": (
        "Protocol {protocol} missing method signatures",
        "Add typed method signatures to Protocol: def method_name(self, ...) -> ReturnType: ...",
        9
    ),

    # Dependency Errors (E030)
    "TASKS-E030": (
        "Circular dependency detected: {cycle}",
        "Break circular dependency chain by reordering tasks or removing blocking relationships",
        7
    ),
}

# ============================================================================
# WARNING CODES (W-prefix, 33 codes)
# ============================================================================

TASKS_WARNING_CODES: Dict[str, ErrorCodeData] = {
    # Metadata Warnings (W001-W002)
    "TASKS-W001": (
        "Missing layer-10-artifact tag in frontmatter",
        "Add 'layer-10-artifact' to tags array in frontmatter",
        2
    ),
    "TASKS-W002": (
        "Invalid status value: {status}",
        "Use valid status enum: Draft | Ready | In Progress | Completed | Blocked",
        3
    ),

    # Phase Warnings (W003-W004, W032-W033)
    "TASKS-W003": (
        "No TASK-NNN items found (expected ≥1)",
        "Add task items: #### TASK-001: [Task Description]",
        5
    ),
    "TASKS-W004": (
        "No task checkboxes found (expected ≥1)",
        "Add checkboxes to task items: - [ ] Task step",
        5
    ),
    "TASKS-W032": (
        "Phase numbering not sequential: {sequence}",
        "Renumber phases sequentially starting from 1",
        5
    ),
    "TASKS-W033": (
        "Phase {phase_num} has no TASK-NNN items",
        "Add at least one task to Phase {phase_num}",
        5
    ),

    # Task Detail Warnings (W005-W008)
    "TASKS-W005": (
        "Missing 'Input:' field in task details",
        "Add Input: field to each task specifying required inputs",
        6
    ),
    "TASKS-W006": (
        "Missing 'Output:' field in task details",
        "Add Output: field to each task specifying expected outputs",
        6
    ),
    "TASKS-W007": (
        "Missing 'Acceptance:' field in task details",
        "Add Acceptance: field to each task specifying acceptance criteria",
        6
    ),
    "TASKS-W008": (
        "No file references found",
        "Add file references in backticks: `path/to/file.py`",
        6
    ),

    # Dependencies Warnings (W009-W011, W030-W031)
    "TASKS-W009": (
        "Missing upstream dependencies section",
        "Document upstream dependencies in Section 3",
        7
    ),
    "TASKS-W010": (
        "Missing downstream dependencies section",
        "Document downstream dependencies in Section 3",
        7
    ),
    "TASKS-W011": (
        "No blocking relationships documented",
        "Document blocking relationships: 'blocks', 'blocked by', 'depends on'",
        7
    ),
    "TASKS-W030": (
        "Orphan task (no dependencies): {task_id}",
        "Add upstream or downstream dependencies to connect task to workflow",
        7
    ),
    "TASKS-W031": (
        "Inconsistent bidirectional dependency: {relationship}",
        "Ensure symmetric dependency declarations (if A→B, then B has A in upstream)",
        7
    ),

    # Acceptance Criteria Warnings (W012-W014)
    "TASKS-W012": (
        "No test coverage targets found",
        "Add test coverage targets: 'unit: 95%', 'integration: 85%', 'e2e: 75%'",
        8
    ),
    "TASKS-W013": (
        "No BDD scenario references found",
        "Add BDD references: BDD-NNN scenario IDs",
        8
    ),
    "TASKS-W014": (
        "No completion criteria documented",
        "Add completion criteria using keywords: 'definition of done', 'completion criteria', 'done when'",
        8
    ),

    # Implementation Contracts Warnings (W015, W022-W024)
    "TASKS-W015": (
        "Contract methods missing return type hints",
        "Add return type hints to all contract methods: def method(...) -> ReturnType:",
        9
    ),
    "TASKS-W022": (
        "Exception {exception} missing error_code attribute",
        "Add error_code attribute to exception class for error tracking",
        9
    ),
    "TASKS-W023": (
        "State enum {enum} missing VALID_TRANSITIONS map",
        "Add VALID_TRANSITIONS mapping for state machine validation",
        9
    ),
    "TASKS-W024": (
        "Pydantic model {model} missing field validators",
        "Add @validator decorators for field validation logic",
        9
    ),

    # Cross-Reference Warnings (W016-W017, W025-W027)
    "TASKS-W016": (
        "No REQ references found",
        "Add references to atomic requirements: REQ-NNN",
        12
    ),
    "TASKS-W017": (
        "No ADR references found",
        "Add references to architecture decisions: ADR-NNN",
        12
    ),
    "TASKS-W025": (
        "Parent SPEC {spec_id} CODE-Ready score < 90%: {score}%",
        "Improve parent SPEC quality before proceeding with TASKS implementation",
        12
    ),
    "TASKS-W026": (
        "Referenced REQ not found: {req_id}",
        "Create REQ file in ../07_REQ/ or update reference",
        12
    ),
    "TASKS-W027": (
        "Referenced ADR not found: {adr_id}",
        "Create ADR file in ../05_ADR/ or update reference",
        12
    ),

    # Code Generation Warnings (W018-W020)
    "TASKS-W018": (
        "Missing code structure elements",
        "Document module/file/class/function structure for code generation",
        13
    ),
    "TASKS-W019": (
        "Missing import/dependency information",
        "Document import statements and package dependencies",
        13
    ),
    "TASKS-W020": (
        "Missing error handling documentation",
        "Document error handling approach and exception types",
        13
    ),

    # Token Size Warnings (W021)
    "TASKS-W021": (
        "File size {size_kb}KB exceeds 200KB optimal",
        "Consider splitting into multiple TASKS files (TASKS-NNN-part1.md, TASKS-NNN-part2.md)",
        14
    ),
}

# ============================================================================
# INFO CODES (I-prefix, 1 code)
# ============================================================================

TASKS_INFO_CODES: Dict[str, ErrorCodeData] = {
    "TASKS-I001": (
        "No embedded contracts found (may not be needed)",
        "Implementation Contracts (Section 7-8) are optional - only needed for parallel development",
        9
    ),
}

# ============================================================================
# COMBINED REGISTRY
# ============================================================================

ALL_CODES: Dict[str, ErrorCodeData] = {
    **TASKS_ERROR_CODES,
    **TASKS_WARNING_CODES,
    **TASKS_INFO_CODES,
}

# ============================================================================
# ERROR CATEGORIES
# ============================================================================

ERROR_CATEGORIES = {
    "Structure": ["E001", "E002", "E007"],
    "Metadata": ["E003", "E004", "E005", "W001"],
    "DocControl": ["E006", "W002"],
    "Phase": ["E008", "E035", "W003", "W004", "W032", "W033"],
    "ElementID": ["E009"],
    "Traceability": ["E010", "E011"],
    "CrossRef": ["E012", "W016", "W017", "W025", "W026", "W027"],
    "Contracts": ["E020", "E021", "E022", "E023", "E024", "W015", "W022", "W023", "W024", "I001"],
    "Dependencies": ["E030", "W009", "W010", "W011", "W030", "W031"],
    "TaskDetail": ["W005", "W006", "W007", "W008"],
    "Acceptance": ["W012", "W013", "W014"],
    "CodeGen": ["W018", "W019", "W020"],
    "TokenSize": ["W021"],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_error_message(code: str, **kwargs) -> str:
    """Get formatted error message for given code.

    Args:
        code: Error code (e.g., "TASKS-E001")
        **kwargs: Template variables for message formatting

    Returns:
        Formatted error message

    Example:
        >>> get_error_message("TASKS-E001", filename="TASKS_001.md")
        'Invalid filename format: TASKS_001.md'
    """
    if code not in ALL_CODES:
        return f"Unknown error code: {code}"

    message_template, _, _ = ALL_CODES[code]
    try:
        return message_template.format(**kwargs)
    except KeyError as e:
        return f"{message_template} (missing template variable: {e})"


def get_remediation(code: str) -> str:
    """Get remediation guidance for given code.

    Args:
        code: Error code (e.g., "TASKS-E001")

    Returns:
        Remediation guidance text

    Example:
        >>> get_remediation("TASKS-E001")
        'Rename file to TASKS-NNN_descriptive_slug.md format...'
    """
    if code not in ALL_CODES:
        return f"No remediation available for unknown code: {code}"

    _, remediation, _ = ALL_CODES[code]
    return remediation


def get_check_number(code: str) -> Optional[int]:
    """Get check number for given code.

    Args:
        code: Error code (e.g., "TASKS-E001")

    Returns:
        Check number (1-14) or None if unknown

    Example:
        >>> get_check_number("TASKS-E001")
        1
    """
    if code not in ALL_CODES:
        return None

    _, _, check_num = ALL_CODES[code]
    return check_num


def get_severity(code: str) -> str:
    """Get severity level for given code.

    Args:
        code: Error code (e.g., "TASKS-E001")

    Returns:
        Severity: "ERROR", "WARNING", or "INFO"

    Example:
        >>> get_severity("TASKS-E001")
        'ERROR'
    """
    if code in TASKS_ERROR_CODES:
        return "ERROR"
    elif code in TASKS_WARNING_CODES:
        return "WARNING"
    elif code in TASKS_INFO_CODES:
        return "INFO"
    else:
        return "UNKNOWN"


def get_category(code: str) -> Optional[str]:
    """Get category for given code.

    Args:
        code: Error code (e.g., "TASKS-E001")

    Returns:
        Category name or None if not found

    Example:
        >>> get_category("TASKS-E001")
        'Structure'
    """
    code_suffix = code.replace("TASKS-", "")

    for category, codes in ERROR_CATEGORIES.items():
        if code_suffix in codes:
            return category

    return None


def list_codes_by_category(category: str) -> list:
    """List all error codes in given category.

    Args:
        category: Category name (e.g., "Structure")

    Returns:
        List of error codes in category

    Example:
        >>> list_codes_by_category("Structure")
        ['TASKS-E001', 'TASKS-E002', 'TASKS-E007']
    """
    codes = ERROR_CATEGORIES.get(category, [])
    return [f"TASKS-{code}" for code in codes]


def list_codes_by_severity(severity: str) -> list:
    """List all error codes with given severity.

    Args:
        severity: "ERROR", "WARNING", or "INFO"

    Returns:
        List of error codes with that severity

    Example:
        >>> list_codes_by_severity("ERROR")
        ['TASKS-E001', 'TASKS-E002', ...]
    """
    if severity == "ERROR":
        return list(TASKS_ERROR_CODES.keys())
    elif severity == "WARNING":
        return list(TASKS_WARNING_CODES.keys())
    elif severity == "INFO":
        return list(TASKS_INFO_CODES.keys())
    else:
        return []


def list_codes_by_check(check_num: int) -> list:
    """List all error codes for given check number.

    Args:
        check_num: Check number (1-14)

    Returns:
        List of error codes for that check

    Example:
        >>> list_codes_by_check(1)
        ['TASKS-E001']
    """
    codes = []
    for code, (_, _, check) in ALL_CODES.items():
        if check == check_num:
            codes.append(code)
    return sorted(codes)


# ============================================================================
# REGISTRY STATISTICS
# ============================================================================

def get_statistics() -> dict:
    """Get error code registry statistics.

    Returns:
        Dictionary with counts by severity, category, check

    Example:
        >>> stats = get_statistics()
        >>> stats['total_codes']
        35
    """
    return {
        "total_codes": len(ALL_CODES),
        "errors": len(TASKS_ERROR_CODES),
        "warnings": len(TASKS_WARNING_CODES),
        "info": len(TASKS_INFO_CODES),
        "categories": len(ERROR_CATEGORIES),
        "category_breakdown": {
            cat: len(codes) for cat, codes in ERROR_CATEGORIES.items()
        },
        "check_breakdown": {
            f"CHECK_{i}": len(list_codes_by_check(i))
            for i in range(1, 15)
        },
    }


# ============================================================================
# MODULE CONSTANTS
# ============================================================================

VERSION = "1.0.0"
RELEASE_DATE = "2026-03-06"
TOTAL_CODES = len(ALL_CODES)
TOTAL_ERRORS = len(TASKS_ERROR_CODES)
TOTAL_WARNINGS = len(TASKS_WARNING_CODES)
TOTAL_INFO = len(TASKS_INFO_CODES)

# Flag to check if error codes are available (for graceful degradation)
HAS_ERROR_CODES = True


if __name__ == "__main__":
    # Display registry statistics
    print("=" * 60)
    print("TASKS Error Code Registry")
    print("=" * 60)
    print(f"Version: {VERSION}")
    print(f"Release Date: {RELEASE_DATE}")
    print(f"Total Codes: {TOTAL_CODES}")
    print(f"  - Errors: {TOTAL_ERRORS}")
    print(f"  - Warnings: {TOTAL_WARNINGS}")
    print(f"  - Info: {TOTAL_INFO}")
    print()

    print("Category Breakdown:")
    for category, codes in ERROR_CATEGORIES.items():
        print(f"  {category}: {len(codes)} codes")
    print()

    print("Check Breakdown:")
    for i in range(1, 15):
        codes = list_codes_by_check(i)
        if codes:
            print(f"  CHECK {i}: {len(codes)} codes - {', '.join([c.replace('TASKS-', '') for c in codes])}")
