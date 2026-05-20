#!/usr/bin/env python3
"""Create issues for test failures."""

import argparse
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


def run_gh_command(args: list[str]) -> int:
    """Run gh CLI."""
    env = os.environ.copy()
    env["GH_HOST"] = "{GITHUB_HOST}"
    result = subprocess.run(args, capture_output=True, text=True, env=env)
    return result.returncode


def parse_failures(junit_file: Path) -> list[dict]:
    """Parse JUnit XML for failures."""
    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing JUnit XML: {e}")
        return []
    except OSError as e:
        print(f"Error reading JUnit file: {e}")
        return []

    failures = []
    for testcase in root.iter("testcase"):
        failure = testcase.find("failure")
        error = testcase.find("error")

        if failure is not None or error is not None:
            elem = failure if failure is not None else error
            failures.append({
                "classname": testcase.get("classname", "unknown"),
                "name": testcase.get("name", "unknown"),
                "message": elem.get("message", "")[:500],
                "text": (elem.text or "")[:1500]
            })

    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit-xml", required=True, type=Path)
    parser.add_argument("--phase", required=True, type=int)
    parser.add_argument("--labels", required=True)
    args = parser.parse_args()

    if not args.junit_xml.exists():
        print("JUnit XML not found")
        return

    failures = parse_failures(args.junit_xml)

    for f in failures:
        title = f"[Regression] {f['classname']}::{f['name']}"
        body = f"""## Test Failure

**Phase**: {args.phase}
**Test**: `{f['classname']}::{f['name']}`

## Planning Package (Required Before `ai:ready`)

| Field | Value |
|:------|:------|
| Planning Roadmap | Pending |
| Planning Index | Pending |
| Changelog Plan | Pending |
| Approved IPLAN | Pending |
| Plan Approval | Pending (Human or LLM-as-judge) |

### Error
```
{f['message']}
```

### Details
```
{f['text']}
```
"""
        run_gh_command([
            "gh", "issue", "create",
            "--title", title[:200],
            "--body", body,
            "--label", args.labels
        ])
        print(f"Created issue: {title[:50]}...")


if __name__ == "__main__":
    main()
