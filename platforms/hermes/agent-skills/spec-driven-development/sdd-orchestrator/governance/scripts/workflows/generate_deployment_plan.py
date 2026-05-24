#!/usr/bin/env python3
"""
Generate Deployment Plan from Phase PRs

Collects deployment considerations from all issues in a phase,
identifies migration sequences, and generates a deployment plan.

Usage:
    python generate_deployment_plan.py --phase 1 --repo owner/repo

Environment:
    GH_TOKEN: GitHub token with issues read access

References:
    - work_plans/ai_governance_automation.md (Item #6)
"""

import argparse
import json
import os
import re
import subprocess
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


def extract_deployment_info(body: str) -> dict:
    """Extract deployment-related information from issue body."""
    info = {
        "migrations": [],
        "config_changes": [],
        "dependencies": [],
        "rollback_notes": [],
        "environment_vars": [],
    }

    # Extract migration references
    for match in re.finditer(r"migration|migrate|schema|database", body, re.IGNORECASE):
        context = body[max(0, match.start() - 50) : match.end() + 100]
        info["migrations"].append(context.strip())

    # Extract config changes
    for match in re.finditer(r"config|configuration|setting|environment", body, re.IGNORECASE):
        context = body[max(0, match.start() - 50) : match.end() + 100]
        info["config_changes"].append(context.strip())

    # Extract dependency mentions
    for match in re.finditer(r"depends on #(\d+)|requires #(\d+)", body, re.IGNORECASE):
        issue_num = match.group(1) or match.group(2)
        info["dependencies"].append(f"#{issue_num}")

    # Extract environment variables
    for match in re.finditer(r"([A-Z][A-Z0-9_]{2,})", body):
        if len(match.group(1)) > 3:  # Filter out short matches
            info["environment_vars"].append(match.group(1))

    return info


def determine_deployment_order(issues: list[dict]) -> list[dict]:
    """Order issues by dependencies for deployment sequence."""
    # Simple topological sort based on "Depends on" references
    ordered = []
    remaining = list(issues)
    seen_numbers = set()

    while remaining:
        # Find issues with no unseen dependencies
        for issue in remaining[:]:
            deps = []
            body = issue.get("body", "")
            for match in re.finditer(r"depends on #(\d+)", body, re.IGNORECASE):
                deps.append(int(match.group(1)))

            unseen_deps = [d for d in deps if d not in seen_numbers]
            if not unseen_deps:
                ordered.append(issue)
                seen_numbers.add(issue["number"])
                remaining.remove(issue)
                break
        else:
            # No progress - circular dependency or external deps
            # Add remaining in order
            ordered.extend(remaining)
            break

    return ordered


def generate_deployment_plan(phase: int, issues: list[dict], repo: str) -> str:
    """Generate deployment plan content."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    ordered_issues = determine_deployment_order(issues)

    lines = [
        f"# Deployment Plan: Phase {phase}",
        "",
        "## Metadata",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| **Phase** | {phase} |",
        f"| **Generated** | {timestamp} |",
        f"| **Total Issues** | {len(issues)} |",
        f"| **Repository** | {repo} |",
        "",
        "---",
        "",
        "## Deployment Sequence",
        "",
        "Deploy in this order to respect dependencies:",
        "",
    ]

    for i, issue in enumerate(ordered_issues, 1):
        state_icon = "[CLOSED]" if issue.get("state") == "CLOSED" else "[OPEN]"
        lines.append(f"{i}. #{issue['number']} - {issue['title']} {state_icon}")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Pre-Deployment Checklist",
            "",
            f"- [ ] All phase {phase} issues are closed",
            "- [ ] All PRs are merged to main",
            "- [ ] CI/CD pipeline passes on main",
            "- [ ] Database backups completed",
            "- [ ] Rollback plan reviewed",
            "- [ ] Team notified of deployment window",
            "",
            "---",
            "",
            "## Configuration Changes",
            "",
        ]
    )

    all_config_changes = []
    all_env_vars = set()
    for issue in issues:
        info = extract_deployment_info(issue.get("body", ""))
        all_config_changes.extend(info["config_changes"][:2])  # Limit per issue
        all_env_vars.update(info["environment_vars"])

    if all_env_vars:
        lines.append("### Environment Variables")
        lines.append("")
        for var in sorted(all_env_vars)[:10]:  # Limit total
            lines.append(f"- `{var}`")
        lines.append("")
    else:
        lines.append("*No configuration changes detected.*")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Migration Steps",
            "",
        ]
    )

    has_migrations = False
    for issue in issues:
        info = extract_deployment_info(issue.get("body", ""))
        if info["migrations"]:
            has_migrations = True
            lines.append(f"### #{issue['number']}")
            for mig in info["migrations"][:2]:
                lines.append(f"- {mig[:100]}...")
            lines.append("")

    if not has_migrations:
        lines.append("*No database migrations detected.*")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Rollback Procedure",
            "",
            "1. Revert deployment in reverse order",
            "2. Restore database from backup if migrations were applied",
            "3. Verify rollback success with smoke tests",
            "4. Notify team of rollback completion",
            "",
            "---",
            "",
            "## Post-Deployment Verification",
            "",
            "- [ ] Smoke tests pass",
            "- [ ] No error spikes in monitoring",
            "- [ ] Key user flows work correctly",
            "- [ ] Performance metrics within acceptable range",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate deployment plan")
    parser.add_argument("--phase", type=int, required=True, help="Phase number")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--output-dir", default="governance/plans", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without saving")
    args = parser.parse_args()

    # Get phase issues
    issues = get_phase_issues(args.repo, args.phase)
    if not issues:
        print(f"No issues found for phase {args.phase}")
        return

    print(f"Found {len(issues)} issues for phase {args.phase}")

    # Generate plan
    plan_content = generate_deployment_plan(args.phase, issues, args.repo)

    if args.dry_run:
        print(plan_content)
        return

    # Save plan
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"DEPLOY-P{args.phase}-{timestamp}.md"
    filepath = os.path.join(args.output_dir, filename)

    os.makedirs(args.output_dir, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(plan_content)

    print(f"Created deployment plan: {filepath}")


if __name__ == "__main__":
    main()
