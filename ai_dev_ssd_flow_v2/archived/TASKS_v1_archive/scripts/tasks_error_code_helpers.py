"""TASKS Error Code Helper Functions v1.0 (2026-03-06)

Utility functions for formatting error/warning messages with error codes.
Provides consistent formatting across all TASKS validators.

Based on TSPEC error_code_helpers.py pattern.
Designed for use in validate_tasks.py and related validators.

Usage:
    from tasks_error_code_helpers import format_error, format_warning, calculate_exit_code

    issues.append(format_error("TASKS-E001", filename="TASKS_001.md"))
    warnings.append(format_warning("TASKS-W003"))
    exit_code = calculate_exit_code(errors=2, warnings=5)
"""

from typing import Optional
from tasks_error_codes import (
    HAS_ERROR_CODES,
    get_error_message,
    get_severity,
    TASKS_ERROR_CODES,
    TASKS_WARNING_CODES,
)


def format_error(code: str, context: str = "", **kwargs) -> str:
    """Format error message with error code prefix.

    Args:
        code: Error code (e.g., "TASKS-E001")
        context: Additional context string (optional)
        **kwargs: Template variables for error message

    Returns:
        Formatted error message: "[CODE] Message (context)"

    Example:
        >>> format_error("TASKS-E001", filename="TASKS_001.md")
        '[TASKS-E001] Invalid filename format: TASKS_001.md'

        >>> format_error("TASKS-E006", "TASKS-001", field="Author")
        '[TASKS-E006] Missing document control field: Author (TASKS-001)'
    """
    if not HAS_ERROR_CODES:
        # Graceful degradation if error codes unavailable
        return context if context else "Error occurred"

    message = get_error_message(code, **kwargs)

    if context:
        return f"[{code}] {message} ({context})"
    else:
        return f"[{code}] {message}"


def format_warning(code: str, context: str = "", **kwargs) -> str:
    """Format warning message with warning code prefix.

    Args:
        code: Warning code (e.g., "TASKS-W003")
        context: Additional context string (optional)
        **kwargs: Template variables for warning message

    Returns:
        Formatted warning message: "[CODE] Message (context)"

    Example:
        >>> format_warning("TASKS-W003")
        '[TASKS-W003] No TASK-NNN items found (expected ≥1)'

        >>> format_warning("TASKS-W032", sequence="[1, 3, 4]")
        '[TASKS-W032] Phase numbering not sequential: [1, 3, 4]'
    """
    if not HAS_ERROR_CODES:
        # Graceful degradation if error codes unavailable
        return context if context else "Warning occurred"

    message = get_error_message(code, **kwargs)

    if context:
        return f"[{code}] {message} ({context})"
    else:
        return f"[{code}] {message}"


def format_info(code: str, context: str = "", **kwargs) -> str:
    """Format informational message with info code prefix.

    Args:
        code: Info code (e.g., "TASKS-I001")
        context: Additional context string (optional)
        **kwargs: Template variables for info message

    Returns:
        Formatted info message: "[CODE] Message (context)"

    Example:
        >>> format_info("TASKS-I001")
        '[TASKS-I001] No embedded contracts found (may not be needed)'
    """
    if not HAS_ERROR_CODES:
        # Graceful degradation if error codes unavailable
        return context if context else "Info"

    message = get_error_message(code, **kwargs)

    if context:
        return f"[{code}] {message} ({context})"
    else:
        return f"[{code}] {message}"


def calculate_exit_code(errors: int, warnings: int) -> int:
    """Calculate exit code based on error/warning counts.

    Exit codes:
    - 0: Pass (no errors, no warnings)
    - 1: Pass with warnings (no errors, warnings present)
    - 2: Fail (errors present)

    Args:
        errors: Number of errors
        warnings: Number of warnings

    Returns:
        Exit code (0, 1, or 2)

    Example:
        >>> calculate_exit_code(errors=0, warnings=0)
        0
        >>> calculate_exit_code(errors=0, warnings=5)
        1
        >>> calculate_exit_code(errors=2, warnings=5)
        2
    """
    if errors > 0:
        return 2  # FAIL
    elif warnings > 0:
        return 1  # PASS WITH WARNINGS
    else:
        return 0  # PASS


def get_severity_emoji(severity: str) -> str:
    """Get emoji for severity level.

    Args:
        severity: "ERROR", "WARNING", or "INFO"

    Returns:
        Emoji string

    Example:
        >>> get_severity_emoji("ERROR")
        '❌'
    """
    emoji_map = {
        "ERROR": "❌",
        "WARNING": "⚠️",
        "INFO": "ℹ️",
        "PASS": "✅",
    }
    return emoji_map.get(severity, "")


def get_severity_color(severity: str) -> str:
    """Get ANSI color code for severity level.

    Args:
        severity: "ERROR", "WARNING", or "INFO"

    Returns:
        ANSI color code string

    Example:
        >>> get_severity_color("ERROR")
        '\033[0;31m'  # Red
    """
    color_map = {
        "ERROR": "\033[0;31m",    # Red
        "WARNING": "\033[1;33m",  # Yellow
        "INFO": "\033[0;34m",     # Blue
        "PASS": "\033[0;32m",     # Green
        "RESET": "\033[0m",       # Reset
    }
    return color_map.get(severity, color_map["RESET"])


def format_colored(text: str, severity: str) -> str:
    """Format text with ANSI color for severity.

    Args:
        text: Text to color
        severity: "ERROR", "WARNING", "INFO", or "PASS"

    Returns:
        Colored text with reset code

    Example:
        >>> format_colored("Error message", "ERROR")
        '\033[0;31mError message\033[0m'
    """
    color = get_severity_color(severity)
    reset = get_severity_color("RESET")
    return f"{color}{text}{reset}"


def format_summary(errors: int, warnings: int, info: int = 0) -> str:
    """Format validation summary with colors.

    Args:
        errors: Number of errors
        warnings: Number of warnings
        info: Number of info messages

    Returns:
        Formatted summary string with colors

    Example:
        >>> format_summary(errors=2, warnings=5)
        '❌ Errors: 2 | ⚠️ Warnings: 5'
    """
    parts = []

    if errors > 0:
        parts.append(f"{get_severity_emoji('ERROR')} Errors: {format_colored(str(errors), 'ERROR')}")
    else:
        parts.append(f"{get_severity_emoji('PASS')} Errors: {format_colored('0', 'PASS')}")

    if warnings > 0:
        parts.append(f"{get_severity_emoji('WARNING')} Warnings: {format_colored(str(warnings), 'WARNING')}")
    else:
        parts.append(f"Warnings: {warnings}")

    if info > 0:
        parts.append(f"{get_severity_emoji('INFO')} Info: {info}")

    return " | ".join(parts)


def validate_code_exists(code: str) -> bool:
    """Check if error code exists in registry.

    Args:
        code: Error code to check

    Returns:
        True if code exists, False otherwise

    Example:
        >>> validate_code_exists("TASKS-E001")
        True
        >>> validate_code_exists("TASKS-E999")
        False
    """
    return code in TASKS_ERROR_CODES or code in TASKS_WARNING_CODES


def get_code_prefix(code: str) -> Optional[str]:
    """Extract prefix from error code.

    Args:
        code: Error code (e.g., "TASKS-E001")

    Returns:
        Prefix ("E", "W", or "I") or None if invalid

    Example:
        >>> get_code_prefix("TASKS-E001")
        'E'
        >>> get_code_prefix("TASKS-W003")
        'W'
    """
    if not code or "-" not in code:
        return None

    # Extract middle part: TASKS-E001 → E
    parts = code.split("-")
    if len(parts) != 2:
        return None

    prefix = parts[1][0] if parts[1] else None
    return prefix if prefix in ("E", "W", "I") else None


def is_error_code(code: str) -> bool:
    """Check if code is an error (E-prefix).

    Args:
        code: Error code to check

    Returns:
        True if error code, False otherwise

    Example:
        >>> is_error_code("TASKS-E001")
        True
        >>> is_error_code("TASKS-W003")
        False
    """
    return get_code_prefix(code) == "E"


def is_warning_code(code: str) -> bool:
    """Check if code is a warning (W-prefix).

    Args:
        code: Error code to check

    Returns:
        True if warning code, False otherwise

    Example:
        >>> is_warning_code("TASKS-W003")
        True
        >>> is_warning_code("TASKS-E001")
        False
    """
    return get_code_prefix(code) == "W"


def is_info_code(code: str) -> bool:
    """Check if code is informational (I-prefix).

    Args:
        code: Error code to check

    Returns:
        True if info code, False otherwise

    Example:
        >>> is_info_code("TASKS-I001")
        True
        >>> is_info_code("TASKS-E001")
        False
    """
    return get_code_prefix(code) == "I"


def extract_code_from_message(message: str) -> Optional[str]:
    """Extract error code from formatted message.

    Args:
        message: Formatted message with code

    Returns:
        Error code or None if not found

    Example:
        >>> extract_code_from_message("[TASKS-E001] Invalid filename")
        'TASKS-E001'
    """
    import re

    match = re.match(r'^\[(TASKS-[EWI]\d+)\]', message)
    return match.group(1) if match else None


def count_by_severity(messages: list) -> dict:
    """Count messages by severity level.

    Args:
        messages: List of formatted messages with error codes

    Returns:
        Dictionary with counts: {"errors": N, "warnings": M, "info": P}

    Example:
        >>> msgs = ["[TASKS-E001] Error", "[TASKS-W003] Warning"]
        >>> count_by_severity(msgs)
        {'errors': 1, 'warnings': 1, 'info': 0}
    """
    counts = {"errors": 0, "warnings": 0, "info": 0}

    for msg in messages:
        code = extract_code_from_message(msg)
        if code:
            if is_error_code(code):
                counts["errors"] += 1
            elif is_warning_code(code):
                counts["warnings"] += 1
            elif is_info_code(code):
                counts["info"] += 1

    return counts


# ============================================================================
# MODULE METADATA
# ============================================================================

VERSION = "1.0.0"
RELEASE_DATE = "2026-03-06"


if __name__ == "__main__":
    # Demo usage
    print("=" * 60)
    print("TASKS Error Code Helpers Demo")
    print("=" * 60)
    print()

    # Error formatting
    print("Error Examples:")
    print(format_error("TASKS-E001", filename="TASKS_001.md"))
    print(format_error("TASKS-E006", "TASKS-001", field="Author"))
    print()

    # Warning formatting
    print("Warning Examples:")
    print(format_warning("TASKS-W003"))
    print(format_warning("TASKS-W032", sequence="[1, 3, 4]"))
    print()

    # Info formatting
    print("Info Examples:")
    print(format_info("TASKS-I001"))
    print()

    # Exit code calculation
    print("Exit Code Examples:")
    print(f"  0 errors, 0 warnings → exit {calculate_exit_code(0, 0)}")
    print(f"  0 errors, 5 warnings → exit {calculate_exit_code(0, 5)}")
    print(f"  2 errors, 5 warnings → exit {calculate_exit_code(2, 5)}")
    print()

    # Summary formatting
    print("Summary Examples:")
    print(f"  {format_summary(0, 0)}")
    print(f"  {format_summary(0, 5)}")
    print(f"  {format_summary(2, 5)}")
    print()

    # Code validation
    print("Code Validation:")
    print(f"  TASKS-E001 exists: {validate_code_exists('TASKS-E001')}")
    print(f"  TASKS-E999 exists: {validate_code_exists('TASKS-E999')}")
    print(f"  TASKS-E001 is error: {is_error_code('TASKS-E001')}")
    print(f"  TASKS-W003 is warning: {is_warning_code('TASKS-W003')}")
