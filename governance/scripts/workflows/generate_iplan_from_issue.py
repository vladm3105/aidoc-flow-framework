#!/usr/bin/env python3
"""
Generate IPLAN from GitHub Issue

Creates an implementation plan (IPLAN) template from a GitHub issue
when the `ai:ready` label is added. Maps acceptance criteria to tasks.

Usage:
    python generate_iplan_from_issue.py --issue-number 123 --repo owner/repo

Environment:
    GH_TOKEN: GitHub token with issues/pulls write access

References:
    - work_plans/ai_governance_automation.md (Item #2)
    - ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md
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


def slugify(text: str, max_length: int = 40) -> str:
    """Convert text to URL-friendly slug."""
    # Remove special characters, convert spaces to hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug[:max_length]


def extract_phase(title: str, labels: list[str]) -> str:
    """Extract phase from title or labels."""
    # Check title for [P1-...] or [P2-...] pattern
    match = re.search(r'\[P(\d+)', title)
    if match:
        return f"Phase {match.group(1)}"

    # Check labels for phase:N
    for label in labels:
        if label.startswith("phase:"):
            return f"Phase {label.split(':')[1]}"

    return "Unassigned"


def extract_acceptance_criteria(body: str) -> list[str]:
    """Extract acceptance criteria checkboxes from issue body."""
    criteria = []
    for match in re.finditer(r'- \[[ x]\] (.+)', body):
        criteria.append(match.group(1).strip())
    return criteria


def extract_description(body: str) -> str:
    """Extract description section from issue body."""
    # Try to find description section
    desc_match = re.search(
        r'##\s*Description\s*\n(.*?)(?=\n##|\Z)',
        body,
        re.IGNORECASE | re.DOTALL
    )
    if desc_match:
        return desc_match.group(1).strip()

    # Fall back to first paragraph
    paragraphs = body.split('\n\n')
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('#') and not p.startswith('-'):
            return p[:500]

    return "See linked issue for details."


def extract_references(body: str) -> list[str]:
    """Extract ADR, SPEC, and other document references."""
    refs = []

    # ADR references
    for match in re.finditer(r'ADR-\d+', body, re.IGNORECASE):
        refs.append(match.group(0))

    # SPEC references
    for match in re.finditer(r'SPEC-\d+', body, re.IGNORECASE):
        refs.append(match.group(0))

    # Issue references (Depends on, Blocks)
    for match in re.finditer(r'(Depends on|Blocks|Related to)\s*#(\d+)', body, re.IGNORECASE):
        refs.append(f"Issue #{match.group(2)}")

    return list(set(refs))


def generate_tasks(criteria: list[str]) -> list[dict]:
    """Convert acceptance criteria to IPLAN tasks."""
    tasks = []
    for i, criterion in enumerate(criteria, 1):
        task = {
            "id": f"TASK-{i:03d}",
            "description": criterion,
            "type": infer_task_type(criterion),
            "estimated_complexity": infer_complexity(criterion)
        }
        tasks.append(task)
    return tasks


def infer_task_type(criterion: str) -> str:
    """Infer task type from criterion text."""
    text = criterion.lower()
    if any(w in text for w in ["test", "coverage", "spec"]):
        return "testing"
    if any(w in text for w in ["document", "readme", "comment"]):
        return "documentation"
    if any(w in text for w in ["refactor", "cleanup", "rename"]):
        return "refactoring"
    if any(w in text for w in ["fix", "bug", "patch"]):
        return "bugfix"
    return "implementation"


def infer_complexity(criterion: str) -> int:
    """Infer complexity (1-5) from criterion text."""
    text = criterion.lower()
    # Simple tasks
    if any(w in text for w in ["add", "update", "rename", "comment"]):
        return 1
    # Medium tasks
    if any(w in text for w in ["create", "implement", "write"]):
        return 2
    # Complex tasks
    if any(w in text for w in ["refactor", "migrate", "integrate"]):
        return 3
    # Very complex tasks
    if any(w in text for w in ["architect", "design", "security"]):
        return 4
    return 2  # Default medium


def generate_iplan(
    issue_number: int,
    title: str,
    body: str,
    labels: list[str],
    author: str
) -> str:
    """Generate IPLAN content from issue data."""
    slug = slugify(title)
    phase = extract_phase(title, labels)
    description = extract_description(body)
    criteria = extract_acceptance_criteria(body)
    references = extract_references(body)
    tasks = generate_tasks(criteria)
    timestamp = datetime.now().strftime("%Y-%m-%d")

    # Build IPLAN content
    lines = [
        f"# IPLAN-{issue_number}: {title}",
        f"",
        f"## Metadata",
        f"",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| **Issue** | #{issue_number} |",
        f"| **Phase** | {phase} |",
        f"| **Status** | Draft |",
        f"| **Created** | {timestamp} |",
        f"| **Author** | @{author} |",
        f"| **AI Agent** | Pending assignment |",
        f"",
        f"---",
        f"",
        f"## Summary",
        f"",
        f"{description}",
        f"",
        f"---",
        f"",
        f"## Acceptance Criteria Mapping",
        f"",
    ]

    if criteria:
        lines.append(f"| # | Criterion | Task ID | Type | Complexity |")
        lines.append(f"|---|-----------|---------|------|------------|")
        for i, (criterion, task) in enumerate(zip(criteria, tasks), 1):
            lines.append(
                f"| {i} | {criterion[:50]}{'...' if len(criterion) > 50 else ''} | "
                f"{task['id']} | {task['type']} | {task['estimated_complexity']}/5 |"
            )
    else:
        lines.append("*No acceptance criteria found in issue. Add criteria before implementation.*")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## Tasks",
        f"",
    ])

    if tasks:
        for task in tasks:
            lines.extend([
                f"### {task['id']}: {task['description'][:60]}",
                f"",
                f"- **Type**: {task['type']}",
                f"- **Complexity**: {task['estimated_complexity']}/5",
                f"- **Status**: Pending",
                f"",
                f"#### Steps",
                f"",
                f"1. [ ] Analyze requirements",
                f"2. [ ] Implement changes",
                f"3. [ ] Write/update tests",
                f"4. [ ] Verify acceptance criterion",
                f"",
            ])
    else:
        lines.append("*Tasks will be generated from acceptance criteria.*")

    lines.extend([
        f"---",
        f"",
        f"## References",
        f"",
    ])

    if references:
        for ref in references:
            lines.append(f"- {ref}")
    else:
        lines.append("- Issue #{issue_number}")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## Risks & Considerations",
        f"",
        f"<!-- AI Agent: Document risks, edge cases, and considerations -->",
        f"",
        f"- [ ] Review impact on existing functionality",
        f"- [ ] Consider backward compatibility",
        f"- [ ] Identify test coverage gaps",
        f"",
        f"---",
        f"",
        f"## Session Notes",
        f"",
        f"<!-- AI Agent: Add notes during implementation -->",
        f"",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate IPLAN from GitHub issue")
    parser.add_argument("--issue-number", type=int, required=True, help="Issue number")
    parser.add_argument("--repo", required=True, help="Repository (owner/repo)")
    parser.add_argument("--output-dir", default="governance/plans", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Print IPLAN without creating")
    args = parser.parse_args()

    # Get issue details
    issue_json = run_gh([
        "issue", "view", str(args.issue_number),
        "--repo", args.repo,
        "--json", "title,body,labels,author"
    ])
    issue_data = json.loads(issue_json)

    title = issue_data.get("title", f"Issue {args.issue_number}")
    body = issue_data.get("body", "")
    labels = [l.get("name", "") for l in issue_data.get("labels", [])]
    author = issue_data.get("author", {}).get("login", "unknown")

    # Generate IPLAN content
    iplan_content = generate_iplan(args.issue_number, title, body, labels, author)

    if args.dry_run:
        print(iplan_content)
        return

    # Create output file
    slug = slugify(title)
    filename = f"IPLAN-{args.issue_number}_{slug}.md"
    filepath = os.path.join(args.output_dir, filename)

    os.makedirs(args.output_dir, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(iplan_content)

    print(f"Created IPLAN: {filepath}")

    # Output for workflow use (GitHub Actions format)
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"iplan-path={filepath}\n")
            f.write(f"iplan-filename={filename}\n")
    else:
        # Fallback for local testing
        print(f"iplan-path={filepath}")
        print(f"iplan-filename={filename}")


if __name__ == "__main__":
    main()
