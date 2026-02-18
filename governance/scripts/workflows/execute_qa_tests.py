#!/usr/bin/env python3
"""Execute comprehensive QA tests on staging environment."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# === TSPEC Registry Integration ===

def load_tspec_registry(path: Path = Path("docs/10_TSPEC/test_registry.yaml")) -> dict:
    """Load TSPEC test registry for result mapping."""
    if not YAML_AVAILABLE:
        return {"tests": []}
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {"tests": []}
    return {"tests": []}


def map_results_to_tspec(pytest_results: dict, registry: dict) -> list:
    """Map pytest results to TSPEC entries for traceability."""
    registry_map = {t["nodeid"]: t for t in registry.get("tests", [])}
    mapped = []
    for test in pytest_results.get("tests", []):
        tspec_entry = registry_map.get(test.get("nodeid", ""))
        if tspec_entry:
            mapped.append({
                "tspec_id": tspec_entry.get("tspec_id"),
                "bdd_scenario": tspec_entry.get("bdd_scenario"),
                "outcome": test.get("outcome"),
                "duration": test.get("duration", 0),
                "upstream_refs": tspec_entry.get("upstream_refs", [])
            })
    return mapped


def generate_traceability_report(mapped_results: list) -> str:
    """Generate markdown traceability report for QA issue."""
    if not mapped_results:
        return ""
    lines = ["## Test Traceability Report", "", "| TSPEC ID | Outcome | Duration | Upstream |"]
    lines.append("|----------|---------|----------|----------|")
    for r in mapped_results:
        refs = ", ".join(r.get("upstream_refs", [])[:2])
        duration = r.get("duration", 0)
        lines.append(f"| {r.get('tspec_id', 'N/A')} | {r.get('outcome', 'unknown')} | {duration:.2f}s | {refs} |")
    return "\n".join(lines)


def run_tests(
    test_type: str,
    staging_url: str,
    timeout_minutes: int,
    phase: int,
) -> dict:
    """Run a specific type of test."""
    result = {
        "type": test_type,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "duration_seconds": 0,
    }

    env = os.environ.copy()
    env["STAGING_URL"] = staging_url
    env["TEST_PHASE"] = str(phase)

    test_paths = {
        "unit": "tests/unit/",
        "integration": "tests/integration/",
        "e2e": "tests/e2e/",
        "acceptance": f"tests/acceptance/phase{phase}/",
        "smoke": "tests/acceptance/smoke/",
    }

    test_path = test_paths.get(test_type, "tests/")

    if not Path(test_path).exists():
        result["skipped"] = 1
        result["errors"].append(f"Test path {test_path} does not exist")
        return result

    cmd = [
        "python", "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        f"--timeout={timeout_minutes * 60}",
        "--json-report",
        "--json-report-file=/tmp/pytest_report.json",
    ]

    start_time = datetime.now()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_minutes * 60,
            env=env,
        )
        result["duration_seconds"] = (datetime.now() - start_time).total_seconds()

        # Parse pytest JSON report
        report_file = Path("/tmp/pytest_report.json")
        if report_file.exists():
            try:
                report = json.loads(report_file.read_text())
            except json.JSONDecodeError:
                report = {"summary": {}, "tests": []}
            summary = report.get("summary", {})
            result["passed"] = summary.get("passed", 0)
            result["failed"] = summary.get("failed", 0)
            result["skipped"] = summary.get("skipped", 0)

            # Extract failure details
            for test in report.get("tests", []):
                if test.get("outcome") == "failed":
                    error = {
                        "test_file": test.get("nodeid", "").split("::")[0],
                        "test_name": test.get("nodeid", "").split("::")[-1],
                        "error_type": "AssertionError",
                        "error_message": test.get("call", {}).get("longrepr", "")[:500],
                        "stack_trace": test.get("call", {}).get("longrepr", "")[:2000],
                    }
                    result["errors"].append(error)
        else:
            # Fallback: parse stdout
            if proc.returncode == 0:
                result["passed"] = 1
            else:
                result["failed"] = 1
                result["errors"].append({
                    "test_file": test_path,
                    "test_name": "test_suite",
                    "error_type": "TestSuiteError",
                    "error_message": proc.stderr[:500] if proc.stderr else proc.stdout[:500],
                    "stack_trace": proc.stderr[:2000] if proc.stderr else proc.stdout[:2000],
                })

    except subprocess.TimeoutExpired:
        result["failed"] = 1
        result["errors"].append({
            "test_file": test_path,
            "test_name": "test_suite",
            "error_type": "TimeoutError",
            "error_message": f"Test suite timed out after {timeout_minutes} minutes",
            "stack_trace": "",
        })

    except Exception as e:
        result["failed"] = 1
        result["errors"].append({
            "test_file": test_path,
            "test_name": "test_suite",
            "error_type": type(e).__name__,
            "error_message": str(e)[:500],
            "stack_trace": "",
        })

    return result


def main():
    parser = argparse.ArgumentParser(description="Execute QA tests")
    parser.add_argument("--phase", required=True, type=int, help="Phase number")
    parser.add_argument(
        "--qa-issues", required=True, help="Comma-separated QA issue numbers"
    )
    parser.add_argument("--staging-url", required=True, help="Staging environment URL")
    parser.add_argument(
        "--timeout-minutes", type=int, default=120, help="Timeout in minutes"
    )
    parser.add_argument(
        "--output-file", required=True, type=Path, help="Output JSON file"
    )
    args = parser.parse_args()

    qa_issues = [int(i.strip()) for i in args.qa_issues.split(",") if i.strip()]

    # Run all test types
    test_types = ["smoke", "unit", "integration", "acceptance"]
    all_results = {}
    all_errors = []

    for test_type in test_types:
        print(f"Running {test_type} tests...")
        result = run_tests(
            test_type,
            args.staging_url,
            args.timeout_minutes // len(test_types),
            args.phase,
        )
        all_results[test_type] = result
        all_errors.extend(result["errors"])

    # Calculate totals
    total_passed = sum(r["passed"] for r in all_results.values())
    total_failed = sum(r["failed"] for r in all_results.values())
    total_skipped = sum(r["skipped"] for r in all_results.values())

    all_passed = total_failed == 0

    # Assign results to QA issues (simplified: all issues get same result)
    issue_results = {}
    passed_issues = []
    failed_issues = []

    for issue in qa_issues:
        issue_str = str(issue)
        if all_passed:
            passed_issues.append(issue_str)
            issue_results[issue_str] = {
                "status": "passed",
                "summary": f"All {total_passed} tests passed",
                "failures": "",
            }
        else:
            failed_issues.append(issue_str)
            failures_summary = "\n".join([
                f"- {e['test_file']}::{e['test_name']}: {e['error_message'][:100]}"
                for e in all_errors[:5]
            ])
            issue_results[issue_str] = {
                "status": "failed",
                "summary": f"Passed: {total_passed}, Failed: {total_failed}",
                "failures": failures_summary,
            }

    # Load TSPEC registry for traceability
    tspec_registry = load_tspec_registry()

    # Collect all test nodeids for TSPEC mapping
    all_tests = []
    for test_type, result in all_results.items():
        # Try to load pytest JSON report if available
        report_file = Path("/tmp/pytest_report.json")
        if report_file.exists():
            try:
                report = json.loads(report_file.read_text())
                all_tests.extend(report.get("tests", []))
            except json.JSONDecodeError:
                pass

    # Map results to TSPEC entries
    tspec_mapped = map_results_to_tspec({"tests": all_tests}, tspec_registry)
    tspec_report = generate_traceability_report(tspec_mapped)

    output = {
        "phase": args.phase,
        "all_passed": all_passed,
        "passed_count": len(passed_issues),
        "failed_count": len(failed_issues),
        "passed_issues": passed_issues,
        "failed_issues": failed_issues,
        "issue_results": issue_results,
        "test_results": all_results,
        "errors": all_errors,
        "total": {
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
        },
        "tspec_traceability": {
            "mapped_tests": len(tspec_mapped),
            "report": tspec_report,
        },
        "executed_at": datetime.utcnow().isoformat() + "Z",
    }

    args.output_file.write_text(json.dumps(output, indent=2))

    print(f"\nTest Summary:")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    print(f"  Skipped: {total_skipped}")
    print(f"  All Passed: {all_passed}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
