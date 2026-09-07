#!/usr/bin/env python3
"""Extract test plan from development issue acceptance criteria."""

import argparse
import re
from pathlib import Path


def extract_acceptance_criteria(issue_body: str) -> list[str]:
    """Extract acceptance criteria from issue body."""
    criteria = []

    # Look for acceptance criteria section
    ac_patterns = [
        r"##\s*Acceptance\s*Criteria\s*\n(.*?)(?=\n##|\Z)",
        r"##\s*AC\s*\n(.*?)(?=\n##|\Z)",
        r"\*\*Acceptance\s*Criteria\*\*\s*\n(.*?)(?=\n\*\*|\Z)",
        r"Acceptance\s*Criteria:\s*\n(.*?)(?=\n[A-Z]|\Z)",
    ]

    for pattern in ac_patterns:
        match = re.search(pattern, issue_body, re.DOTALL | re.IGNORECASE)
        if match:
            ac_section = match.group(1)
            break
    else:
        ac_section = issue_body

    # Extract checkbox items
    checkbox_pattern = r"[-*]\s*\[\s*[xX ]?\s*\]\s*(.+?)(?=\n|$)"
    checkboxes = re.findall(checkbox_pattern, ac_section)
    criteria.extend([c.strip() for c in checkboxes if c.strip()])

    # Also extract numbered items
    numbered_pattern = r"\d+\.\s+(.+?)(?=\n|$)"
    numbered = re.findall(numbered_pattern, ac_section)
    criteria.extend([n.strip() for n in numbered if n.strip()])

    # Extract bullet points (non-checkbox)
    bullet_pattern = r"[-*]\s+(?!\[)(.+?)(?=\n|$)"
    bullets = re.findall(bullet_pattern, ac_section)
    criteria.extend([b.strip() for b in bullets if b.strip()])

    # Deduplicate while preserving order
    seen = set()
    unique_criteria = []
    for c in criteria:
        if c not in seen:
            seen.add(c)
            unique_criteria.append(c)

    return unique_criteria


def extract_special_instructions(issue_body: str) -> str:
    """Extract special testing instructions from issue body."""
    # Look for testing instructions section
    test_patterns = [
        r"##\s*Testing\s*Instructions?\s*\n(.*?)(?=\n##|\Z)",
        r"##\s*Test\s*Plan\s*\n(.*?)(?=\n##|\Z)",
        r"\*\*Testing\*\*\s*\n(.*?)(?=\n\*\*|\Z)",
        r"Testing\s*Notes?:\s*\n(.*?)(?=\n[A-Z]|\Z)",
    ]

    for pattern in test_patterns:
        match = re.search(pattern, issue_body, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return ""


def format_test_plan(criteria: list[str], special_instructions: str) -> str:
    """Format the extracted information as a test plan."""
    lines = []

    if criteria:
        lines.append("<!-- Extracted from development issue acceptance criteria -->")
        for criterion in criteria[:10]:  # Limit to 10 items
            lines.append(f"- [ ] {criterion}")
    else:
        lines.append("<!-- No acceptance criteria found in development issue -->")
        lines.append("- [ ] Verify feature works as described")
        lines.append("- [ ] Check for edge cases")
        lines.append("- [ ] Validate error handling")

    if special_instructions:
        lines.append("")
        lines.append("### Special Testing Instructions")
        lines.append(special_instructions)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Extract test plan from development issue")
    parser.add_argument(
        "--issue-body-file",
        required=True,
        type=Path,
        help="File containing issue body",
    )
    parser.add_argument("--output-file", required=True, type=Path, help="Output markdown file")
    args = parser.parse_args()

    try:
        issue_body = args.issue_body_file.read_text()
    except FileNotFoundError:
        print(f"Error: Issue body file not found: {args.issue_body_file}")
        return
    except OSError as e:
        print(f"Error reading issue body file: {e}")
        return

    criteria = extract_acceptance_criteria(issue_body)
    special = extract_special_instructions(issue_body)
    test_plan = format_test_plan(criteria, special)

    try:
        args.output_file.write_text(test_plan)
    except OSError as e:
        print(f"Error writing output file: {e}")
        return

    print(f"Extracted {len(criteria)} acceptance criteria")


if __name__ == "__main__":
    main()
