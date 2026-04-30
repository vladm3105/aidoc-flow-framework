#!/usr/bin/env python3
"""Execute QA tests and map results to TDD registry entries."""

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


def load_tdd_registry(path: Path = Path("docs/07_TDD/test_registry.yaml")) -> dict:
    """Load TDD test registry for result mapping."""
    if not YAML_AVAILABLE:
        return {"tests": []}
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f) or {"tests": []}
    return {"tests": []}


def map_results_to_tdd(pytest_results: dict, registry: dict) -> list:
    """Map pytest results to TDD entries for traceability."""
    registry_map = {t.get("nodeid", ""): t for t in registry.get("tests", [])}
    mapped = []
    for test in pytest_results.get("tests", []):
        entry = registry_map.get(test.get("nodeid", ""))
        if entry:
            mapped.append({
                "tdd_id": entry.get("tdd_id"),
                "bdd_scenario": entry.get("bdd_scenario"),
                "outcome": test.get("outcome"),
                "duration": test.get("duration", 0),
                "upstream_refs": entry.get("upstream_refs", []),
            })
    return mapped


def generate_traceability_report(mapped_results: list) -> str:
    if not mapped_results:
        return ""
    lines = ["## Test Traceability Report", "", "| TDD ID | Outcome | Duration | Upstream |"]
    lines.append("|--------|---------|----------|----------|")
    for r in mapped_results:
        refs = ", ".join(r.get("upstream_refs", [])[:2])
        lines.append(f"| {r.get('tdd_id', 'N/A')} | {r.get('outcome', 'unknown')} | {r.get('duration', 0):.2f}s | {refs} |")
    return "\n".join(lines)


def run_tests(test_path: str, timeout_seconds: int, env: dict) -> dict:
    result = {"passed": 0, "failed": 0, "skipped": 0, "errors": [], "tests": []}
    if not Path(test_path).exists():
        result["skipped"] = 1
        return result

    cmd = [
        "python", "-m", "pytest", test_path, "-v", "--tb=short",
        f"--timeout={timeout_seconds}", "--json-report",
        "--json-report-file=/tmp/pytest_report.json",
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds, env=env)
    except subprocess.TimeoutExpired:
        result["failed"] = 1
        result["errors"].append("timeout")
        return result

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
        result["tests"] = report.get("tests", [])
    elif proc.returncode != 0:
        result["failed"] = 1
    else:
        result["passed"] = 1
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute QA tests")
    parser.add_argument("--phase", required=True, type=int)
    parser.add_argument("--qa-issues", required=True)
    parser.add_argument("--staging-url", required=True)
    parser.add_argument("--timeout-minutes", type=int, default=120)
    parser.add_argument("--output-file", required=True, type=Path)
    args = parser.parse_args()

    qa_issues = [i.strip() for i in args.qa_issues.split(",") if i.strip()]
    env = os.environ.copy()
    env["STAGING_URL"] = args.staging_url
    env["TEST_PHASE"] = str(args.phase)

    test_paths = ["tests/acceptance/smoke/", "tests/unit/", "tests/integration/", f"tests/acceptance/phase{args.phase}/"]
    per_suite_timeout = max(60, (args.timeout_minutes * 60) // len(test_paths))

    suite_results = []
    all_tests = []
    for p in test_paths:
        r = run_tests(p, per_suite_timeout, env)
        suite_results.append({"path": p, **r})
        all_tests.extend(r.get("tests", []))

    total_passed = sum(r["passed"] for r in suite_results)
    total_failed = sum(r["failed"] for r in suite_results)
    total_skipped = sum(r["skipped"] for r in suite_results)
    all_passed = total_failed == 0

    registry = load_tdd_registry()
    mapped = map_results_to_tdd({"tests": all_tests}, registry)

    issue_results = {}
    for issue in qa_issues:
        issue_results[issue] = {
            "status": "passed" if all_passed else "failed",
            "summary": f"Passed: {total_passed}, Failed: {total_failed}, Skipped: {total_skipped}",
        }

    output = {
        "phase": args.phase,
        "all_passed": all_passed,
        "issue_results": issue_results,
        "test_results": suite_results,
        "total": {"passed": total_passed, "failed": total_failed, "skipped": total_skipped},
        "tdd_traceability": {"mapped_tests": len(mapped), "report": generate_traceability_report(mapped)},
        "executed_at": datetime.utcnow().isoformat() + "Z",
    }

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(json.dumps(output, indent=2))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
