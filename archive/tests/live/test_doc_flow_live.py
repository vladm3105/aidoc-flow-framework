"""Live acceptance: doc-flow surfaces dual-axis status and refuses confabulation."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import invoke_skill, skipUnlessLive

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import fixtures_for

BANNED_PHRASES = [
    "compact 10-section",
    "documented walkthrough",
    "pinned to lint",
    "enterprise template",
    "10-section markdown variant",
]


@skipUnlessLive
class DocFlowProbeTests(unittest.TestCase):
    def test_doc_flow_reports_dual_axis_and_no_confabulation(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            src = fixtures_for(1, "valid")
            (ws / "docs" / "01_BRD").mkdir(parents=True)
            for item in src.iterdir():
                if item.is_file():
                    (ws / "docs" / "01_BRD" / item.name).write_bytes(item.read_bytes())

            output = invoke_skill(
                "/aidoc-flow:doc-flow scan and report position plus template-conformance drift",
                cwd=ws,
                timeout=420,
                test_id="T3b.docflow",
            )
            lc = output.lower()
            for phrase in BANNED_PHRASES:
                self.assertNotIn(phrase, lc, f"doc-flow used banned phrase: {phrase}")
            self.assertRegex(
                output, r"(?i)progress.*\d+/\d+", "doc-flow output missing progress fraction"
            )
            self.assertRegex(
                output,
                r"(?i)template[- ]conformance",
                "doc-flow output missing template-conformance axis",
            )
