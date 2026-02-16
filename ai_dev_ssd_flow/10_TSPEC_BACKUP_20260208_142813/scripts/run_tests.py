#!/usr/bin/env python3
"""
Unified Test Runner for AI Dev Flow.

Runs tests by type (unit, integration, smoke, functional) with optional
coverage reporting and result saving.

Usage:
    python run_tests.py --type utest          # Run unit tests
    python run_tests.py --type itest          # Run integration tests
    python run_tests.py --type stest          # Run smoke tests
    python run_tests.py --type ftest          # Run functional tests
    python run_tests.py --type all            # Run all tests
    python run_tests.py --type utest --save   # Save results for comparison
    python run_tests.py --type all --coverage # Run with coverage
"""

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Paths
SCRIPT_DIR = Path(__file__).parent
TSPEC_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = TSPEC_DIR.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
RESULTS_DIR = TESTS_DIR / "results"

# Test type mappings
TEST_TYPE_MAP = {
    "utest": {"code": 40, "dir": "unit", "marker": "unit"},
    "itest": {"code": 41, "dir": "integration", "marker": "integration"},
    "stest": {"code": 42, "dir": "smoke", "marker": "smoke"},
    "ftest": {"code": 43, "dir": "functional", "marker": "functional"},
}


@dataclass
class TestResult:
    """Result of a test run."""

    run_id: str
    started_at: str
    completed_at: str
    test_type: str
    environment: str
    summary: Dict
    tests: List[Dict] = field(default_factory=list)
    git_commit: Optional[str] = None
    git_branch: Optional[str] = None
    triggered_by: str = "manual"
    coverage_percent: Optional[float] = None
    metadata: Dict = field(default_factory=dict)


def get_git_info() -> tuple:
    """Get current git commit and branch."""
    commit = None
    branch = None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            commit = result.stdout.strip()

        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
    except FileNotFoundError:
        pass
    return commit, branch


def run_pytest(
    test_type: str,
    coverage: bool = False,
    verbose: bool = False,
) -> tuple:
    """Run pytest for specified test type."""
    config = TEST_TYPE_MAP.get(test_type)
    if not config:
        return None, 1

    test_dir = TESTS_DIR / config["dir"]
    if not test_dir.exists():
        print(f"Warning: Test directory not found: {test_dir}")
        return None, 1

    # Build pytest command
    cmd = ["python", "-m", "pytest", str(test_dir)]

    # Add marker filter
    cmd.extend(["-m", config["marker"]])

    # JSON output for parsing
    json_output = RESULTS_DIR / f"pytest_output_{test_type}.json"
    cmd.extend(["--json-report", f"--json-report-file={json_output}"])

    # Coverage options
    if coverage:
        cmd.extend([
            f"--cov={PROJECT_ROOT / 'src'}",
            "--cov-report=json",
            f"--cov-report=html:{TESTS_DIR / 'coverage_html'}",
        ])

    # Verbose output
    if verbose:
        cmd.append("-v")

    # Run pytest
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)

    # Parse JSON output if available
    output_data = None
    if json_output.exists():
        try:
            output_data = json.loads(json_output.read_text())
        except json.JSONDecodeError:
            pass

    return output_data, result.returncode


def parse_pytest_output(output_data: dict, test_type: str) -> TestResult:
    """Parse pytest JSON output into TestResult."""
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    started_at = datetime.now().isoformat()

    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "duration_seconds": 0.0,
    }

    tests = []

    if output_data:
        # Parse summary
        summary_data = output_data.get("summary", {})
        summary["total"] = summary_data.get("total", 0)
        summary["passed"] = summary_data.get("passed", 0)
        summary["failed"] = summary_data.get("failed", 0)
        summary["skipped"] = summary_data.get("skipped", 0)
        summary["errors"] = summary_data.get("error", 0)
        summary["duration_seconds"] = output_data.get("duration", 0.0)

        # Parse individual tests
        for test in output_data.get("tests", []):
            tests.append({
                "name": test.get("name", ""),
                "nodeid": test.get("nodeid", ""),
                "outcome": test.get("outcome", "unknown"),
                "duration": test.get("duration", 0.0),
            })

    git_commit, git_branch = get_git_info()

    return TestResult(
        run_id=run_id,
        started_at=started_at,
        completed_at=datetime.now().isoformat(),
        test_type=test_type.upper(),
        environment="test",
        summary=summary,
        tests=tests,
        git_commit=git_commit,
        git_branch=git_branch,
        triggered_by="manual",
        metadata={
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
        },
    )


def save_result(result: TestResult, test_type: str) -> Path:
    """Save test result to JSON file."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{test_type}_{result.run_id}.json"
    filepath = RESULTS_DIR / filename

    filepath.write_text(json.dumps(asdict(result), indent=2))
    print(f"Results saved to: {filepath}")
    return filepath


def print_summary(result: TestResult) -> None:
    """Print test result summary."""
    s = result.summary
    status = "PASS" if s["failed"] == 0 and s["errors"] == 0 else "FAIL"
    status_icon = "✅" if status == "PASS" else "❌"

    print(f"\n{status_icon} {result.test_type} Test Results: {status}")
    print(f"  Total:   {s['total']}")
    print(f"  Passed:  {s['passed']}")
    print(f"  Failed:  {s['failed']}")
    print(f"  Skipped: {s['skipped']}")
    print(f"  Errors:  {s['errors']}")
    print(f"  Duration: {s['duration_seconds']:.2f}s")


def main():
    parser = argparse.ArgumentParser(description="Unified test runner for AI Dev Flow")
    parser.add_argument(
        "--type",
        required=True,
        choices=["utest", "itest", "stest", "ftest", "all"],
        help="Test type to run",
    )
    parser.add_argument("--save", action="store_true", help="Save results for comparison")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Determine test types to run
    if args.type == "all":
        test_types = ["utest", "itest", "stest", "ftest"]
    else:
        test_types = [args.type]

    all_passed = True
    results = []

    for test_type in test_types:
        print(f"\n{'='*60}")
        print(f"Running {test_type.upper()} tests...")
        print("=" * 60)

        output_data, returncode = run_pytest(
            test_type,
            coverage=args.coverage,
            verbose=args.verbose,
        )

        if output_data is None:
            print(f"Warning: Could not parse results for {test_type}")
            # Create minimal result
            result = TestResult(
                run_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                started_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat(),
                test_type=test_type.upper(),
                environment="test",
                summary={
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "errors": 1 if returncode != 0 else 0,
                    "duration_seconds": 0.0,
                },
            )
        else:
            result = parse_pytest_output(output_data, test_type)

        print_summary(result)

        if args.save:
            save_result(result, test_type)

        results.append(result)

        if returncode != 0:
            all_passed = False

    # Final summary for 'all'
    if args.type == "all":
        print(f"\n{'='*60}")
        print("Overall Summary")
        print("=" * 60)
        total_passed = sum(r.summary["passed"] for r in results)
        total_failed = sum(r.summary["failed"] for r in results)
        total_tests = sum(r.summary["total"] for r in results)
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {total_passed}")
        print(f"  Failed: {total_failed}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
