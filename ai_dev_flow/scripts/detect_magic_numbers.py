#!/usr/bin/env python3
"""
detect_magic_numbers.py - Magic Number Detection for SDD Framework Documents

Detects hardcoded quantitative values in documentation that should use @threshold
registry references instead.

Usage:
    python detect_magic_numbers.py [--path PATH] [--fix] [--verbose]
    python detect_magic_numbers.py docs/BDD/
    python detect_magic_numbers.py docs/SPEC/ --verbose
    python detect_magic_numbers.py --path docs/ --fix

Exit codes:
    0 - No violations found
    1 - Violations found
    2 - Error during execution

Version: 1.0.0
Date: 2025-11-30
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Generator


@dataclass
class MagicNumberViolation:
    """Represents a detected magic number violation."""
    file_path: str
    line_number: int
    line_content: str
    detected_value: str
    suggested_category: str
    context: str


# Patterns for detecting magic numbers
MAGIC_NUMBER_PATTERNS = [
    # Performance patterns
    (r'\b(\d+)\s*ms\b', 'perf', 'latency or timeout value'),
    (r'\b(\d+)\s*milliseconds?\b', 'perf', 'latency or timeout value'),
    (r'\b(\d+)\s*seconds?\b', 'timeout', 'timeout value'),
    (r'p\d{2}[_\s]*[:=<>]\s*(\d+)', 'perf', 'percentile latency'),
    (r'latency[_\s]*[:=<>]\s*(\d+)', 'perf', 'latency target'),
    (r'response[_\s]*time[_\s]*[:=<>]\s*(\d+)', 'perf', 'response time target'),

    # Rate limit patterns
    (r'(\d+)\s*req(?:uest)?s?/s(?:ec(?:ond)?)?\b', 'limit', 'requests per second'),
    (r'(\d+)\s*requests?\s*per\s*(?:second|minute|hour)', 'limit', 'rate limit'),
    (r'rate[_\s]*limit[_\s]*[:=]\s*(\d+)', 'limit', 'rate limit'),
    (r'burst[_\s]*[:=]\s*(\d+)', 'limit', 'burst limit'),
    (r'concurrent[_\s]*[:=<>]\s*(\d+)', 'limit', 'concurrency limit'),

    # SLA patterns
    (r'(\d+(?:\.\d+)?)\s*%\s*(?:uptime|availability|success)', 'sla', 'availability target'),
    (r'uptime[_\s]*[:=<>]\s*(\d+(?:\.\d+)?)', 'sla', 'uptime target'),
    (r'availability[_\s]*[:=<>]\s*(\d+(?:\.\d+)?)', 'sla', 'availability target'),
    (r'error[_\s]*rate[_\s]*[:=<>]\s*(\d+(?:\.\d+)?)', 'sla', 'error rate threshold'),

    # Resource patterns
    (r'(\d+)\s*(?:GB|MB|KB|bytes?)\b', 'resource', 'memory or storage limit'),
    (r'(\d+)\s*IOPS\b', 'resource', 'disk IOPS'),
    (r'(\d+)\s*cores?\b', 'resource', 'CPU cores'),
    (r'memory[_\s]*[:=]\s*(\d+)', 'resource', 'memory limit'),
    (r'cpu[_\s]*[:=]\s*(\d+)', 'resource', 'CPU limit'),

    # Timeout patterns
    (r'timeout[_\s]*[:=]\s*(\d+)', 'timeout', 'timeout configuration'),
    (r'max[_\s]*retries?[_\s]*[:=]\s*(\d+)', 'retry', 'retry configuration'),
    (r'retry[_\s]*(?:count|attempts?)[_\s]*[:=]\s*(\d+)', 'retry', 'retry count'),

    # Batch patterns
    (r'batch[_\s]*size[_\s]*[:=]\s*(\d+)', 'batch', 'batch size'),
    (r'page[_\s]*size[_\s]*[:=]\s*(\d+)', 'batch', 'page size'),

    # Compliance patterns (currency)
    (r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'compliance', 'monetary threshold'),
    (r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD', 'compliance', 'monetary threshold'),
]

# Patterns that indicate @threshold is already used (exclude from violations)
THRESHOLD_REF_PATTERN = re.compile(r'@threshold:\s*PRD-\d{3}:[a-z._]+')

# File extensions to scan
SCANNABLE_EXTENSIONS = {'.md', '.feature', '.yaml', '.yml'}

# Lines to skip (comments explaining the pattern, not violations)
SKIP_PATTERNS = [
    re.compile(r'^\s*#.*example', re.IGNORECASE),
    re.compile(r'^\s*<!--'),
    re.compile(r'example:', re.IGNORECASE),
    re.compile(r'format:', re.IGNORECASE),
    re.compile(r'@threshold:'),  # Already using threshold reference
]


def should_skip_line(line: str) -> bool:
    """Check if line should be skipped from analysis."""
    for pattern in SKIP_PATTERNS:
        if pattern.search(line):
            return True
    return False


def detect_magic_numbers_in_file(file_path: Path) -> list[MagicNumberViolation]:
    """Scan a file for magic number violations."""
    violations = []

    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return []

    for line_num, line in enumerate(lines, start=1):
        # Skip lines that are threshold references or examples
        if should_skip_line(line):
            continue

        # Check if line already has @threshold reference
        if THRESHOLD_REF_PATTERN.search(line):
            continue

        # Check each magic number pattern
        for pattern, category, context in MAGIC_NUMBER_PATTERNS:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                value = match.group(1) if match.groups() else match.group(0)

                # Skip very small numbers (often not configurable thresholds)
                try:
                    numeric_value = float(value.replace(',', ''))
                    if numeric_value < 1 and category not in ('sla',):
                        continue
                except ValueError:
                    pass

                violations.append(MagicNumberViolation(
                    file_path=str(file_path),
                    line_number=line_num,
                    line_content=line.strip(),
                    detected_value=value,
                    suggested_category=category,
                    context=context,
                ))

    return violations


def scan_directory(path: Path, extensions: set[str] = None) -> Generator[Path, None, None]:
    """Recursively scan directory for files with given extensions."""
    if extensions is None:
        extensions = SCANNABLE_EXTENSIONS

    if path.is_file():
        if path.suffix in extensions:
            yield path
        return

    for item in path.rglob('*'):
        if item.is_file() and item.suffix in extensions:
            # Skip template files if they're in the ai_dev_flow directory
            # (templates are allowed to have placeholder patterns)
            if 'TEMPLATE' in item.name:
                continue
            yield item


def format_violation(v: MagicNumberViolation, verbose: bool = False) -> str:
    """Format a violation for output."""
    suggestion = f"@threshold: PRD-NNN:{v.suggested_category}.<key>"

    output = f"{v.file_path}:{v.line_number}: Magic number '{v.detected_value}' ({v.context})"

    if verbose:
        output += f"\n  Line: {v.line_content}"
        output += f"\n  Suggestion: Replace with {suggestion}"

    return output


def generate_report(violations: list[MagicNumberViolation]) -> str:
    """Generate a summary report of violations."""
    if not violations:
        return "No magic number violations detected."

    # Group by file
    by_file: dict[str, list[MagicNumberViolation]] = {}
    for v in violations:
        by_file.setdefault(v.file_path, []).append(v)

    # Group by category
    by_category: dict[str, int] = {}
    for v in violations:
        by_category[v.suggested_category] = by_category.get(v.suggested_category, 0) + 1

    report = [
        "=" * 60,
        "MAGIC NUMBER DETECTION REPORT",
        "=" * 60,
        "",
        f"Total violations: {len(violations)}",
        f"Files affected: {len(by_file)}",
        "",
        "By category:",
    ]

    for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
        report.append(f"  {category}: {count}")

    report.extend([
        "",
        "By file:",
    ])

    for file_path, file_violations in sorted(by_file.items()):
        report.append(f"  {file_path}: {len(file_violations)} violations")

    report.extend([
        "",
        "=" * 60,
        "RECOMMENDATION: Replace hardcoded values with @threshold references",
        "See: ai_dev_flow/PRD/PRD-000_threshold_registry_template.md",
        "=" * 60,
    ])

    return '\n'.join(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Detect magic numbers in SDD framework documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s docs/BDD/              # Scan BDD directory
    %(prog)s docs/SPEC/ --verbose   # Scan with detailed output
    %(prog)s --path docs/           # Scan all docs
        """
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to scan (file or directory)'
    )
    parser.add_argument(
        '--path', '-p',
        dest='path_opt',
        help='Alternative path specification'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed violation information'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Generate summary report'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Only output count of violations'
    )

    args = parser.parse_args()

    # Determine path to scan
    scan_path = Path(args.path_opt or args.path)

    if not scan_path.exists():
        print(f"Error: Path does not exist: {scan_path}", file=sys.stderr)
        sys.exit(2)

    # Collect all violations
    all_violations: list[MagicNumberViolation] = []

    for file_path in scan_directory(scan_path):
        violations = detect_magic_numbers_in_file(file_path)
        all_violations.extend(violations)

    # Output results
    if args.quiet:
        print(len(all_violations))
    else:
        if args.report:
            print(generate_report(all_violations))
            print()

        if all_violations:
            print("Violations found:")
            for v in all_violations:
                print(format_violation(v, verbose=args.verbose))
                if args.verbose:
                    print()

    # Exit with appropriate code
    sys.exit(0 if not all_violations else 1)


if __name__ == '__main__':
    main()
