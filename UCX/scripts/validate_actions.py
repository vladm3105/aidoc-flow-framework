#!/usr/bin/env python3
"""
Validate UCX action format in BRD review reports.

Usage:
    python validate_actions.py <report.md> [--strict]

Options:
    --strict    Fail on warnings (unknown types/targets still allowed but warned)

Examples:
    python validate_actions.py BRD-01.UCR_review.md
    python validate_actions.py BRD-01.UCR_review.md --strict
"""

import re
import sys
import argparse
from pathlib import Path

# Known values (extensible - unknown values generate warnings, not errors)
KNOWN_TYPES = {'HANDOFF', 'INFORM', 'REVIEW', 'DEFER'}
KNOWN_TARGETS = {'PRD', 'EARS', 'BDD', 'ADR', 'CTR'}
KNOWN_PRIORITIES = {'P0', 'P1', 'P2'}

# Required fields
REQUIRED_FIELDS = [
    'ACTION_ID', 'TYPE', 'TARGET', 'PRIORITY',
    'SOURCE', 'PERSONA', 'CONTEXT', 'REQUIREMENT'
]


def validate_actions(content: str) -> tuple[list, list]:
    """
    Validate actions and return (errors, warnings).

    Errors: Missing fields, malformed format
    Warnings: Unknown types/targets (allows future extension)
    """
    errors = []
    warnings = []

    # Find all action blocks
    pattern = r'<!-- UCX-ACTION-START -->(.*?)<!-- UCX-ACTION-END -->'
    for match in re.finditer(pattern, content, re.DOTALL):
        block = match.group(1)
        line_num = content[:match.start()].count('\n') + 1

        # Extract ACTION_ID for error reporting
        id_match = re.search(r'ACTION_ID:\s*(ACT-[a-f0-9]+)', block)
        action_id = id_match.group(1) if id_match else "UNKNOWN"

        # Check required fields
        for field in REQUIRED_FIELDS:
            if f'{field}:' not in block:
                errors.append((line_num, action_id, f"Missing required field: {field}"))

        # Validate ACTION_ID format (simple: ACT-{hex})
        if id_match:
            if not re.match(r'ACT-[a-f0-9]{6,10}$', action_id):
                errors.append((
                    line_num, action_id,
                    "Invalid ACTION_ID format. Expected: ACT-{6-10 hex chars} (e.g., ACT-7f3a2b1c)"
                ))

        # Check TYPE (warn if unknown, don't error - allows future types)
        type_match = re.search(r'TYPE:\s*(\w+)', block)
        if type_match:
            action_type = type_match.group(1).upper()
            if action_type not in KNOWN_TYPES:
                warnings.append((
                    line_num, action_id,
                    f"Unknown TYPE: {action_type}. Known types: {KNOWN_TYPES}"
                ))

        # Check TARGET (warn if unknown - allows future targets)
        target_match = re.search(r'TARGET:\s*(\w+)', block)
        if target_match:
            target = target_match.group(1).upper()
            if target not in KNOWN_TARGETS:
                warnings.append((
                    line_num, action_id,
                    f"Unknown TARGET: {target}. Known targets: {KNOWN_TARGETS}"
                ))

        # Validate PRIORITY (error if invalid - strict set)
        priority_match = re.search(r'PRIORITY:\s*(P[012])', block)
        if not priority_match and 'PRIORITY:' in block:
            errors.append((
                line_num, action_id,
                f"Invalid PRIORITY format. Must be: {KNOWN_PRIORITIES}"
            ))

    # Check for unmatched markers
    start_count = content.count('<!-- UCX-ACTION-START -->')
    end_count = content.count('<!-- UCX-ACTION-END -->')
    if start_count != end_count:
        errors.append((
            0, "GLOBAL",
            f"Unmatched markers: {start_count} starts, {end_count} ends"
        ))

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate UCX action format")
    parser.add_argument("report", help="Path to UCR review report")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Error: File not found: {report_path}")
        sys.exit(1)

    content = report_path.read_text()
    errors, warnings = validate_actions(content)

    # Count actions
    action_count = content.count('<!-- UCX-ACTION-START -->')

    # Print results
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for line_num, action_id, msg in errors:
            print(f"  Line {line_num} [{action_id}]: {msg}")
        print()

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for line_num, action_id, msg in warnings:
            print(f"  Line {line_num} [{action_id}]: {msg}")
        print()

    # Determine exit status
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} errors in {action_count} actions")
        sys.exit(1)
    elif warnings and args.strict:
        print(f"VALIDATION FAILED (strict): {len(warnings)} warnings in {action_count} actions")
        sys.exit(1)
    else:
        status = f" ({len(warnings)} warnings)" if warnings else ""
        print(f"VALIDATION PASSED: {action_count} actions{status}")
        sys.exit(0)


if __name__ == "__main__":
    main()
