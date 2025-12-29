#!/usr/bin/env python3
"""
Compatibility wrapper for historical `check_broken_references.py`.
Delegates to `validate_links.py` with sensible defaults.
"""

import subprocess
import sys
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    validator = here / "validate_links.py"
    if not validator.exists():
        print("❌ validate_links.py not found", file=sys.stderr)
        return 1

    # Prefer 'ai_dev_flow' if present; otherwise scan current repo root
    repo_root = here.parent
    default_docs = repo_root / "ai_dev_flow"
    docs_dir = default_docs if default_docs.exists() else repo_root

    cmd = [sys.executable, str(validator), "--docs-dir", str(docs_dir)]
    # Pass through additional args
    cmd.extend(sys.argv[1:])

    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())

