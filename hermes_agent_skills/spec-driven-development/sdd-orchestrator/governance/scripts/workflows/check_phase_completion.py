#!/usr/bin/env python3
"""Check if a project phase is complete with rate limiting."""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls: int):
        self.max_calls = max_calls
        self.calls = 0

    def check(self) -> bool:
        if self.calls >= self.max_calls:
            return False
        self.calls += 1
        return True

    def wait_and_retry(self) -> None:
        time.sleep(1)


def run_gh_command(args: list[str], rate_limiter: RateLimiter) -> tuple[int, str, str]:
    """Run gh CLI with rate limiting and retry."""
    if not rate_limiter.check():
        print("Rate limit reached", file=sys.stderr)
        return 1, "", "Rate limit exceeded"

    env = os.environ.copy()
    env["GH_HOST"] = "{GITHUB_HOST}"

    for attempt in range(3):
        result = subprocess.run(args, capture_output=True, text=True, env=env)
        if result.returncode == 0:
            return result.returncode, result.stdout, result.stderr
        if "rate limit" in result.stderr.lower():
            rate_limiter.wait_and_retry()
            continue
        break

    return result.returncode, result.stdout, result.stderr


def get_phase_issues(phase: int, rate_limiter: RateLimiter) -> list[dict]:
    """Get development issues for a phase.

    Only checks ai:development issues, not deployment/QA issues.
    Deployment and QA issues are created AFTER phase completion.
    """
    code, stdout, _ = run_gh_command([
        "gh", "issue", "list",
        "--label", f"phase:{phase}",
        "--label", "ai:development",
        "--state", "all",
        "--json", "number,title,state,labels"
    ], rate_limiter)
    return json.loads(stdout) if code == 0 and stdout else []


def get_project_item_status(issue_number: int, rate_limiter: RateLimiter) -> str:
    """Get issue status from Project Board #{PROJECT_BOARD_NUMBER}."""
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          projectItems(first: 1) {
            nodes {
              fieldValueByName(name: "Status") {
                ... on ProjectV2ItemFieldSingleSelectValue { name }
              }
            }
          }
        }
      }
    }
    """
    repo = os.environ.get("GITHUB_REPOSITORY", "{GITHUB_ORG}/{REPO_NAME}")
    owner, name = repo.split("/")

    code, stdout, _ = run_gh_command([
        "gh", "api", "graphql",
        "-f", f"query={query}",
        "-F", f"owner={owner}",
        "-F", f"repo={name}",
        "-F", f"number={issue_number}"
    ], rate_limiter)

    if code != 0:
        return "unknown"

    try:
        data = json.loads(stdout)
        return data["data"]["repository"]["issue"]["projectItems"]["nodes"][0]["fieldValueByName"]["name"]
    except (KeyError, IndexError, TypeError):
        return "unknown"


def check_blockers(rate_limiter: RateLimiter) -> list[int]:
    """Get list of open blocker issues."""
    code, stdout, _ = run_gh_command([
        "gh", "issue", "list",
        "--label", "blocker",
        "--state", "open",
        "--json", "number"
    ], rate_limiter)
    issues = json.loads(stdout) if code == 0 and stdout else []
    return [i["number"] for i in issues]


def load_tracking(tracking_file: Path) -> dict:
    """Load phase tracking file."""
    if tracking_file.exists():
        return json.loads(tracking_file.read_text())
    return {
        "config": {"total_phases": 8},
        "phases": {},
        "last_check": None,
        "production": {}
    }


def save_tracking(tracking_file: Path, tracking: dict) -> None:
    """Save phase tracking file."""
    tracking["last_check"] = datetime.now(timezone.utc).isoformat()
    tracking_file.write_text(json.dumps(tracking, indent=2) + "\n")


def check_previous_phases(phase: int, tracking: dict) -> tuple[bool, str]:
    """Verify all previous phases are deployed and passed."""
    for prev in range(1, phase):
        prev_data = tracking.get("phases", {}).get(str(prev), {})
        status = prev_data.get("status")
        test_results = prev_data.get("test_results")

        if status == "needs-revalidation":
            return False, f"Phase {prev} needs revalidation"
        if status != "deployed":
            return False, f"Phase {prev} not deployed"
        if test_results != "passed":
            return False, f"Phase {prev} tests not passed"

    return True, ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-file", required=True, type=Path)
    parser.add_argument("--total-phases", type=int, default=8)
    parser.add_argument("--output-github-actions", action="store_true")
    parser.add_argument("--rate-limit", type=int, default=100)
    args = parser.parse_args()

    rate_limiter = RateLimiter(args.rate_limit)
    tracking = load_tracking(args.tracking_file)

    for phase in range(1, args.total_phases + 1):
        phase_key = str(phase)
        phase_data = tracking.get("phases", {}).get(phase_key, {})

        # Skip deployed+passed phases
        if phase_data.get("status") == "deployed" and phase_data.get("test_results") == "passed":
            continue

        # Skip needs-revalidation (waiting for fix)
        if phase_data.get("status") == "needs-revalidation":
            continue

        # Check prerequisites
        prev_ok, prev_msg = check_previous_phases(phase, tracking)
        if not prev_ok:
            print(f"Phase {phase}: {prev_msg}", file=sys.stderr)
            continue

        # Get issues
        issues = get_phase_issues(phase, rate_limiter)
        if not issues:
            print(f"Phase {phase}: no issues", file=sys.stderr)
            continue

        # Check all issues done
        all_done = True
        for issue in issues:
            status = get_project_item_status(issue["number"], rate_limiter)
            if status != "Done":
                all_done = False
                break

        if not all_done:
            continue

        # Check blockers
        blockers = check_blockers(rate_limiter)
        if blockers:
            print(f"Phase {phase}: blocked by {blockers}", file=sys.stderr)
            continue

        # Phase complete!
        save_tracking(args.tracking_file, tracking)

        if args.output_github_actions:
            print(f"phase_completed=true")
            print(f"phase_number={phase}")
        else:
            print(f"Phase {phase} complete")
        return

    save_tracking(args.tracking_file, tracking)

    if args.output_github_actions:
        print("phase_completed=false")
        print("phase_number=0")


if __name__ == "__main__":
    main()
