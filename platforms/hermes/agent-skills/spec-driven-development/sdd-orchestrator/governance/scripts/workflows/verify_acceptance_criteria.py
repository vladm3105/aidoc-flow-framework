#!/usr/bin/env python3
"""
Verify Acceptance Criteria for Pull Requests

Extracts acceptance criteria from linked issue, verifies each criterion
against PR changes (files, tests, CI status), and generates a report.

Usage:
    python verify_acceptance_criteria.py --pr-number 123 --repo owner/repo

Environment:
    GH_TOKEN: GitHub token with issues/pulls read access

References:
    - work_plans/ai_governance_automation.md (Item #1)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class Criterion:
    """Single acceptance criterion with verification status."""

    text: str
    verified: bool = False
    note: str = ""
    evidence: str = ""


def run_gh(args: list[str], check: bool = True) -> str:
    """Run gh CLI command and return output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        check=check,
        env={**os.environ, "GH_TOKEN": os.environ.get("GH_TOKEN", "")},
    )
    return result.stdout.strip()


def get_linked_issue(pr_body: str) -> int | None:
    """Extract linked issue number from PR body."""
    match = re.search(r"(Closes|Fixes|Resolves|closes|fixes|resolves)\s*#(\d+)", pr_body)
    return int(match.group(2)) if match else None


def extract_criteria(issue_body: str) -> list[Criterion]:
    """Extract acceptance criteria (checkboxes) from issue body."""
    criteria = []
    # Match unchecked checkboxes: - [ ] text
    for match in re.finditer(r"- \[ \] (.+)", issue_body):
        criteria.append(Criterion(text=match.group(1).strip()))
    return criteria


def get_changed_files(repo: str, pr_number: int) -> list[str]:
    """Get list of files changed in the PR."""
    output = run_gh(
        ["api", f"/repos/{repo}/pulls/{pr_number}/files", "--jq", ".[].filename"], check=False
    )
    return output.split("\n") if output else []


def get_ci_status(repo: str, pr_number: int) -> dict:
    """Get CI check status for the PR."""
    output = run_gh(
        ["pr", "view", str(pr_number), "--repo", repo, "--json", "statusCheckRollup"], check=False
    )
    try:
        data = json.loads(output) if output else {}
        checks = data.get("statusCheckRollup", [])
        return {
            "total": len(checks),
            "passed": sum(1 for c in checks if c.get("conclusion") == "SUCCESS"),
            "failed": sum(1 for c in checks if c.get("conclusion") == "FAILURE"),
            "pending": sum(1 for c in checks if c.get("status") == "IN_PROGRESS"),
        }
    except json.JSONDecodeError:
        return {"total": 0, "passed": 0, "failed": 0, "pending": 0}


def verify_criterion(
    criterion: Criterion, changed_files: list[str], ci_status: dict, test_files: list[str]
) -> Criterion:
    """Verify a single criterion against available evidence."""
    text_lower = criterion.text.lower()

    # Check 1: File patterns mentioned in criterion
    file_patterns = re.findall(r"`([^`]+\.\w+)`", criterion.text)
    if file_patterns:
        matched = [f for f in changed_files for p in file_patterns if p in f]
        if matched:
            criterion.verified = True
            criterion.note = "File patterns matched"
            criterion.evidence = ", ".join(matched[:3])
            return criterion

    # Check 2: Test-related criteria
    test_keywords = ["test", "coverage", "unit test", "integration", "spec"]
    if any(kw in text_lower for kw in test_keywords):
        if test_files:
            criterion.verified = True
            criterion.note = "Test files modified"
            criterion.evidence = f"{len(test_files)} test file(s)"
            return criterion
        if ci_status["passed"] > 0:
            criterion.verified = True
            criterion.note = "CI tests passed"
            criterion.evidence = f"{ci_status['passed']}/{ci_status['total']} checks"
            return criterion

    # Check 3: Implementation keywords with file changes
    impl_keywords = ["add", "create", "implement", "update", "fix", "remove", "modify"]
    if any(kw in text_lower for kw in impl_keywords) and changed_files:
        criterion.verified = True
        criterion.note = "Code changes detected"
        criterion.evidence = f"{len(changed_files)} file(s) modified"
        return criterion

    # Check 4: Documentation criteria
    doc_keywords = ["document", "readme", "comment", "docstring"]
    if any(kw in text_lower for kw in doc_keywords):
        doc_files = [f for f in changed_files if f.endswith((".md", ".rst", ".txt"))]
        if doc_files:
            criterion.verified = True
            criterion.note = "Documentation updated"
            criterion.evidence = ", ".join(doc_files[:3])
            return criterion

    # Not verified - needs human review
    criterion.note = "Requires human verification"
    return criterion


def generate_report(
    criteria: list[Criterion], pr_number: int, issue_number: int, blocking: bool
) -> tuple[str, bool]:
    """Generate verification report and determine pass/fail."""
    verified_count = sum(1 for c in criteria if c.verified)
    total_count = len(criteria)
    all_verified = verified_count == total_count

    lines = [
        "## Acceptance Criteria Verification",
        "",
        f"**PR**: #{pr_number}",
        f"**Linked Issue**: #{issue_number}",
        f"**Status**: {'PASS' if all_verified else 'NEEDS REVIEW'}",
        f"**Verified**: {verified_count}/{total_count}",
        "",
        "### Criteria Status",
        "",
    ]

    for c in criteria:
        status = "[PASS]" if c.verified else "[REVIEW]"
        lines.append(f"- {status} {c.text}")
        if c.note:
            lines.append(f"  - {c.note}")
        if c.evidence:
            lines.append(f"  - Evidence: {c.evidence}")

    if not all_verified:
        lines.extend(
            [
                "",
                "### Action Required",
                "",
                "Some criteria could not be automatically verified. "
                "A human reviewer should confirm these items before merging.",
            ]
        )

    if blocking and not all_verified:
        lines.extend(
            [
                "",
                "> **Note**: This check is configured as blocking. "
                "Merge will be blocked until all criteria are verified.",
            ]
        )

    report = "\n".join(lines)
    should_pass = all_verified or not blocking
    return report, should_pass


def main():
    parser = argparse.ArgumentParser(description="Verify PR acceptance criteria")
    parser.add_argument("--pr-number", type=int, required=True, help="PR number")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--blocking", action="store_true", help="Fail if criteria unverified")
    parser.add_argument("--post-comment", action="store_true", help="Post report as PR comment")
    args = parser.parse_args()

    # Get PR details
    pr_json = run_gh(
        ["pr", "view", str(args.pr_number), "--repo", args.repo, "--json", "body,title"]
    )
    pr_data = json.loads(pr_json)
    pr_body = pr_data.get("body", "")

    # Get linked issue
    issue_number = get_linked_issue(pr_body)
    if not issue_number:
        print("No linked issue found in PR body. Skipping verification.")
        sys.exit(0)

    # Get issue body
    issue_json = run_gh(["issue", "view", str(issue_number), "--repo", args.repo, "--json", "body"])
    issue_data = json.loads(issue_json)
    issue_body = issue_data.get("body", "")

    # Extract criteria
    criteria = extract_criteria(issue_body)
    if not criteria:
        print("No acceptance criteria found in issue. Skipping verification.")
        sys.exit(0)

    print(f"Found {len(criteria)} acceptance criteria in issue #{issue_number}")

    # Get verification context
    changed_files = get_changed_files(args.repo, args.pr_number)
    ci_status = get_ci_status(args.repo, args.pr_number)
    test_files = [f for f in changed_files if "test" in f.lower() or f.endswith("_test.py")]

    # Verify each criterion
    for criterion in criteria:
        verify_criterion(criterion, changed_files, ci_status, test_files)

    # Generate report
    report, should_pass = generate_report(criteria, args.pr_number, issue_number, args.blocking)
    print(report)

    # Post comment if requested
    if args.post_comment:
        run_gh(
            ["pr", "comment", str(args.pr_number), "--repo", args.repo, "--body", report],
            check=False,
        )
        print(f"\nPosted verification report to PR #{args.pr_number}")

    # Exit with appropriate code
    sys.exit(0 if should_pass else 1)


if __name__ == "__main__":
    main()
