#!/usr/bin/env python3
"""Deprecated: legacy TASKS sync workflow.

This script is retained for compatibility only and is not part of the active
v3 governance workflow.

Replacement:
- Use v3 artifact generation (`sdd_create`) and issue-driven execution plans
  (`IPLAN`) instead of bidirectional TASKS sync.

Removal criteria:
- Remove this file after all downstream repositories complete governance v3
  migration and no runbooks reference sync-tasks automation.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description='Deprecated legacy script')
    parser.add_argument('--phase')
    parser.add_argument('--repo')
    parser.add_argument('--output')
    parser.add_argument('--dry-run', action='store_true')
    _ = parser.parse_args()

    msg = (
        'DEPRECATED: sync_tasks_from_issues.py is legacy-only and disabled in '
        'governance v3. Use sdd_create + IPLAN workflows.'
    )
    print(msg)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
