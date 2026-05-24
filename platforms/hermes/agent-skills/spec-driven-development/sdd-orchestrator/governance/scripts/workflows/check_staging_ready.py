#!/usr/bin/env python3
"""
Check Staging Readiness for Production Deployment

Evaluates staging environment readiness by checking:
- All QA tests pass
- All acceptance criteria for phase issues are met
- No open blockers

Usage:
    python check_staging_ready.py --phase 1 --repo owner/repo

Environment:
    GH_TOKEN: GitHub token with issues read access

References:
    - work_plans/ai_governance_automation.md (Item #7)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime


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


def get_phase_issues(repo: str, phase: int) -> list[dict]:
    """Get all issues for a specific phase."""
    output = run_gh(
        [
            "issue",
            "list",
            "--repo",
            repo,
            "--label",
            f"phase:{phase}",
            "--state",
            "all",
            "--json",
            "number,title,body,state,labels",
            "--limit",
            "100",
        ],
        check=False,
    )
    return json.loads(output) if output else []


def check_acceptance_criteria(issue: dict) -> dict:
    """Check if all acceptance criteria are met for an issue."""
    body = issue.get("body", "")

    # Find all checkboxes
    total = len(re.findall(r"- \[[ x]\]", body))
    checked = len(re.findall(r"- \[x\]", body))
    unchecked = len(re.findall(r"- \[ \]", body))

    return {
        "total": total,
        "checked": checked,
        "unchecked": unchecked,
        "complete": total > 0 and unchecked == 0,
    }


def check_blocker_labels(issue: dict) -> bool:
    """Check if issue has blocker labels."""
    labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
    blocker_labels = ["blocker", "blocked", "needs-human", "critical"]
    return any(bl in label for label in labels for bl in blocker_labels)


def evaluate_staging_readiness(repo: str, phase: int, issues: list[dict]) -> dict:
    """Evaluate overall staging readiness."""
    result = {
        "ready": True,
        "phase": phase,
        "total_issues": len(issues),
        "closed_issues": 0,
        "open_issues": 0,
        "criteria_complete": 0,
        "criteria_incomplete": 0,
        "blockers": [],
        "warnings": [],
        "details": [],
    }

    for issue in issues:
        issue_num = issue["number"]
        issue_title = issue["title"][:50]
        state = issue.get("state", "OPEN")

        detail = {
            "number": issue_num,
            "title": issue_title,
            "state": state,
            "criteria": None,
            "blocker": False,
        }

        if state == "CLOSED":
            result["closed_issues"] += 1
        else:
            result["open_issues"] += 1
            result["ready"] = False
            result["warnings"].append(f"Issue #{issue_num} is still open")

        # Check acceptance criteria
        criteria = check_acceptance_criteria(issue)
        detail["criteria"] = criteria
        if criteria["complete"]:
            result["criteria_complete"] += 1
        else:
            result["criteria_incomplete"] += 1
            if criteria["unchecked"] > 0:
                result["warnings"].append(
                    f"Issue #{issue_num} has {criteria['unchecked']} unchecked criteria"
                )

        # Check for blockers
        if check_blocker_labels(issue):
            detail["blocker"] = True
            result["blockers"].append(f"Issue #{issue_num}: {issue_title}")
            result["ready"] = False

        result["details"].append(detail)

    return result


def generate_report(evaluation: dict) -> str:
    """Generate staging readiness report."""
    verdict = "GO" if evaluation["ready"] else "NO-GO"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "## Staging Readiness Report",
        "",
        f"**Verdict**: **{verdict}**",
        f"**Phase**: {evaluation['phase']}",
        f"**Generated**: {timestamp}",
        "",
        "---",
        "",
        "### Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Issues | {evaluation['total_issues']} |",
        f"| Closed | {evaluation['closed_issues']} |",
        f"| Open | {evaluation['open_issues']} |",
        f"| Criteria Complete | {evaluation['criteria_complete']} |",
        f"| Criteria Incomplete | {evaluation['criteria_incomplete']} |",
        f"| Blockers | {len(evaluation['blockers'])} |",
        "",
    ]

    if evaluation["blockers"]:
        lines.extend(
            [
                "### Blockers",
                "",
            ]
        )
        for blocker in evaluation["blockers"]:
            lines.append(f"- {blocker}")
        lines.append("")

    if evaluation["warnings"]:
        lines.extend(
            [
                "### Warnings",
                "",
            ]
        )
        for warning in evaluation["warnings"][:10]:  # Limit warnings
            lines.append(f"- {warning}")
        lines.append("")

    if not evaluation["ready"]:
        lines.extend(
            [
                "### Action Required",
                "",
                "Before proceeding to production:",
                "",
            ]
        )
        if evaluation["open_issues"] > 0:
            lines.append(f"- [ ] Close {evaluation['open_issues']} open issues")
        if evaluation["criteria_incomplete"] > 0:
            lines.append(
                f"- [ ] Complete acceptance criteria for {evaluation['criteria_incomplete']} issues"
            )
        if evaluation["blockers"]:
            lines.append(f"- [ ] Resolve {len(evaluation['blockers'])} blockers")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check staging readiness")
    parser.add_argument("--phase", type=int, required=True, help="Phase number")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--post-comment", type=int, help="Post report to this issue number")
    args = parser.parse_args()

    # Get phase issues
    issues = get_phase_issues(args.repo, args.phase)
    if not issues:
        print(f"No issues found for phase {args.phase}")
        sys.exit(0)

    # Evaluate readiness
    evaluation = evaluate_staging_readiness(args.repo, args.phase, issues)

    # Generate report
    report = generate_report(evaluation)
    print(report)

    # Post comment if requested
    if args.post_comment:
        run_gh(
            ["issue", "comment", str(args.post_comment), "--repo", args.repo, "--body", report],
            check=False,
        )
        print(f"\nPosted report to issue #{args.post_comment}")

    # Exit with appropriate code
    sys.exit(0 if evaluation["ready"] else 1)


if __name__ == "__main__":
    main()
