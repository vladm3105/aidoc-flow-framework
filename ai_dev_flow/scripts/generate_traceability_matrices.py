#!/usr/bin/env python3
"""
Compatibility wrapper for historical references to `generate_traceability_matrices.py`.
Delegates to `generate_traceability_matrix.py`.

DEPRECATION NOTICE: Use `scripts/generate_traceability_matrix.py`.
This wrapper remains for backward compatibility and may be removed in a future release.

Supported modes:
- --type TYPE --input DIR --output FILE  (direct pass-through)
- --auto  (generate matrices for all supported types found in the repo)

Unknown flags are ignored with a warning to keep backward compatibility.
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
GEN = SCRIPT_DIR / "generate_traceability_matrix.py"

SUPPORTED_TYPES = [
    'BRD', 'PRD', 'EARS', 'BDD', 'ADR', 'SYS',
    'REQ', 'IMPL', 'CTR', 'SPEC', 'TASKS', 'IPLAN', 'ICON'
]


def run_single(doc_type: str, input_dir: Path, output_path: Path) -> int:
    cmd = [sys.executable, str(GEN), "--type", doc_type, "--input", str(input_dir), "--output", str(output_path)]
    return subprocess.call(cmd)


def auto_mode(base: Path) -> int:
    """Generate matrices for all supported types present under base."""
    status = 0
    for t in SUPPORTED_TYPES:
        t_dir = base / t
        if t_dir.exists():
            # Default output file in that directory
            out = t_dir / f"{t}-00_TRACEABILITY_MATRIX.md"
            rc = run_single(t, t_dir, out)
            if rc != 0:
                status = rc
    return status


def main():
    parser = argparse.ArgumentParser(description="Wrapper: generate traceability matrices (plural → singular)")
    parser.add_argument("--type")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--auto", action="store_true")
    parser.add_argument("--tags")  # ignored for compatibility
    parser.add_argument("--report", action="store_true")  # ignored

    args, unknown = parser.parse_known_args()

    if not GEN.exists():
        print("❌ Missing generator script: generate_traceability_matrix.py", file=sys.stderr)
        return 1

    print("[DEPRECATED] Use scripts/generate_traceability_matrix.py (singular).", file=sys.stderr)

    if args.auto:
        base = Path(__file__).resolve().parent.parent
        return auto_mode(base)

    if args.type and args.input and args.output:
        return run_single(args.type.upper(), Path(args.input), Path(args.output))

    if unknown:
        print(f"[WARN] Ignoring unsupported args: {' '.join(unknown)}")

    print("Usage: --auto OR --type TYPE --input DIR --output FILE")
    return 2


if __name__ == "__main__":
    sys.exit(main())
