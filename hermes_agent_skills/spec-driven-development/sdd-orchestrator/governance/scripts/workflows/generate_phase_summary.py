#!/usr/bin/env python3
"""
Generate Phase Completion Summary

Creates a summary report when a phase completes, including:
- All issues closed in the phase
- Bug/rework counts
- Cycle time metrics

Usage:
    python generate_phase_summary.py --phase 1 --repo owner/repo

Environment:
    GH_TOKEN: GitHub token with issues read access

References:
    - work_plans/ai_governance_automation.md (Item #8)
"""

import argparse
import json
import os
import subprocess
from datetime import datetime
from typing import Optional


def run_gh(args: list[str], check: bool = True) -> str:
    """Run gh CLI command and return output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        check=check,
        env={**os.environ, "GH_TOKEN": os.environ.get("GH_TOKEN", "")}
    )
    return result.stdout.strip()


def get_phase_issues(repo: str, phase: int) -> list[dict]:
    """Get all closed issues for a specific phase."""
    output = run_gh([
        "issue", "list",
        "--repo", repo,
        "--label", f"phase:{phase}",
        "--state", "closed",
        "--json", "number,title,labels,createdAt,closedAt,author",
        "--limit", "200"
    ], check=False)
    return json.loads(output) if output else []


def categorize_issues(issues: list[dict]) -> dict:
    """Categorize issues by type based on labels."""
    categories = {
        "features": [],
        "bugs": [],
        "documentation": [],
        "chores": [],
        "ai_implemented": [],
        "other": []
    }

    for issue in issues:
        labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
        issue_info = {
            "number": issue["number"],
            "title": issue["title"],
            "created": issue.get("createdAt", ""),
            "closed": issue.get("closedAt", "")
        }

        # Check for AI implementation
        if any("ai:" in label for label in labels):
            categories["ai_implemented"].append(issue_info)

        # Categorize by type
        if any(l in labels for l in ["bug", "bugfix", "fix"]):
            categories["bugs"].append(issue_info)
        elif any(l in labels for l in ["documentation", "docs"]):
            categories["documentation"].append(issue_info)
        elif any(l in labels for l in ["chore", "maintenance"]):
            categories["chores"].append(issue_info)
        elif any(l in labels for l in ["feature", "enhancement"]):
            categories["features"].append(issue_info)
        else:
            categories["other"].append(issue_info)

    return categories


def calculate_cycle_times(issues: list[dict]) -> dict:
    """Calculate cycle time metrics."""
    cycle_times = []

    for issue in issues:
        created = issue.get("createdAt", "")
        closed = issue.get("closedAt", "")

        if created and closed:
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                closed_dt = datetime.fromisoformat(closed.replace("Z", "+00:00"))
                days = (closed_dt - created_dt).days
                cycle_times.append(days)
            except (ValueError, TypeError):
                pass

    if not cycle_times:
        return {"avg": 0, "min": 0, "max": 0, "total": 0}

    return {
        "avg": sum(cycle_times) / len(cycle_times),
        "min": min(cycle_times),
        "max": max(cycle_times),
        "total": len(cycle_times)
    }


def generate_summary(
    phase: int,
    issues: list[dict],
    repo: str
) -> str:
    """Generate phase completion summary."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    categories = categorize_issues(issues)
    cycle_times = calculate_cycle_times(issues)

    lines = [
        f"# Phase {phase} Completion Summary",
        f"",
        f"## Metadata",
        f"",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| **Phase** | {phase} |",
        f"| **Generated** | {timestamp} |",
        f"| **Repository** | {repo} |",
        f"| **Total Issues** | {len(issues)} |",
        f"",
        f"---",
        f"",
        f"## Issue Breakdown",
        f"",
        f"| Category | Count |",
        f"|----------|-------|",
        f"| Features | {len(categories['features'])} |",
        f"| Bug Fixes | {len(categories['bugs'])} |",
        f"| Documentation | {len(categories['documentation'])} |",
        f"| Chores | {len(categories['chores'])} |",
        f"| Other | {len(categories['other'])} |",
        f"| **AI Implemented** | {len(categories['ai_implemented'])} |",
        f"",
        f"---",
        f"",
        f"## Cycle Time Metrics",
        f"",
        f"| Metric | Days |",
        f"|--------|------|",
        f"| Average | {cycle_times['avg']:.1f} |",
        f"| Minimum | {cycle_times['min']} |",
        f"| Maximum | {cycle_times['max']} |",
        f"| Issues Measured | {cycle_times['total']} |",
        f"",
        f"---",
        f"",
        f"## AI Implementation Rate",
        f"",
    ]

    ai_count = len(categories['ai_implemented'])
    total = len(issues)
    ai_rate = (ai_count / total * 100) if total > 0 else 0

    lines.extend([
        f"- **AI Implemented**: {ai_count}/{total} ({ai_rate:.1f}%)",
        f"- **Human Implemented**: {total - ai_count}/{total} ({100 - ai_rate:.1f}%)",
        f"",
        f"---",
        f"",
        f"## Completed Issues",
        f"",
    ])

    for category_name, category_issues in categories.items():
        if category_issues and category_name != "ai_implemented":
            lines.append(f"### {category_name.replace('_', ' ').title()}")
            lines.append("")
            for issue in category_issues[:20]:  # Limit per category
                lines.append(f"- #{issue['number']}: {issue['title'][:60]}")
            lines.append("")

    lines.extend([
        f"---",
        f"",
        f"## Lessons Learned",
        f"",
        f"<!-- Add retrospective notes here -->",
        f"",
        f"- ",
        f"",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate phase summary")
    parser.add_argument("--phase", type=int, required=True, help="Phase number")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--output-dir", default="governance/plans", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Print without saving")
    args = parser.parse_args()

    # Get closed phase issues
    issues = get_phase_issues(args.repo, args.phase)
    if not issues:
        print(f"No closed issues found for phase {args.phase}")
        return

    print(f"Found {len(issues)} closed issues for phase {args.phase}")

    # Generate summary
    summary = generate_summary(args.phase, issues, args.repo)

    if args.dry_run:
        print(summary)
        return

    # Save summary
    filename = f"PHASE-{args.phase}-SUMMARY.md"
    filepath = os.path.join(args.output_dir, filename)

    os.makedirs(args.output_dir, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(summary)

    print(f"Created phase summary: {filepath}")


if __name__ == "__main__":
    main()
