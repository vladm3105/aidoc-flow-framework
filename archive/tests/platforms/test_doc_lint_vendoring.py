"""Conformance: the vendored ``sdd_doc_lint`` copies stay byte-identical to the
canonical ``tools/sdd_doc_lint/`` (PLATFORM-ALIGN Part A).

The linter is deliberately vendored into each platform so the plugin's
``on_author`` hook (and a Hermes-side entry) can run it at consumer runtime
without depending on the other platform. To keep that vendoring from drifting
into divergent copies (the D-0013 single-source ethos), this guard asserts the
vendored ``__init__.py`` / ``__main__.py`` / ``trace_graph.py`` (the shared
@-tag trace primitives, CFB-PR-2 DD-1) / ``rehash.py`` (the Model-2 content-hash
verifier, PROVISIONAL-IDS-002) match the canonical source byte-for-byte.

Re-sync after editing the canonical linter:
    bash tools/sdd_doc_lint/sync-vendored.sh
"""

import unittest

from _spec import REPO_ROOT

CANONICAL = REPO_ROOT / "tools" / "sdd_doc_lint"
VENDORED = [
    REPO_ROOT / "platforms" / "claude-code-plugin" / "sdd_doc_lint",
    REPO_ROOT / "platforms" / "hermes" / "sdd_doc_lint",
]
MODULES = ("__init__.py", "__main__.py", "trace_graph.py", "rehash.py")


class DocLintVendoring(unittest.TestCase):
    def test_vendored_copies_are_byte_identical(self):
        canonical = {m: (CANONICAL / m).read_bytes() for m in MODULES}
        for dest in VENDORED:
            for m in MODULES:
                with self.subTest(copy=dest.relative_to(REPO_ROOT).as_posix(), module=m):
                    path = dest / m
                    self.assertTrue(path.is_file(), f"missing vendored linter module: {path}")
                    self.assertEqual(
                        path.read_bytes(),
                        canonical[m],
                        f"{path.relative_to(REPO_ROOT).as_posix()} drifted from the canonical "
                        "tools/sdd_doc_lint — re-run tools/sdd_doc_lint/sync-vendored.sh",
                    )


if __name__ == "__main__":
    unittest.main()
