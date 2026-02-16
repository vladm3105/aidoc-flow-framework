#!/usr/bin/env python3
"""Update staging tracking after staging deployment.

This script updates the staging section of phase-deployments.json.

Staging status values:
- pending: Waiting for all phases to complete on dev
- deploying: Staging deployment in progress
- deployed: Staging deployed, acceptance tests passed
- failed: Staging deployment or tests failed
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-file", required=True, type=Path)
    parser.add_argument("--status", required=True,
                        choices=["pending", "deploying", "deployed", "failed"])
    parser.add_argument("--image-tag", default=None)
    parser.add_argument("--url", default=None)
    parser.add_argument("--test-results", default=None)
    parser.add_argument("--test-report-url", default=None)
    args = parser.parse_args()

    tracking = json.loads(args.tracking_file.read_text()) if args.tracking_file.exists() else {
        "config": {"total_phases": 8},
        "phases": {},
        "staging": {},
        "production": {},
        "last_check": None
    }

    now = datetime.now(timezone.utc).isoformat()

    # Ensure staging section exists
    if "staging" not in tracking:
        tracking["staging"] = {
            "status": "pending",
            "deployed_at": None,
            "url": None,
            "image_tag": None,
            "test_results": None,
            "test_report_url": None
        }

    # Update staging fields
    tracking["staging"]["status"] = args.status

    if args.image_tag:
        tracking["staging"]["image_tag"] = args.image_tag

    if args.status in ("deployed", "failed"):
        tracking["staging"]["deployed_at"] = now

    if args.url:
        tracking["staging"]["url"] = args.url

    if args.test_results:
        tracking["staging"]["test_results"] = args.test_results

    if args.test_report_url:
        tracking["staging"]["test_report_url"] = args.test_report_url

    tracking["last_check"] = now

    args.tracking_file.write_text(json.dumps(tracking, indent=2) + "\n")

    # Output for GitHub Actions
    print(f"Updated staging: {args.status}")
    if args.test_results:
        print(f"Acceptance tests: {args.test_results}")


if __name__ == "__main__":
    main()
