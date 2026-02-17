#!/usr/bin/env python3
"""Verify prerequisites for phase deployment.

This script checks that all previous phases have been successfully deployed
to dev before allowing the current phase to deploy.

For dev deployment: Checks that previous phases are dev_deployed.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-file", required=True, type=Path)
    parser.add_argument("--target-phase", required=True, type=int)
    args = parser.parse_args()

    try:
        tracking = json.loads(args.tracking_file.read_text())
    except FileNotFoundError:
        print(f"::error::Tracking file not found: {args.tracking_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"::error::Invalid JSON in tracking file: {e}")
        sys.exit(1)

    for prev in range(1, args.target_phase):
        phase_data = tracking.get("phases", {}).get(str(prev), {})
        status = phase_data.get("status")
        dev_data = phase_data.get("dev", {})
        smoke_results = dev_data.get("smoke_results")

        # Check for revalidation needed
        if status == "needs-revalidation":
            print(f"::error::Phase {prev} needs revalidation before Phase {args.target_phase}")
            print("can_deploy=false", file=sys.stdout)
            github_output = os.environ.get("GITHUB_OUTPUT")
            if github_output:
                with open(github_output, "a") as f:
                    f.write("can_deploy=false\n")
            sys.exit(1)

        # Check if phase is deployed to dev
        if status != "dev_deployed":
            print(f"::error::Phase {prev} not deployed to dev (status: {status})")
            print("can_deploy=false", file=sys.stdout)
            sys.exit(1)

        # Check if smoke tests passed
        if smoke_results != "passed":
            print(f"::error::Phase {prev} smoke tests not passed (result: {smoke_results})")
            print("can_deploy=false", file=sys.stdout)
            sys.exit(1)

    print(f"Prerequisites met for Phase {args.target_phase}")
    print("can_deploy=true", file=sys.stdout)

    # Write to GITHUB_OUTPUT if available
    import os
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write("can_deploy=true\n")


if __name__ == "__main__":
    main()
