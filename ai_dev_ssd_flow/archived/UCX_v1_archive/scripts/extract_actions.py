#!/usr/bin/env python3
"""
Extract UCX actions from BRD review reports.

Usage:
    python extract_actions.py <report.md> [options]

Options:
    --target PRD|EARS|BDD|ADR|CTR    Filter by target layer
    --type HANDOFF|INFORM|REVIEW|DEFER    Filter by action type
    --priority P0|P1|P2    Filter by priority
    --format json|md|csv|summary    Output format (default: json)
    --output FILE    Write to file instead of stdout

Examples:
    python extract_actions.py BRD-01.UCR_review.md --format summary
    python extract_actions.py BRD-01.UCR_review.md --target ADR --format md
    python extract_actions.py BRD-01.UCR_review.md --type HANDOFF --format json
"""

import re
import json
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class Action:
    """Represents a UCX action for downstream layer handoff."""
    action_id: str
    action_type: str
    target: str
    priority: str
    source: str
    persona: str
    context: str
    requirement: str


# Simple pattern: ACT-{6-10 char hex}
ACTION_PATTERN = re.compile(
    r'<!-- UCX-ACTION-START -->\s*'
    r'ACTION_ID:\s*(?P<action_id>ACT-[a-f0-9]{6,10})\s*'
    r'TYPE:\s*(?P<action_type>\w+)\s*'
    r'TARGET:\s*(?P<target>\w+)\s*'
    r'PRIORITY:\s*(?P<priority>P[012])\s*'
    r'SOURCE:\s*(?P<source>[^\n]+)\s*'
    r'PERSONA:\s*(?P<persona>[^\n]+)\s*'
    r'CONTEXT:\s*(?P<context>[^\n]+)\s*'
    r'REQUIREMENT:\s*(?P<requirement>[^\n]+)\s*'
    r'<!-- UCX-ACTION-END -->',
    re.MULTILINE
)

# Configurable valid values (easy to extend)
VALID_TYPES = {'HANDOFF', 'INFORM', 'REVIEW', 'DEFER'}
VALID_TARGETS = {'PRD', 'EARS', 'BDD', 'ADR', 'CTR'}
VALID_PRIORITIES = {'P0', 'P1', 'P2'}


def extract_actions(content: str) -> list[Action]:
    """Extract actions from review report."""
    actions = []
    for match in ACTION_PATTERN.finditer(content):
        actions.append(Action(**match.groupdict()))
    return actions


def filter_actions(
    actions: list[Action],
    target: str = None,
    action_type: str = None,
    priority: str = None
) -> list[Action]:
    """Filter actions by criteria."""
    result = actions
    if target:
        result = [a for a in result if a.target.upper() == target.upper()]
    if action_type:
        result = [a for a in result if a.action_type.upper() == action_type.upper()]
    if priority:
        result = [a for a in result if a.priority.upper() == priority.upper()]
    return result


def output_json(actions: list[Action]) -> str:
    """Output actions as JSON."""
    return json.dumps([asdict(a) for a in actions], indent=2)


def output_csv(actions: list[Action]) -> str:
    """Output actions as CSV."""
    if not actions:
        return "action_id,type,target,priority,source,persona,context,requirement"
    header = "action_id,type,target,priority,source,persona,context,requirement"
    rows = []
    for a in actions:
        # Escape quotes in context and requirement
        ctx = a.context.replace('"', '""')
        req = a.requirement.replace('"', '""')
        src = a.source.replace('"', '""')
        row = f'{a.action_id},{a.action_type},{a.target},{a.priority},"{src}",{a.persona},"{ctx}","{req}"'
        rows.append(row)
    return header + "\n" + "\n".join(rows)


def output_md(actions: list[Action]) -> str:
    """Output actions as markdown table."""
    if not actions:
        return "No actions found."
    lines = [
        "| Action ID | Type | Target | Priority | Source | Requirement |",
        "|-----------|------|--------|----------|--------|-------------|"
    ]
    for a in actions:
        req = a.requirement[:50] + "..." if len(a.requirement) > 50 else a.requirement
        lines.append(f"| {a.action_id} | {a.action_type} | {a.target} | {a.priority} | {a.source} | {req} |")
    return "\n".join(lines)


def output_summary(actions: list[Action]) -> str:
    """Output summary statistics."""
    if not actions:
        return "No actions found."

    by_type = {}
    by_target = {}
    by_priority = {}

    for a in actions:
        by_type[a.action_type] = by_type.get(a.action_type, 0) + 1
        by_target[a.target] = by_target.get(a.target, 0) + 1
        by_priority[a.priority] = by_priority.get(a.priority, 0) + 1

    lines = [
        f"Total Actions: {len(actions)}",
        "",
        "By Type:",
        *[f"  {k}: {v}" for k, v in sorted(by_type.items())],
        "",
        "By Target:",
        *[f"  {k}: {v}" for k, v in sorted(by_target.items())],
        "",
        "By Priority:",
        *[f"  {k}: {v}" for k, v in sorted(by_priority.items())],
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Extract UCX actions from BRD review reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_actions.py report.md --format summary
  python extract_actions.py report.md --target ADR --format md
  python extract_actions.py report.md --type HANDOFF -o actions.json
        """
    )
    parser.add_argument("report", help="Path to UCR review report")
    parser.add_argument("--target", choices=list(VALID_TARGETS),
                        help="Filter by target layer")
    parser.add_argument("--type", dest="action_type", choices=list(VALID_TYPES),
                        help="Filter by action type")
    parser.add_argument("--priority", choices=list(VALID_PRIORITIES),
                        help="Filter by priority")
    parser.add_argument("--format", choices=["json", "csv", "md", "summary"],
                        default="json", help="Output format")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Error: File not found: {report_path}", file=sys.stderr)
        sys.exit(1)

    content = report_path.read_text()
    actions = extract_actions(content)
    actions = filter_actions(actions, args.target, args.action_type, args.priority)

    formatters = {
        'json': output_json,
        'csv': output_csv,
        'md': output_md,
        'summary': output_summary
    }
    result = formatters[args.format](actions)

    if args.output:
        Path(args.output).write_text(result)
        print(f"Written {len(actions)} actions to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
