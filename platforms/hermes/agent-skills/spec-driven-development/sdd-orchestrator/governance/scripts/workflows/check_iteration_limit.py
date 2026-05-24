#!/usr/bin/env python3
"""Check if QA iteration limit has been reached."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Check QA iteration limit")
    parser.add_argument("--iteration", required=True, type=int, help="Current iteration number")
    parser.add_argument("--max-iterations", type=int, default=3, help="Maximum allowed iterations")
    parser.add_argument("--output-file", required=True, type=Path, help="Output JSON file")
    args = parser.parse_args()

    within_limit = args.iteration <= args.max_iterations
    remaining = max(0, args.max_iterations - args.iteration)

    if within_limit:
        action = "create_bug"
        message = f"Iteration {args.iteration}/{args.max_iterations} - creating bug issue"
    else:
        action = "escalate"
        message = (
            f"Iteration {args.iteration} exceeds max {args.max_iterations} - escalating to human"
        )

    result = {
        "iteration": args.iteration,
        "max_iterations": args.max_iterations,
        "within_limit": within_limit,
        "remaining": remaining,
        "action": action,
        "message": message,
    }

    args.output_file.write_text(json.dumps(result, indent=2))

    print(f"Iteration: {args.iteration}/{args.max_iterations}")
    print(f"Action: {action}")
    print(f"Message: {message}")


if __name__ == "__main__":
    main()
