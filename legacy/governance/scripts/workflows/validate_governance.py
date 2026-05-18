#!/usr/bin/env python3
"""
Validate Governance Documentation

Detects drift between governance docs and reality:
- ROADMAP phase dates vs actual issue timelines
- PROJECT_PLAN gap analysis vs open issues
- IPLAN references in issues

Usage:
    python validate_governance.py --repo owner/repo

Environment:
    GH_TOKEN: GitHub token with issues read access

References:
    - work_plans/ai_governance_automation.md (Item #11)
"""

import argparse
import json
import os
import re
import subprocess
import sys
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


def read_file(path: str) -> Optional[str]:
    """Read file contents if exists."""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None


def validate_roadmap(roadmap_content: str, issues: list[dict]) -> list[str]:
    """Validate ROADMAP against actual issues."""
    warnings = []

    # Extract phase dates from ROADMAP
    phase_dates = {}
    for match in re.finditer(
        r'Phase\s*(\d+).*?(\d{4}-\d{2}-\d{2})',
        roadmap_content,
        re.IGNORECASE
    ):
        phase_dates[int(match.group(1))] = match.group(2)

    # Check if phases have issues
    phases_with_issues = set()
    for issue in issues:
        labels = [l.get("name", "") for l in issue.get("labels", [])]
        for label in labels:
            if label.startswith("phase:"):
                try:
                    phase_num = int(label.split(":")[1])
                    phases_with_issues.add(phase_num)
                except ValueError:
                    pass

    # Check for phases in ROADMAP without issues
    for phase in phase_dates:
        if phase not in phases_with_issues:
            warnings.append(
                f"ROADMAP: Phase {phase} has target date {phase_dates[phase]} "
                f"but no issues with phase:{phase} label"
            )

    return warnings


def validate_project_plan(plan_content: str, issues: list[dict]) -> list[str]:
    """Validate PROJECT_PLAN gap analysis."""
    warnings = []

    # Extract gaps mentioned in PROJECT_PLAN
    gaps_section = re.search(
        r'##.*Gap.*Analysis.*?\n(.*?)(?=\n##|\Z)',
        plan_content,
        re.IGNORECASE | re.DOTALL
    )

    if not gaps_section:
        return warnings

    gaps_text = gaps_section.group(1)

    # Count mentioned gaps vs open issues
    gap_count = len(re.findall(r'- \[[ x]\]', gaps_text))
    open_issues = sum(1 for i in issues if i.get("state") == "OPEN")

    if abs(gap_count - open_issues) > 5:
        warnings.append(
            f"PROJECT_PLAN: Gap analysis lists {gap_count} items, "
            f"but there are {open_issues} open issues. Consider updating."
        )

    return warnings


def validate_iplan_references(issues: list[dict]) -> list[str]:
    """Validate IPLAN references in issues."""
    warnings = []

    for issue in issues:
        body = issue.get("body", "")
        number = issue["number"]

        # Check if issue mentions IPLAN
        iplan_refs = re.findall(r'IPLAN-(\d+)', body, re.IGNORECASE)

        for ref in iplan_refs:
            iplan_path = f"governance/plans/IPLAN-{ref}_*.md"
            # This would need glob expansion in real implementation
            if not os.path.exists(f"governance/plans"):
                continue

            # Check if referenced IPLAN exists
            import glob
            matches = glob.glob(f"governance/plans/IPLAN-{ref}_*.md")
            if not matches:
                warnings.append(
                    f"Issue #{number}: References IPLAN-{ref} which does not exist"
                )

    return warnings


def validate_governance_files() -> list[str]:
    """Validate required governance files exist."""
    warnings = []

    required_files = [
        "governance/GOVERNANCE_RULES.md",
        "governance/PROJECT_PLAN.md",
        "governance/ROADMAP.md",
        "governance/DEFINITION_OF_DONE.md",
        "CLAUDE.md"
    ]

    for filepath in required_files:
        if not os.path.exists(filepath):
            warnings.append(f"Missing required governance file: {filepath}")

    return warnings


def generate_report(all_warnings: list[str]) -> str:
    """Generate validation report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"## Governance Validation Report",
        f"",
        f"**Generated**: {timestamp}",
        f"**Status**: {'PASS' if not all_warnings else 'WARNINGS'}",
        f"**Issues Found**: {len(all_warnings)}",
        f"",
    ]

    if all_warnings:
        lines.extend([
            f"### Warnings",
            f"",
        ])
        for warning in all_warnings:
            lines.append(f"- {warning}")
        lines.append("")
    else:
        lines.extend([
            f"No governance drift detected.",
            f"",
        ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validate governance docs")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings")
    args = parser.parse_args()

    all_warnings = []

    # Validate required files exist
    all_warnings.extend(validate_governance_files())

    # Get all issues
    output = run_gh([
        "issue", "list",
        "--repo", args.repo,
        "--state", "all",
        "--json", "number,title,body,state,labels",
        "--limit", "500"
    ], check=False)
    issues = json.loads(output) if output else []

    # Validate ROADMAP
    roadmap = read_file("governance/ROADMAP.md")
    if roadmap:
        all_warnings.extend(validate_roadmap(roadmap, issues))

    # Validate PROJECT_PLAN
    project_plan = read_file("governance/PROJECT_PLAN.md")
    if project_plan:
        all_warnings.extend(validate_project_plan(project_plan, issues))

    # Validate IPLAN references
    all_warnings.extend(validate_iplan_references(issues))

    # Generate report
    report = generate_report(all_warnings)
    print(report)

    # Exit code
    if args.strict and all_warnings:
        sys.exit(1)


if __name__ == "__main__":
    main()
