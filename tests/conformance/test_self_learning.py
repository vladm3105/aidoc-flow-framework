"""Conformance: self-learn governance carries no direct-write exemption (CHG-17)."""

import re
import unittest

from _spec import FRAMEWORK

SELF_LEARNING = FRAMEWORK / "governance" / "SELF_LEARNING.md"

# Language of the removed solo-project exemption (CHG-17 purged it).
EXEMPTION_PATTERNS = [
    re.compile(r"writes directly to governance documents for solo projects"),
    re.compile(r"requiring a CHG record[\s\S]*adds unnecessary latency"),
    re.compile(r"Rules for direct governance updates"),
    re.compile(r"revert to the\nCHG-mediated process"),
]

# Language the authorization routing must carry instead.
REQUIRED_PATTERNS = [
    re.compile(r"authorizing CHG"),
    re.compile(r"In-Progress IPLAN"),
    re.compile(r"no exemption", re.IGNORECASE),
    re.compile(r"self-approved C3"),
]


class SelfLearnAuthorization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SELF_LEARNING.read_text(encoding="utf-8")

    def test_no_direct_write_exemption(self):
        for pattern in EXEMPTION_PATTERNS:
            with self.subTest(pattern=pattern.pattern[:50]):
                self.assertIsNone(
                    pattern.search(self.text),
                    f"exemption language still present: {pattern.pattern[:60]}",
                )

    def test_chg_iplan_routing_present(self):
        for pattern in REQUIRED_PATTERNS:
            with self.subTest(pattern=pattern.pattern[:50]):
                self.assertIsNotNone(
                    pattern.search(self.text),
                    f"authorization routing missing: {pattern.pattern[:60]}",
                )


if __name__ == "__main__":
    unittest.main()
