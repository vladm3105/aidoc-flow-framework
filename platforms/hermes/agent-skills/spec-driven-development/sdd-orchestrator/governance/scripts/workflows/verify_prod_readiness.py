#!/usr/bin/env python3
"""Verify production deployment readiness."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def check_blockers() -> list[int]:
    """Get open blocker issues."""
    env = os.environ.copy()
    env["GH_HOST"] = "{GITHUB_HOST}"
    result = subprocess.run(
        ["gh", "issue", "list", "--label", "blocker", "--state", "open", "--json", "number"],
        capture_output=True,
        text=True,
        env=env,
    )
    issues = json.loads(result.stdout) if result.returncode == 0 and result.stdout else []
    return [i["number"] for i in issues]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-file", required=True, type=Path)
    parser.add_argument("--total-phases", type=int, default=8)
    parser.add_argument("--check-blockers", action="store_true")
    args = parser.parse_args()

    tracking = json.loads(args.tracking_file.read_text())

    for phase in range(1, args.total_phases + 1):
        phase_data = tracking.get("phases", {}).get(str(phase), {})

        if phase_data.get("status") == "needs-revalidation":
            print(f"::error::Phase {phase} needs revalidation")
            print("ready=false")
            sys.exit(1)

        if phase_data.get("status") != "deployed":
            print(f"::error::Phase {phase} not deployed")
            print("ready=false")
            sys.exit(1)

        if phase_data.get("test_results") != "passed":
            print(f"::error::Phase {phase} tests not passed")
            print("ready=false")
            sys.exit(1)

    if args.check_blockers:
        blockers = check_blockers()
        if blockers:
            print(f"::error::Open blockers: {blockers}")
            print("ready=false")
            sys.exit(1)

    print("Production ready")
    print("ready=true")


if __name__ == "__main__":
    main()
