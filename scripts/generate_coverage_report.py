#!/usr/bin/env python3
"""
Generate coverage reports and track trends for AI Dev Flow.

Provides functionality to:
- Run coverage.py during test execution
- Generate HTML, JSON, and terminal reports
- Track coverage trends over time
- Alert on coverage decreases
- Enforce coverage thresholds

Usage:
    python scripts/generate_coverage_report.py --type utest
    python scripts/generate_coverage_report.py --type all --html
    python scripts/generate_coverage_report.py --trend tests/results/
    python scripts/generate_coverage_report.py --check --threshold 80

Reference: ai_dev_flow/10_TSPEC/, TESTING_STRATEGY_TDD.md
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TESTS_DIR = PROJECT_ROOT / "tests"
RESULTS_DIR = TESTS_DIR / "results"
COVERAGE_DIR = TESTS_DIR / "coverage_html"

# Default threshold
DEFAULT_THRESHOLD = 80


def run_coverage(
    test_type: str = "all",
    source_dirs: Optional[List[str]] = None,
    html_report: bool = False,
    json_report: bool = True,
) -> Tuple[float, Dict]:
    """
    Run tests with coverage collection.

    Args:
        test_type: Type of tests to run (utest, itest, stest, ftest, all)
        source_dirs: Source directories to measure coverage for
        html_report: Generate HTML report
        json_report: Generate JSON report

    Returns:
        Tuple of (coverage_percent, coverage_data)
    """
    if source_dirs is None:
        source_dirs = ["src"]

    # Build pytest command with coverage
    cmd = ["python", "-m", "pytest"]

    # Test path based on type
    test_paths = {
        "utest": "tests/unit",
        "itest": "tests/integration",
        "stest": "tests/smoke",
        "ftest": "tests/functional",
        "all": "tests",
    }

    test_path = PROJECT_ROOT / test_paths.get(test_type, "tests")
    if test_path.exists():
        cmd.append(str(test_path))
    else:
        cmd.append(str(TESTS_DIR))

    # Add coverage options
    for src in source_dirs:
        cmd.extend([f"--cov={src}"])

    cmd.append("--cov-report=term-missing")

    # JSON report
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / f"coverage_{test_type}_{run_id}.json"
    cmd.append(f"--cov-report=json:{json_path}")

    # HTML report
    if html_report:
        COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
        cmd.append(f"--cov-report=html:{COVERAGE_DIR}")

    # Run tests
    print(f"\nRunning {test_type} tests with coverage...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,
        )
    except FileNotFoundError:
        print("Error: pytest-cov not found. Install with: pip install pytest-cov")
        return 0.0, {}

    # Parse JSON report
    coverage_data = {}
    coverage_percent = 0.0

    if json_path.exists():
        try:
            coverage_data = json.loads(json_path.read_text())
            totals = coverage_data.get("totals", {})
            coverage_percent = totals.get("percent_covered", 0.0)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not parse coverage JSON: {e}")

    return coverage_percent, coverage_data


def check_threshold(
    coverage_percent: float,
    threshold: float = DEFAULT_THRESHOLD,
) -> bool:
    """
    Check if coverage meets minimum threshold.

    Args:
        coverage_percent: Current coverage percentage
        threshold: Minimum required coverage

    Returns:
        True if coverage meets threshold
    """
    if coverage_percent >= threshold:
        print(f"\nCoverage: {coverage_percent:.1f}% >= {threshold}%")
        return True
    else:
        print(f"\nCoverage: {coverage_percent:.1f}% < {threshold}% (BELOW THRESHOLD)")
        return False


def get_coverage_trend(results_dir: Path, limit: int = 10) -> List[Dict]:
    """
    Get coverage trend from historical reports.

    Args:
        results_dir: Directory containing coverage JSON files
        limit: Maximum number of entries to return

    Returns:
        List of coverage data points
    """
    trend = []

    for file in sorted(
        results_dir.glob("coverage_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:limit]:
        try:
            data = json.loads(file.read_text())
            totals = data.get("totals", {})

            # Extract test type and timestamp from filename
            parts = file.stem.split("_")
            test_type = parts[1] if len(parts) > 1 else "unknown"
            run_id = "_".join(parts[2:]) if len(parts) > 2 else ""

            trend.append(
                {
                    "file": file.name,
                    "test_type": test_type,
                    "run_id": run_id,
                    "covered_lines": totals.get("covered_lines", 0),
                    "missing_lines": totals.get("missing_lines", 0),
                    "total_lines": totals.get("num_statements", 0),
                    "percent_covered": totals.get("percent_covered", 0.0),
                    "timestamp": datetime.fromtimestamp(
                        file.stat().st_mtime
                    ).isoformat(),
                }
            )
        except (json.JSONDecodeError, KeyError):
            continue

    return trend


def generate_trend_report(results_dir: Path, limit: int = 10) -> str:
    """
    Generate coverage trend report.

    Args:
        results_dir: Directory containing coverage JSON files
        limit: Maximum number of entries

    Returns:
        Markdown formatted report
    """
    trend = get_coverage_trend(results_dir, limit)

    if not trend:
        return "No coverage data found."

    lines = [
        "# Coverage Trend Report",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Runs Analyzed**: {len(trend)}",
        "",
        "## Coverage Over Time",
        "",
        "| Run ID | Type | Lines | Covered | Missing | Coverage |",
        "|--------|------|-------|---------|---------|----------|",
    ]

    for entry in trend:
        lines.append(
            f"| {entry['run_id'][:15]} | {entry['test_type']} | "
            f"{entry['total_lines']} | {entry['covered_lines']} | "
            f"{entry['missing_lines']} | {entry['percent_covered']:.1f}% |"
        )

    lines.append("")

    # Calculate statistics
    if len(trend) >= 2:
        latest = trend[0]["percent_covered"]
        previous = trend[1]["percent_covered"]
        change = latest - previous

        lines.extend(
            [
                "## Latest Change",
                "",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| Current Coverage | {latest:.1f}% |",
                f"| Previous Coverage | {previous:.1f}% |",
                f"| Change | {change:+.1f}% |",
                "",
            ]
        )

        if change < 0:
            lines.append(f"**Warning**: Coverage decreased by {abs(change):.1f}%")
            lines.append("")

    return "\n".join(lines)


def get_uncovered_files(coverage_data: Dict) -> List[Dict]:
    """
    Get list of files with low coverage.

    Args:
        coverage_data: Coverage JSON data

    Returns:
        List of files with coverage below threshold
    """
    uncovered = []

    files = coverage_data.get("files", {})
    for filepath, data in files.items():
        summary = data.get("summary", {})
        percent = summary.get("percent_covered", 100)

        if percent < DEFAULT_THRESHOLD:
            uncovered.append(
                {
                    "file": filepath,
                    "percent_covered": percent,
                    "missing_lines": summary.get("missing_lines", 0),
                    "covered_lines": summary.get("covered_lines", 0),
                }
            )

    # Sort by coverage (lowest first)
    uncovered.sort(key=lambda x: x["percent_covered"])
    return uncovered


def generate_coverage_report(coverage_data: Dict) -> str:
    """
    Generate detailed coverage report.

    Args:
        coverage_data: Coverage JSON data

    Returns:
        Markdown formatted report
    """
    totals = coverage_data.get("totals", {})

    lines = [
        "# Coverage Report",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Lines | {totals.get('num_statements', 0)} |",
        f"| Covered Lines | {totals.get('covered_lines', 0)} |",
        f"| Missing Lines | {totals.get('missing_lines', 0)} |",
        f"| Coverage | {totals.get('percent_covered', 0):.1f}% |",
        "",
    ]

    # Add uncovered files section
    uncovered = get_uncovered_files(coverage_data)
    if uncovered:
        lines.extend(
            [
                "## Files Below Threshold",
                "",
                f"Files with coverage below {DEFAULT_THRESHOLD}%:",
                "",
                "| File | Coverage | Missing |",
                "|------|----------|---------|",
            ]
        )
        for file in uncovered[:20]:
            filepath = file["file"].replace(str(PROJECT_ROOT) + "/", "")
            lines.append(
                f"| `{filepath}` | {file['percent_covered']:.1f}% | "
                f"{file['missing_lines']} lines |"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate coverage reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/generate_coverage_report.py --type utest
    python scripts/generate_coverage_report.py --type all --html
    python scripts/generate_coverage_report.py --check --threshold 80
    python scripts/generate_coverage_report.py --trend
        """,
    )

    parser.add_argument(
        "--type",
        choices=["utest", "itest", "stest", "ftest", "all"],
        default="all",
        help="Type of tests to run (default: all)",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check coverage against threshold",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Minimum coverage threshold (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--trend",
        action="store_true",
        help="Generate trend report from historical data",
    )
    parser.add_argument(
        "--source",
        action="append",
        help="Source directory to measure (can be specified multiple times)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file for report",
    )

    args = parser.parse_args()

    # Trend report mode
    if args.trend:
        report = generate_trend_report(RESULTS_DIR)
        if args.output:
            args.output.write_text(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)
        return 0

    # Run coverage
    coverage_percent, coverage_data = run_coverage(
        test_type=args.type,
        source_dirs=args.source,
        html_report=args.html,
    )

    # Generate report
    if coverage_data:
        report = generate_coverage_report(coverage_data)
        if args.output:
            args.output.write_text(report)
            print(f"Report saved to: {args.output}")
        else:
            print("\n" + report)

    if args.html:
        print(f"\nHTML report: {COVERAGE_DIR}/index.html")

    # Check threshold
    if args.check:
        if not check_threshold(coverage_percent, args.threshold):
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
