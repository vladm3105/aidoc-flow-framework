#!/usr/bin/env python3
"""Update production tracking."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-file", required=True, type=Path)
    parser.add_argument("--commit-sha", default=None)
    parser.add_argument("--current-revision", required=True)
    parser.add_argument("--previous-revision", default=None)
    parser.add_argument("--revision-history", default=None)
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()

    tracking = json.loads(args.tracking_file.read_text())

    tracking["production"] = {
        "deployed": True,
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "commit_sha": args.commit_sha,
        "current_revision": args.current_revision,
        "previous_revision": args.previous_revision,
        "revision_history": args.revision_history or "",
        "last_action": "rollback" if args.rollback else "deploy"
    }

    args.tracking_file.write_text(json.dumps(tracking, indent=2) + "\n")

    action = "Rollback" if args.rollback else "Deploy"
    print(f"Production {action}: {args.current_revision}")


if __name__ == "__main__":
    main()
