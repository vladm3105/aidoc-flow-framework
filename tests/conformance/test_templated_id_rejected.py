"""Conformance: a PRODUCED artifact carrying a templated placeholder element ID
(``TYPE.NN.SS.xxxx`` / ``TYPE.01.03.xxxx``) is rejected by ``ID03`` + ``ID01``.

Part B of SEED-ABSORPTION-001 (GD-08). The templated ``xxxx`` form is legitimate
in the layer templates and README snippets — it is the *shape* of a future ID —
but must never survive into a produced document artifact, where a real hex ID
(``BDD.01.03.d7a2``) is required. That prevention already exists (``ID03`` at
``__init__.py``: any element-id-shaped token failing ``id_patterns.element``;
``ID01``: the ``@``-tag citation form). What was missing is a regression fixture
pinning it — the nearest negative fixture (``brd-broken-tags.md``) exercises a
different malformed shape (3-segment ``BRD.01.aaaa``), not the templated form. A
refactor of the id scanner could silently stop catching the templated form and no
existing test would fail; this guard closes that gap.

This test PASSES today (the prevention holds); it goes red only if the prevention
is ever removed.
"""

import sys
import unittest

from _spec import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import lint_path  # noqa: E402

FIXTURE = REPO_ROOT / "tests" / "acceptance" / "fixtures" / "negative" / "brd-templated-ids.md"


class TemplatedIdRejected(unittest.TestCase):
    def setUp(self):
        self.assertTrue(FIXTURE.is_file(), f"missing negative fixture: {FIXTURE}")
        self.findings = lint_path(FIXTURE)
        self.codes = [f.code for f in self.findings]

    def test_id03_fires(self):
        """The templated element-id form is rejected as a malformed element id in
        the `id:` declaration, the `@`-tag value, and free prose."""
        self.assertIn(
            "ID03",
            self.codes,
            "ID03 no longer rejects the templated element-id form in a produced artifact",
        )

    def test_id01_fires(self):
        """The templated `@bdd:` citation form is rejected as a malformed trace-tag id."""
        self.assertIn(
            "ID01",
            self.codes,
            "ID01 no longer rejects the templated `@`-tag citation form in a produced artifact",
        )

    def test_fixture_does_not_pass(self):
        """A produced artifact with a templated ID must never lint clean —
        at least one blocking (error-severity) finding is present."""
        errors = [f for f in self.findings if f.severity == "error"]
        self.assertTrue(errors, "templated-ID fixture unexpectedly produced no blocking finding")


if __name__ == "__main__":
    unittest.main()
