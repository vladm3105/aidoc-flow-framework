#!/usr/bin/env python3
"""Update phase tracking after dev or staging deployment.

This script supports two modes:
1. Dev deployment: Updates phase status with dev-specific fields
2. Staging deployment (legacy): Updates phase status for staging

Status values per phase:
- pending: Not started
- dev_deploying: Dev deployment in progress
- dev_deployed: Dev deployed, smoke tests passed
- dev_failed: Dev deployment or smoke tests failed
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-file", required=True, type=Path)
    parser.add_argument("--phase", required=True, type=int)
    parser.add_argument(
        "--status",
        required=True,
        choices=["pending", "dev_deploying", "dev_deployed", "dev_failed", "deployed"],
    )
    parser.add_argument("--commit-sha", default=None)
    parser.add_argument("--image-tag", default=None)
    # Dev-specific fields
    parser.add_argument("--dev-url", default=None)
    parser.add_argument("--dev-smoke-results", default=None)
    # Legacy staging fields (for backwards compatibility)
    parser.add_argument("--staging-url", default=None)
    parser.add_argument("--test-results", default=None)
    parser.add_argument("--test-report-url", default=None)
    args = parser.parse_args()

    try:
        tracking = (
            json.loads(args.tracking_file.read_text())
            if args.tracking_file.exists()
            else {
                "config": {"total_phases": 8},
                "phases": {},
                "staging": {},
                "production": {},
                "last_check": None,
            }
        )
    except json.JSONDecodeError as e:
        print(f"Error parsing tracking file: {e}")
        tracking = {
            "config": {"total_phases": 8},
            "phases": {},
            "staging": {},
            "production": {},
            "last_check": None,
        }

    phase_key = str(args.phase)
    now = datetime.now(UTC).isoformat()

    # Get existing phase data or create new
    phase_data = tracking.get("phases", {}).get(phase_key, {})

    # Update common fields
    phase_data["status"] = args.status
    if args.commit_sha:
        phase_data["commit_sha"] = args.commit_sha
    if args.image_tag:
        phase_data["image_tag"] = args.image_tag

    # Ensure dev sub-object exists
    if "dev" not in phase_data:
        phase_data["dev"] = {"deployed_at": None, "url": None, "smoke_results": None}

    # Update dev-specific fields
    if args.status in ("dev_deploying", "dev_deployed", "dev_failed"):
        if args.status == "dev_deployed" or args.status == "dev_failed":
            phase_data["dev"]["deployed_at"] = now
        if args.dev_url:
            phase_data["dev"]["url"] = args.dev_url
        if args.dev_smoke_results:
            phase_data["dev"]["smoke_results"] = args.dev_smoke_results

    # Legacy staging fields (for backwards compatibility during transition)
    if args.staging_url:
        phase_data["staging_url"] = args.staging_url
    if args.test_results:
        phase_data["test_results"] = args.test_results
    if args.test_report_url:
        phase_data["test_report_url"] = args.test_report_url
    if args.status == "deployed":
        phase_data["deployed_at"] = now

    # Update tracking
    if "phases" not in tracking:
        tracking["phases"] = {}
    tracking["phases"][phase_key] = phase_data
    tracking["last_check"] = now

    args.tracking_file.write_text(json.dumps(tracking, indent=2) + "\n")

    # Output for GitHub Actions
    print(f"Updated Phase {args.phase}: {args.status}")
    if args.dev_smoke_results:
        print(f"Smoke tests: {args.dev_smoke_results}")
    if args.test_results:
        print(f"Acceptance tests: {args.test_results}")


if __name__ == "__main__":
    main()
