#!/usr/bin/env python3
"""Handle issue reopen - mark phase as needs-revalidation."""

import argparse
import json
import os
import subprocess
from pathlib import Path


def get_issue_labels(issue_number: int) -> list[str]:
    """Get labels for an issue."""
    env = os.environ.copy()
    env["GH_HOST"] = "{GITHUB_HOST}"
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number), "--json", "labels", "--jq", ".labels[].name"],
        capture_output=True, text=True, env=env
    )
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-file", required=True, type=Path)
    parser.add_argument("--issue-number", required=True, type=int)
    args = parser.parse_args()

    # Get issue's phase label
    labels = get_issue_labels(args.issue_number)
    phase = None
    for label in labels:
        if label.startswith("phase:"):
            phase = label.split(":")[1]
            break

    if not phase:
        print(f"Issue #{args.issue_number} has no phase label")
        return

    # Load tracking
    tracking = json.loads(args.tracking_file.read_text())

    # Check if phase was deployed
    phase_data = tracking.get("phases", {}).get(phase, {})
    if phase_data.get("status") == "deployed":
        print(f"Phase {phase} marked as needs-revalidation due to issue #{args.issue_number} reopen")
        tracking["phases"][phase]["status"] = "needs-revalidation"
        args.tracking_file.write_text(json.dumps(tracking, indent=2) + "\n")


if __name__ == "__main__":
    main()
