"""Conformance: sync-version-refs covers every swept-form pin (T3, #663).

The next MINOR bump must not silently no-op: every old-version literal
standing in a swept form (`framework_spec_version:`, `framework_version:`,
`| Framework Version |`) within the script's scope must be a member of its
`OLD_VERSIONS` list (or the current VERSION). Scopes mirror the script:
frontmatter pins under framework/playbooks/ only (docs/TAGGING.md and
plans/ snapshots are point-in-time prose — reworded, never swept);
metadata rows under framework/ minus framework/archive/CHG-*/ snapshots.

Live execution is deliberately NOT asserted here — the script rewrites and
re-stages files, which a test must not do. Execution (exit 0, idempotent)
is verified manually per IPLAN-08.
"""

import re
import unittest
from pathlib import Path

from _spec import FRAMEWORK, REPO_ROOT

HOOK = REPO_ROOT / "hooks" / "sync-version-refs.sh"
PLAYBOOKS = FRAMEWORK / "playbooks"
VERSION_FILE = FRAMEWORK / "VERSION"
DOCS = REPO_ROOT / "docs"

SPEC_FORM = re.compile(r'framework_spec_version: "(\d+\.\d+\.\d+)"')
META_FORM = re.compile(r'framework_version: "(\d+\.\d+\.\d+)"')
ROW_FORM = re.compile(r"\| Framework Version \| (\d+\.\d+\.\d+) \|")
LIST_RE = re.compile(r'^OLD_VERSIONS="([^"]+)"', re.MULTILINE)


def _hook_text() -> str:
    return HOOK.read_text(encoding="utf-8")


def _old_versions() -> set[str]:
    match = LIST_RE.search(_hook_text())
    assert match, "sync-version-refs.sh carries no OLD_VERSIONS list"
    versions = set(match.group(1).split())
    assert all(re.fullmatch(r"\d+\.\d+\.\d+", v) for v in versions), versions
    return versions


def _current() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def _literals(root: Path, patterns: tuple[re.Pattern, ...]) -> dict[str, list[str]]:
    """Map version literal → files holding it in a swept form (archive excluded)."""
    found: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if "archive/CHG-" in path.as_posix():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for pattern in patterns:
            for version in pattern.findall(text):
                found.setdefault(version, []).append(str(path.relative_to(REPO_ROOT)))
    return found


class SyncVersionRefsCoverage(unittest.TestCase):
    def test_playbook_pins_covered(self):
        """Every frontmatter pin under framework/playbooks/ is current or listed."""
        allowed = _old_versions() | {_current()}
        stray = {
            version: files
            for version, files in _literals(PLAYBOOKS, (SPEC_FORM,)).items()
            if version not in allowed
        }
        self.assertFalse(
            stray,
            f"swept-form pins missing from OLD_VERSIONS: {stray} — extend the list",
        )

    def test_metadata_pins_covered(self):
        """Every metadata/document-control pin under framework/ is current or listed."""
        allowed = _old_versions() | {_current()}
        stray = {
            version: files
            for version, files in _literals(FRAMEWORK, (META_FORM, ROW_FORM)).items()
            if version not in allowed
        }
        self.assertFalse(
            stray,
            f"swept-form pins missing from OLD_VERSIONS: {stray} — extend the list",
        )

    def test_docs_metadata_pins_covered(self):
        """Every metadata/document-control pin under docs/ is current or listed."""
        allowed = _old_versions() | {_current()}
        stray = {
            version: files
            for version, files in _literals(DOCS, (META_FORM, ROW_FORM)).items()
            if version not in allowed
        }
        self.assertFalse(
            stray,
            f"swept-form pins in docs/ missing from OLD_VERSIONS: {stray} — extend the list",
        )

    def test_checkout_pins_current(self):
        """Every `checkout framework/vX` literal outside archive/ pins the current VERSION.

        The bare checkout form is not swept by sync-version-refs.sh (literal
        sweep would risk prefix corruption across OLD_VERSIONS, e.g. 0.96.1
        inside 0.96.13), so this guard fails loudly instead of drifting
        silently (CHG-132, issue #1030).
        """
        pattern = re.compile(r"checkout framework/v(\d+\.\d+\.\d+)")
        current = _current()
        stale: dict[str, list[str]] = {}
        for root in (REPO_ROOT / "docs", REPO_ROOT / ".aidoc"):
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*")):
                if not path.is_file() or "archive/CHG-" in path.as_posix():
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                for version in pattern.findall(text):
                    if version != current:
                        stale.setdefault(version, []).append(str(path.relative_to(REPO_ROOT)))
        self.assertFalse(
            stale,
            f"stale checkout pins (not {current}): {stale} — update to the current VERSION",
        )

    def test_hook_syntax_valid(self):
        """The hook parses under bash (catches refactor breakage)."""
        import subprocess

        result = subprocess.run(
            ["bash", "-n", str(HOOK)], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_root_readme_spec_version_matches(self):
        """Root README.md post-cutover tracking spec citation matches framework/VERSION."""
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        match = re.search(r"tracking framework spec \*\*`([^`]+)`\*\*", readme)
        self.assertIsNotNone(match, "README.md missing tracking framework spec version pattern")
        self.assertEqual(
            match.group(1),
            _current(),
            f"README.md tracking spec version ({match.group(1)}) disagrees with framework/VERSION ({_current()})",
        )


if __name__ == "__main__":
    unittest.main()
