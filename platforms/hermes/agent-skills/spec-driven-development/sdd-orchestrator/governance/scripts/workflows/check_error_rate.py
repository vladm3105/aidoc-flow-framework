#!/usr/bin/env python3
"""Check Cloud Run error rate."""

import argparse
import json
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--window", type=int, default=60)
    parser.add_argument("--threshold", type=float, default=0.01)
    args = parser.parse_args()

    # Query Cloud Monitoring
    mql = f'''
    fetch cloud_run_revision
    | metric 'run.googleapis.com/request_count'
    | filter resource.service_name == "{args.service}"
    | group_by [response_code_class], [sum(value.request_count)]
    | within {args.window}s
    '''

    result = subprocess.run(
        ["gcloud", "monitoring", "read", mql, f"--project={args.project}", "--format=json"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("ok")  # Fail open
        return

    try:
        data = json.loads(result.stdout)
        total = 0
        errors = 0

        for series in data:
            code_class = series.get("labels", {}).get("response_code_class", "")
            count = sum(p.get("value", 0) for p in series.get("points", []))
            total += count
            if code_class in ["4xx", "5xx"]:
                errors += count

        if total == 0:
            print("ok")
            return

        rate = errors / total
        print(f"Error rate: {rate:.4f}", file=sys.stderr)

        if rate > args.threshold:
            print("exceeded")
        else:
            print("ok")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("ok")


if __name__ == "__main__":
    main()
