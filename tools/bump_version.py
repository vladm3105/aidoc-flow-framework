#!/usr/bin/env python3
"""Bump the FRAMEWORK SPEC version across everything that must equal it.

Bumps `framework/VERSION`, both platforms' `FRAMEWORK_SPEC_VERSION` pins, and
the `framework_spec_version` of every skill manifest AND every playbook (and
`SKILL_AUTHORING.md`), then runs the sync scripts (bundle + vendored lint +
`sync-version-refs.sh`, which fans the spec-version string into the READMEs /
PARITY / CLAUDE.md).

Usage:  python3 tools/bump_version.py <semver>

Does NOT touch the plugin's own `VERSION` (independent stream — bump it
separately when the plugin releases). One manual step remains: the deliberate
hard-pin in `tests/conformance/platforms/test_plugin_release_metadata.py`
(printed as a reminder).

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
# `\s*` (not `\s+`): skill frontmatter indents framework_spec_version under
# metadata.custom_fields, but playbook frontmatter declares it at column 0.
# The old `\s+` silently skipped all 51 playbooks → conformance red after a bump.
FSV_RE = re.compile(
    r'^(?P<lead>\s*framework_spec_version:\s*")[^"]+(?P<trail>".*)$',
    re.MULTILINE,
)


def bump_plugin_readme(new: str) -> None:
    """Update the plugin README's framework-spec strings (conformance-checked):
    the prose ``framework spec `X``` and the ``$ cat FRAMEWORK_SPEC_VERSION`` block.
    Conformance runs BEFORE sync-version-refs.sh at commit time, so this can't be
    left to that hook."""
    readme = BUNDLE / "README.md"
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8")
    text = re.sub(r"(framework spec `)\d+\.\d+\.\d+(`)", rf"\g<1>{new}\g<2>", text)
    text = re.sub(
        r"(\$ cat FRAMEWORK_SPEC_VERSION\n)\d+\.\d+\.\d+",
        rf"\g<1>{new}",
        text,
    )
    readme.write_text(text, encoding="utf-8")


def die(msg: str, code: int = 2) -> None:
    print(f"bump_version: {msg}", file=sys.stderr)
    sys.exit(code)


def bump_fsv(paths, new: str) -> int:
    """Rewrite every `framework_spec_version: "..."` to `new`. Returns count."""
    updated = 0
    for path in paths:
        original = path.read_text(encoding="utf-8")
        patched = FSV_RE.sub(rf"\g<lead>{new}\g<trail>", original)
        if patched != original:
            path.write_text(patched, encoding="utf-8")
            updated += 1
    return updated


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not SEMVER.match(argv[1]):
        die("Usage: bump_version.py <semver>")
    new = argv[1]

    version_file = FRAMEWORK_SPEC / "VERSION"
    if not version_file.exists():
        die(f"missing {version_file}", 1)
    old = version_file.read_text(encoding="utf-8").strip()
    print(f"Bumping framework spec {old} -> {new}")

    # framework/VERSION + the two platform FRAMEWORK_SPEC_VERSION pins.
    # NOT the plugin's own VERSION (BUNDLE / "VERSION") — independent stream.
    for path in [
        FRAMEWORK_SPEC / "VERSION",
        BUNDLE / "FRAMEWORK_SPEC_VERSION",
        REPO_ROOT / "platforms" / "hermes" / "FRAMEWORK_SPEC_VERSION",
    ]:
        if path.exists():
            path.write_text(new + "\n", encoding="utf-8")

    # Single-declaration files (clean frontmatter — straggler-guarded):
    #   - plugin skills (indented frontmatter)
    #   - canonical playbooks (column-0 frontmatter) — bundle copies follow via sync
    strict_paths = sorted((BUNDLE / "skills").glob("*/SKILL.md"))
    strict_paths += sorted((FRAMEWORK_SPEC / "playbooks").glob("**/*.md"))
    n = bump_fsv(strict_paths, new)

    # SKILL_AUTHORING.md carries the canonical declaration in its frontmatter
    # example PLUS illustrative `framework_spec_version: "..."` strings in prose
    # (the §6 checklist). Bump it but do NOT straggler-guard it — a stale doc
    # example is not a contract violation; conformance only asserts the new value
    # is present.
    skill_authoring = BUNDLE / "docs" / "SKILL_AUTHORING.md"
    if skill_authoring.exists():
        n += bump_fsv([skill_authoring], new)
    print(f"Updated {n} framework_spec_version declaration(s)")

    # Plugin README framework-spec strings (conformance-checked; must be fixed
    # before the pre-commit conformance hook, which runs before sync-version-refs).
    bump_plugin_readme(new)

    # Sync: bundle (propagates canonical playbooks → vendored copies), vendored
    # lint, and the version-string fanout into README/PARITY/CLAUDE.md.
    for sync in [
        REPO_ROOT / "tools" / "sync-plugin-framework.sh",
        REPO_ROOT / "tools" / "sdd_doc_lint" / "sync-vendored.sh",
        REPO_ROOT / "scripts" / "sync-version-refs.sh",
    ]:
        if sync.exists():
            subprocess.run(["bash", str(sync)], check=True)

    # Straggler guard — no skill/playbook frontmatter may still declare old.
    stragglers = [
        str(p.relative_to(REPO_ROOT))
        for p in strict_paths
        if f'framework_spec_version: "{old}"' in p.read_text(encoding="utf-8")
    ]
    if stragglers:
        die(f"{len(stragglers)} file(s) still reference {old}: {stragglers}", 1)

    print(f"Bump complete: framework spec {old} -> {new}")
    print(
        "  Reminder: update the hard-pin in "
        "tests/conformance/platforms/test_plugin_release_metadata.py "
        f'(assertEqual(..., "{new}")) — a deliberate per-release tripwire.'
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
