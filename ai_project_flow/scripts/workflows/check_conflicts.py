#!/usr/bin/env python3
"""Check for merge conflicts with open PRs."""

import argparse
import json
import os
import subprocess
import sys


def run_gh_command(args: list[str]) -> tuple[int, str]:
    """Run gh CLI command."""
    env = os.environ.copy()
    env["GH_HOST"] = "{GITHUB_HOST}"
    result = subprocess.run(args, capture_output=True, text=True, env=env)
    return result.returncode, result.stdout


def get_open_prs() -> list[dict]:
    """Get all open PRs with ai:in-progress label."""
    code, stdout = run_gh_command([
        "gh", "pr", "list",
        "--label", "ai:in-progress",
        "--state", "open",
        "--json", "number,headRefName,files"
    ])
    return json.loads(stdout) if code == 0 and stdout else []


def get_modified_files() -> set[str]:
    """Get files modified in current branch."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True, text=True
    )
    return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()


def check_conflicts() -> tuple[bool, list[str]]:
    """Check if current branch conflicts with open PRs."""
    my_files = get_modified_files()
    if not my_files:
        return False, []

    open_prs = get_open_prs()
    conflicts = []

    for pr in open_prs:
        pr_files = set(f["path"] for f in pr.get("files", []))
        overlap = my_files & pr_files
        if overlap:
            conflicts.append(f"PR #{pr['number']}: {', '.join(overlap)}")

    return bool(conflicts), conflicts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait", action="store_true", help="Wait for conflicts to resolve")
    parser.add_argument("--max-wait", type=int, default=30, help="Max wait time in minutes")
    args = parser.parse_args()

    has_conflict, conflicts = check_conflicts()

    if not has_conflict:
        print("No conflicts detected")
        sys.exit(0)

    print("Conflicts detected:")
    for c in conflicts:
        print(f"  - {c}")

    if not args.wait:
        sys.exit(1)

    # Wait mode: poll until conflicts resolve
    import time
    wait_time = 0
    while wait_time < args.max_wait * 60:
        time.sleep(300)  # 5 minutes
        wait_time += 300

        has_conflict, conflicts = check_conflicts()
        if not has_conflict:
            print("Conflicts resolved")
            # Rebase on main
            subprocess.run(["git", "fetch", "origin", "main"])
            subprocess.run(["git", "rebase", "origin/main"])
            sys.exit(0)

        print(f"Still waiting... ({wait_time // 60} / {args.max_wait} min)")

    print("Timeout waiting for conflicts to resolve")
    sys.exit(1)


if __name__ == "__main__":
    main()
