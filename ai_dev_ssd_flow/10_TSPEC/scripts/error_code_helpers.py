#!/usr/bin/env python3
"""
Error Code Helper Functions for TSPEC Validators

Provides utilities to work with the centralized error code registry.
"""

import sys
from pathlib import Path
from typing import Tuple, Optional

# Add parent scripts directory to path to import error_codes
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from error_codes import ERROR_REGISTRY, Severity
    HAS_ERROR_CODES = True
except ImportError:
    HAS_ERROR_CODES = False
    ERROR_REGISTRY = {}


def get_error_info(error_code: str) -> Tuple[str, str, str]:
    """Get error message, remediation, and severity from error code.

    Args:
        error_code: Error code (e.g., "TSPEC-E001", "UTEST-W001")

    Returns:
        Tuple of (message, remediation, severity_letter)

    Examples:
        >>> get_error_info("TSPEC-E001")
        ('Invalid test type', 'Use UTEST/ITEST/STEST/FTEST/PTEST/SECTEST', 'E')

        >>> get_error_info("UTEST-W001")
        ('Low pseudocode coverage', 'Add pseudocode to complex tests', 'W')
    """
    if not HAS_ERROR_CODES or error_code not in ERROR_REGISTRY:
        return (error_code, "Unknown error", "E")

    message, remediation = ERROR_REGISTRY[error_code]

    # Extract severity from error code (e.g., "TSPEC-E001" -> "E")
    parts = error_code.split("-")
    if len(parts) == 2 and len(parts[1]) > 0:
        severity_letter = parts[1][0]  # E, W, or I
    else:
        severity_letter = "E"  # Default to error

    return (message, remediation, severity_letter)


def format_error(error_code: str, context: str = "") -> str:
    """Format error message with code, message, and optional context.

    Args:
        error_code: Error code (e.g., "TSPEC-E001")
        context: Optional context information (e.g., "field: metadata")

    Returns:
        Formatted error string

    Examples:
        >>> format_error("TSPEC-E001")
        '[TSPEC-E001] Invalid test type'

        >>> format_error("UTEST-E002", "test case TC-001")
        '[UTEST-E002] Missing I/O table (test case TC-001)'
    """
    message, remediation, severity = get_error_info(error_code)

    if context:
        return f"[{error_code}] {message} ({context})"
    else:
        return f"[{error_code}] {message}"


def format_warning(error_code: str, context: str = "") -> str:
    """Format warning message with code, message, and optional context.

    Args:
        error_code: Warning code (e.g., "UTEST-W001")
        context: Optional context information

    Returns:
        Formatted warning string
    """
    return format_error(error_code, context)


def get_severity(error_code: str) -> str:
    """Get severity letter from error code.

    Args:
        error_code: Error code (e.g., "TSPEC-E001", "UTEST-W001")

    Returns:
        Severity letter: "E" (error), "W" (warning), or "I" (info)

    Examples:
        >>> get_severity("TSPEC-E001")
        'E'

        >>> get_severity("UTEST-W001")
        'W'
    """
    _, _, severity = get_error_info(error_code)
    return severity


def is_error(error_code: str) -> bool:
    """Check if error code represents an error (not warning or info).

    Args:
        error_code: Error code to check

    Returns:
        True if error code is an error (severity E)
    """
    return get_severity(error_code) == "E"


def is_warning(error_code: str) -> bool:
    """Check if error code represents a warning.

    Args:
        error_code: Error code to check

    Returns:
        True if error code is a warning (severity W)
    """
    return get_severity(error_code) == "W"


def calculate_exit_code(errors: list, warnings: list) -> int:
    """Calculate exit code based on error and warning lists.

    Args:
        errors: List of error messages (may contain error codes)
        warnings: List of warning messages (may contain error codes)

    Returns:
        Exit code: 0 (pass), 1 (warnings only), 2 (errors present)

    Examples:
        >>> calculate_exit_code([], [])
        0

        >>> calculate_exit_code([], ["warning"])
        1

        >>> calculate_exit_code(["error"], ["warning"])
        2
    """
    if errors and len(errors) > 0:
        return 2  # Errors present
    elif warnings and len(warnings) > 0:
        return 1  # Warnings only
    else:
        return 0  # Pass


# Convenience function for validators
def add_to_result(result, error_code: str, context: str = "") -> None:
    """Add error or warning to ValidationResult based on error code severity.

    Args:
        result: ValidationResult object
        error_code: Error code (e.g., "TSPEC-E001", "UTEST-W001")
        context: Optional context information

    Note:
        Automatically determines whether to add to errors or warnings list
        based on error code severity.
    """
    if is_error(error_code):
        result.issues.append(format_error(error_code, context))
    elif is_warning(error_code):
        result.warnings.append(format_warning(error_code, context))
    # Info messages are not added to issues/warnings
