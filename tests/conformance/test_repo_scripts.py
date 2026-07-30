"""Registration shim: pull repo-script unit tests into the conformance suite.

WHY THIS FILE EXISTS. `tests/unit/` is executed by no hook and no workflow —
`.pre-commit-config.yaml` discovers `tests/conformance` only, and the workflows
run `tests/conformance`, `tests/acceptance/deterministic`,
`tools/sdd_doc_lint/tests` and Hermes' own suite. `pre_push_check.sh` invokes no
`unittest` at all. So a test placed under `tests/unit/` proves something once,
locally, and never again after merge.

`unittest discover -s tests/conformance` walks that directory only, so it cannot
reach `tests/unit/` by pattern. This module loads the modules it names
explicitly, via the `load_tests` protocol, so they run wherever the conformance
suite runs — which includes the `always_run` pre-commit hook and the
`Framework + platform conformance` required context.

SCOPE, stated honestly: this registers the modules NAMED BELOW, not the
directory. The other ~30 modules under `tests/unit/` remain unguarded after
merge. Fixing the class rather than the instance — wiring `tests/unit` into
`.pre-commit-config.yaml`, or dropping the `|| true` from the two uncalled
`unittest discover tests/unit` invocations in `tests/scripts/test-plugin.sh` —
is tracked separately and is the better long-term fix.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Modules under tests/unit/ that must run wherever conformance runs.
REGISTERED = ("tests.unit.test_pin_currency_reader",)


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
