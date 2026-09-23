"""Conformance: EVAL report canon — REPORT template, RPT tombstoned (P1-1, #664).

Canon (CHG-08): `EVAL-REPORT-TEMPLATE.yaml` is the single report template
(11 sections incl. §4 `test_results`, `EVAL.NN.SS.xxxx` grammar).
`EVAL-RPT-TEMPLATE.yaml` is a tombstone pointer; RPT survives only as the
report *filename* shorthand. The retired `EVAL-NN.BDD-NN.TC-NN.NN` /
`BDD.NN.TC-NN.NN` ID forms are banned from normative template positions
(documentary mentions in tombstone/canon notes are not normative).
"""

import unittest

import yaml
from _spec import FRAMEWORK

LAYER = FRAMEWORK / "layers" / "10_EVAL"
REPORT = LAYER / "EVAL-REPORT-TEMPLATE.yaml"
RPT = LAYER / "EVAL-RPT-TEMPLATE.yaml"
STRATEGY = LAYER / "EVAL-TEMPLATE.yaml"


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


class ReportCanonTests(unittest.TestCase):
    def test_report_has_test_results_section(self):
        """Canon REPORT pins §4 `test_results` with new-grammar case IDs."""
        # NOTE: textual, not parsed — the template mixes a `_guidance` block
        # with a sequence under one key, so it is not a plain YAML mapping.
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Section 4: Test Results", text)
        self.assertIn("test_results:", text)
        self.assertIn('eval_case_id: "EVAL.NN.SS.xxxx"', text)

    def test_rpt_is_tombstone(self):
        """RPT file carries only the tombstone pointer, no report shape."""
        doc = _load(RPT)
        self.assertEqual(
            set(doc), {"tombstone"}, f"RPT tombstone gained keys: {sorted(doc)}"
        )
        self.assertEqual(doc["tombstone"]["status"], "retired")
        self.assertEqual(
            doc["tombstone"]["canonical_template"], "./EVAL-REPORT-TEMPLATE.yaml"
        )

    def test_old_id_forms_banned_from_normative_positions(self):
        """Retired ID forms appear nowhere as template example values."""
        bad = []
        for path in (REPORT, RPT, STRATEGY):
            for i, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1
            ):
                code = line.split("#", 1)[0]
                if "EVAL-NN.BDD-NN" in code or "BDD.NN.TC-NN" in code:
                    bad.append(f"{path.name}:{i}: {line.strip()}")
        self.assertEqual(bad, [], f"retired ID forms in normative positions: {bad}")


if __name__ == "__main__":
    unittest.main()
