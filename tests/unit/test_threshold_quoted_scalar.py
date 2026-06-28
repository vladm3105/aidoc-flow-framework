"""Unit: an inline ``@threshold:`` that ends a quoted YAML scalar must NOT
false-fire TH01 (YAML-BDD-SCHEMA Pass-2 LB-1).

When BDD scenarios move into a ``​```yaml`` block, a step is a quoted scalar
and a trailing ``@threshold:`` sits right before the closing ``'``/``"``. The
``_THRESHOLD`` capture must stop before that quote so the threshold token stays
well-formed (else the quote is glommed into the value and TH01 fires).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Resolve sdd_doc_lint to the canonical tools/ copy.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from sdd_doc_lint import (  # noqa: E402
    _THRESHOLD,
    _THRESHOLD_FORM,
    _load_registry,
    lint_text,
)


class ThresholdQuotedScalar(unittest.TestCase):
    def test_capture_excludes_trailing_quote(self) -> None:
        for line in (
            "  - 'the API SHALL redirect WITHIN @threshold:PRD.01.perf.redirectp95'",
            '  - "the API SHALL redirect WITHIN @threshold:PRD.01.perf.redirectp95"',
        ):
            m = _THRESHOLD.search(line)
            self.assertIsNotNone(m, line)
            self.assertEqual(m.group(1), "PRD.01.perf.redirectp95", line)
            self.assertTrue(_THRESHOLD_FORM.match(m.group(1)), line)

    def test_mid_scalar_threshold_still_captured(self) -> None:
        # A threshold not at the quote boundary must remain unaffected.
        line = "  - 'within @threshold:PRD.01.rate.window per second'"
        m = _THRESHOLD.search(line)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "PRD.01.rate.window")

    def test_no_th01_on_quoted_scalar_threshold(self) -> None:
        layers, doc_re, elem_re = _load_registry(None)
        text = (
            "---\ndoc_id: BDD-01\nartifact_type: BDD\n---\n\n"
            "```yaml\n"
            "scenarios:\n"
            "  then:\n"
            "    - 'the API SHALL redirect WITHIN @threshold:PRD.01.perf.redirectp95'\n"
            "```\n"
        )
        findings = lint_text(text, "BDD", "BDD-01.md", layers, doc_re, elem_re)
        self.assertEqual([f for f in findings if f.code == "TH01"], [])


if __name__ == "__main__":
    unittest.main()
