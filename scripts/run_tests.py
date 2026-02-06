#!/usr/bin/env python3
"""
Unified test runner for AI Dev Flow.

Executes tests by type (UTEST, ITEST, STEST, FTEST) with consistent
configuration and result collection. Supports saving results for
comparison and regression detection.

Usage:
    python scripts/run_tests.py --type utest           # Run unit tests
    python scripts/run_tests.py --type itest           # Run integration tests
    python scripts/run_tests.py --type stest           # Run smoke tests
    python scripts/run_tests.py --type ftest           # Run functional tests
    python scripts/run_tests.py --type all             # Run all tests
    python scripts/run_tests.py --type utest --save    # Run and save results
    python scripts/run_tests.py --type all --coverage  # Run with coverage
    python scripts/run_tests.py --compare baseline.json current.json

Reference: ai_dev_flow/10_TSPEC/, TESTING_STRATEGY_TDD.md
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TESTS_DIR = PROJECT_ROOT / "tests"
RESULTS_DIR = TESTS_DIR / "results"

# Test type configurations
TEST_TYPES = {
    "utest": {
        "path": "tests/unit",
        "marker": "utest",
        "timeout": 120,
        "description": "Unit tests (fast, isolated)",
    },
    "itest": {
        "path": "tests/integration",
        "marker": "itest",
        "timeout": 600,
        "description": "Integration tests (requires services)",
    },
    "stest": {
        "path": "tests/smoke",
        "marker": "stest",
        "timeout": 300,
        "description": "Smoke tests (deployment health)",
    },
    "ftest": {
        "path": "tests/functional",
        "marker": "ftest",
        "timeout": 900,
        "description": "Functional tests (end-to-end)",
    },
}


def get_git_info() -> Dict[str, str]:
    """Get current git commit and branch information."""
    info = {"git_commit": "", "git_branch": ""}

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            info["git_commit"] = result.stdout.strip()

        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            info["git_branch"] = result.stdout.strip()
    except FileNotFoundError:
        pass

    return info


def run_tests(
    test_type: str,
    save_results: bool = False,
    coverage: bool = False,
    verbose: bool = False,
    extra_args: Optional[List[str]] = None,
) -> Dict:
    """
    Run tests of specified type and return results.

    Args:
        test_type: One of 'utest', 'itest', 'stest', 'ftest', or 'all'
        save_results: Save results to JSON file
        coverage: Enable coverage collection
        verbose: Enable verbose output
        extra_args: Additional pytest arguments

    Returns:
        Dictionary containing test results and metadata
    """
    results = {
        "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "started_at": datetime.now().isoformat(),
        "test_type": test_type.upper(),
        "environment": "test",
        "triggered_by": "manual",
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration_seconds": 0.0,
        },
        "tests": [],
    }

    # Add git info
    results.update(get_git_info())

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if test_type == "all":
        cmd.append(str(TESTS_DIR))
    else:
        config = TEST_TYPES.get(test_type)
        if not config:
            print(f"Error: Unknown test type '{test_type}'")
            return results

        test_path = PROJECT_ROOT / config["path"]
        if test_path.exists():
            cmd.append(str(test_path))
        else:
            # Fall back to marker-based selection
            cmd.extend(["-m", config["marker"]])
            cmd.append(str(TESTS_DIR))

        cmd.extend(["--timeout", str(config["timeout"])])

    # Add standard options
    cmd.extend(["-v", "--tb=short"])

    # Add JSON report output
    json_report = RESULTS_DIR / f"pytest_report_{test_type}_{results['run_id']}.json"
    cmd.extend(["--json-report", f"--json-report-file={json_report}"])

    # Add coverage if requested
    if coverage:
        cmd.extend(
            [
                "--cov=src",
                "--cov-report=term-missing",
                f"--cov-report=json:{RESULTS_DIR}/coverage_{results['run_id']}.json",
            ]
        )

    if verbose:
        cmd.append("-vv")

    if extra_args:
        cmd.extend(extra_args)

    # Ensure results directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Print header
    print(f"\n{'=' * 60}")
    print(f"Running {test_type.upper()} tests")
    if test_type in TEST_TYPES:
        print(f"  {TEST_TYPES[test_type]['description']}")
    print(f"{'=' * 60}\n")

    # Run pytest
    start_time = datetime.now()

    try:
        process = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,
        )
        exit_code = process.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Install with: pip install pytest")
        return results

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    results["completed_at"] = end_time.isoformat()
    results["summary"]["duration_seconds"] = duration

    # Parse JSON report if available
    if json_report.exists():
        try:
            report_data = json.loads(json_report.read_text())
            summary = report_data.get("summary", {})

            results["summary"]["total"] = summary.get("total", 0)
            results["summary"]["passed"] = summary.get("passed", 0)
            results["summary"]["failed"] = summary.get("failed", 0)
            results["summary"]["skipped"] = summary.get("skipped", 0)
            results["summary"]["errors"] = summary.get("error", 0)

            # Extract individual test results
            for test in report_data.get("tests", []):
                results["tests"].append(
                    {
                        "name": test.get("name", ""),
                        "nodeid": test.get("nodeid", ""),
                        "outcome": test.get("outcome", ""),
                        "duration": test.get("call", {}).get("duration", 0),
                    }
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not parse pytest JSON report: {e}")

    # Print summary
    print(f"\n{'=' * 60}")
    print("Test Summary")
    print(f"{'=' * 60}")
    print(f"  Total:   {results['summary']['total']}")
    print(f"  Passed:  {results['summary']['passed']}")
    print(f"  Failed:  {results['summary']['failed']}")
    print(f"  Skipped: {results['summary']['skipped']}")
    print(f"  Errors:  {results['summary']['errors']}")
    print(f"  Duration: {duration:.2f}s")
    print(f"{'=' * 60}\n")

    # Save results
    if save_results:
        result_file = RESULTS_DIR / f"results_{test_type}_{results['run_id']}.json"
        result_file.write_text(json.dumps(results, indent=2))
        print(f"Results saved to: {result_file}")

        # Update latest symlink
        latest_file = RESULTS_DIR / f"latest_{test_type}.json"
        if latest_file.exists():
            latest_file.unlink()
        result_file_rel = result_file.name
        # Write results to latest file directly instead of symlink (Windows compatible)
        latest_file.write_text(json.dumps(results, indent=2))
        print(f"Latest results: {latest_file}")

    return results


def run_all_tests(
    save_results: bool = False,
    coverage: bool = False,
) -> Dict[str, Dict]:
    """Run all test types and aggregate results."""
    all_results = {}

    for test_type in TEST_TYPES:
        test_path = PROJECT_ROOT / TEST_TYPES[test_type]["path"]
        if test_path.exists() and any(test_path.glob("test_*.py")):
            all_results[test_type] = run_tests(
                test_type,
                save_results=save_results,
                coverage=coverage,
            )
        else:
            print(f"Skipping {test_type}: no tests found in {test_path}")

    return all_results


def compare_results(baseline_path: Path, current_path: Path) -> int:
    """
    Compare two result files for regressions.

    Returns exit code: 0 = no regressions, 1 = regressions found
    """
    from scripts.compare_test_results import compare_runs, generate_report, load_results

    baseline = load_results(baseline_path)
    current = load_results(current_path)
    comparison = compare_runs(baseline, current)

    report = generate_report(comparison)
    print(report)

    return 1 if comparison.regression_count > 0 else 0


def main():
    parser = argparse.ArgumentParser(
        description="Unified test runner for AI Dev Flow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_tests.py --type utest           # Run unit tests
    python scripts/run_tests.py --type all --save      # Run all tests, save results
    python scripts/run_tests.py --type itest --coverage # Run with coverage
    python scripts/run_tests.py --compare baseline.json current.json
        """,
    )

    parser.add_argument(
        "--type",
        choices=["utest", "itest", "stest", "ftest", "all"],
        default="all",
        help="Type of tests to run (default: all)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to JSON file",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Enable coverage collection",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("BASELINE", "CURRENT"),
        help="Compare two result files",
    )
    parser.add_argument(
        "--output",
        default="tests/results",
        help="Output directory for results (default: tests/results)",
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Additional arguments to pass to pytest",
    )

    args = parser.parse_args()

    # Update results directory if specified
    global RESULTS_DIR
    RESULTS_DIR = Path(args.output)

    # Compare mode
    if args.compare:
        baseline = Path(args.compare[0])
        current = Path(args.compare[1])
        if not baseline.exists():
            print(f"Error: Baseline file not found: {baseline}")
            return 1
        if not current.exists():
            print(f"Error: Current file not found: {current}")
            return 1
        return compare_results(baseline, current)

    # Run tests
    results = run_tests(
        args.type,
        save_results=args.save,
        coverage=args.coverage,
        verbose=args.verbose,
        extra_args=args.pytest_args if args.pytest_args else None,
    )

    # Determine exit code
    if results["summary"]["failed"] > 0 or results["summary"]["errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
