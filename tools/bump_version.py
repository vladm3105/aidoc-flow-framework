#!/usr/bin/env python3
"""Bump framework/VERSION + FRAMEWORK_SPEC_VERSION files + every skill's
framework_spec_version, then re-sync the bundle.

Usage:  python3 tools/bump_version.py <semver>

Portable (no GNU-sed deps).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_SPEC = REPO_ROOT / "framework"
BUNDLE = REPO_ROOT / "platforms" / "claude-code-plugin"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SKILL_SPEC_RE = re.compile(
    r'^(?P<lead>\s+framework_spec_version:\s*")[^"]+(?P<trail>".*)$',
    re.MULTILINE,
)


def die(msg: str, code: int = 2) -> None:
    print(f"bump_version: {msg}", file=sys.stderr)
    sys.exit(code)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not SEMVER.match(argv[1]):
        die("Usage: bump_version.py <semver>")
    new = argv[1]

    version_file = FRAMEWORK_SPEC / "VERSION"
    if not version_file.exists():
        die(f"missing {version_file}", 1)
    old = version_file.read_text(encoding="utf-8").strip()
    print(f"Bumping {old} -> {new}")

    for path in [
        FRAMEWORK_SPEC / "VERSION",
        BUNDLE / "VERSION",
        BUNDLE / "FRAMEWORK_SPEC_VERSION",
        REPO_ROOT / "platforms" / "hermes" / "FRAMEWORK_SPEC_VERSION",
    ]:
        if path.exists():
            path.write_text(new + "\n", encoding="utf-8")

    skills_root = BUNDLE / "skills"
    updated = 0
    if skills_root.exists():
        for skill_md in skills_root.glob("*/SKILL.md"):
            original = skill_md.read_text(encoding="utf-8")
            patched = SKILL_SPEC_RE.sub(rf"\g<lead>{new}\g<trail>", original)
            if patched != original:
                skill_md.write_text(patched, encoding="utf-8")
                updated += 1
    print(f"Updated {updated} skill manifest(s)")

    for sync in [
        REPO_ROOT / "tools" / "sync-plugin-framework.sh",
        REPO_ROOT / "tools" / "sdd_doc_lint" / "sync-vendored.sh",
    ]:
        if sync.exists():
            subprocess.run(["bash", str(sync)], check=True)

    if skills_root.exists():
        stragglers = [
            p
            for p in skills_root.glob("*/SKILL.md")
            if f'framework_spec_version: "{old}"' in p.read_text(encoding="utf-8")
        ]
        if stragglers:
            die(
                f"{len(stragglers)} skill(s) still reference {old}: "
                f"{[str(p.relative_to(REPO_ROOT)) for p in stragglers]}",
                1,
            )

    print(f"Bump complete: {old} -> {new}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
