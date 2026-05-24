#!/usr/bin/env python3
"""Create bug issues from QA test failures."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def run_gh_command(args: list[str]) -> tuple[int, str, str]:
    """Run a gh CLI command."""
    env = os.environ.copy()
    env["GH_HOST"] = "{GITHUB_HOST}"

    proc = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr


def get_existing_bug_issues(phase: int, test_name: str) -> list[int]:
    """Get existing bug issues for a test."""
    returncode, stdout, _ = run_gh_command(
        [
            "issue",
            "list",
            "--label",
            f"phase:{phase}",
            "--label",
            "bug",
            "--json",
            "number,title",
        ]
    )

    if returncode != 0 or not stdout:
        return []

    issues = json.loads(stdout)
    matching = [i["number"] for i in issues if test_name.lower() in i["title"].lower()]
    return matching


def trigger_bug_workflow(
    qa_issue: str,
    failure: dict,
    iteration: int,
) -> bool:
    """Trigger the create-bug-issue workflow."""
    failure_json = json.dumps(failure)

    returncode, _, stderr = run_gh_command(
        [
            "workflow",
            "run",
            "create-bug-issue.yml",
            "-f",
            f"qa_issue={qa_issue}",
            "-f",
            f"failure_details={failure_json}",
            "-f",
            f"iteration={iteration}",
        ]
    )

    if returncode != 0:
        print(f"Error triggering workflow: {stderr}", file=sys.stderr)
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Create bug issues from QA failures")
    parser.add_argument("--phase", required=True, type=int, help="Phase number")
    parser.add_argument("--results-file", required=True, type=Path, help="QA results JSON file")
    parser.add_argument("--max-iterations", type=int, default=3, help="Maximum iterations")
    args = parser.parse_args()

    try:
        results = json.loads(args.results_file.read_text())
    except FileNotFoundError:
        print(f"Results file not found: {args.results_file}")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing results file: {e}")
        return

    if results.get("all_passed", True):
        print("All tests passed, no bug issues needed")
        return

    errors = results.get("errors", [])
    failed_issues = results.get("failed_issues", [])

    if not errors:
        print("No error details available")
        return

    created_count = 0
    skipped_count = 0

    for error in errors:
        test_name = error.get("test_name", "unknown")

        # Check for existing bug issues
        existing = get_existing_bug_issues(args.phase, test_name)
        iteration = len(existing) + 1

        if iteration > args.max_iterations:
            print(f"Skipping {test_name}: max iterations ({args.max_iterations}) reached")
            skipped_count += 1
            continue

        # Use first failed QA issue as source
        qa_issue = failed_issues[0] if failed_issues else "unknown"

        print(f"Creating bug issue for {test_name} (iteration {iteration})...")

        success = trigger_bug_workflow(qa_issue, error, iteration)
        if success:
            created_count += 1
        else:
            print(f"Failed to create bug issue for {test_name}")

    print("\nSummary:")
    print(f"  Created: {created_count}")
    print(f"  Skipped (max iterations): {skipped_count}")


if __name__ == "__main__":
    main()
