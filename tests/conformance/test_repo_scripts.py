"""Registration shim: pull repo-script unit tests into the conformance suite.

WHY THIS FILE EXISTS. `tests/unit/` is executed by no hook and no workflow —
`.pre-commit-config.yaml` discovers `tests/conformance` only, and the workflows
run `tests/conformance`, `tests/acceptance/deterministic` and
`sdd_doc_lint/tests`. So a test placed under `tests/unit/` proves something
once, locally, and never again after merge.

`unittest discover -s tests/conformance` walks that directory only, so it cannot
reach `tests/unit/` by pattern. This module loads the modules it names
explicitly, via the `load_tests` protocol, so they run wherever the conformance
suite runs — which includes the `always_run` pre-commit hook and the
`Framework + platform conformance` required context.

SCOPE (CLEANUP-001): only runnable modules are registered. Modules coupled to
deleted surfaces (`test_sync_website_badge` → `scripts/sync-version-refs.sh` three-source sweep,
`test_sdd_coverage` → `tools/sdd_coverage.py`, `test_sync_scripts` →
`tools/sync-plugin-framework.sh`, `test_skill_manifests` / `test_nonlayer_skills` /
`test_provisional_ids` / `test_ref_granularity` / `test_reuse_manifest` →
`skill_dirs()`/`plugin_bundle_root()`) stay unregistered until their subjects
return or they are rewritten. Registering an unrunnable module reds the suite,
not the subject. (`test_pin_currency_reader` re-registered by #710: its
subjects were restored under `hooks/`.)
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Modules under tests/unit/ that must run wherever conformance runs.
REGISTERED = (
    "tests.unit.test_pin_currency_reader",
    "tests.unit.test_sdd_doc_lint_trace_resolution",
    "tests.unit.test_spec_helpers",
    "tests.unit.test_template_yaml",
)


def load_tests(loader, tests, pattern):  # noqa: ARG001 — unittest protocol
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    for name in REGISTERED:
        tests.addTests(loader.loadTestsFromName(name))
    return tests


class RegistrationShimTests(unittest.TestCase):
    def test_every_registered_module_exists(self):
        """A typo in REGISTERED would otherwise register nothing, silently —
        `loadTestsFromName` turns an ImportError into a _FailedTest that reports
        as a failure, but only once the module is actually reached."""
        for name in REGISTERED:
            with self.subTest(module=name):
                relative = Path(*name.split(".")).with_suffix(".py")
                self.assertTrue(
                    (REPO_ROOT / relative).is_file(),
                    f"{name} is registered but {relative} does not exist",
                )
