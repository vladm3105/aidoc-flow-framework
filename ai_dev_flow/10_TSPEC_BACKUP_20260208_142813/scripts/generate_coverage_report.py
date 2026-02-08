#!/usr/bin/env python3
"""
Coverage Report Generator for AI Dev Flow.

Generates coverage reports, checks thresholds, and tracks coverage trends.

Usage:
    python generate_coverage_report.py --type all --html
    python generate_coverage_report.py --check --threshold 80
    python generate_coverage_report.py --trend
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Paths
SCRIPT_DIR = Path(__file__).parent
TSPEC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = TSPEC_DIR.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
RESULTS_DIR = TESTS_DIR / "results"
COVERAGE_HTML_DIR = TESTS_DIR / "coverage_html"
COVERAGE_JSON = RESULTS_DIR / "coverage.json"
COVERAGE_HISTORY = RESULTS_DIR / "coverage_history.json"

# Test type mappings
TEST_TYPE_MAP = {
    "utest": {"code": 40, "dir": "unit", "marker": "unit"},
    "itest": {"code": 41, "dir": "integration", "marker": "integration"},
    "stest": {"code": 42, "dir": "smoke", "marker": "smoke"},
    "ftest": {"code": 43, "dir": "functional", "marker": "functional"},
}


@dataclass
class CoverageReport:
    """Coverage report data."""

    timestamp: str
    test_type: str
    total_statements: int = 0
    covered_statements: int = 0
    missing_statements: int = 0
    coverage_percent: float = 0.0
    files: List[Dict] = field(default_factory=list)
    threshold: Optional[int] = None
    threshold_passed: Optional[bool] = None


def run_coverage(test_type: str, html: bool = False) -> Optional[Dict]:
    """Run pytest with coverage for specified test type."""
    if test_type == "all":
        test_dirs = [TESTS_DIR / config["dir"] for config in TEST_TYPE_MAP.values()]
        test_dirs = [d for d in test_dirs if d.exists()]
    else:
        config = TEST_TYPE_MAP.get(test_type)
        if not config:
            print(f"Error: Unknown test type: {test_type}")
            return None
        test_dir = TESTS_DIR / config["dir"]
        if not test_dir.exists():
            print(f"Warning: Test directory not found: {test_dir}")
            return None
        test_dirs = [test_dir]

    if not test_dirs:
        print("No test directories found")
        return None

    # Build pytest command with coverage
    cmd = [
        "python", "-m", "pytest",
        *[str(d) for d in test_dirs],
        f"--cov={PROJECT_ROOT / 'src'}",
        "--cov-report=json",
        f"--cov-report=json:{COVERAGE_JSON}",
    ]

    if html:
        COVERAGE_HTML_DIR.mkdir(parents=True, exist_ok=True)
        cmd.append(f"--cov-report=html:{COVERAGE_HTML_DIR}")

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        print(f"Warning: Tests failed with return code {result.returncode}")
        # Continue to parse coverage even if tests failed

    # Parse coverage JSON
    if COVERAGE_JSON.exists():
        try:
            return json.loads(COVERAGE_JSON.read_text())
        except json.JSONDecodeError as e:
            print(f"Error parsing coverage JSON: {e}")
            return None

    return None


def parse_coverage(coverage_data: Dict, test_type: str) -> CoverageReport:
    """Parse coverage.py JSON output into CoverageReport."""
    report = CoverageReport(
        timestamp=datetime.now().isoformat(),
        test_type=test_type,
    )

    if not coverage_data:
        return report

    totals = coverage_data.get("totals", {})
    report.total_statements = totals.get("num_statements", 0)
    report.covered_statements = totals.get("covered_lines", 0)
    report.missing_statements = totals.get("missing_lines", 0)
    report.coverage_percent = totals.get("percent_covered", 0.0)

    # File-level coverage
    files_data = coverage_data.get("files", {})
    for filepath, file_info in files_data.items():
        summary = file_info.get("summary", {})
        report.files.append({
            "path": filepath,
            "statements": summary.get("num_statements", 0),
            "covered": summary.get("covered_lines", 0),
            "missing": summary.get("missing_lines", 0),
            "percent": summary.get("percent_covered", 0.0),
        })

    # Sort by coverage percentage (lowest first)
    report.files.sort(key=lambda f: f["percent"])

    return report


def check_threshold(report: CoverageReport, threshold: int) -> bool:
    """Check if coverage meets threshold."""
    report.threshold = threshold
    report.threshold_passed = report.coverage_percent >= threshold
    return report.threshold_passed


def save_history(report: CoverageReport) -> None:
    """Save coverage report to history."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    history = []
    if COVERAGE_HISTORY.exists():
        try:
            history = json.loads(COVERAGE_HISTORY.read_text())
        except json.JSONDecodeError:
            pass

    # Add new entry
    history.append({
        "timestamp": report.timestamp,
        "test_type": report.test_type,
        "coverage_percent": report.coverage_percent,
        "total_statements": report.total_statements,
        "covered_statements": report.covered_statements,
    })

    # Keep last 100 entries
    history = history[-100:]

    COVERAGE_HISTORY.write_text(json.dumps(history, indent=2))


def load_history() -> List[Dict]:
    """Load coverage history."""
    if not COVERAGE_HISTORY.exists():
        return []
    try:
        return json.loads(COVERAGE_HISTORY.read_text())
    except json.JSONDecodeError:
        return []


def print_report(report: CoverageReport) -> None:
    """Print coverage report."""
    status_icon = "✅" if report.coverage_percent >= 80 else "⚠️" if report.coverage_percent >= 60 else "❌"

    print(f"\n{status_icon} Coverage Report: {report.test_type.upper()}")
    print("=" * 60)
    print(f"  Coverage:   {report.coverage_percent:.1f}%")
    print(f"  Statements: {report.covered_statements}/{report.total_statements}")
    print(f"  Missing:    {report.missing_statements}")

    if report.threshold is not None:
        threshold_icon = "✅" if report.threshold_passed else "❌"
        print(f"  Threshold:  {report.threshold}% {threshold_icon}")

    # Show lowest coverage files
    if report.files:
        print("\nLowest Coverage Files:")
        for file_info in report.files[:5]:
            path = file_info["path"]
            # Shorten path if too long
            if len(path) > 45:
                path = "..." + path[-42:]
            percent = file_info["percent"]
            icon = "❌" if percent < 50 else "⚠️" if percent < 80 else "✅"
            print(f"  {icon} {path}: {percent:.1f}%")

    print()


def print_trend(history: List[Dict]) -> None:
    """Print coverage trend."""
    if not history:
        print("No coverage history available.")
        return

    print("\nCoverage Trend (last 10 runs):")
    print("=" * 60)
    print(f"{'Timestamp':<20} {'Type':<8} {'Coverage':>10}")
    print("-" * 60)

    for entry in history[-10:]:
        timestamp = entry["timestamp"][:16]  # Trim to minutes
        test_type = entry.get("test_type", "unknown")
        coverage = entry.get("coverage_percent", 0)

        # Trend indicator
        idx = history.index(entry)
        if idx > 0:
            prev = history[idx - 1].get("coverage_percent", 0)
            if coverage > prev:
                trend = "↑"
            elif coverage < prev:
                trend = "↓"
            else:
                trend = "→"
        else:
            trend = " "

        print(f"{timestamp:<20} {test_type:<8} {coverage:>8.1f}% {trend}")

    # Summary
    if len(history) >= 2:
        first = history[0].get("coverage_percent", 0)
        last = history[-1].get("coverage_percent", 0)
        delta = last - first
        print("-" * 60)
        print(f"Overall change: {delta:+.1f}% ({first:.1f}% → {last:.1f}%)")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate coverage reports for AI Dev Flow"
    )
    parser.add_argument(
        "--type",
        choices=["utest", "itest", "stest", "ftest", "all"],
        default="all",
        help="Test type to measure coverage for",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML coverage report",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check coverage against threshold",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=80,
        help="Coverage threshold percentage (default: 80)",
    )
    parser.add_argument(
        "--trend",
        action="store_true",
        help="Show coverage trend",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to history",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    # Show trend only
    if args.trend and not args.check:
        history = load_history()
        print_trend(history)
        return 0

    # Run coverage
    coverage_data = run_coverage(args.type, html=args.html)
    if coverage_data is None:
        # Try to load existing coverage.json
        if COVERAGE_JSON.exists():
            try:
                coverage_data = json.loads(COVERAGE_JSON.read_text())
            except json.JSONDecodeError:
                print("Error: No coverage data available")
                return 1
        else:
            print("Error: No coverage data available")
            return 1

    report = parse_coverage(coverage_data, args.type)

    # Check threshold
    if args.check:
        check_threshold(report, args.threshold)

    # Save to history
    if args.save:
        save_history(report)

    # Output
    if args.json:
        output = {
            "timestamp": report.timestamp,
            "test_type": report.test_type,
            "total_statements": report.total_statements,
            "covered_statements": report.covered_statements,
            "missing_statements": report.missing_statements,
            "coverage_percent": report.coverage_percent,
            "threshold": report.threshold,
            "threshold_passed": report.threshold_passed,
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(report)

        if args.trend:
            history = load_history()
            print_trend(history)

    # Return code based on threshold check
    if args.check:
        return 0 if report.threshold_passed else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
