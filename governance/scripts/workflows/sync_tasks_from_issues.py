#!/usr/bin/env python3
"""
Sync TASKS Files with GitHub Issues

Bidirectional sync between TASKS files and GitHub issues:
- Fetches phase issues from GitHub
- Maps to TASKS YAML structure
- Detects changes (new, closed, updated)
- Generates updated TASKS file

Usage:
    python sync_tasks_from_issues.py --phase 1 --repo owner/repo

Environment:
    GH_TOKEN: GitHub token with issues read access

References:
    - work_plans/ai_governance_automation.md (Item #9)
"""

import argparse
import json
import os
import re
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
    """Get all issues for a specific phase."""
    output = run_gh([
        "issue", "list",
        "--repo", repo,
        "--label", f"phase:{phase}",
        "--state", "all",
        "--json", "number,title,body,state,labels,assignees",
        "--limit", "200"
    ], check=False)
    return json.loads(output) if output else []


def parse_existing_tasks(tasks_file: str) -> dict:
    """Parse existing TASKS file to extract task IDs and statuses."""
    tasks = {}
    if not os.path.exists(tasks_file):
        return tasks

    with open(tasks_file, "r") as f:
        content = f.read()

    # Extract task entries (simplified YAML parsing)
    for match in re.finditer(
        r'- id:\s*"?([^"\n]+)"?\s*\n\s*title:\s*"?([^"\n]+)"?\s*\n\s*status:\s*"?([^"\n]+)"?',
        content
    ):
        task_id = match.group(1).strip()
        tasks[task_id] = {
            "title": match.group(2).strip(),
            "status": match.group(3).strip()
        }

    return tasks


def issue_to_task(issue: dict, phase: int) -> dict:
    """Convert GitHub issue to TASKS entry."""
    labels = [l.get("name", "") for l in issue.get("labels", [])]
    assignees = [a.get("login", "") for a in issue.get("assignees", [])]

    # Determine status from issue state and labels
    if issue.get("state") == "CLOSED":
        status = "completed"
    elif any("in-progress" in l.lower() for l in labels):
        status = "in_progress"
    elif any("blocked" in l.lower() for l in labels):
        status = "blocked"
    else:
        status = "pending"

    # Determine task type from labels
    task_type = "implementation"
    if any(l in ["bug", "bugfix"] for l in labels):
        task_type = "bugfix"
    elif any(l in ["documentation", "docs"] for l in labels):
        task_type = "documentation"
    elif any(l in ["test", "testing"] for l in labels):
        task_type = "testing"

    # Extract task ID from title if present
    title = issue.get("title", "")
    task_id_match = re.search(r'\[P\d+-T(\d+)\]', title)
    if task_id_match:
        task_id = f"TASK-{phase}{task_id_match.group(1).zfill(2)}"
    else:
        task_id = f"TASK-{phase}{str(issue['number']).zfill(3)}"

    return {
        "id": task_id,
        "title": re.sub(r'^\[P\d+-T\d+\]\s*', '', title),
        "issue_number": issue["number"],
        "status": status,
        "type": task_type,
        "assignees": assignees,
        "labels": labels
    }


def generate_tasks_yaml(
    tasks: list[dict],
    phase: int,
    repo: str
) -> str:
    """Generate TASKS YAML content."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# TASKS File - Phase {phase}",
        f"# Auto-generated from GitHub Issues",
        f"# Repository: {repo}",
        f"# Generated: {timestamp}",
        f"",
        f"metadata:",
        f"  phase: {phase}",
        f"  repo: {repo}",
        f"  generated: \"{timestamp}\"",
        f"  total_tasks: {len(tasks)}",
        f"  completed: {sum(1 for t in tasks if t['status'] == 'completed')}",
        f"  in_progress: {sum(1 for t in tasks if t['status'] == 'in_progress')}",
        f"  pending: {sum(1 for t in tasks if t['status'] == 'pending')}",
        f"",
        f"tasks:",
    ]

    for task in sorted(tasks, key=lambda t: t["id"]):
        lines.extend([
            f"  - id: \"{task['id']}\"",
            f"    title: \"{task['title']}\"",
            f"    issue: {task['issue_number']}",
            f"    status: \"{task['status']}\"",
            f"    type: \"{task['type']}\"",
        ])
        if task["assignees"]:
            lines.append(f"    assignees: {task['assignees']}")
        lines.append("")

    return "\n".join(lines)


def detect_changes(
    old_tasks: dict,
    new_tasks: list[dict]
) -> dict:
    """Detect changes between old and new tasks."""
    changes = {
        "added": [],
        "removed": [],
        "status_changed": [],
        "unchanged": []
    }

    new_task_ids = {t["id"]: t for t in new_tasks}

    # Check for added and changed tasks
    for task_id, task in new_task_ids.items():
        if task_id not in old_tasks:
            changes["added"].append(task)
        elif old_tasks[task_id]["status"] != task["status"]:
            changes["status_changed"].append({
                "task": task,
                "old_status": old_tasks[task_id]["status"],
                "new_status": task["status"]
            })
        else:
            changes["unchanged"].append(task)

    # Check for removed tasks
    for task_id in old_tasks:
        if task_id not in new_task_ids:
            changes["removed"].append({
                "id": task_id,
                "title": old_tasks[task_id]["title"]
            })

    return changes


def main():
    parser = argparse.ArgumentParser(description="Sync TASKS from GitHub issues")
    parser.add_argument("--phase", type=int, required=True, help="Phase number")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Show diff without saving")
    args = parser.parse_args()

    # Determine output file
    output_file = args.output or f"docs/TASKS/TASKS-P{args.phase}.yaml"

    # Get existing tasks
    old_tasks = parse_existing_tasks(output_file)
    print(f"Existing tasks: {len(old_tasks)}")

    # Get issues from GitHub
    issues = get_phase_issues(args.repo, args.phase)
    print(f"GitHub issues: {len(issues)}")

    # Convert issues to tasks
    new_tasks = [issue_to_task(issue, args.phase) for issue in issues]

    # Detect changes
    changes = detect_changes(old_tasks, new_tasks)

    print(f"\n=== Changes Detected ===")
    print(f"Added: {len(changes['added'])}")
    print(f"Removed: {len(changes['removed'])}")
    print(f"Status Changed: {len(changes['status_changed'])}")
    print(f"Unchanged: {len(changes['unchanged'])}")

    if changes["added"]:
        print(f"\nNew Tasks:")
        for task in changes["added"]:
            print(f"  + {task['id']}: {task['title'][:50]}")

    if changes["status_changed"]:
        print(f"\nStatus Changes:")
        for change in changes["status_changed"]:
            print(f"  ~ {change['task']['id']}: {change['old_status']} -> {change['new_status']}")

    if changes["removed"]:
        print(f"\nRemoved Tasks:")
        for task in changes["removed"]:
            print(f"  - {task['id']}: {task['title'][:50]}")

    if args.dry_run:
        print(f"\n=== Generated TASKS (dry run) ===")
        print(generate_tasks_yaml(new_tasks, args.phase, args.repo))
        return

    # Generate and save TASKS file
    tasks_yaml = generate_tasks_yaml(new_tasks, args.phase, args.repo)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as f:
        f.write(tasks_yaml)

    print(f"\nUpdated: {output_file}")


if __name__ == "__main__":
    main()
