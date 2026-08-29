"""Conformance: no pre-commit hook's ``files:`` pattern is dead.

`pre-commit` applies the global ``exclude:`` **after** each hook's ``files:``,
so a path a hook explicitly names can be silently removed from its own trigger.
Nothing reports this: the hook simply prints ``(no files to check) Skipped``,
which is indistinguishable from "this commit touched nothing relevant".

**Regression cover: #574.** `sync-version-refs` declares
``files: '^(platforms/[^/]+/VERSION|framework/VERSION)$'`` and the global
``exclude:`` began ``^(legacy/|framework/|…``. So the `framework/VERSION` half
of its trigger matched nothing: **a framework spec bump could not fire the hook
that exists to propagate it**, while a platform bump could. It stayed invisible
for three reasons — the two settings are read as one predicate but applied in
sequence; the hook always exits 0 and is ``pass_filenames: false``, so a skip
and a successful no-op look identical; and the common bump moves *both* VERSION
files, so the hook fires anyway for the platform path and the dead half is
invisible in exactly the case a contributor would check.

The invariant is asserted over **real repository paths** rather than by
reasoning about the two regexes: a hook that names a pattern must have at least
one file in the tree that both matches it and survives the exclude. That is
stronger than checking the one path #574 named, and it is what makes this a
guard on the class rather than on the instance.
"""

from __future__ import annotations

import re
import subprocess
import unittest

import yaml
from _spec import REPO_ROOT

CONFIG = REPO_ROOT / ".pre-commit-config.yaml"

# Hooks whose `files:` is deliberately narrower than anything in the tree would
# satisfy are not defects. None exist today; the empty tuple is the seam, so a
# future exemption has to be named here rather than weakening the assertion.
KNOWN_UNREACHABLE: tuple = ()


def _tracked_files() -> list:
    out = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return out.stdout.splitlines()


class PreCommitTriggersAreReachable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CONFIG.open(encoding="utf-8") as fh:
            cls.config = yaml.safe_load(fh)
        cls.files = _tracked_files()
        cls.exclude = re.compile(cls.config["exclude"]) if cls.config.get("exclude") else None

    def test_a_global_exclude_is_declared(self):
        """Guards the guard: with no `exclude:` every assertion below passes vacuously."""
        self.assertIsNotNone(self.exclude, "no global exclude: — this module would prove nothing")

    def test_every_hook_files_pattern_matches_something_that_survives_exclude(self):
        checked = 0
        for repo in self.config.get("repos", []):
            for hook in repo.get("hooks", []):
                pattern = hook.get("files")
                if not pattern:
                    continue
                hook_id = hook.get("id", "<unnamed>")
                if hook_id in KNOWN_UNREACHABLE:
                    continue
                checked += 1
                with self.subTest(hook=hook_id):
                    matcher = re.compile(pattern)
                    matched = [f for f in self.files if matcher.search(f)]
                    self.assertTrue(
                        matched,
                        f"{hook_id}: files: {pattern!r} matches no tracked file at all",
                    )
                    survivors = [f for f in matched if not self.exclude.match(f)]
                    self.assertTrue(
                        survivors,
                        f"{hook_id}: every file matching its own files: pattern "
                        f"{pattern!r} is removed by the global exclude:, so the hook "
                        f"can never fire. Matched but excluded: {matched[:5]}",
                    )
        self.assertGreater(checked, 0, "no hook declares files: — the walk found nothing")

    def test_sync_version_refs_can_fire_on_a_framework_bump(self):
        """#574 named, so a failure says *what* broke rather than *which hook*.

        Asserted on both halves of the trigger. The platform half never broke,
        and including it is the point: it is why the defect survived — a bump
        that moves both files fires the hook for the wrong reason.
        """
        hooks = [h for r in self.config.get("repos", []) for h in r.get("hooks", [])]
        hook = next((h for h in hooks if h.get("id") == "sync-version-refs"), None)
        self.assertIsNotNone(hook, "sync-version-refs hook not found")
        matcher = re.compile(hook["files"])

        # The second path trips detect-secrets as "Base64 High Entropy String". It is a
        # repository path, not a credential; the pragma must sit on the flagged line.
        for path in (
            "framework/VERSION",
            "platforms/claude-code-plugin/VERSION",  # pragma: allowlist secret
        ):
            with self.subTest(path=path):
                self.assertTrue(matcher.search(path), f"{path} is not in the hook's files:")
                self.assertFalse(
                    self.exclude.match(path),
                    f"{path} matches the hook's files: but is removed by the global "
                    "exclude:, so bumping it cannot trigger the version-reference fanout",
                )

    def test_the_spec_tree_is_still_excluded(self):
        """The carve-out spares one path — not the tree it sits in.

        Without this, widening the exclude to fix #574 would silently expose the
        GATE-SPEC-governed spec and its byte-identical plugin mirror to the
        autofixing hooks, which is the reason the exclude exists.
        """
        for path in (
            "framework/governance/DECISIONS.md",
            "framework/layers/01_BRD/BRD-TEMPLATE.yaml",
            "framework/registry/LAYER_REGISTRY.yaml",
            "platforms/claude-code-plugin/framework/governance/DECISIONS.md",
        ):
            with self.subTest(path=path):
                self.assertTrue(
                    self.exclude.match(path),
                    f"{path} is no longer excluded — an autofixing hook may now rewrite "
                    "the spec tree or its byte-identical vendored mirror",
                )


if __name__ == "__main__":
    unittest.main()
