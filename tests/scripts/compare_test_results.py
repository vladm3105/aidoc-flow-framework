#!/usr/bin/env python3
"""
Compare test results between runs to detect regressions.

Analyzes two test result files and identifies:
- Regressions (tests that went from pass to fail)
- Fixes (tests that went from fail to pass)
- New tests added
- Tests removed
- Performance changes (>20% duration difference)

Usage:
    python scripts/compare_test_results.py baseline.json current.json
    python scripts/compare_test_results.py --latest tests/results/
    python scripts/compare_test_results.py --threshold 95 baseline.json current.json
    python scripts/compare_test_results.py --json baseline.json current.json

Exit codes:
    0 = No regressions detected
    1 = Regressions found

Reference: ai_dev_flow/10_TSPEC/test_result_schema.yaml
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TestComparison:
    """Result of comparing two test runs."""

    baseline_run_id: str
    current_run_id: str

    # Test changes
    new_tests: List[str] = field(default_factory=list)
    removed_tests: List[str] = field(default_factory=list)

    # Status changes
    regressions: List[Dict] = field(default_factory=list)
    fixes: List[Dict] = field(default_factory=list)
    flaky: List[Dict] = field(default_factory=list)

    # Performance changes
    slower_tests: List[Dict] = field(default_factory=list)
    faster_tests: List[Dict] = field(default_factory=list)

    # Summary
    regression_count: int = 0
    pass_rate_change: float = 0.0
    total_duration_change: float = 0.0
    baseline_pass_rate: float = 0.0
    current_pass_rate: float = 0.0


def load_results(path: Path) -> Dict:
    """Load test results from JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")
    return json.loads(path.read_text())


def find_latest_results(results_dir: Path, test_type: str = "all") -> List[Path]:
    """Find the two most recent result files."""
    pattern = f"results_{test_type}_*.json" if test_type else "results_*.json"
    files = sorted(results_dir.glob(pattern), key=lambda p: p.stat().st_mtime)

    if len(files) < 2:
        raise ValueError(f"Need at least 2 result files to compare, found {len(files)}")

    return files[-2:]  # Return baseline (second-to-last) and current (last)


def compare_runs(baseline: Dict, current: Dict) -> TestComparison:
    """
    Compare two test runs and identify changes.

    Args:
        baseline: Previous test run results
        current: Current test run results

    Returns:
        TestComparison with detailed analysis
    """
    # Build test lookup maps
    baseline_tests = {t["nodeid"]: t for t in baseline.get("tests", [])}
    current_tests = {t["nodeid"]: t for t in current.get("tests", [])}

    comparison = TestComparison(
        baseline_run_id=baseline.get("run_id", "unknown"),
        current_run_id=current.get("run_id", "unknown"),
    )

    # Find new and removed tests
    baseline_ids = set(baseline_tests.keys())
    current_ids = set(current_tests.keys())

    comparison.new_tests = sorted(current_ids - baseline_ids)
    comparison.removed_tests = sorted(baseline_ids - current_ids)

    # Compare common tests
    common_tests = baseline_ids & current_ids

    for test_id in common_tests:
        baseline_test = baseline_tests[test_id]
        current_test = current_tests[test_id]

        baseline_outcome = baseline_test.get("outcome", "unknown")
        current_outcome = current_test.get("outcome", "unknown")

        # Detect regressions (pass -> fail)
        if baseline_outcome == "passed" and current_outcome == "failed":
            comparison.regressions.append(
                {
                    "test_id": test_id,
                    "name": current_test.get("name", ""),
                    "baseline_outcome": baseline_outcome,
                    "current_outcome": current_outcome,
                }
            )
            comparison.regression_count += 1

        # Detect fixes (fail -> pass)
        elif baseline_outcome == "failed" and current_outcome == "passed":
            comparison.fixes.append(
                {
                    "test_id": test_id,
                    "name": current_test.get("name", ""),
                    "baseline_outcome": baseline_outcome,
                    "current_outcome": current_outcome,
                }
            )

        # Detect flaky tests (different results each time)
        elif baseline_outcome != current_outcome and current_outcome not in ["passed", "failed"]:
            comparison.flaky.append(
                {
                    "test_id": test_id,
                    "name": current_test.get("name", ""),
                    "baseline_outcome": baseline_outcome,
                    "current_outcome": current_outcome,
                }
            )

        # Detect performance changes (>20% difference)
        baseline_duration = baseline_test.get("duration", 0)
        current_duration = current_test.get("duration", 0)

        if baseline_duration > 0.1:  # Only check tests that take measurable time
            change_pct = (current_duration - baseline_duration) / baseline_duration * 100

            if change_pct > 20:
                comparison.slower_tests.append(
                    {
                        "test_id": test_id,
                        "name": current_test.get("name", ""),
                        "baseline_duration": round(baseline_duration, 3),
                        "current_duration": round(current_duration, 3),
                        "change_percent": round(change_pct, 1),
                    }
                )
            elif change_pct < -20:
                comparison.faster_tests.append(
                    {
                        "test_id": test_id,
                        "name": current_test.get("name", ""),
                        "baseline_duration": round(baseline_duration, 3),
                        "current_duration": round(current_duration, 3),
                        "change_percent": round(change_pct, 1),
                    }
                )

    # Calculate pass rate changes
    baseline_tests_list = baseline.get("tests", [])
    current_tests_list = current.get("tests", [])

    baseline_passed = sum(1 for t in baseline_tests_list if t.get("outcome") == "passed")
    current_passed = sum(1 for t in current_tests_list if t.get("outcome") == "passed")

    baseline_total = len(baseline_tests_list)
    current_total = len(current_tests_list)

    comparison.baseline_pass_rate = (baseline_passed / baseline_total * 100) if baseline_total > 0 else 0
    comparison.current_pass_rate = (current_passed / current_total * 100) if current_total > 0 else 0
    comparison.pass_rate_change = comparison.current_pass_rate - comparison.baseline_pass_rate

    # Calculate duration changes
    baseline_duration = baseline.get("summary", {}).get("duration_seconds", 0)
    current_duration = current.get("summary", {}).get("duration_seconds", 0)
    comparison.total_duration_change = current_duration - baseline_duration

    return comparison


def generate_report(comparison: TestComparison) -> str:
    """Generate human-readable comparison report in markdown format."""
    lines = [
        "# Test Comparison Report",
        "",
        f"**Baseline Run**: {comparison.baseline_run_id}",
        f"**Current Run**: {comparison.current_run_id}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Regressions | {comparison.regression_count} |",
        f"| Fixes | {len(comparison.fixes)} |",
        f"| New Tests | {len(comparison.new_tests)} |",
        f"| Removed Tests | {len(comparison.removed_tests)} |",
        f"| Baseline Pass Rate | {comparison.baseline_pass_rate:.1f}% |",
        f"| Current Pass Rate | {comparison.current_pass_rate:.1f}% |",
        f"| Pass Rate Change | {comparison.pass_rate_change:+.1f}% |",
        f"| Duration Change | {comparison.total_duration_change:+.2f}s |",
        "",
    ]

    # Regressions section (critical)
    if comparison.regressions:
        lines.extend(
            [
                "## Regressions (REQUIRES ATTENTION)",
                "",
                "These tests previously passed but now fail:",
                "",
                "| Test | Previous | Current |",
                "|------|----------|---------|",
            ]
        )
        for reg in comparison.regressions:
            name = reg.get("name", reg["test_id"].split("::")[-1])
            lines.append(
                f"| `{name}` | {reg['baseline_outcome']} | {reg['current_outcome']} |"
            )
        lines.append("")

    # Fixes section
    if comparison.fixes:
        lines.extend(
            [
                "## Fixes",
                "",
                "These tests previously failed but now pass:",
                "",
                "| Test | Previous | Current |",
                "|------|----------|---------|",
            ]
        )
        for fix in comparison.fixes:
            name = fix.get("name", fix["test_id"].split("::")[-1])
            lines.append(
                f"| `{name}` | {fix['baseline_outcome']} | {fix['current_outcome']} |"
            )
        lines.append("")

    # New tests
    if comparison.new_tests:
        lines.extend(
            [
                "## New Tests",
                "",
            ]
        )
        for test_id in comparison.new_tests[:10]:  # Limit to first 10
            lines.append(f"- `{test_id}`")
        if len(comparison.new_tests) > 10:
            lines.append(f"- ... and {len(comparison.new_tests) - 10} more")
        lines.append("")

    # Removed tests
    if comparison.removed_tests:
        lines.extend(
            [
                "## Removed Tests",
                "",
            ]
        )
        for test_id in comparison.removed_tests[:10]:
            lines.append(f"- `{test_id}`")
        if len(comparison.removed_tests) > 10:
            lines.append(f"- ... and {len(comparison.removed_tests) - 10} more")
        lines.append("")

    # Performance changes
    if comparison.slower_tests:
        lines.extend(
            [
                "## Performance Regressions",
                "",
                "Tests that are >20% slower:",
                "",
                "| Test | Baseline | Current | Change |",
                "|------|----------|---------|--------|",
            ]
        )
        for test in sorted(comparison.slower_tests, key=lambda x: -x["change_percent"])[:10]:
            name = test.get("name", test["test_id"].split("::")[-1])
            lines.append(
                f"| `{name}` | {test['baseline_duration']:.3f}s | "
                f"{test['current_duration']:.3f}s | +{test['change_percent']:.0f}% |"
            )
        lines.append("")

    if comparison.faster_tests:
        lines.extend(
            [
                "## Performance Improvements",
                "",
                "Tests that are >20% faster:",
                "",
                "| Test | Baseline | Current | Change |",
                "|------|----------|---------|--------|",
            ]
        )
        for test in sorted(comparison.faster_tests, key=lambda x: x["change_percent"])[:10]:
            name = test.get("name", test["test_id"].split("::")[-1])
            lines.append(
                f"| `{name}` | {test['baseline_duration']:.3f}s | "
                f"{test['current_duration']:.3f}s | {test['change_percent']:.0f}% |"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Compare test results between runs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/compare_test_results.py baseline.json current.json
    python scripts/compare_test_results.py --latest tests/results/
    python scripts/compare_test_results.py --json baseline.json current.json
    python scripts/compare_test_results.py --output report.md baseline.json current.json
        """,
    )

    parser.add_argument(
        "baseline",
        type=Path,
        nargs="?",
        help="Baseline results file",
    )
    parser.add_argument(
        "current",
        type=Path,
        nargs="?",
        help="Current results file",
    )
    parser.add_argument(
        "--latest",
        type=Path,
        metavar="DIR",
        help="Use latest two result files from directory",
    )
    parser.add_argument(
        "--type",
        choices=["utest", "itest", "stest", "ftest", "all"],
        default="all",
        help="Test type filter when using --latest",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=100.0,
        help="Minimum pass rate to succeed (default: 100)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Save report to file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of markdown",
    )

    args = parser.parse_args()

    # Determine which files to compare
    if args.latest:
        try:
            baseline_path, current_path = find_latest_results(args.latest, args.type)
            print(f"Comparing: {baseline_path.name} vs {current_path.name}")
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    elif args.baseline and args.current:
        baseline_path = args.baseline
        current_path = args.current
    else:
        parser.print_help()
        print("\nError: Provide either --latest DIR or BASELINE CURRENT arguments")
        return 1

    # Load and compare
    try:
        baseline = load_results(baseline_path)
        current = load_results(current_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return 1

    comparison = compare_runs(baseline, current)

    # Output results
    if args.json:
        output = json.dumps(
            {
                "baseline_run_id": comparison.baseline_run_id,
                "current_run_id": comparison.current_run_id,
                "regression_count": comparison.regression_count,
                "regressions": comparison.regressions,
                "fixes": comparison.fixes,
                "new_tests": comparison.new_tests,
                "removed_tests": comparison.removed_tests,
                "slower_tests": comparison.slower_tests,
                "faster_tests": comparison.faster_tests,
                "pass_rate_change": comparison.pass_rate_change,
                "baseline_pass_rate": comparison.baseline_pass_rate,
                "current_pass_rate": comparison.current_pass_rate,
            },
            indent=2,
        )
        print(output)
    else:
        report = generate_report(comparison)
        print(report)

    # Save output if requested
    if args.output:
        if args.json:
            args.output.write_text(output)
        else:
            args.output.write_text(report)
        print(f"\nReport saved to: {args.output}")

    # Exit with error if regressions found
    if comparison.regression_count > 0:
        print(f"\n{comparison.regression_count} regression(s) detected!")
        return 1

    # Check pass rate threshold
    if comparison.current_pass_rate < args.threshold:
        print(
            f"\nPass rate {comparison.current_pass_rate:.1f}% "
            f"is below threshold {args.threshold}%"
        )
        return 1

    print("\nNo regressions detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
