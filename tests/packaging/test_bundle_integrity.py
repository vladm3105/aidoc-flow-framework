"""Packaging: bundle/framework/ files are byte-identical to source.

The sync script (`tools/sync-plugin-framework.sh`) uses an explicit allow-list:
  SUBTREES=(layers governance registry)
  ROOT_FILES=(SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)

This test parses that allow-list and asserts every file the sync script WOULD
copy is byte-identical between source and bundle. Complements
`tests/conformance/platforms/test_plugin_framework_bundle.py` (presence check)
with a SHA-256 content check.
"""

import hashlib
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK, plugin_bundle_root


def hash_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parse_sync_allowlist() -> tuple[list[str], list[str]]:
    """Parse `tools/sync-plugin-framework.sh` and return (subtrees, root_files).

    Looks for lines like `SUBTREES=(layers governance registry)` and
    `ROOT_FILES=(SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)`.
    """
    repo_root = FRAMEWORK.parent
    sync = repo_root / "tools" / "sync-plugin-framework.sh"
    if not sync.exists():
        return ["layers", "governance", "registry"], ["SPEC_DRIVEN_DEVELOPMENT_GUIDE.md"]
    text = sync.read_text(encoding="utf-8")
    subtrees: list[str] = []
    root_files: list[str] = []
    m = re.search(r"^\s*SUBTREES=\(([^)]*)\)", text, re.MULTILINE)
    if m:
        subtrees = m.group(1).split()
    m = re.search(r"^\s*ROOT_FILES=\(([^)]*)\)", text, re.MULTILINE)
    if m:
        root_files = m.group(1).split()
    return subtrees, root_files


class BundleIntegrityTests(unittest.TestCase):
    def test_allowlist_parses(self):
        subtrees, root_files = parse_sync_allowlist()
        self.assertTrue(subtrees, "SUBTREES allow-list parsed empty")
        # ROOT_FILES may be empty in some configurations; do not assert non-empty.

    def test_bundle_files_byte_identical_to_source(self):
        subtrees, root_files = parse_sync_allowlist()
        bundle_fw = plugin_bundle_root() / "framework"
        missing: list[str] = []
        drift: list[str] = []
        for sub in subtrees:
            src_root = FRAMEWORK / sub
            if not src_root.exists():
                continue
            for src in src_root.rglob("*"):
                if not src.is_file():
                    continue
                rel = src.relative_to(FRAMEWORK)
                mirror = bundle_fw / rel
                if not mirror.exists():
                    missing.append(str(rel))
                    continue
                if hash_file(src) != hash_file(mirror):
                    drift.append(str(rel))
        for rf in root_files:
            src = FRAMEWORK / rf
            mirror = bundle_fw / rf
            if not src.exists():
                continue
            if not mirror.exists():
                missing.append(rf)
            elif hash_file(src) != hash_file(mirror):
                drift.append(rf)
        self.assertFalse(missing, f"bundle missing files from allow-list: {missing[:5]}")
        self.assertFalse(drift, f"bundle content drift: {drift[:5]}")
