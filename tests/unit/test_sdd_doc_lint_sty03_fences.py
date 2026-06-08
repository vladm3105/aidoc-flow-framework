"""Unit: STY03 (whole-document body size) excludes code-fenced blocks.

Regression for the fence-counting bug: a BDD body is mostly fenced Gherkin,
which the doc-bdd skill allows up to ~50k tokens before a split. STY03 must
count prose only — like STY02 — so a fenced-heavy but prose-light document
does not trip the blocking gate, while a prose-heavy document still does.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root

sys.path.insert(0, str(plugin_bundle_root()))
from sdd_doc_lint import _check_style  # noqa: E402

# BDD STY03 target is 1500 words; blocking at >2250.
_FILLER = " ".join(["word"] * 400)  # 400 prose words per repeat


def _doc(prose_blocks: int, fenced_blocks: int) -> str:
    lines = ["---", "artifact_id: BDD-01", "layer: 4", "---", "# BDD-01", ""]
    for _ in range(prose_blocks):
        lines += ["## Prose", _FILLER, ""]
    for _ in range(fenced_blocks):
        lines += ["## Scenarios", "```gherkin", _FILLER, "```", ""]
    return "\n".join(lines)


def _codes(text: str) -> set[str]:
    return {f.code for f in _check_style(text, "BDD", "BDD-01.md", 0)}


class Sty03FenceExclusionTests(unittest.TestCase):
    def test_fenced_content_does_not_trip_sty03(self):
        # ~800 prose words (under 1500 target) + ~4000 fenced words.
        text = _doc(prose_blocks=2, fenced_blocks=10)
        self.assertNotIn("STY03", _codes(text), "fenced Gherkin must not count toward STY03")

    def test_prose_over_blocking_still_trips_sty03(self):
        # ~2800 prose words, above the 2250 blocking threshold.
        text = _doc(prose_blocks=7, fenced_blocks=0)
        self.assertIn("STY03", _codes(text), "prose over blocking must trip STY03")


if __name__ == "__main__":
    unittest.main()
