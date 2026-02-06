#!/usr/bin/env python3
"""
Test Result Comparison and Regression Detection for AI Dev Flow.

Compares test results between runs to detect regressions.

Usage:
    python compare_test_results.py baseline.json current.json
    python compare_test_results.py --latest tests/results/
    python compare_test_results.py --json baseline.json current.json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class RegressionReport:
    """Report of regressions detected between test runs."""

    baseline_run_id: str
    current_run_id: str
    baseline_file: str
    current_file: str
    has_regressions: bool = False
    new_failures: List[Dict] = field(default_factory=list)
    fixed_tests: List[Dict] = field(default_factory=list)
    new_tests: List[Dict] = field(default_factory=list)
    removed_tests: List[Dict] = field(default_factory=list)
    summary: Dict = field(default_factory=dict)


def load_result(filepath: Path) -> Optional[Dict]:
    """Load test result from JSON file."""
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return None
    try:
        return json.loads(filepath.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        return None


def find_latest_results(directory: Path) -> Tuple[Optional[Path], Optional[Path]]:
    """Find the two most recent result files in a directory."""
    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        return None, None

    # Find all JSON result files
    result_files = sorted(
        [f for f in directory.glob("*.json") if not f.name.startswith("pytest_output")],
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    if len(result_files) < 2:
        print(f"Error: Need at least 2 result files, found {len(result_files)}")
        return None, None

    return result_files[1], result_files[0]  # baseline, current


def compare_results(baseline: Dict, current: Dict) -> RegressionReport:
    """Compare two test results and generate regression report."""
    report = RegressionReport(
        baseline_run_id=baseline.get("run_id", "unknown"),
        current_run_id=current.get("run_id", "unknown"),
        baseline_file="",
        current_file="",
    )

    # Build test result maps
    baseline_tests = {t["nodeid"]: t for t in baseline.get("tests", [])}
    current_tests = {t["nodeid"]: t for t in current.get("tests", [])}

    baseline_nodeids = set(baseline_tests.keys())
    current_nodeids = set(current_tests.keys())

    # Find new failures (passed in baseline, failed in current)
    for nodeid in baseline_nodeids & current_nodeids:
        base_outcome = baseline_tests[nodeid].get("outcome", "unknown")
        curr_outcome = current_tests[nodeid].get("outcome", "unknown")

        if base_outcome == "passed" and curr_outcome in ("failed", "error"):
            report.new_failures.append({
                "nodeid": nodeid,
                "name": current_tests[nodeid].get("name", ""),
                "baseline_outcome": base_outcome,
                "current_outcome": curr_outcome,
            })
            report.has_regressions = True

        elif base_outcome in ("failed", "error") and curr_outcome == "passed":
            report.fixed_tests.append({
                "nodeid": nodeid,
                "name": current_tests[nodeid].get("name", ""),
                "baseline_outcome": base_outcome,
                "current_outcome": curr_outcome,
            })

    # Find new tests (in current but not baseline)
    for nodeid in current_nodeids - baseline_nodeids:
        report.new_tests.append({
            "nodeid": nodeid,
            "name": current_tests[nodeid].get("name", ""),
            "outcome": current_tests[nodeid].get("outcome", "unknown"),
        })

    # Find removed tests (in baseline but not current)
    for nodeid in baseline_nodeids - current_nodeids:
        report.removed_tests.append({
            "nodeid": nodeid,
            "name": baseline_tests[nodeid].get("name", ""),
            "outcome": baseline_tests[nodeid].get("outcome", "unknown"),
        })

    # Generate summary
    baseline_summary = baseline.get("summary", {})
    current_summary = current.get("summary", {})

    report.summary = {
        "baseline": {
            "total": baseline_summary.get("total", 0),
            "passed": baseline_summary.get("passed", 0),
            "failed": baseline_summary.get("failed", 0),
        },
        "current": {
            "total": current_summary.get("total", 0),
            "passed": current_summary.get("passed", 0),
            "failed": current_summary.get("failed", 0),
        },
        "delta": {
            "total": current_summary.get("total", 0) - baseline_summary.get("total", 0),
            "passed": current_summary.get("passed", 0) - baseline_summary.get("passed", 0),
            "failed": current_summary.get("failed", 0) - baseline_summary.get("failed", 0),
        },
        "new_failures": len(report.new_failures),
        "fixed_tests": len(report.fixed_tests),
        "new_tests": len(report.new_tests),
        "removed_tests": len(report.removed_tests),
    }

    return report


def print_report(report: RegressionReport) -> None:
    """Print regression report to console."""
    status_icon = "❌" if report.has_regressions else "✅"
    status = "REGRESSIONS DETECTED" if report.has_regressions else "NO REGRESSIONS"

    print(f"\n{status_icon} Regression Analysis: {status}")
    print("=" * 60)

    print(f"\nComparing: {report.baseline_run_id} → {report.current_run_id}")

    # Summary stats
    s = report.summary
    print(f"\nTest Count Changes:")
    print(f"  Baseline: {s['baseline']['total']} total, {s['baseline']['passed']} passed, {s['baseline']['failed']} failed")
    print(f"  Current:  {s['current']['total']} total, {s['current']['passed']} passed, {s['current']['failed']} failed")
    print(f"  Delta:    {s['delta']['total']:+d} total, {s['delta']['passed']:+d} passed, {s['delta']['failed']:+d} failed")

    # New failures (regressions)
    if report.new_failures:
        print(f"\n❌ New Failures ({len(report.new_failures)}):")
        for test in report.new_failures[:10]:
            print(f"  - {test['nodeid']}")
            print(f"    Was: {test['baseline_outcome']} → Now: {test['current_outcome']}")
        if len(report.new_failures) > 10:
            print(f"  ... and {len(report.new_failures) - 10} more")

    # Fixed tests
    if report.fixed_tests:
        print(f"\n✅ Fixed Tests ({len(report.fixed_tests)}):")
        for test in report.fixed_tests[:10]:
            print(f"  - {test['nodeid']}")
        if len(report.fixed_tests) > 10:
            print(f"  ... and {len(report.fixed_tests) - 10} more")

    # New tests
    if report.new_tests:
        print(f"\n📝 New Tests ({len(report.new_tests)}):")
        for test in report.new_tests[:5]:
            outcome_icon = "✅" if test["outcome"] == "passed" else "❌"
            print(f"  {outcome_icon} {test['nodeid']}")
        if len(report.new_tests) > 5:
            print(f"  ... and {len(report.new_tests) - 5} more")

    # Removed tests
    if report.removed_tests:
        print(f"\n🗑️  Removed Tests ({len(report.removed_tests)}):")
        for test in report.removed_tests[:5]:
            print(f"  - {test['nodeid']}")
        if len(report.removed_tests) > 5:
            print(f"  ... and {len(report.removed_tests) - 5} more")

    print()


def report_to_dict(report: RegressionReport) -> Dict:
    """Convert report to dictionary for JSON output."""
    return {
        "baseline_run_id": report.baseline_run_id,
        "current_run_id": report.current_run_id,
        "baseline_file": report.baseline_file,
        "current_file": report.current_file,
        "has_regressions": report.has_regressions,
        "new_failures": report.new_failures,
        "fixed_tests": report.fixed_tests,
        "new_tests": report.new_tests,
        "removed_tests": report.removed_tests,
        "summary": report.summary,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compare test results and detect regressions"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Two result files to compare (baseline current)",
    )
    parser.add_argument(
        "--latest",
        type=Path,
        help="Compare two most recent results in directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    # Determine files to compare
    if args.latest:
        baseline_path, current_path = find_latest_results(args.latest)
        if not baseline_path or not current_path:
            return 1
    elif len(args.files) == 2:
        baseline_path = Path(args.files[0])
        current_path = Path(args.files[1])
    else:
        parser.print_help()
        print("\nError: Provide two files or use --latest with a directory")
        return 1

    # Load results
    baseline = load_result(baseline_path)
    current = load_result(current_path)

    if not baseline or not current:
        return 1

    # Compare
    report = compare_results(baseline, current)
    report.baseline_file = str(baseline_path)
    report.current_file = str(current_path)

    # Output
    if args.json:
        print(json.dumps(report_to_dict(report), indent=2))
    else:
        print_report(report)

    return 1 if report.has_regressions else 0


if __name__ == "__main__":
    sys.exit(main())
